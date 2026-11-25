#!/usr/bin/env python3
"""Regenerate the review catalog from the pinned PTO-C checkout (no compilation)."""
import pathlib, re, subprocess, sys
root = pathlib.Path(sys.argv[1] if len(sys.argv)>1 else '.work/Linx-TileOP-API')
out = pathlib.Path(__file__).resolve().parent
src = root / 'include/jcore/template_asm.hpp'
s = src.read_text()
names = {}
for m in re.finditer(r'\b(?:void|SharedTile<[^>]+>)\s+((?:T[A-Z]|MGATHER|MSCATTER|GMOV|ACC)[A-Za-z0-9_]*)\s*\(', s):
    names.setdefault(m.group(1), s.count('\n',0,m.start())+1)
for m in re.finditer(r'^PTO_(?:DEFINE_\w+|TEPL_ASS_\w+)\((\w+)',s,re.M):
    n=m.group(1)
    if re.match(r'(?:T[A-Z]|MGATHER|MSCATTER)',n):
        n += '_ASS' if 'TEPL_ASS_' in m.group() else ''
        names.setdefault(n,s.count('\n',0,m.start())+1)
retired=set('ACCCVT ACCCVT_RMAX_SCALE_NZ2DN ACCSCALE_NZ2DN ACCSCALE_T THISTOGRAM TFMOD TFMODS TPRELU TADDC TSUBC TLRELU TAXPY TADDSC TSUBSC TEXTRACT TINSERT TFILLPAD TRANDOM TQUANT TDEQUANT TSORT TSORT32 TMRGSORT TTRANS TPARTADD TPARTMUL TPARTMAX TPARTMIN TCONCAT TGATHERB'.split())
alias={'TCVT_T':'TCVT','TCI_ROW':'TCI_2D','TCI_COL':'TCI_2D'}
# Each item stores real data operands; common blocks expand to scalar parameters.
ops={}
def add(ns,args,family):
    for n in ns.split():ops[n]=(args,family)
add('TADD TSUB TMUL TDIV TREM TAND TOR TXOR TSHL TSHR TMAX TMIN TEXPDIF','OUT, IN(a), IN(b), GEOMETRY, FORMAT','TEPL binary')
add('TABS TNOT TNEG TEXP TLOG TRECIP TSQRT TRSQRT TRELU','OUT, IN(src), GEOMETRY, FORMAT','TEPL unary')
add('TADDS TSUBS TMULS TDIVS TREMS TANDS TORS TXORS TSHLS TSHRS TMAXS TMINS','OUT, IN(src), uint64_t scalar_bits, GEOMETRY, FORMAT','TEPL scalar')
add('TCMP','OUT, IN(a), IN(b), unsigned cmp_mode, GEOMETRY, FORMAT','compare')
add('TCMPS','OUT, IN(src), uint64_t scalar_bits, unsigned cmp_mode, GEOMETRY, FORMAT','compare scalar')
add('TCVT','OUT, IN(src), unsigned rounding_mode, GEOMETRY, FORMAT','convert')
add('TFMA','OUT, IN(a), IN(b), IN(c), GEOMETRY, FORMAT','fma')
add('TSEL','OUT, IN(predicate), IN(true_value), IN(false_value), GEOMETRY, FORMAT','select: false_value is old dst in PTO wrapper')
add('TSELS','OUT, IN(predicate), IN(true_value), uint64_t false_scalar_bits, GEOMETRY, FORMAT','select scalar')
add('TEXPANDS','OUT, uint64_t scalar_bits, GEOMETRY, FORMAT','splat')
add('TCI','OUT, uint64_t start_bits, unsigned descending, GEOMETRY, FORMAT','iota 1D')
add('TCI_2D','OUT, uint64_t start_bits, uint64_t packed_row_col_steps, GEOMETRY, FORMAT','iota 2D')
add('TTRI','OUT, GEOMETRY, FORMAT','triangle')
add('TGPR2T','OUT, uint64_t gpr0, uint64_t gpr1, uint64_t gpr2, uint64_t gpr3, GEOMETRY, FORMAT','gpr to tile')
for axis in ('ROW','COL'):
    add(' '.join('T'+axis+x for x in ('SUM','MAX','MIN','PROD','ARGMAX','ARGMIN')),'OUT, IN(src), GEOMETRY, FORMAT','reduce: source geometry')
    add('T'+axis+'EXPAND','OUT, IN(src), GEOMETRY, FORMAT','expand: output geometry')
    add(' '.join('T'+axis+'EXPAND'+x for x in ('ADD','SUB','MUL','DIV','MAX','MIN','EXPDIF')),'OUT, IN(a), IN(b), GEOMETRY, FORMAT','expand binary: output geometry')
