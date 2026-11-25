#!/usr/bin/env python3
"""Compile marked manual examples against declaration/type mocks, not a backend.

The real signatures are extracted from the manual. Unique return tags test the
selected overload for every mapped call. Type mocks check capacity and basic
primary/scale geometry; Options mocks check spelling, not execution or lowering.
"""
import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from check_contracts import ROOT, inventory

PRELUDE = r'''
#include <cstddef>
#include <cstdint>
#include <type_traits>
struct __half {};
struct __fp8_e4m3 {};
struct __fp8_e8m0 {};
struct __fp8_e6m2 {};
struct __fp8_rcpe6m2 {};
struct __fp4_e2m1x2 {};
struct __fp4_e1m2x2 {};
struct __fp4_hif4x2 {};
struct __int4x2 {};
namespace pto {
using std::size_t;
constexpr int DYNAMIC = -1;
enum class Location { Vec, Left, Right, Acc, Bias };
enum class BLayout { RowMajor, CubeM16, CubeM32, CubeN8 };
template<class T> constexpr int bits_v = sizeof(T)*8;
template<> constexpr int bits_v<__half> = 16;
template<> constexpr int bits_v<__bf16> = 16;
template<> constexpr int bits_v<__fp4_e2m1x2> = 4;
template<> constexpr int bits_v<__fp4_e1m2x2> = 4;
template<> constexpr int bits_v<__fp4_hif4x2> = 4;
template<> constexpr int bits_v<__int4x2> = 4;
constexpr int encoded_capacity(int bytes) {
  int result=128;
  while (result<bytes) result*=2;
  return result;
}
template<Location R, class E, int Rows, int Cols,
         BLayout L=BLayout::RowMajor, int VR=Rows, int VC=Cols>
struct Tile {
  using dtype=E;
  static constexpr Location role=R;
  static constexpr BLayout layout=L;
  static constexpr bool shared=false;
  static constexpr int rows=Rows, cols=Cols, vr=VR, vc=VC;
  // Only the documented RowMajor TCVT profile admits capacity slack here.
  static constexpr bool odd_columns_profile=L==BLayout::RowMajor &&
      (Cols&(Cols-1)) && (std::is_same_v<E,float> ||
      std::is_same_v<E,__half> || std::is_same_v<E,__bf16> ||
      std::is_same_v<E,__fp4_e2m1x2> || std::is_same_v<E,__fp4_e1m2x2>);
  static constexpr int capacity=odd_columns_profile ?
      encoded_capacity(Rows*((Cols*bits_v<E>+7)/8)) : Rows*Cols*bits_v<E>/8;
  static_assert(capacity>=128 && capacity<=65536 && !(capacity&(capacity-1)));
  static_assert((VR==DYNAMIC || (VR>=0 && VR<=Rows)) &&
                (VC==DYNAMIC || (VC>=0 && VC<=Cols)));
  Tile()=default;
  Tile(int,int) {}
};
template<class S> struct SharedTile : S {
  static constexpr bool shared=true;
  SharedTile()=default;
  explicit SharedTile(const S&) {}
};
template<class E,int R,int C,int VR=R,int VC=C>
using CubeTileM16=Tile<Location::Left,E,R,C,BLayout::CubeM16,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using CubeTileM32=Tile<Location::Left,E,R,C,BLayout::CubeM32,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using CubeTileN8=Tile<Location::Right,E,R,C,BLayout::CubeN8,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using CubeAccumulatorM16=Tile<Location::Acc,E,R,C,BLayout::CubeM16,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using CubeAccumulatorM32=Tile<Location::Acc,E,R,C,BLayout::CubeM32,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using VecTileM16=Tile<Location::Vec,E,R,C,BLayout::CubeM16,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using VecTileM32=Tile<Location::Vec,E,R,C,BLayout::CubeM32,VR,VC>;
template<class E,int C,int VC=C>
using CubeBias=Tile<Location::Bias,E,128/bits_v<E>,C,BLayout::CubeN8,1,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using SharedMatrixLeft=Tile<Location::Left,E,R,C,BLayout::RowMajor,VR,VC>;
template<class E,int R,int C,int VR=R,int VC=C>
using SharedMatrixRight=Tile<Location::Right,E,R,C,BLayout::RowMajor,VR,VC>;
struct NoOperand {};
template<class T> concept is_any_tile_data_v=requires { T::role; T::shared; };
template<class T> concept is_tile_data_v=is_any_tile_data_v<T> && !T::shared;
template<class T> concept is_local_tile_v=is_tile_data_v<T>;
template<class T> concept is_local_or_shared_left=is_any_tile_data_v<T> && T::role==Location::Left;
template<class T> concept is_local_or_shared_right=is_any_tile_data_v<T> && T::role==Location::Right;
template<class T> constexpr auto tile_role_v=T::role;
template<class T> constexpr bool needs_scale_v=
    std::is_same_v<T,__fp8_e4m3> || std::is_same_v<T,__fp4_e2m1x2> ||
    std::is_same_v<T,__fp4_hif4x2>;
template<class L,class R> constexpr int mx_scale_mask_v=
    ((std::is_same_v<typename L::dtype,__half> || needs_scale_v<typename L::dtype>) &&
     (std::is_same_v<typename R::dtype,__half> || needs_scale_v<typename R::dtype>)) ?
    (needs_scale_v<typename L::dtype> ? 1:0) | (needs_scale_v<typename R::dtype> ? 2:0) : -1;
enum class FixpReluMode { None, Relu };
enum class FixpPreQuantMode { None, F322F16, F322BF16, QF322S8Pre, VQF322S8Pre };
struct FixpAttr {
  int mode=0;
  static constexpr FixpAttr f16(FixpReluMode=FixpReluMode::None) { return {1}; }
};
namespace fixp {
struct MockOptions {
  constexpr MockOptions relu() const { return {}; }
  constexpr MockOptions lrelu(uint64_t) const { return {}; }
  template<is_local_tile_v T> constexpr MockOptions prelu(T&) const { return {}; }
  template<is_local_tile_v T> constexpr MockOptions row_max(T&) const { return {}; }
  template<is_local_tile_v T,is_local_tile_v U> constexpr MockOptions row_max(T&,U&) const { return {}; }
  template<int N,is_local_tile_v T> constexpr MockOptions group_max(T&) const { return {}; }
  constexpr MockOptions max_abs() const { return {}; }
  template<bool E=true> constexpr MockOptions transpose_a() const { return {}; }
  template<bool E=true> constexpr MockOptions transpose_b() const { return {}; }
  template<bool E=true> constexpr MockOptions cscale_enable() const { return {}; }
  template<is_local_tile_v T> constexpr MockOptions cscale(T&) const { return {}; }
  constexpr MockOptions raw_acc() const { return {}; }
  constexpr MockOptions acc_hint() const { return {}; }
};
template<class T> concept is_options_v=std::is_same_v<T,MockOptions>;
constexpr MockOptions keep_acc() { return {}; }
constexpr MockOptions f16() { return {}; }
constexpr MockOptions bf16() { return {}; }
template<FixpPreQuantMode M=FixpPreQuantMode::None> constexpr MockOptions convert() { return {}; }
template<FixpPreQuantMode M> constexpr MockOptions scalar(uint64_t) { return {}; }
template<FixpPreQuantMode M,is_local_tile_v T> constexpr MockOptions vector(T&) { return {}; }
constexpr MockOptions s8(uint64_t) { return {}; }
template<is_local_tile_v T> constexpr MockOptions s8(T&) { return {}; }
}
template<class T> concept Writable=is_local_tile_v<std::remove_cvref_t<T>>;
template<class T> concept Readable=Writable<T>;
constexpr int LINX_RNONE=0,LINX_RNE=1,LINX_RTZ=2,LINX_RNA=5;
template<class S,class P,bool Left> constexpr void check_scale() {
  if constexpr(needs_scale_v<typename P::dtype>) {
    static_assert(S::shared==P::shared);
    static_assert(S::layout==(P::shared ? BLayout::RowMajor : BLayout::CubeM32));
    using E=std::conditional_t<std::is_same_v<typename P::dtype,__fp4_hif4x2>,uint32_t,__fp8_e8m0>;
    static_assert(std::is_same_v<typename S::dtype,E>);
    // Shared primary may be transposed by Options; its logical dimensions
    // require manual review because the mock does not model Options values.
    if constexpr(!P::shared) {
      constexpr int k=Left ? P::vc : P::vr;
      constexpr int major=Left ? P::vr : P::vc;
      constexpr int group=std::is_same_v<E,uint32_t> ? 64 : 32;
      static_assert(S::vc==(k+group-1)/group && S::vr==major);
    }
  } else {
    static_assert(std::is_same_v<S,NoOperand>);
  }
}
'''

