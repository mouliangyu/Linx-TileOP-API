#!/usr/bin/env python3
"""Validate overload inventory and evidence freshness; render the review ledger."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'TileOpContractLedger.json'
REPORT = ROOT / 'TileOpContractLedger.md'
DIMENSIONS = ('declaration', 'roles', 'types', 'geometry', 'parameters', 'semantics', 'sources', 'examples')
LABELS = dict(zip(DIMENSIONS, ('声明', '角色', '类型配对', '形状', '参数编码', '语义', '来源', '示例')))
STATES = {'pending': '待核对', 'inventoried': '已登记', 'issue': '有缺口', 'verified': '已核实', 'not_applicable': '不适用'}


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def inventory():
    result = []
    for page in sorted((ROOT / 'TileOpReference').glob('*.md')):
        if not page.stem.isupper() or page.stem == 'README':
            continue
        text = page.read_text()
        section = text.split('## 声明与重载', 1)[1].split('## 参数与操作数角色', 1)[0]
        declarations = []
        for block in re.findall(r'```cpp\n(.*?)```', section, re.S):
            for match in re.finditer(r'(template\s*<.*?\b' + re.escape(page.stem) + r'\s*\(.*?\)\s*;)', block, re.S):
                signature = match.group(1).strip()
                # Exclude preceding helper declarations when a block defines a struct.
                normalized = ' '.join(signature.split())
                declarations.append((signature, normalized))
        expected = len(re.findall(r'\b' + re.escape(page.stem) + r'\s*\([^;]*\)\s*;', '\n'.join(re.findall(r'```cpp\n(.*?)```', section, re.S)), re.S))
        if not declarations or len(declarations) != expected:
            raise ValueError(f'{page.name}: extracted {len(declarations)}, declaration count {expected}')
        for ordinal, (signature, normalized) in enumerate(declarations, 1):
            result.append(dict(id=page.stem + '-' + digest(normalized)[:12], op=page.stem,
                               ordinal=ordinal, page='TileOpReference/' + page.name,
                               signature=signature, signature_hash=digest(normalized)))
    return result


def validate(data):
    errors = []
    current = {row['id']: row for row in inventory()}
    # Operation signatures have one home; public pages illustrate calls instead.
    operations = {row['op'] for row in current.values()}
    names = '|'.join(re.escape(op) for op in sorted(operations, key=len, reverse=True))
    declaration = re.compile(
        r'\b(?:void|auto|bool|unsigned|int|size_t|u?int\d+_t|Tile(?:\s*<[^;{}]+>)?)'
        r'\s+(' + names + r')\s*\([^;{}]*\)\s*;', re.S)
    for page in sorted((ROOT / 'TileOpReference').glob('*.md')):
        for block in re.findall(r'```(?:cpp|c\+\+|c)\n(.*?)```', page.read_text(), re.S):
            for match in declaration.finditer(block):
                if match.group(1) != page.stem:
                    errors.append(f'{page.name}: operation declaration belongs in {match.group(1)}.md')
    entries = data['overloads']
    public = data.get('public_contracts', {})
    recorded = {row['id']: row for row in entries}
    if 'blockers' in data:
        assigned = set()
        for blocker in data['blockers']:
            if not blocker.get('description') or not blocker.get('overloads'):
                errors.append('empty blocker: ' + blocker.get('id', '?'))
            for ident in blocker.get('overloads', []):
                if ident not in recorded or recorded[ident].get('closed'):
                    errors.append('blocker references missing/closed overload: ' + ident)
                assigned.add(ident)
        for row in entries:
            if not row.get('closed') and row['id'] not in assigned:
                errors.append('open overload lacks blocker group: ' + row['id'])
    if len(entries) != len(recorded):
        errors.append('duplicate overload IDs')
    for ident in current.keys() - recorded.keys():
        errors.append('unregistered declaration: ' + ident)
    for ident in recorded.keys() - current.keys():
        errors.append('removed/changed declaration: ' + ident)
    for path, fingerprint in data['document_fingerprints'].items():
        file = ROOT / path
        if not file.exists() or digest(file.read_text()) != fingerprint:
            errors.append('document changed; reassess dependent records: ' + path)
    for path, fingerprint in data.get('support_fingerprints', {}).items():
        file = ROOT / path
        if not file.exists() or digest(file.read_text()) != fingerprint:
            errors.append('shared evidence changed; reassess dependencies: ' + path)
    for ident, check in public.items():
        if check.get('status') not in STATES or not check.get('evidence'):
            errors.append('invalid public contract: ' + ident)
        for ref in check.get('references', []):
            if '://' not in ref and not (ROOT / ref.split('#', 1)[0]).is_file():
                errors.append('missing public reference: ' + ident + ': ' + ref)
    actual_pages = {str(p.relative_to(ROOT)) for p in (ROOT / 'TileOpReference').glob('*.md')}
    if actual_pages != set(data['document_fingerprints']):
        errors.append('reference page inventory changed')
    for row in entries:
        if row['id'] in current and row['signature_hash'] != current[row['id']]['signature_hash']:
            errors.append('signature mismatch: ' + row['id'])
        if set(row['checks']) != set(DIMENSIONS):
            errors.append('missing review dimensions: ' + row['id'])
        for key, check in row['checks'].items():
            if check['status'] not in STATES:
                errors.append('unknown state: ' + row['id'] + '/' + key)
            if check['status'] in ('verified', 'not_applicable', 'issue') and not check.get('evidence'):
                errors.append('missing evidence: ' + row['id'] + '/' + key)
            for ref in check.get('references', []):
                if '://' not in ref and not (ROOT / ref.split('#', 1)[0]).is_file():
                    errors.append('missing evidence reference: ' + row['id'] + ': ' + ref)
        if row.get('closed') and any(c['status'] not in ('verified', 'not_applicable') for c in row['checks'].values()):
            errors.append('invalid closure: ' + row['id'])
        if row.get('closed'):
            if not row.get('branches') or not row.get('dependencies'):
                errors.append('closure lacks branch/dependency scope: ' + row['id'])
            for dep in row.get('dependencies', []):
                if public.get(dep, {}).get('status') not in ('verified', 'not_applicable'):
                    errors.append('unverified closure dependency: ' + row['id'] + ': ' + dep)
            if row.get('validation', {}).get('spec_review') != 'verified':
                errors.append('closure lacks spec review: ' + row['id'])
            for issue in row.get('issues', []):
                if not row.get('issue_disposition', {}).get(issue):
                    errors.append('closure lacks issue disposition: ' + row['id'] + ': ' + issue)
        elif not row.get('remaining_work'):
            errors.append('open overload lacks next review action: ' + row['id'])
    return errors


def render(data):
    rows = data['overloads']
    lines = ['# TileOP 逐重载核对表', '',
             '维护规则见 [核对流程](TileOpContractReview.md)。机器可读记录为 [JSON 台账](TileOpContractLedger.json)。', '',
             f"当前登记 {len(set(r['op'] for r in rows))} 个操作、{len(rows)} 条重载声明；闭合 {sum(bool(r.get('closed')) for r in rows)} 条。", '',
             '已登记表示从正文提取了声明或查询入口；已核实需要逐项证据。示例存在、页面结构通过均不自动提升为语义已核实。', '',
             '## 核对进度', '', '| 维度 | 已核实 | 不适用 | 有缺口 | 待核对 | 已登记 |', '| --- | ---: | ---: | ---: | ---: | ---: |']
    for key in DIMENSIONS:
        counts = Counter(r['checks'][key]['status'] for r in rows)
        lines.append('| ' + LABELS[key] + ' | ' + ' | '.join(str(counts[s]) for s in ('verified', 'not_applicable', 'issue', 'pending', 'inventoried')) + ' |')
    lines += ['', '设计合同闭合与实现验证分别记录。示例规范推导完成不代表已编译或已在硬件运行。', '',
              '## 公共依赖', '', '| 范围 | 状态 | 结论与证据 |', '| --- | --- | --- |']
    for ident, check in sorted(data.get('public_contracts', {}).items()):
        links = ' '.join(f'[{ref.rsplit("/", 1)[-1]}]({ref})' for ref in check.get('references', []))
        lines.append(f'| {ident} | {STATES[check["status"]]} | {check["evidence"].replace("|", "/")} {links} |')
    lines += ['', '带后缀的公共项只闭合所列范围；完整项包含其他存储和操作分支。', '',
              '## 剩余问题分组', '',
              '同一公共问题可影响多条重载，下表的影响数会重叠；每条重载仍保留自己的八维证据。', '',
              '| 问题 | 影响重载 | 当前证据与关闭条件 |', '| --- | ---: | --- |']
    for blocker in data.get('blockers', []):
        lines.append('| ' + blocker['id'] + ' | ' + str(len(blocker['overloads'])) +
                     ' | ' + blocker['description'].replace('|', '/') + ' |')
    lines += ['', '## 模型验证记录', '']
    for note in data.get('model_validation_notes', []):
        lines.append('- ' + note['id'] + '：' + note['evidence'] + ' 执行状态：' + note['execution'] + '。')
    lines += ['',
              '## 未闭合队列', '', '| 操作 | 剩余重载 | 具体下一步 |', '| --- | ---: | --- |']
    for op in sorted(set(r['op'] for r in rows if not r.get('closed'))):
        subset = [r for r in rows if r['op'] == op and not r.get('closed')]
        reasons = list(dict.fromkeys(r['remaining_work'] for r in subset))
        lines.append(f'| [{op}](#{op.lower()}) | {len(subset)} | ' + '；'.join(reasons).replace('|', '/') + ' |')
    lines += ['', '## 操作索引', '', '| 操作 | 重载数 | 已闭合 | 记录 |', '| --- | ---: | ---: | --- |']
    for op in sorted(set(r['op'] for r in rows)):
        subset = [r for r in rows if r['op'] == op]
        lines.append(f'| {op} | {len(subset)} | {sum(bool(r.get("closed")) for r in subset)} | [核对记录](#{op.lower()}) |')
    for op in sorted(set(r['op'] for r in rows)):
        lines += ['', '## ' + op, '']
        for row in (r for r in rows if r['op'] == op):
            lines += ['### ' + row['id'], '', f"声明序号 {row['ordinal']}；[操作页]({row['page']})。", '', '```cpp', row['signature'], '```', '',
                      '| 核对项 | 状态 | 条文入口与证据 |', '| --- | --- | --- |']
            for key in DIMENSIONS:
                check = row['checks'][key]
                evidence = check.get('evidence', '尚未逐项核对。')
                links = ' '.join(f'[{ref.rsplit("/", 1)[-1]}]({ref})' for ref in check.get('references', []))
                lines.append(f'| {LABELS[key]} | {STATES[check["status"]]} | {evidence.replace(chr(10), " ").replace("|", " / ")} {links} |')
            lines += ['', '闭合：' + ('已闭合' if row.get('closed') else '未闭合；' + row['remaining_work']), '',
                      '核对分支：' + '；'.join(row.get('branches', ['见各维度证据。'])), '',
                      '公共依赖：' + '、'.join(row.get('dependencies', ['尚未完成依赖绑定。'])), '',
                      '验证记录：`' + json.dumps(row.get('validation', {}), ensure_ascii=False) + '`', '',
                      '来源入口：' + ('；'.join(row['source_candidates']) or '待定位。'), '',
                      '关联问题：' + ('、'.join(row['issues']) or '无已登记问题。')]
    REPORT.write_text('\n'.join(lines) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    args = parser.parse_args()
    data = json.loads(DATA.read_text())
    errors = validate(data)
    if errors:
        print('\n'.join(errors))
        raise SystemExit(1)
    if args.render:
        render(data)
    print(f"PASS: {len(data['overloads'])} overload records; declaration inventory and document fingerprints match. Semantic closure is tracked separately.")


if __name__ == '__main__':
    main()