add('TGATHER TSCATTER','OUT, IN(src), IN(indices), GEOMETRY, FORMAT','local index: indices geometry')
add('TPERMUTE','OUT, IN(a), IN(b), IN(indices), GEOMETRY, FORMAT','permute')
add('TSHUF','OUT, IN(src), IN(controls), uint64_t control, GEOMETRY, FORMAT','shuffle')
add('TPACK','OUT, IN(a), IN(b), uint64_t control, GEOMETRY, FORMAT','pack')
add('TUNPACK','OUT, IN(src), uint64_t control, GEOMETRY, FORMAT','unpack')
add('TLOAD TLOAD_CUBE','OUT, const void *base, int64_t stride_bytes, GEOMETRY, FORMAT, unsigned memory_dtype','load')
add('TLOAD_WEIGHT','OUT, const void *base, uint64_t shape_word, uint64_t start_word, GEOMETRY, FORMAT, unsigned memory_dtype','weight load')
add('TLOAD_SLOT','unsigned slot, unsigned size_code, const void *base, uint64_t shape_word, uint64_t start_word, GEOMETRY, FORMAT, unsigned memory_dtype','fixed shared slot weight load')
add('TSTORE TSTORE_CUBE TSTORE_PART','void *base, int64_t stride_bytes, IN(src), GEOMETRY, FORMAT, unsigned memory_dtype','store')
add('TPREFETCH','const void *base, int64_t stride_bytes, GEOMETRY, FORMAT','prefetch')
for k in (2,4):
    for layout in ('ND2NZ','ND2ZN','DN2ZN'):
        add(f'TLOAD{k}_{layout}',', '.join(f'OUT_N(d{i})' for i in range(k))+', const void *base, int64_t stride_bytes, GEOMETRY, FORMAT, unsigned memory_dtype','multi-output load (one block)')
add('TSTORE2_DN2DN','void *base, int64_t stride_bytes, IN(src0), IN(src1), GEOMETRY, FORMAT, unsigned memory_dtype','two-source store')
add('TMOV TMOV_L2S_INSERT TMOV_L2S_PUBLISH TMOV_CUBE_TO_SHARED_ND TMOV_SHARED_ND_TO_CUBE TMOV_S2L_BROADCAST TMOV_S2L_EXTRACT','OUT, IN(src), GEOMETRY, FORMAT','move; per-op Local/Shared constraints')
add('GMOV','OUT, IN(src), uint64_t peer_tid, GEOMETRY, FORMAT','peer move')
add('TIMG2COL TIMG2COL_SPART','OUT, const void *base, uint64_t param0, uint64_t param1, uint64_t param2, GEOMETRY, FORMAT','image to column')
add('TIMG2COL_SPART_SLOT','unsigned slot, unsigned size_code, const void *base, uint64_t param0, uint64_t param1, uint64_t param2, GEOMETRY, FORMAT','fixed shared slot image')
add('MGATHER','OUT, const void *base, IN(byte_offsets), RANGE, GEOMETRY, FORMAT','gather; byte offsets')
add('MGATHER_MASK','OUT, const void *base, IN(byte_offsets), IN(predicate), RANGE, GEOMETRY, FORMAT','masked gather')
add('MSCATTER','void *base, IN(byte_offsets), IN(values), RANGE, GEOMETRY, FORMAT','scatter; byte offsets')
add('MSCATTER_MASK','void *base, IN(byte_offsets), IN(values), IN(predicate), RANGE, GEOMETRY, FORMAT','masked scatter')
add('MGATHER_CAS','OUT, void *base, IN(indices), IN(expected), IN(replacement), RANGE, GEOMETRY, FORMAT','atomic CAS: old-value output')
for n in 'EXCH MAX MIN ADD INC DEC AND OR XOR'.split():
    add('MGATHER_'+n,'OUT, void *base, IN(indices), IN(value_or_limit), RANGE, GEOMETRY, FORMAT','atomic with old-value output')
