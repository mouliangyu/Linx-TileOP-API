# 矩阵 Options 参考

`<common/pto_tileop.hpp>`，`pto::fixp`。options 在一次 TMATMUL/TGEMV 调用中配置 accumulator 输出转换、激活、辅助规约以及合法的输入变换。它借用参数 Tile，不拥有其数据；相关对象须存活到调用完成。builder 返回新 options，需使用返回值。

## 构造函数

```cpp
namespace pto::fixp {
constexpr auto keep_acc();
constexpr auto f16();
constexpr auto bf16();
template <FixpPreQuantMode Mode = FixpPreQuantMode::None>
constexpr auto convert();
template <FixpPreQuantMode Mode>
constexpr auto scalar(uint64_t descriptor);
template <FixpPreQuantMode Mode, is_local_tile_v T>
constexpr auto vector(T &parameter);
constexpr auto s8(uint64_t descriptor);
template <is_local_tile_v T> constexpr auto s8(T &parameter);
}
```

keep_acc 保留 FP32/S32/U32 accumulator；f16/bf16 要求 FP32 accumulator 并分别产生 FP16/BF16。convert 只接受 None/F322F16/F322BF16。scalar/vector 只接受对应参数类别的 mode；s8 是 QF322S8Pre/VQF322S8Pre 快捷入口。不能仅凭 D 类型选择 mode，必须同时匹配 A/B 派生的 accumulator 类。

## 链式方法

以下是 Options 对象的成员声明，auto 返回新的具体 Options 类型。

```cpp
constexpr auto relu() const;
constexpr auto lrelu(uint64_t descriptor) const;
template <is_local_tile_v T> constexpr auto prelu(T &parameter) const;
template <is_local_tile_v T> constexpr auto row_max(T &output) const;
template <is_local_tile_v I, is_local_tile_v O>
constexpr auto row_max(I &input, O &output) const;
template <int GroupN, is_local_tile_v T>
constexpr auto group_max(T &output) const;
constexpr auto max_abs() const;
template <bool Enable = true> constexpr auto transpose_a() const;
template <bool Enable = true> constexpr auto transpose_b() const;
template <is_local_tile_v T> constexpr auto cscale(T &scale) const;
template <bool Enable = true> constexpr auto cscale_enable() const;
constexpr auto raw_acc() const;
constexpr auto acc_hint() const;
```

| 方法 | 参数方向、结果与限制 |
| --- | --- |
| relu | 不需要 operand；启用 ReLU |
| lrelu | in，低 19 位 FP19 slope，高位零 |
| prelu | in，Local U64 CUBE_N8，有效 1×N，每项低 19 位 FP19 slope，高位零 |
| row_max(output) | out，fresh reduction，有效 M×1 |
| row_max(input,output) | in/out 分离，将已有 row maximum 纳入结果，均为 M×1 |
| group_max<GroupN> | out，M×ceil(N/GroupN)；GroupN 为 8/16/32/48/64/80/96/112/128 |
| max_abs | 作用于已经启用的 RowMax/GroupMax；至少启用一个 |
| transpose_a/b | 仅对应 Shared primary，不转置 Local 或 MX scale |
| cscale_enable | 只设置属性，默认 Enable=true；不会提供 scale operand，启用后仍须合法的 cscale Tile |
| cscale | in，Local U8 CUBE_M32 M×1；仅 FP32 TMATMUL_ACC/TMATMUL_MX_ACC |
| raw_acc | CCTRL[0]，发布真实可读 accumulator D；禁止最终转换、激活及辅助 reduction |
| acc_hint | CCTRL[1]，仅 ACC 形式；显式 C 的透明缓存提示，不改变数学结果 |

CScale 的精确公式为 `scaled_C[r,n] = C[r,n] * 2^(-scale[r,0])`。U8 0 表示不缩放，1 表示乘 1/2，255 表示乘 2^-255（浮点舍入/下溢仍适用）。它是输入变换，raw_acc 允许合法 CScale。keep_acc 不自动开启 raw_acc 或 acc_hint。

