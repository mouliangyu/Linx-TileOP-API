# TMATMUL_MX_ACC

以C为初值，加上按组缩放后的乘积之和，再执行 options 选定的后处理。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

无 options 重载使用 Attr；需额外后处理操作数时选择 options 重载。带 groupM 重载用于 Local-A/Shared-B 的核级行分配。 MX 的 scale 参数按输入 dtype 选择，见 [MX scale](MatrixRules.md#mx-scale)。

```cpp
template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d,
          is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a, typename tile_shape_sa,
          is_local_or_shared_right tile_shape_b, typename tile_shape_sb>
  requires(mx_scale_mask_v<tile_shape_a, tile_shape_b> == 3)
void TMATMUL_MX_ACC(tile_shape_d &d, tile_shape_c &c, tile_shape_a &a,
                    tile_shape_sa &scale_a, tile_shape_b &b,
                    tile_shape_sb &scale_b);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a, typename tile_shape_sa,
          is_local_or_shared_right tile_shape_b, typename tile_shape_sb>
  requires(mx_scale_mask_v<tile_shape_a, tile_shape_b> == 3)
void TMATMUL_MX_ACC(tile_shape_d &d, tile_shape_c &c, tile_shape_a &a,
                    tile_shape_sa &scale_a, tile_shape_b &b,
                    tile_shape_sb &scale_b, size_t groupM);

template <int ScaleMask = 3, is_tile_data_v tile_shape_d, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a, typename tile_shape_sa,
          is_local_or_shared_right tile_shape_b, typename tile_shape_sb,
          fixp::is_options_v Options>
  requires(mx_scale_mask_v<tile_shape_a, tile_shape_b> == ScaleMask)
void TMATMUL_MX_ACC(tile_shape_d &d, tile_shape_c &c, tile_shape_a &a,
                    tile_shape_sa &scale_a, tile_shape_b &b,
                    tile_shape_sb &scale_b, const Options &options);

template <int ScaleMask = 3, is_tile_data_v tile_shape_d, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a, typename tile_shape_sa,
          is_local_or_shared_right tile_shape_b, typename tile_shape_sb,
          fixp::is_options_v Options>
  requires(mx_scale_mask_v<tile_shape_a, tile_shape_b> == ScaleMask)
void TMATMUL_MX_ACC(tile_shape_d &d, tile_shape_c &c, tile_shape_a &a,
                    tile_shape_sa &scale_a, tile_shape_b &b,
                    tile_shape_sb &scale_b, const Options &options,
                               size_t groupM);

template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 0)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b,
                                      const Options &options);

template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_any_tile_data_v SA,
          is_local_or_shared_right B, fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 1)
void TMATMUL_MX_ACC(D &d, C &c, A &a, SA &sa, B &b,
                                      const Options &options);

template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          is_any_tile_data_v SB, fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 2)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b, SB &sb,
                                      const Options &options);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B>
  requires(mx_scale_mask_v<A, B> == 0)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_any_tile_data_v SA,
          is_local_or_shared_right B>
  requires(mx_scale_mask_v<A, B> == 1)
void TMATMUL_MX_ACC(D &d, C &c, A &a, SA &sa, B &b);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          is_any_tile_data_v SB>
  requires(mx_scale_mask_v<A, B> == 2)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b, SB &sb);

// 显式核级行分配；scale 存在性由相应便利重载决定。
template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 0)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b,
                                      const Options &options, size_t groupM);

template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_any_tile_data_v SA,
          is_local_or_shared_right B, fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 1)
void TMATMUL_MX_ACC(D &d, C &c, A &a, SA &sa, B &b,
                                      const Options &options, size_t groupM);

template <is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          is_any_tile_data_v SB, fixp::is_options_v Options>
  requires(mx_scale_mask_v<A, B> == 2)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b, SB &sb,
                                      const Options &options, size_t groupM);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B>
  requires(mx_scale_mask_v<A, B> == 0)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b, size_t groupM);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_any_tile_data_v SA,
          is_local_or_shared_right B>
  requires(mx_scale_mask_v<A, B> == 1)
void TMATMUL_MX_ACC(D &d, C &c, A &a, SA &sa, B &b, size_t groupM);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D, is_tile_data_v C,
          is_local_or_shared_left A, is_local_or_shared_right B,
          is_any_tile_data_v SB>
  requires(mx_scale_mask_v<A, B> == 2)
void TMATMUL_MX_ACC(D &d, C &c, A &a, B &b, SB &sb, size_t groupM);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Attr` | 不需额外 operand 的 FixpAttr 后处理配置 | `FixpAttr{}` |
| `tile_shape_d` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_c` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_a` | 由对应实参推导的类型，满足 `is_local_or_shared_left` 约束 | 由实参推导 |
| `tile_shape_sa` | Attr 形式为完整 scale Tile；Options 形式按 ScaleMask 使用完整 scale Tile 或 NoOperand | 由实参推导 |
| `tile_shape_b` | 由对应实参推导的类型，满足 `is_local_or_shared_right` 约束 | 由实参推导 |
| `tile_shape_sb` | Attr 形式为完整 scale Tile；Options 形式按 ScaleMask 使用完整 scale Tile 或 NoOperand | 由实参推导 |
| `ScaleMask` | MX scale 存在位；bit0 为 A/vec，bit1 为 B/mtx | `3` |
| `Options` | 后处理与累加选项类型 | 由实参推导 |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `C` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `SA` | 由对应实参推导的类型，满足 `is_any_tile_data_v` 约束 | 由实参推导 |
| `SB` | 由对应实参推导的类型，满足 `is_any_tile_data_v` 约束 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `d` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `c` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `a` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `scale_a` | 完整 scale Tile；Options 缺失槽为 NoOperand | ScaleMask 对应位为 1 时支持 | 不接受 | 不接受 |
| `b` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `scale_b` | 完整 scale Tile；Options 缺失槽为 NoOperand | ScaleMask 对应位为 1 时支持 | 不接受 | 不接受 |
| `sa` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `sb` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `d` | out | 新结果输出 | 必填 |
| `c` | in | 已定义的累加输入 C | 必填 |
| `a` | in | 矩阵 Left 输入，逻辑 M×K | 必填 |
| `scale_a` | in | A 的分组 scale；Options 形式对应位为 0 时填 NoOperand | 必填 |
| `b` | in | 矩阵 Right 输入，逻辑 K×N；Shared 物理排列见矩阵合同 | 必填 |
| `scale_b` | in | B 的分组 scale；Options 形式对应位为 0 时填 NoOperand | 必填 |
| `groupM` | in | 四 PE 核级行数，非单 PE 行数 | 必填 |
| `options` | in | 后处理及累加选项，字段见 Options | 必填 |
| `sa` | in | A 的分组 scale | 必填 |
| `sb` | in | B 的分组 scale | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

Attr 完整参数形式要求两个 scale 均存在（ScaleMask=3）。Options 完整参数形式中，ScaleMask 的 bit0 对应 A/vec，bit1 对应 B/mtx；置位的槽传完整 scale Tile，清零的槽传 `NoOperand`。便利重载省略缺失的 scale 参数。实际 scale 的 Local/Shared 存储与对应 primary 一致。具体类型、形状和掩码组合见[MX 重载约束](MatrixRules.md#mx-重载约束)。

## 操作语义

以C为初值，加上按组缩放后的乘积之和，再执行 options 选定的后处理。有效输出为当前 PE 的 M×N。

## 合法组合与限制

无 scale、仅 A scale、仅 B scale 的便利重载分别选择 ScaleMask=0、1、2；带 groupM 的便利重载使用相同选择规则。省略的 scale 不占用实参位置。groupM 的单位、Local-A/Shared-B 条件及每 PE 行数分配见 [矩阵公共规则](MatrixRules.md)。这些便利重载属于新库接口设计。

本页各重载按声明接受完整 Left/Right/Acc/Bias/Scale 角色对象。K 分片使用已完成 C 输入与独立 D 输出形成累加链；raw_acc 结果为完整可读 Tile。groupM 指定核级行分配，options 提供后处理及累加控制。

布局、dtype 配对、协作行分配与累加链见 [矩阵公共规则](MatrixRules.md)，后处理字段见 [Options](Options.md)。

## 示例

### Local 输入与逐重载调用

<!-- audit-example: tmatmul_mx_acc_local -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_mx_acc_local {
using D = CubeAccumulatorM16<float, 16, 8, 16, 8>;
using Row = VecTileM16<float, 16, 2, 16, 1>;
using A16 = CubeTileM16<__half, 16, 64, 16, 35>;
using B16 = CubeTileN8<__half, 64, 8, 35, 8>;
using A8 = CubeTileM16<__fp8_e4m3, 16, 64, 16, 35>;
using B8 = CubeTileN8<__fp8_e4m3, 64, 8, 35, 8>;
using SA = VecTileM32<__fp8_e8m0, 32, 4, 16, 2>;
using SB = VecTileM32<__fp8_e8m0, 32, 4, 8, 2>;

void scale0(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, b);
  TMATMUL_MX_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row));
}