for n in 'MAX MIN ADD INC DEC AND OR XOR'.split():
    add('MSCATTER_'+n,'void *base, IN(indices), IN(value_or_limit), RANGE, GEOMETRY, FORMAT','atomic reduction without output')
add('MSCATTER_POPC','void *base, IN(indices), RANGE, GEOMETRY, FORMAT','atomic popcount: no values operand')
for n in 'ADD MIN MAX AND OR XOR INC DEC'.split():
    add('TSTORE_ATOMIC_'+n,'void *base, int64_t stride_bytes, IN(src), unsigned predicate_enabled, IN(predicate), unsigned predicate_invert, GEOMETRY, FORMAT','atomic store Local/Shared; predicated Local only')
for prefix in ('TMATMUL','TGEMV'):
    for suffix in ('','_ACC','_BIAS','_MX','_MX_ACC','_MX_BIAS'):
        args=['OUT','IN(a)','IN(b)']
        if 'ACC' in suffix:args+=['IN(accum)']
        if 'BIAS' in suffix:args+=['IN(bias)']
        if 'MX' in suffix:args+=['unsigned scale_mask','IN(scale_a)','IN(scale_b)']
        args+=['int64_t m','int64_t n','int64_t k','FORMAT','FPATR']
        add(prefix+suffix,', '.join(args),'CUBE with explicit FPATR extra operands/results')
add('TMATMUL_SLOT','OUT, unsigned slot_a, unsigned slot_b, unsigned a_dtype, unsigned b_dtype, int64_t m, int64_t n, int64_t k, FORMAT, FPATR','fixed shared input slots; not assemble')
pred={'compare_scalar':'TCMPS','logical_and':'TAND','logical_or':'TOR','logical_xor':'TXOR','select':'TSEL','select_scalar':'TSELS','scatter':'MSCATTER_MASK'}
add('PREDICATE_SUBVIEW','OUT, IN(src), GEOMETRY, FORMAT','predicate materialization via TMOV plus SUBVIEW')
add('PREDICATE_CONCATENATE','OUT, IN(left), IN(right), GEOMETRY, FORMAT','two TAND assemble blocks, not one opcode')
add('PREDICATE_LOGICAL_NUMERIC','OUT, IN(predicate), IN(numeric), unsigned logical_opcode, GEOMETRY, FORMAT','U8 logical numeric')
add('PREDICATE_ATOMIC_ADD','void *base, IN(offsets), IN(values), IN(predicate), unsigned predicate_invert, RANGE, GEOMETRY, FORMAT','predicate atomic add')
unknown=[];rows=[]
for n,line in sorted(names.items()):
    if n in retired:target='—';state='退役诊断，不定义 builtin'
    elif n in ('TTRANS_ASS','TCONCAT_ASS'):target='—';state='冲突：普通 selector 退役，但 ASS 宏仍存在；待 ISA 核对'
    else:
        base=alias.get(n,n[:-4] if n.endswith('_ASS') else n)
        if base not in ops:unknown.append(n);continue
        target='`__builtin_'+base.lower()+'`'
        state='ASS 阶段参数' if n.endswith('_ASS') else ('别名；ROW=(1,0)，COL=(0,1)' if n in ('TCI_ROW','TCI_COL') else '参数映射')
    rows.append(f'| `{n}` | {target} | {state} | [L{line}](https://github.com/LinxISA/Linx-TileOP-API/blob/REV/include/jcore/template_asm.hpp#L{line}) |')