RowMax/GroupMax 基于最终编码后的 D，输入/输出 dtype 必须等于 D，且 D 只允许 FP32/FP16/BF16。RowMax carrier 使用与 primary 相同的 M16/M32 布局及输出 dtype，有效形状 M×1；物理列数和 CELL 容量按该 dtype 的合法 CUBE 几何推导。辅助输出也须满足最小 CELL 容量，不可只按有效元素字节数分配。禁止与数学输入或 D 非法 alias。

## PreQuantMode 枚举

| 编码 | 名称 | 参数 |
| --- | --- | --- |
| 0 | None | 无 |
| 1 | F322F16 | 无 |
| 2 / 3 | VREQS8Pre / REQS8Pre | vector / scalar |
| 4 / 5 | VDEQF16 / DEQF16 | vector / scalar |
| 12 / 13 | VSHIFTS322S16 / SHIFTS322S16 | vector / scalar |
| 16 | F322BF16 | 无 |
| 17 / 18 | QF322S4Pre / VQF322S4Pre | scalar / vector |
| 19 / 20 | QF322S16Pre / VQF322S16Pre | scalar / vector |
| 23 / 24 | VQF322S8Pre / QF322S8Pre | vector / scalar |
| 25 / 28 | QF322HIF8Pre / VQF322HIF8Pre | scalar / vector |
| 26 / 37 | QF322FP8Pre / VQF322FP8Pre | scalar / vector |
| 27 / 38 | QF322F32Pre / VQF322F32Pre | scalar / vector |
| 32 / 33 | QF322F16Pre / VQF322F16Pre | scalar / vector |
| 34 / 36 | QF322BF16Pre / VQF322BF16Pre | scalar / vector |
| 35 / 39 | QS322BF16Pre / VQS322BF16Pre | scalar / vector |

REQ/DEQ/SHIFT 和 QS322 类接受 S32 accumulator；QF322 类接受 FP32。U32 只支持 None。未列编码保留。输出分别为名称所示 S4/S8/S16/FP16/BF16/FP8/HiF8/FP32；FP8 模式的目标为 E4M3。

## Descriptor 与 vector 参数

scalar descriptor 是 uint64_t；vector 参数是 Local U64 CUBE_N8 Tile，有效 1×N，物理基本 CELL 为 K2×N8，每项使用相同编码。所有未使用位必须为零。

| 模式 | 有效位域 |
| --- | --- |
| SHIFT 12/13 | [35:32] code=0..15，算术右移量为 code+1 |
| S4 17/18 | [31:13] FP19 scale；[41:37] 有符号 5 位 offset |
| S8 2/3/23/24 | [31:13] FP19 scale；[45:37] 有符号 9 位 offset |
| S16 19/20 | [31:13] FP19 scale；[53:37] 有符号 17 位 offset |
| 其他参数化 mode | [31:13] FP19 scale |

FP19 编码的 sign 位为 [18]，exponent 为 [17:10]（bias=127），fraction 为 [9:0]。正正规值为 `(1 + fraction/1024) * 2^(exponent-127)`。量化 scale 须为正正规数；激活 slope 可为正零或正正规数。scale=2 的编码为 `128 << 10`。编码按 [FP19 定义](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/arch/data-types/fp19.asl) 校验。

```cpp
constexpr uint64_t s8_descriptor(uint32_t encoded_fp19, int16_t offset) {
  // 前提：encoded_fp19 合法且 < 2^19，offset 在 [-256,255]。
  return (uint64_t(encoded_fp19) << 13) |
         ((uint64_t(offset) & 0x1ff) << 37);
}
```

## 后处理计算

令 x 为矩阵累加结果（ACC 的输入 C 先按 CScale 缩放再参与累加）。标量参数用于所有列，vector 参数按逻辑列 n 取值。有限数的处理顺序如下：

1. 根据 x 的符号选择乘数 m：未启用激活或 x 非负时取 quant scale（无参数模式取 1）；负值 ReLU 取 0；负值 LReLU/PReLU 取该列 slope。
2. 计算 y=x*m。带 offset 的模式先对 y 舍入并饱和到指定中间有符号位宽，再加 offset。
3. 按目标 dtype 编码结果。RowMax/GroupMax 按列递增顺序读取最终编码的 D；D、辅助结果和 sticky flags 一起提交。