void scale1(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b);
  TMATMUL_MX_ACC(by_options, c, a, sa, b, fixp::keep_acc().row_max(row));
}

void scale2(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, b, sb);
  TMATMUL_MX_ACC(by_options, c, a, b, sb, fixp::keep_acc().row_max(row));
}

void scale3(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b, sb);
  TMATMUL_MX_ACC(by_options, c, a, sa, b, sb, fixp::keep_acc().row_max(row));
}

void explicit_slots0(D &dst, D &c, A16 &a, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<0>(dst, c, a, absent, b, absent, fixp::keep_acc());
}

void explicit_slots1(D &dst, D &c, A8 &a, SA &sa, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<1>(dst, c, a, sa, b, absent, fixp::keep_acc());
}

void explicit_slots2(D &dst, D &c, A16 &a, B8 &b, SB &sb) {
  NoOperand absent;
  TMATMUL_MX_ACC<2>(dst, c, a, absent, b, sb, fixp::keep_acc());
}

}
```
输入的有效 K=35，物理 K=64；有效 M=16、N=8。所有 primary 的有效元素取数值1。每侧需要 scale 时，第0组用 E8M0 `0x7f`（1），第1组用 `0x80`（2）。两组分别覆盖 k=0..31 和 k=32..34。Local SA/SB物理形状均为32×4=128B，分别有M×2和8×2元素有效。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

| 函数 | scale 存在位 | 每个有效输出的数学预期 |
| --- | ---: | --- |
| `scale0` | 0 | 32 + 3 × 1 + 2 = 37 |
| `scale1` | 1 | 32 + 3 × 2 + 2 = 40 |
| `scale2` | 2 | 32 + 3 × 2 + 2 = 40 |
| `scale3` | 3 | 32 + 3 × 4 + 2 = 46 |

`explicit_slots0/1/2` 使用同一组输入，结果分别与 `scale0/1/2` 相同；完整 Options 重载显式提供 `NoOperand` 占位。结果按[矩阵数值规则](MatrixRules.md#数值规则)计算。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 8 | `scale0` 中的 `by_attr` 调用 |
| 5 | `scale0` 中的 `by_options` 调用 |
| 9 | `scale1` 中的 `by_attr` 调用 |
| 6 | `scale1` 中的 `by_options` 调用 |
| 10 | `scale2` 中的 `by_attr` 调用 |
| 7 | `scale2` 中的 `by_options` 调用 |
| 1 | `scale3` 中的 `by_attr` 调用 |
| 3 | `scale3` 中的 `by_options` 调用 |

### Local A 与 Shared B：显式 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；A 使用 `(validM, 35)` 构造并准备对应核级行块；Local SA 使用 `(validM, 2)` 构造；C 使用 `(validM, 8)` 构造，参与行的初值为2；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_mx_acc_mixed -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_mx_acc_mixed {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = CubeTileM16<__half, 16, 64, DYNAMIC, 35>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;
using A8 = CubeTileM16<__fp8_e4m3, 16, 64, DYNAMIC, 35>;
using B8 = SharedTile<SharedMatrixRight<__fp8_e4m3, 8, 64, 8, 35>>;
using SA = VecTileM32<__fp8_e8m0, 32, 4, DYNAMIC, 2>;
using SB = SharedTile<Tile<Location::Vec, __fp8_e8m0, 8, 16, BLayout::RowMajor, 8, 2>>;

void scale0(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, b, size_t{20});
  TMATMUL_MX_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row), size_t{20});
}

void scale1(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b, size_t{20});
  TMATMUL_MX_ACC(by_options, c, a, sa, b, fixp::keep_acc().row_max(row), size_t{20});
}

void scale2(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, b, sb, size_t{20});
  TMATMUL_MX_ACC(by_options, c, a, b, sb, fixp::keep_acc().row_max(row), size_t{20});
}

void scale3(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b, sb, size_t{20});
  TMATMUL_MX_ACC(by_options, c, a, sa, b, sb, fixp::keep_acc().row_max(row), size_t{20});
}

void explicit_slots0(D &dst, D &c, A16 &a, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<0>(dst, c, a, absent, b, absent, fixp::keep_acc(), size_t{20});
}

void explicit_slots1(D &dst, D &c, A8 &a, SA &sa, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<1>(dst, c, a, sa, b, absent, fixp::keep_acc(), size_t{20});
}

void explicit_slots2(D &dst, D &c, A16 &a, B8 &b, SB &sb) {
  NoOperand absent;
  TMATMUL_MX_ACC<2>(dst, c, a, absent, b, sb, fixp::keep_acc(), size_t{20});
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；所有 primary 的有效元素取数值1。每侧需要 scale 时，第0组用 E8M0 `0x7f`（1），第1组用 `0x80`（2）。两组分别覆盖 k=0..31 和 k=32..34。Local SA物理32×4=128B、有效M×2；Shared SB物理8×16=128B、有效8×2。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

| 函数 | scale 存在位 | 每个有效输出的数学预期 |
| --- | ---: | --- |
| `scale0` | 0 | 32 + 3 × 1 + 2 = 37 |
| `scale1` | 1 | 32 + 3 × 2 + 2 = 40 |
| `scale2` | 2 | 32 + 3 × 2 + 2 = 40 |
| `scale3` | 3 | 32 + 3 × 4 + 2 = 46 |

`explicit_slots0/1/2` 使用同一组输入，结果分别与 `scale0/1/2` 相同；完整 Options 重载显式提供 `NoOperand` 占位。结果按[矩阵数值规则](MatrixRules.md#数值规则)计算。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 14 | `scale0` 中的 `by_attr` 调用 |
| 11 | `scale0` 中的 `by_options` 调用 |
| 15 | `scale1` 中的 `by_attr` 调用 |
| 12 | `scale1` 中的 `by_options` 调用 |
| 16 | `scale2` 中的 `by_attr` 调用 |
| 13 | `scale2` 中的 `by_options` 调用 |
| 2 | `scale3` 中的 `by_attr` 调用 |
| 4 | `scale3` 中的 `by_options` 调用 |

### Shared A 与 Shared B：推导 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；C 使用 `(validM, 8)` 构造，参与行的初值为2；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_mx_acc_shared -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_mx_acc_shared {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = SharedTile<SharedMatrixLeft<__half, 32, 64, 20, 35>>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;
using A8 = SharedTile<SharedMatrixLeft<__fp8_e4m3, 32, 64, 20, 35>>;
using B8 = SharedTile<SharedMatrixRight<__fp8_e4m3, 8, 64, 8, 35>>;
using SA = SharedTile<Tile<Location::Vec, __fp8_e8m0, 32, 4, BLayout::RowMajor, 20, 2>>;
using SB = SharedTile<Tile<Location::Vec, __fp8_e8m0, 8, 16, BLayout::RowMajor, 8, 2>>;

void scale0(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, b);
  TMATMUL_MX_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row));
}

void scale1(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B16 &b) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b);
  TMATMUL_MX_ACC(by_options, c, a, sa, b, fixp::keep_acc().row_max(row));
}

void scale2(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, b, sb);
  TMATMUL_MX_ACC(by_options, c, a, b, sb, fixp::keep_acc().row_max(row));
}

void scale3(D &by_attr, D &by_options, Row &row, D &c, A8 &a, SA &sa, B8 &b, SB &sb) {
  TMATMUL_MX_ACC(by_attr, c, a, sa, b, sb);
  TMATMUL_MX_ACC(by_options, c, a, sa, b, sb, fixp::keep_acc().row_max(row));
}

void explicit_slots0(D &dst, D &c, A16 &a, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<0>(dst, c, a, absent, b, absent, fixp::keep_acc());
}

void explicit_slots1(D &dst, D &c, A8 &a, SA &sa, B16 &b) {
  NoOperand absent;
  TMATMUL_MX_ACC<1>(dst, c, a, sa, b, absent, fixp::keep_acc());
}

void explicit_slots2(D &dst, D &c, A16 &a, B8 &b, SB &sb) {
  NoOperand absent;
  TMATMUL_MX_ACC<2>(dst, c, a, absent, b, sb, fixp::keep_acc());
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；Shared A 有效20×35、物理32×64；所有 primary 的有效元素取数值1。每侧需要 scale 时，第0组用 E8M0 `0x7f`（1），第1组用 `0x80`（2）。两组分别覆盖 k=0..31 和 k=32..34。Shared SA物理32×4=128B、有效20×2；Shared SB物理8×16=128B、有效8×2。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

| 函数 | scale 存在位 | 每个有效输出的数学预期 |
| --- | ---: | --- |
| `scale0` | 0 | 32 + 3 × 1 + 2 = 37 |
| `scale1` | 1 | 32 + 3 × 2 + 2 = 40 |
| `scale2` | 2 | 32 + 3 × 2 + 2 = 40 |
| `scale3` | 3 | 32 + 3 × 4 + 2 = 46 |

`explicit_slots0/1/2` 使用同一组输入，结果分别与 `scale0/1/2` 相同；完整 Options 重载显式提供 `NoOperand` 占位。结果按[矩阵数值规则](MatrixRules.md#数值规则)计算。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 8 | `scale0` 中的 `by_attr` 调用 |
| 5 | `scale0` 中的 `by_options` 调用 |
| 9 | `scale1` 中的 `by_attr` 调用 |
| 6 | `scale1` 中的 `by_options` 调用 |
| 10 | `scale2` 中的 `by_attr` 调用 |
| 7 | `scale2` 中的 `by_options` 调用 |
| 1 | `scale3` 中的 `by_attr` 调用 |
| 3 | `scale3` 中的 `by_options` 调用 |

### 后处理与辅助输出

完整的转换、RowMax/GroupMax、CScale、raw_acc、acc_hint、量化和转置函数见 [Options 组合示例](Options.md#完整组合示例)。M32 的协作尾行和其他 scale 格式见[矩阵边界示例](MatrixRules.md#更多形状与格式示例)。

## 公共规则与相关接口

本接口同时遵守 [Matrix 公共参数、类型、形状、别名及示例](MatrixRules.md)。该页中的规则与本页声明共同构成调用合同。

**Tile 生命周期：** [矩阵与 Shared 操作边界](StorageBoundaries.md)。

[返回算子索引](README.md)