assert not unknown,unknown
rev=subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()

# Internal schema abbreviations are expanded in every published prototype.
PARAMETER_GROUPS = {'OUT': 'T_dst *dst, unsigned dst_space, unsigned capacity_code, unsigned assemble_phase, int64_t dst_base_units, unsigned dst_offset_units, unsigned writer_size_code', 'OUT_N(x)': 'T_x *x, unsigned x_space, unsigned x_capacity_code', 'IN(x)': 'T_x x, unsigned x_space, unsigned x_dtype, unsigned x_capacity_code, unsigned x_view_enabled, int64_t x_view_base_units, unsigned x_view_offset_units, unsigned x_view_size_code', 'GEOMETRY': 'int64_t lb0, int64_t lb1, int64_t lb2', 'FORMAT': 'unsigned operation_dtype, unsigned layout, unsigned pad, unsigned pe_mask', 'RANGE': 'unsigned range_enabled, uint64_t range_min, uint64_t range_max', 'FPATR': 'unsigned pre_quant, unsigned relu, unsigned group_n_code, unsigned row_max_enable, unsigned group_max_enable, unsigned row_max_init, unsigned max_abs_enable, unsigned transpose_a, unsigned transpose_b, unsigned cscale_enable, unsigned cube_control, uint64_t quant_descriptor, uint64_t lrelu_descriptor, IN(quant), IN(relu_parameter), IN(row_max_in), IN(cscale), OUT_N(row_max_out), OUT_N(group_max_out)'}

def expand_parameters(args):
    result = []
    for arg in args.split(','):
        arg = arg.strip()
        match = re.fullmatch(r'(IN|OUT_N)\((\w+)\)', arg)
        if match:
            kind, name = match.groups()
            group = PARAMETER_GROUPS[kind + '(x)']
            group = re.sub(r'\bx(?=\b|_)', name, group).replace('T_x', 'T_' + name)
            result.extend(expand_parameters(group))
        elif arg in PARAMETER_GROUPS:
            result.extend(expand_parameters(PARAMETER_GROUPS[arg]))
        else:
            result.append(arg)
    return result