| 模式 | accumulator → 输出 | 中间计算 |
| --- | --- | --- |
| None | FP32/S32/U32 → 原类型 | 保留累加结果；启用激活时按激活路径计算 |
| F322F16 / F322BF16 | FP32 → FP16/BF16 | 按目标格式舍入 |
| REQS8 / QF322S8（含 vector） | S32 / FP32 → S8 | `S9_sat(round(y)) + signed9(offset)`，再编码 S8 |
| QF322S4（含 vector） | FP32 → S4X2 | `S5_sat(round(y)) + signed5(offset)`，再编码 packed S4 |
| QF322S16（含 vector） | FP32 → S16 | `S17_sat(round(y)) + signed17(offset)`，再编码 S16 |
| SHIFT 12/13 | S32 → S16 | 对 S32 算术右移 code+1 位，再钳制到 [-32768,32767] |
| DEQF16 / QS322BF16 | S32 → FP16/BF16 | 对 y 执行目标浮点编码 |
| 其他 QF322 浮点模式 | FP32 → 对应浮点格式 | 对 y 执行目标浮点编码；FP8 的目标为 E4M3 |

本库现有 Options 声明采用 B.DATR 默认 RMode=NONE、Sat=0。固定浮点模式 1/16/26/32/33/34/36/37 使用 RNE；HiF8 模式 25/28 使用 RHB；其他可配置模式的默认 numeric control 使用 RNE。中间 S5/S9/S17 饱和始终执行，最终整数编码在 Sat=0 下保留目标低位。SHIFT 固定执行 S16 饱和。默认舍入依据 [ResolveTileNumericExecutionControl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/numeric-control.asl)。特殊值、浮点溢出与状态位按下列固定函数定义。

例如 `fixp::s8((uint64_t{128 << 10} << 13) | (uint64_t{3} << 37))` 表示 scale=2、offset=3。x=10 时 y=20，中间 S9 为20，结果 S8 为23；x=200 时 y=400，中间饱和为255，加3后为258，默认最终 S8 编码为低8位 `0x02`。两个输入均为整数精确值，因此不依赖平局舍入。示例为规范推导，未编译运行。

数值来源：[MatrixSelectedMultiplier、MatrixPostQuantBaseWithFlags](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/matrix-postprocess.asl)、[MatrixQuantizedAffine、MatrixShiftS32ToS16](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/matrix-quantization.asl)、[B.FPATR 模式与舍入控制](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/attributes/B.FPATR.asl)。辅助载体依据 [matrix-postprocess 合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-postprocess.asl)。

## 属性存储与错误

FixpAttr 的默认值关闭全部功能。PreQuant、Relu、GroupN 和开关属于编译期属性；Options 另外保存运行时 descriptor 和借用 Tile。ReluMode 为 None=0、Relu=1、LRelu=2、PRelu=3。不要直接填写保留值或通过遗漏参数模拟关闭功能。

重复配置同类 operand、max_abs 缺少规约、raw_acc 与后处理并用、acc_hint 用于非 ACC、CScale 用于 GEMV，均为非法组合。模板静态检查不能替代输入内容合法性检查。矩阵输出组按 D、RowMaxOut、GroupMaxOut 发布；非法 bundle 不应发布部分 Tile 输出。

```cpp
auto partial = fixp::keep_acc().raw_acc().acc_hint();
auto final = fixp::f16().relu();
// TMATMUL_ACC(next, previous, a, b, partial);
// TMATMUL_ACC(result_fp16, next, a_tail, b_tail, final);
```

变量类型与完整 K 分片例子见 [TMATMUL_ACC](TMATMUL_ACC.md)。这两个 options 表达不同调用的设置，不会修改 previous 或 next 的 dtype。

## 完整组合示例

以下函数使用已经初始化的输入Tile；所有输出对象彼此独立，并与输入分离。引用参数由调用者准备，options借用的参数和辅助输出存活到调用结束。数值结果按有效元素给出，padding不参与计算。

### 转换、激活与两个辅助输出