def declarations():
    result=[]
    for r in inventory():
        op=r['op']
        if op=='TCVT':
            result.append(r['signature'])
        if not op.startswith(('TMATMUL','TGEMV')): continue
        sig=r['signature']
        # The tag changes only the return type for overload-selection testing.
        sig=sig.replace('void ',f'std::integral_constant<int,{r["ordinal"]}> ',1)
        params=sig.split(op+'(',1)[1].rsplit(')',1)[0]
        names={re.search(r'(\w+)\s*$',p.strip())[1] for p in params.split(',')}
        a='vec' if op.startswith('TGEMV') else 'a'
        b='mtx' if op.startswith('TGEMV') else 'b'
        body=[f'using A=std::remove_reference_t<decltype({a})>;',
              f'using B=std::remove_reference_t<decltype({b})>;',
              'static_assert(A::role==Location::Left && B::role==Location::Right);',
              'static_assert(A::shared || A::layout==BLayout::CubeM16 || A::layout==BLayout::CubeM32);',
              'static_assert(B::shared || B::layout==BLayout::CubeN8);',
              'if constexpr(!A::shared && !B::shared) static_assert(A::vc==B::vr);']
        if '_MX' in op:
            sa=next((n for n in ('ascale','scale_a','sa','svec','scale_vec') if n in names),None)
            sb=next((n for n in ('bscale','scale_b','sb','smtx','scale_mtx') if n in names),None)
            for name,primary,left in [(sa,'A','true'),(sb,'B','false')]:
                t=f'std::remove_reference_t<decltype({name})>' if name else 'NoOperand'
                body.append(f'check_scale<{t},{primary},{left}>();')
        body.append('return {};')
        body_text=re.sub(r'\bA\b','AuditLeft',' '.join(body))
        body_text=re.sub(r'\bB\b','AuditRight',body_text)
        result.append(sig.rstrip(';')+' { '+body_text+' }')
    return '\n'.join(result)+'\n}\n'