header='''# 逐项 C builtin 原型目录

此文件由 `build_tile_builtin_catalog.py` 生成。它是接口设计 schema，尚不是 Clang 支持的 C 头文件。
所有操作统一 `void` 返回，目标通过显式输出位置传入；输入 tile 仍为向量值。
`T`/`T_a`/`T_b` 等表示独立选取容量的向量类型；它们是签名元变量，不是 C++ 模板或一个固定宽度 typedef。
Shared 操作数的值类型为 target Shared carrier，并要求 `space=SHARED`；不能用普通整数冒充 Local tile。

## 参数约定

每个原型都完整列出所有参数，不使用参数宏、descriptor struct 或 `...` 可变参数。

`capacity_code` 为普通输出容量或 INIT parent 容量；没有重复的 dst_size/parent_size。
`dst_base_units + dst_offset_units` 是片段在 parent 内的偏移（128 B 单位），**不是 tile 队列的相对索引**。
parent 身份由 `dst` 指定；队列相对索引由后端分配。
输入参数的 view 基址也表示片段偏移，binder 的输入编号由参数位置决定。
`NONE/INIT/MIDDLE/LAST/INIT_LAST` 分别是无 modifier、(1,0)、(0,0)、(0,1)、(1,1)；
NONE 与 MIDDLE 不能因 INIT/LAST 都为零而混淆。
`NONE` 时 writer/base/offset 必须为零，容量仍有效；无 view 时其 base/offset/size 必须为零。

所有编码枚举、size、space、phase、offset、enable、PE mask 为编译期常量；
DIM、地址、步长、标量位模式、参数控制字、base 可以运行时传入。
标量采用 dtype 对应的原始位模式，浮点不做数值到整数转换。
可选 tile 禁用时必须传对应类型的零载体，可选输出禁用时传 null；编译器不生成这些 binder，不能传未初始化值。
`range_min/range_max` 保留 PTO-C IndexedByteRange 的字节边界语义，不擅自改成元素编号。
atomic 的 indices 单位须随具体 opcode 核对，不能套用普通 MGATHER 的 byte offsets。

公共字段是设计超集，不意味着所有操作都允许 view/assemble/FPATR 全组合。
不支持的字段必须为零并由 Sema 拒绝非法组合；下方 ASS 映射是已发现的支持证据。
Fixed Shared SLOT 是 S0..S63 名称，和 assemble phase 无关。
FPATR enable 与可选 operands/results 必须按 Options 的合法组合检查，不能仅保留一个 fixp_mode。

## 原型（每个入口单独列出）

'''
for n,(args,fam) in sorted(ops.items()):
    parameters = expand_parameters(args)
    parameter_names = [p.split()[-1].lstrip('*') for p in parameters]
    assert len(parameter_names) == len(set(parameter_names)), (n, parameter_names)
    declaration = ',\n'.join('    ' + p for p in parameters)
    header+=f'### `__builtin_{n.lower()}`\n\n{fam}\n\n```c\nvoid __builtin_{n.lower()}(\n{declaration});\n```\n\n'
(out/'TileBuiltinPrototypes.md').write_text(header)
cov=f'''# PTO-C 名称逐项映射

来源 commit：`{rev}`。共 {len(names)} 个 template_asm.hpp 公开/宏生成候选名称，
包含退役诊断和别名，**不是 {len(names)} 条独立 ISA 指令**。
下表为名称覆盖检查，不代表所有重载参数和合法组合已通过编译验证。

| PTO-C 名称 | builtin | 处理 | 源码 |
| --- | --- | --- | --- |
'''+ '\n'.join(rows).replace('REV',rev)+'\n\n## predicate 与 region\n\n'
for name,target in pred.items():cov+=f'- `predicate::{name}` → `__builtin_{target.lower()}`；predicate 使用 U8 向量载体。\n'
for name in ('subview','concatenate','logical_numeric','atomic_add'):cov+=f'- `predicate::{name}` → `__builtin_predicate_{name}`。\n'
cov+='- `predicate::logical<6/7/8>` → `__builtin_tand/tor/txor`。\n- `jcore/TCI.hpp::TCI_2D_Impl` → `__builtin_tci_2d`；一维 vector kernel 路径不属 inline TileOP。\n- `TLOAD` 权重重载 → `__builtin_tload_weight`，携带 shape/start 两个 GPR 字，而非 row stride。\n\nregion 宏实例逐项列在下表；同名 builtin 的 view/assemble 字段承载该路径。\n\n| wrapper 类别 | PTO-C 操作 | 源码行 |\n| --- | --- | --- |\n'
r=(root/'include/common/pto_tile_region_inline_asm.hpp').read_text()
for m in re.finditer(r'^PTO_REGION_(\w+)\((T\w+),',r,re.M):cov+=f'| `{m[1]}` | `{m[2]}` | {r.count(chr(10),0,m.start())+1} |\n'
cov+='\nregion 显式定义的 `TROWSUM/TROWMAX/TROWMIN/TROWPROD/TEXP/TCVT/TMOV` 也映射到同名 builtin。\n'
(out/'TileBuiltinMapping.md').write_text(cov)
print(f'{len(names)} source names classified; {len(ops)} proposed entry signatures; {rev}')