<!-- audit-example: options_reductions -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_reductions {
using A = CubeTileM16<float, 16, 16>;
using B = CubeTileN8<float, 16, 16>;
using F16 = CubeAccumulatorM16<__half, 16, 16>;
using HalfRow = VecTileM16<__half, 16, 4, 16, 1>;
using HalfGroups = VecTileM16<__half, 16, 4, 16, 2>;
using F32 = CubeAccumulatorM16<float, 16, 16>;
using FloatRow = VecTileM16<float, 16, 2, 16, 1>;
using FloatGroups = VecTileM16<float, 16, 2>;
void fresh(F16 &dst, HalfRow &row, HalfGroups &groups, A &a, B &b) {
  auto options = fixp::f16().relu().row_max(row).group_max<8>(groups).max_abs();
  TMATMUL(dst, a, b, options);
}
void merge(F32 &dst, FloatRow &previous, FloatRow &row,
           FloatGroups &groups, A &a, B &b) {
  auto options = fixp::keep_acc().row_max(previous, row)
                                .group_max<8>(groups).max_abs();
  TMATMUL(dst, a, b, options);
}
void compile_time_attr(F16 &dst, A &a, B &b) {
  TMATMUL<FixpAttr::f16(FixpReluMode::Relu)>(dst, a, b);
}
}
```

取A偶数行全部为+1、奇数行全部为−1；B前8列全部为1、后8列全部为2。乘积结果偶数行为 `[16×8,32×8]`，奇数行为 `[−16×8,−32×8]`，其中 `v×8` 表示连续8个值v。

`fresh` 在FP16转换与ReLU后，偶数行保持16/32，奇数行变为0；RowMax分别为32/0，GroupMax分别为 `[16,32]` / `[0,0]`。`compile_time_attr` 的D与 `fresh` 相同。`merge` 保留FP32的有符号D；若previous每行为40，max_abs下新的RowMax每行为40，GroupMax每行均为 `[16,32]`。previous为输入，row为新输出。

主输出F16/F32容量分别为512B/1024B。四种辅助载体均为128B：HalfRow/FloatRow仅1列有效，HalfGroups/FloatGroups有2列有效，与GroupN=8、N=16对应。输出绑定顺序为D、row、groups。

### 无参数转换 builder

<!-- audit-example: options_conversion -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_conversion {
using A = CubeTileM16<__half, 16, 16>;
using B = CubeTileN8<__half, 16, 8>;
using F32 = CubeAccumulatorM16<float, 16, 8>;
using BF16 = CubeAccumulatorM16<__bf16, 16, 8>;
void preserve(F32 &dst, A &a, B &b) {
  TMATMUL(dst, a, b, fixp::convert());
}
void to_bf16(BF16 &dst, A &a, B &b) {
  TMATMUL(dst, a, b, fixp::bf16());
}
}
```

A/B有效元素全部为1时，两种结果均为精确的16；F32容量512B，BF16容量256B。`convert()` 的默认Mode为None，保持FP32累加类型；`bf16()` 选择BF16目标编码。FP16转换的完整调用见上面的 `fresh`，显式 `convert<F322F16>()` 见下面的两步累加。

### 标量与向量量化参数

