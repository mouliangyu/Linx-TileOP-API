#!/usr/bin/env python3
"""Compile the manual's MX declarations with role/dtype mocks (no codegen test)."""
import argparse
import re
import shutil
import subprocess
from pathlib import Path
from check_contracts import inventory

PRELUDE = r'''
#include <cstddef>
#include <type_traits>
#include <utility>
using std::size_t;
enum class Location { Vec, Left, Right, Acc, Bias };
struct FixpAttr {};
template<Location R, int Kind, bool Shared = false> struct Tile {
  static constexpr Location role=R;
  static constexpr int kind=Kind; // 0:FP16, 1:E4M3, 2:E8M0, 3:FP32
  static constexpr bool shared=Shared;
};
struct NoOperand {};
template<class T> concept is_any_tile_data_v = requires { T::role; T::kind; };
template<class T> concept is_tile_data_v = is_any_tile_data_v<T> && !T::shared;
template<class T> concept is_local_tile_v = is_tile_data_v<T>;
template<class T> concept is_local_or_shared_left = is_any_tile_data_v<T> && T::role == Location::Left;
template<class T> concept is_local_or_shared_right = is_any_tile_data_v<T> && T::role == Location::Right;
template<class T> constexpr Location tile_role_v=T::role;
template<class L,class R> constexpr int mx_scale_mask_v =
  (L::kind <= 1 && R::kind <= 1) ? ((L::kind==1 ? 1:0) | (R::kind==1 ? 2:0)) : -1;
namespace fixp {
struct Options {};
template<class T> concept is_options_v = std::is_same_v<T,Options>;
}
'''

def build():
    rows=[r for r in inventory() if r['op'].startswith(('TMATMUL_MX','TGEMV_MX'))]
    lines=[PRELUDE]
    for r in rows:
        # A unique result type proves which overload C++ selected.
        lines.append(r['signature'].replace('void ',f'std::integral_constant<int,{r["ordinal"]}> ',1))
    count=0
    for r in rows:
        sig=r['signature'];op=r['op'];gemv=op.startswith('TGEMV');full='tile_shape_' in sig
        expected_mask=3 if full else 1 if ('ScaleVec' in sig or 'is_any_tile_data_v SA' in sig) else 2 if ('ScaleMtx' in sig or 'is_any_tile_data_v SB' in sig) else 0
        masks=range(4) if full and 'int ScaleMask' in sig else [expected_mask]
        # Include scales with Left/Right roles, not just Vec: this triggered the old ambiguity.
        for mask in masks:
            for scale_role in ['Vec','Left','Right']:
                for storage in (['local'] if gemv else ['mixed'] if 'size_t groupM' in sig else ['local','shared']):
                    args=[]
                    params=sig.split(op+'(',1)[1].rsplit(')',1)[0]
                    for param in params.split(','):
                        param=param.strip().split('=')[0].strip()
                        typ,name=re.match(r'(.*?)\s*&?\s*(\w+)$',param).groups()
                        typ=typ.replace('&','').strip()
                        if name=='options':target='fixp::Options'
                        elif name=='groupM':args.append('size_t{20}');continue
                        else:
                            if name in ('a','vec'):role='Left';kind=1 if mask&1 else 0;shared=storage=='shared'
                            elif name in ('b','mtx'):role='Right';kind=1 if mask&2 else 0;shared=storage!='local'
                            elif name in ('ascale','scale_a','sa','svec','scale_vec'):role=scale_role;kind=2;shared=storage=='shared';present=bool(mask&1)
                            elif name in ('bscale','scale_b','sb','smtx','scale_mtx'):role=scale_role;kind=2;shared=storage!='local';present=bool(mask&2)
                            elif name=='bias':role='Bias';kind=3;shared=False
                            else:role='Acc';kind=3;shared=False
                            if name in ('ascale','scale_a','sa','svec','scale_vec','bscale','scale_b','sb','smtx','scale_mtx') and not present:target='NoOperand'
                            else:target=f'Tile<Location::{role},{kind},{str(shared).lower()}>'
                        args.append(f'std::declval<{target}&>()')
                    explicit=f'<{mask}>' if full and 'int ScaleMask' in sig else ''
                    call=f'{op}{explicit}('+','.join(args)+')'
                    lines.append(f'static_assert(decltype({call})::value == {r["ordinal"]});')
                    count+=1
    return '\n'.join(lines)+'\n',len(rows),count

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path('.work/tileop-manual-audit/mx-declarations'))
    parser.add_argument('--compiler',default='clang++')
    args=parser.parse_args()
    compiler=shutil.which(args.compiler)
    if not compiler:raise SystemExit('C++ compiler not found: '+args.compiler)
    text,rows,cases=build();args.output_dir.mkdir(parents=True,exist_ok=True)
    source=args.output_dir/'declarations.cpp';source.write_text(text)
    subprocess.run([compiler,'-std=c++20','-fsyntax-only',str(source)],check=True)
    print(f'PASS: {rows} MX declarations, {cases} role/dtype overload-selection cases. Mock declaration check only; no TileOP implementation or ISA execution.')
if __name__=='__main__':main()