def build():
    manifest=json.loads((ROOT/'audit/example_cases.json').read_text())
    blocks={}
    for p in sorted((ROOT/'TileOpReference').glob('*.md')):
        for name,body in re.findall(r'<!-- audit-example: ([\w]+) -->\n```cpp\n(.*?)```',p.read_text(),re.S):
            if name in blocks: raise ValueError('duplicate example '+name)
            blocks[name]=(str(p.relative_to(ROOT)),body)
    covered=set();calls=0
    for case in manifest['cases']:
        page,body=blocks[case['block']]
        assert page==case['page']
        assert re.search(r'void\s+'+case['function']+r'\s*\(',body)
        for call in case['calls']:
            expression=call['expression']; n=call['ordinal']
            assert expression+';' in body, (case['block'],expression)
            body=body.replace(expression+';',f'static_assert(decltype({expression})::value == {n});\n  {expression};',1)
            covered.add((case['op'],n));calls+=1
        blocks[case['block']]=(page,body)
    expected={(r['op'],r['ordinal']) for r in inventory() if r['op'].startswith(('TMATMUL','TGEMV'))}
    assert covered==expected, ('missing declaration examples',expected-covered)
    source=PRELUDE+declarations()
    for name,(page,body) in blocks.items():
        source+='\n// '+page+' '+name+'\n'+body.replace('#include <common/pto_tileop.hpp>','')+'\n'
    return source,len(blocks),calls,len(covered)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=Path('.work/tileop-manual-audit/examples'))
    parser.add_argument('--compiler',default='clang++')
    args=parser.parse_args()
    source,blocks,calls,covered=build()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    file=args.output_dir/'examples.cpp';file.write_text(source)
    compiler=shutil.which(args.compiler)
    if not compiler:raise SystemExit('C++ compiler unavailable')
    subprocess.run([compiler,'-std=c++20','-fsyntax-only','-ferror-limit=6',str(file)],check=True)
    print(f'PASS: {blocks} complete example blocks; {calls} mapped calls cover {covered} matrix declarations. Declaration/type mocks only; no implementation, ASL or hardware execution.')

if __name__=='__main__':main()