<!-- audit-example: options_quantization -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_quantization {
using A = CubeTileM16<float, 16, 16>;
using B = CubeTileN8<float, 16, 8>;
using S8 = CubeAccumulatorM16<int8_t, 16, 8>;
using Params = CubeTileN8<uint64_t, 2, 8, 1, 8>;
constexpr uint64_t descriptor = (uint64_t{128 << 10} << 13) |
                                (uint64_t{3} << 37);
void scalar_quant(S8 &dst, A &a, B &b) {
  auto options = fixp::scalar<FixpPreQuantMode::QF322S8Pre>(descriptor);
  TMATMUL(dst, a, b, options);
}
void vector_quant(S8 &dst, A &a, B &b, Params &parameter) {
  auto options = fixp::vector<FixpPreQuantMode::VQF322S8Pre>(parameter);
  TMATMUL(dst, a, b, options);
}
void short_scalar(S8 &dst, A &a, B &b) {
  TMATMUL(dst, a, b, fixp::s8(descriptor));
}
void short_vector(S8 &dst, A &a, B &b, Params &parameter) {
  TMATMUL(dst, a, b, fixp::s8(parameter));
}
}
```

A/B全部为1时acc=16。descriptor的scale=2、offset=3；parameter的8个有效U64元素均存该descriptor。四个函数均得到S8的35。Params物理2×8=128B，有效1×8；S8输出16×8=128B。量化参数由调用者按U64载体准备，保留位为零。

### LReLU 与 PReLU

<!-- audit-example: options_slopes -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_slopes {
using A = CubeTileM16<float, 16, 16>;
using B = CubeTileN8<float, 16, 8>;
using D = CubeAccumulatorM16<float, 16, 8>;
using Slopes = CubeTileN8<uint64_t, 2, 8, 1, 8>;
void scalar_slope(D &dst, A &a, B &b) {
  TMATMUL(dst, a, b, fixp::keep_acc().lrelu(uint64_t{126 << 10}));
}
void vector_slope(D &dst, A &a, B &b, Slopes &slopes) {
  TMATMUL(dst, a, b, fixp::keep_acc().prelu(slopes));
}
}
```

A全为−1、B全为1，累加值为−16；FP19的 `126<<10` 表示0.5。slopes的每个有效U64元素低19位存该编码，高位为零。两个函数的D均为−8；Slopes使用N8的128B参数载体。

### CScale、raw_acc 与 acc_hint 的两步累加

<!-- audit-example: options_acc_chain -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_acc_chain {
using A = CubeTileM16<__half, 16, 16>;
using B = CubeTileN8<__half, 16, 8>;
using Acc = CubeAccumulatorM16<float, 16, 8>;
using Result = CubeAccumulatorM16<__half, 16, 8>;
using CScale = VecTileM32<uint8_t, 32, 4, 16, 1>;
void two_steps(Result &dst, Acc &initial, CScale &scale,
               A &a0, B &b0, A &a1, B &b1) {
  Acc partial;
  auto first = fixp::keep_acc().cscale_enable().cscale(scale)
                              .raw_acc().acc_hint();
  TMATMUL_ACC(partial, initial, a0, b0, first);
  auto final = fixp::convert<FixpPreQuantMode::F322F16>().relu().acc_hint();
  TMATMUL_ACC(dst, partial, a1, b1, final);
}
}
```

initial全为8，scale有效16×1全部为U8的1，两组A/B全部为1。第一步按行将C减半：partial=8×2^-1+16=20；第二步dst=20+16=36，FP16可精确表示。partial是第一步产生的真实FP32 Tile，第二步显式把它绑定为C。CScale物理32×4=128B；initial/partial容量512B，最终Result容量256B。第一步CCTRL同时设置raw_acc和acc_hint，第二步保留acc_hint并执行最终转换及激活。

### Shared 转置与独立 scale

<!-- audit-example: options_shared_transpose -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace options_shared_transpose {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using A = SharedTile<SharedMatrixLeft<__half, 64, 32, 35, 20>>;
using B = SharedTile<SharedMatrixRight<__half, 64, 8, 35, 8>>;
using MXA = SharedTile<SharedMatrixLeft<__fp8_e4m3, 64, 32, 35, 20>>;
using MXB = SharedTile<SharedMatrixRight<__fp8_e4m3, 64, 8, 35, 8>>;
using SA = SharedTile<Tile<Location::Vec, __fp8_e8m0, 32, 4,
                           BLayout::RowMajor, 20, 2>>;
using SB = SharedTile<Tile<Location::Vec, __fp8_e8m0, 8, 16,
                           BLayout::RowMajor, 8, 2>>;
void ordinary(D &dst, A &a, B &b) {
  auto options = fixp::keep_acc().transpose_a().transpose_b();
  TMATMUL(dst, a, b, options);
}
void scaled(D &dst, MXA &a, SA &sa, MXB &b, SB &sb) {
  auto options = fixp::keep_acc().transpose_a<true>().transpose_b<true>();
  TMATMUL_MX(dst, a, sa, b, sb, options);
}
}
```

