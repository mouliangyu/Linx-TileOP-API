# 逐元素算术、逻辑与数学函数：公共规则

**算子声明：** [TABS](TABS.md)、[TAND](TAND.md)、[TDIV](TDIV.md)、[TEXP](TEXP.md)、[TEXPDIF](TEXPDIF.md)、[TFMA](TFMA.md)、[TLOG](TLOG.md)、[TMAX](TMAX.md)、[TMIN](TMIN.md)、[TMUL](TMUL.md)、[TNEG](TNEG.md)、[TNOT](TNOT.md)、[TOR](TOR.md)、[TRECIP](TRECIP.md)、[TRELU](TRELU.md)、[TREM](TREM.md)、[TRSQRT](TRSQRT.md)、[TSHL](TSHL.md)、[TSHR](TSHR.md)、[TSQRT](TSQRT.md)、[TSUB](TSUB.md)、[TXOR](TXOR.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。操作声明由页首链接进入；[TADD](TADD.md)、[TSEL](TSEL.md)、[比较与转换](CompareConvertRules.md) 有独立条目。所有计算只覆盖有效区域，不自动广播、不自动提升 dtype。输入必须已定义，输出不读取旧值。

## 双输入算术



| 操作 | 有效元素上的结果 | 示例：src0=6，src1=2 |
| --- | --- | --- |
| TSUB | src0−src1 | 4 |
| TMUL | src0×src1 | 12 |
| TDIV | src0/src1；整数类型使用整数结果 | 3 |
| TREM | src0 除以 src1 的余数 | 0 |
| TMAX | 两输入的最大值 | 6 |
| TMIN | 两输入的最小值 | 2 |

D/A/B 分别是输出与两个输入的计算视图类型。操作 dtype 按下表选择。

| 操作 | 操作 dtype |
| --- | --- |
| TDIV | FP64、FP32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、S/U16、S/U32、S/U64 |
| TSUB、TMAX、TMIN | FP64、FP32、FP16、BF16、S/U8、S/U16、S/U32、S/U64 |
| TMUL、TREM | FP64、FP32、FP16、BF16、S/U16、S/U32、S/U64 |

三者计算视图的物理形状、布局和 dtype 匹配；输入有效区域覆盖本次计算区域，输出有效区域为本次结果形状；不执行矩阵乘法或规约。

| 参数 | 方向 | 要求/默认值 |
| --- | --- | --- |
| dst | out | 新结果，容量覆盖计算区域 |
| src0 | in | 左操作数；SUB/DIV/REM 的次序不可交换 |
| src1 | in | 右操作数；DIV/REM 中为除数 |
| UserValidCol / UserValidRow | in | 元素单位，默认 0；选择当前计算视图维度，非零值指定计算列/行数；TREM 没有此参数 |

维度选择、计算区域校验及输出元数据遵守 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

整数 ADD/SUB/MUL 在操作位宽 W 上取模。整数 DIV/REM 的有效除数为零时，在输出效果前拒绝。有符号 REM 使用向下取整的模运算，非零结果与除数同号：`-5 mod 3 = 1`、`5 mod -3 = -1`；无符号 REM 使用通常的余数。DIV 及浮点数值运算的逐位合同统一见 [数值参考](Numerics.md#逐元素执行合同)。

## 位运算与移位



AND/OR/XOR/NOT 接受 S/U8、16、32、64 整数 Tile，按元素位模式计算。TSHL/TSHR 接受同一整数集合，src0 提供被移位值，src1 的每个元素提供对应移位量。对元素位宽 W，实际移位量取 src1 的无符号低 log2(W) 位。左移保留结果低 W 位；有符号右移补符号位，无符号右移补零。例如 U32 的移位量 32 等效于 0，33 等效于 1；S32 的 -4 右移 1 得到 -2。源 backing 可经等宽 reinterpret_tile 提供原始位，操作 dtype 决定右移规则。

参数方向、布局及有效维度选择与上节相同，TNOT 只有 dst(out)、src(in)，无维度覆写参数。移位的操作 dtype 使用上述整数集合。

| 操作 | U32 示例 |
| --- | --- |
| TAND | 6 & 3 = 2 |
| TOR | 6 \| 3 = 7 |
| TXOR | 6 ^ 3 = 5 |
| TNOT | ~0 = 0xffffffff |
| TSHL | 3 << 1 = 6 |
| TSHR | 6 >> 1 = 3 |

## 一元算术与数学函数



源目标计算视图的 dtype、形状与布局须匹配；dst 为 out，src 为 in，均无默认参数。有效区域来自源。

| 操作 | 结果 | 类型 | 有限值示例 |
| --- | --- | --- | --- |
| TABS | abs(x) | FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8/16/32/64 | -2→2 |
| TNEG | -x | FP64/32/16、BF16、S64/U64、S32、S16、S8 | 2→-2 |
| TRELU | max(x,0) | FP64/32/16、BF16、S64/U64、S32 | -2→0 |
| TEXP | exp(x) | FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2 | 0→1 |
| TLOG | 自然对数 log(x) | FP64、FP32、FP16、BF16 | 1→0 |
| TRECIP | 1/x | FP64、FP32、FP16、BF16 | 2→约 0.5 |
| TSQRT | sqrt(x) | FP64、FP32、FP16、BF16 | 4→约 2 |
| TRSQRT | 1/sqrt(x) | FP64、FP32、FP16、BF16 | 4→约 0.5 |

整数 ABS/NEG 按元素位宽取模，有符号最小值取绝对值或取负后仍为原位模式；无符号 ABS 保持原值。浮点 ABS 清除符号位，NEG 翻转符号位，二者仅因该变换不产生浮点 invalid。LOG/SQRT/RECIP/RSQRT 的零、负数和无穷按 [数值参考](Numerics.md#数学函数边界) 处理。

## TFMA：三个输入



计算 `dst = src0 * src1 + src2`。D/A/B/C 独立推导输出及三个输入的计算视图；dst 为 out，src0/1/2 为 in，无默认参数。

| 布局 | 操作 dtype | 几何 |
| --- | --- | --- |
| Local RowMajor、CUBE_M32 | FP64、S64、U64、FP16、FP32、BF16 | 四者物理形状、有效形状、dtype 和所选布局相同 |
| Local CUBE_M16 | FP16、FP32、BF16 | 同上；M16 使用非 b64 backing |

M32 的 FP64/S64/U64 使用每逻辑列两个 CELL 的映射。三个源的全部有效元素须已定义。

浮点结果执行融合乘加：乘积保持中间精度，最后按目标 numeric profile 舍入一次。S64/U64 结果按 64 位取模。例：2、3、4 产生 10；U64 的 `UINT64_MAX * 1 + 1` 产生 0。重复源及源目标别名读取操作前快照；结果、padding definedness、数值状态和目标描述符共同发布。

浮点 signaling NaN、0×∞、∞×0，以及无限乘积加反号无穷，产生 quiet NaN 并记录 invalid。PadValue 控制有效区域外的 definedness；默认 Null。类型、维度、源 definedness 或编码不合法时在效果产生前拒绝；分配失败也在发布前拒绝。

依据：固定 PTO 规范 [TFMA.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl) 的 legality、ordering、state_effects。

## TEXPDIF：差值的指数



计算 `dst[r,c] = exp(src0[r,c] - src1[r,c])`。D/A/B 分别是输出/左输入/右输入载体，dst 为 out，其他为 in，无默认参数。本次有效行列为正；不自动广播。该操作可用于 softmax 的减最大值步骤，行广播版本另见 [广播](BroadcastRules.md)。两个输入使用相同的操作类型，合法的（源操作类型，目标类型）配对为 FP64→FP64、FP32→FP32、FP16→FP16、BF16→BF16、FP16→FP32、BF16→FP32。混合精度形式先将两个输入精确扩展到 FP32，再执行 FP32 减法和指数。布局为 Local RowMajor、CUBE_M16 或 CUBE_M32，FP64 使用 RowMajor 或 M32；输入输出布局及逻辑有效形状相同，物理容量按各自 dtype 推导。源计算视图的操作类型与 backing 类型可通过 [reinterpret_tile](CommonTypes.md#reinterpret_tile) 显式关联，须满足等宽、非 packed 及架构 carrier 兼容条件。两个输入全为 2 时输出为 1。

## 类型明确的调用示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using F = Tile<Location::Vec, float, 32, 32, BLayout::RowMajor>;
using U = Tile<Location::Vec, uint32_t, 32, 32, BLayout::RowMajor>;

// x/y/z 以及 bits/count 已由调用者初始化；输出对象与输入独立。
void arithmetic(F &difference, F &product, F &ratio, F &fma,
                F &x, F &y, F &z) {
  TSUB(difference, x, y);
  TMUL(product, x, y);
  TDIV(ratio, x, y);
  TFMA(fma, x, y, z);
}
void shift(U &result, U &bits, U &count) { TSHL(result, bits, count); }
void reciprocal_root(F &result, F &input) { TRSQRT(result, input); }
```

以上为设备函数片段，未编译执行。输入每个元素 x=6、y=2、z=1 时四个算术输出分别为 4、12、3、13。

## Reader/Writer 与别名

双输入逐元素操作的目标角色是 Writable、源角色是 Readable；支持分片的重载必须使每个 Part 的计算形状一致。Writer 输出描述不能放到任何输入位置。TFMA 的三个数学源分别接受 Readable，并独立绑定输入片段。TEXPDIF 的跨类型及 layout 合同也要随 Part 校验。

普通 Local 逐元素源在目标发布前读取旧值；同一调用重复使用一个已定义源合法。普通目标与源同名时执行 read-old/write-new。Reader 描述借用的旧 parent 必须在本次读取完成前保持有效；Local Writer 的 OPEN parent 只能作为组装目标。Writer 输出范围独立满足覆盖规则，finish 后才交出完成的 parent。

布局为 RowMajor/M16/M32；M16 使用非 b64 backing，M32 的 b64 每逻辑列占两个 CELL。各输入选择的操作 dtype 与输出 dtype 一致；允许 reinterpret_tile 时，源 backing 等位宽、非 packed，并按操作 dtype 检查数值编码。TFMA 和 TEXPDIF 的类型关系由各自专节定义。

本章操作的输入合法性、definedness、维度、容量和分配检查在发布前完成。默认 Null padding 未定义；Zero/Max/Min 按所选 dtype 定义有效区域外的物理元素。完整 Tile 一次发布 payload、definedness、描述符和适用的数值状态；Writer 按阶段写入，LAST 完成 parent 发布。静态非法调用应诊断，动态非法绑定按架构 fault 处理。普通操作无 GM 访问。

TAND/TOR/TXOR 另有 CUBE PredicateCell 专用重载，结果种类、U8 basis 和混合 Numeric U8 规则见各算子页；上面的整数规则仅描述数值重载。