两侧primary均按转置后的存储轴准备：A有效K×groupM=35×20，B有效K×N=35×8；运算仍为20×35乘35×8。SA有效20×2、SB有效8×2，按未转置的行/N与K组索引。所有Shared输入已经发布；四PE协作，D按本PE的16/4/0/0有效行构造，零行PE无结果可读。

primary全部为1；scale第0组为 `0x7f`、第1组为 `0x80` 时，ordinary每个有效结果为35，scaled的数学预期为32+3×2×2=44。MX 先缩放各侧输入，再按 K 顺序执行融合乘加。

这些例子按[矩阵操作数合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl)、[辅助操作数合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-postprocess.asl)及本页后处理规则逐参数推导。

## FixpAttr 与 Options 类型声明

```cpp
struct FixpAttr {
  FixpPreQuantMode PreQuant = FixpPreQuantMode::None;
  FixpReluMode Relu = FixpReluMode::None;
  uint8_t GroupNCode = 0;
  bool RowMaxEn = false, GroupMaxEn = false, RowMaxInit = false;
  bool MaxAbsEn = false, TransA = false, TransB = false, CScaleEn = false;
  CubeControl CubeCtrl = CubeCtrlNone;
  static constexpr FixpAttr keep_acc(FixpReluMode mode = FixpReluMode::None);
  static constexpr FixpAttr f16(FixpReluMode mode = FixpReluMode::None);
  static constexpr FixpAttr bf16(FixpReluMode mode = FixpReluMode::None);
  constexpr FixpAttr transpose_a(bool enable = true) const;
  constexpr FixpAttr transpose_b(bool enable = true) const;
  constexpr FixpAttr cscale_enable(bool enable = true) const;
  constexpr FixpAttr with_cube_ctrl(CubeControl control) const;
  constexpr uint32_t encoding() const;
};
namespace fixp {
template <FixpAttr Attr, typename QuantTile = NoOperand,
          typename ReluTile = NoOperand, typename RowMaxIn = NoOperand,
          typename RowMaxOut = NoOperand, typename GroupMaxOut = NoOperand,
          typename CScaleTile = NoOperand>
struct Options;
}
```

Options 的模板参数依次记录 quant、PReLU、RowMax 输入/输出、GroupMax 输出、CScale 的载体类型；通常由 builder 推导。NoOperand 是缺失 operand 的类型标记。

FixpAttr::encoding() 只编码 B.FPATR：PreQuant[31:26]、Relu[25:23]、GroupNCode[22:19]、RowMaxEn[18]、GroupMaxEn[17]、RowMaxInit[16]、MaxAbsEn[15]、CScaleEn[9]、TransB[8]、TransA[7]；保留位不由调用者填充。CubeCtrl 由独立 B.DATR CCTRL 表达，不能通过 FPATR encoding 检查其是否生效。

## 特殊值与输出顺序

固定执行函数先处理 SHIFT 12/13：按code+1算术右移并饱和为S16；该分支直接返回。其他模式先选择激活乘数，再处理特殊值和编码。None且未激活直接保留累加器位值。

在当前Sat=0接口下，进入后处理的NaN转整数得到目标最小值并置NV；转浮点得到该格式canonical NaN，sNaN置NV。无穷转整数得到目标最小值并置NV；转浮点使用目标的无穷/特殊编码，E4M3路径置OF|NX。负无穷且激活乘数为0时进入零值计算路径。负零、非零乘数、零offset且浮点输出时保留负零。矩阵乘积遵守[矩阵数值规则](MatrixRules.md#数值规则)。

Local源绑定顺序为数学输入（ACC先C，之后A及可选scaleA、B及可选scaleB，BIAS最后bias），随后可选CScale、RowMaxIn、vector quant、vector PReLU；Shared输入组从Local流移到独立Shared绑定流。输出顺序为D、RowMaxOut、GroupMaxOut。RowMax/GroupMax逐列归约最终D，并使用相同输出dtype；MaxAbs先对候选值取绝对值。

依据：[后处理特殊值及SHIFT分支](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/matrix-postprocess.asl)、[输出与归约执行](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/postprocess.asl)、[完整输入schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-postprocess.asl)。
