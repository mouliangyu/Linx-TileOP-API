# TGEMV_MX_BIAS

以零为初值累加按组缩放后的乘积，在 K 累加完成后加上按列广播的 bias，再执行 options 选定的后处理。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

无 options 重载使用 Attr；需额外后处理操作数时选择 options 重载。 MX 的 scale 参数按输入 dtype 选择，见 [MX scale](MatrixRules.md#mx-scale)。

```cpp
template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d, is_local_tile_v tile_shape_mtx,
          is_local_tile_v tile_shape_smtx,
          is_local_tile_v tile_shape_vec,
          is_local_tile_v tile_shape_svec,
          is_tile_data_v tile_shape_bias>
  requires(mx_scale_mask_v<tile_shape_vec, tile_shape_mtx> == 3)
void TGEMV_MX_BIAS(tile_shape_d &d, tile_shape_mtx &mtx, tile_shape_smtx &smtx,
                 tile_shape_vec &vec, tile_shape_svec &svec,
                 tile_shape_bias &bias);

template <int ScaleMask = 3, is_tile_data_v tile_shape_d, is_local_tile_v tile_shape_mtx,
          typename tile_shape_smtx,
          is_local_tile_v tile_shape_vec,
          typename tile_shape_svec,
          is_tile_data_v tile_shape_bias, fixp::is_options_v Options>
  requires(mx_scale_mask_v<tile_shape_vec, tile_shape_mtx> == ScaleMask)
void TGEMV_MX_BIAS(tile_shape_d &d, tile_shape_mtx &mtx, tile_shape_smtx &smtx,
                 tile_shape_vec &vec, tile_shape_svec &svec,
                 tile_shape_bias &bias,
                  const Options &options);

template <is_tile_data_v D, is_local_tile_v Mtx, is_local_tile_v Vec,
          is_tile_data_v Bias, fixp::is_options_v Options>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 0)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, Vec &vec, Bias &bias,
                                     const Options &options);

template <is_tile_data_v D, is_local_tile_v Mtx, is_local_tile_v Vec,
          is_local_tile_v ScaleVec, is_tile_data_v Bias,
          fixp::is_options_v Options>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 1)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, Vec &vec,
                                     ScaleVec &scale_vec, Bias &bias,
                                     const Options &options);

template <is_tile_data_v D, is_local_tile_v Mtx,
          is_local_tile_v ScaleMtx, is_local_tile_v Vec, is_tile_data_v Bias,
          fixp::is_options_v Options>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 2)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, ScaleMtx &scale_mtx,
                                     Vec &vec, Bias &bias,
                                     const Options &options);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D,
          is_local_tile_v Mtx, is_local_tile_v Vec, is_tile_data_v Bias>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 0)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, Vec &vec, Bias &bias);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D,
          is_local_tile_v Mtx, is_local_tile_v Vec,
          is_local_tile_v ScaleVec, is_tile_data_v Bias>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 1)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, Vec &vec,
                                     ScaleVec &scale_vec, Bias &bias);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v D,
          is_local_tile_v Mtx, is_local_tile_v ScaleMtx,
          is_local_tile_v Vec, is_tile_data_v Bias>
  requires(tile_role_v<Mtx> == Location::Right &&
           tile_role_v<Vec> == Location::Left &&
           mx_scale_mask_v<Vec, Mtx> == 2)
void TGEMV_MX_BIAS(D &d, Mtx &mtx, ScaleMtx &scale_mtx,
                                     Vec &vec, Bias &bias);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Attr` | 不需额外 operand 的 FixpAttr 后处理配置 | `FixpAttr{}` |
| `tile_shape_d` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_mtx` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `tile_shape_smtx` | Attr 形式为完整 scale Tile；Options 形式按 ScaleMask 使用完整 scale Tile 或 NoOperand | 由实参推导 |
| `tile_shape_vec` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `tile_shape_svec` | Attr 形式为完整 scale Tile；Options 形式按 ScaleMask 使用完整 scale Tile 或 NoOperand | 由实参推导 |
| `tile_shape_bias` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `ScaleMask` | MX scale 存在位；bit0 为 A/vec，bit1 为 B/mtx | `3` |
| `Options` | 后处理与累加选项类型 | 由实参推导 |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `Mtx` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `Vec` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `Bias` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `ScaleVec` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `ScaleMtx` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `d` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `mtx` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `smtx` | 完整 scale Tile；Options 缺失槽为 NoOperand | ScaleMask 对应位为1时支持 | 不接受 | 不接受 |
| `vec` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `svec` | 完整 scale Tile；Options 缺失槽为 NoOperand | ScaleMask 对应位为1时支持 | 不接受 | 不接受 |
| `bias` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `scale_vec` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `scale_mtx` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `d` | out | 新结果输出 | 必填 |
| `mtx` | in | Right 矩阵输入，逻辑 K×N | 必填 |
| `smtx` | in | mtx 的分组 scale | 必填 |
| `vec` | in | Left 向量输入，逻辑 1×K | 必填 |
| `svec` | in | vec 的分组 scale | 必填 |
| `bias` | in | 按列广播的 Bias 输入 | 必填 |
| `options` | in | 后处理及累加选项，字段见 Options | 必填 |
| `scale_vec` | in | vec 的分组 scale | 必填 |
| `scale_mtx` | in | mtx 的分组 scale | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

Attr 完整参数形式要求两个 scale 均存在（ScaleMask=3）。Options 完整参数形式中，ScaleMask 的 bit0 对应 A/vec，bit1 对应 B/mtx；置位的槽传完整 scale Tile，清零的槽传 `NoOperand`。便利重载省略缺失的 scale 参数。实际 scale 为 Local Tile，与对应 primary 配对。具体类型、形状和掩码组合见[MX 重载约束](MatrixRules.md#mx-重载约束)。

## 操作语义

以零为初值累加按组缩放后的乘积，在 K 累加完成后加上按列广播的 bias，再执行 options 选定的后处理。有效输出为 1×N；mtx 为 Right，vec 为 Left。

## 合法组合与限制

本页各重载按声明接受完整 Left/Right/Acc/Bias/Scale 角色对象。K 分片使用已完成 C 输入与独立 D 输出形成累加链；raw_acc 结果为完整可读 Tile。options 提供本页声明所列的控制参数。

布局、dtype 配对、协作行分配与累加链见 [矩阵公共规则](MatrixRules.md)，后处理字段见 [Options](Options.md)。

偏置在K维乘积累加完成后通过MatrixBiasResult加入，浮点舍入顺序按这一顺序执行。依据固定[cube.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/cube.asl)。

## 示例

### Local 输入与逐重载调用

<!-- audit-example: tgemv_mx_bias_local -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tgemv_mx_bias_local {
using D = CubeAccumulatorM16<float, 16, 8, 1, 8>;
using Row = VecTileM16<float, 16, 2, 1, 1>;
using Bias = CubeBias<float, 8>;
using A16 = CubeTileM16<__half, 16, 64, 1, 35>;
using B16 = CubeTileN8<__half, 64, 8, 35, 8>;
using A8 = CubeTileM16<__fp8_e4m3, 16, 64, 1, 35>;
using B8 = CubeTileN8<__fp8_e4m3, 64, 8, 35, 8>;
using SA = VecTileM32<__fp8_e8m0, 32, 4, 1, 2>;
using SB = VecTileM32<__fp8_e8m0, 32, 4, 8, 2>;

void scale0(D &by_attr, D &by_options, Row &row, A16 &a, B16 &b, Bias &bias) {
  TGEMV_MX_BIAS(by_attr, b, a, bias);
  TGEMV_MX_BIAS(by_options, b, a, bias, fixp::keep_acc().row_max(row));
}

void scale1(D &by_attr, D &by_options, Row &row, A8 &a, SA &sa, B16 &b, Bias &bias) {
  TGEMV_MX_BIAS(by_attr, b, a, sa, bias);
  TGEMV_MX_BIAS(by_options, b, a, sa, bias, fixp::keep_acc().row_max(row));
}

void scale2(D &by_attr, D &by_options, Row &row, A16 &a, B8 &b, SB &sb, Bias &bias) {
  TGEMV_MX_BIAS(by_attr, b, sb, a, bias);
  TGEMV_MX_BIAS(by_options, b, sb, a, bias, fixp::keep_acc().row_max(row));
}

void scale3(D &by_attr, D &by_options, Row &row, A8 &a, SA &sa, B8 &b, SB &sb, Bias &bias) {
  TGEMV_MX_BIAS(by_attr, b, sb, a, sa, bias);
  TGEMV_MX_BIAS(by_options, b, sb, a, sa, bias, fixp::keep_acc().row_max(row));
}

void explicit_slots0(D &dst, A16 &a, B16 &b, Bias &bias) {
  NoOperand absent;
  TGEMV_MX_BIAS<0>(dst, b, absent, a, absent, bias, fixp::keep_acc());
}

void explicit_slots1(D &dst, A8 &a, SA &sa, B16 &b, Bias &bias) {
  NoOperand absent;
  TGEMV_MX_BIAS<1>(dst, b, absent, a, sa, bias, fixp::keep_acc());
}

void explicit_slots2(D &dst, A16 &a, B8 &b, SB &sb, Bias &bias) {
  NoOperand absent;
  TGEMV_MX_BIAS<2>(dst, b, sb, a, absent, bias, fixp::keep_acc());
}

}
```
输入的有效 K=35，物理 K=64；有效 M=1、N=8。所有 primary 的有效元素取数值1。每侧需要 scale 时，第0组用 E8M0 `0x7f`（1），第1组用 `0x80`（2）。两组分别覆盖 k=0..31 和 k=32..34。Local SA/SB物理形状均为32×4=128B，分别有M×2和8×2元素有效。bias 的8个有效元素均为2，乘积和完成后加入。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

| 函数 | scale 存在位 | 每个有效输出的数学预期 |
| --- | ---: | --- |
| `scale0` | 0 | 32 + 3 × 1 + 2 = 37 |
| `scale1` | 1 | 32 + 3 × 2 + 2 = 40 |
| `scale2` | 2 | 32 + 3 × 2 + 2 = 40 |
| `scale3` | 3 | 32 + 3 × 4 + 2 = 46 |

`explicit_slots0/1/2` 使用同一组输入，结果分别与 `scale0/1/2` 相同；完整 Options 重载显式提供 `NoOperand` 占位。结果按[矩阵数值规则](MatrixRules.md#数值规则)计算。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 6 | `scale0` 中的 `by_attr` 调用 |
| 3 | `scale0` 中的 `by_options` 调用 |
| 7 | `scale1` 中的 `by_attr` 调用 |
| 4 | `scale1` 中的 `by_options` 调用 |
| 8 | `scale2` 中的 `by_attr` 调用 |
| 5 | `scale2` 中的 `by_options` 调用 |
| 1 | `scale3` 中的 `by_attr` 调用 |
| 2 | `scale3` 中的 `by_options` 调用 |

### 后处理与辅助输出

完整的转换、RowMax/GroupMax、CScale、raw_acc、acc_hint、量化和转置函数见 [Options 组合示例](Options.md#完整组合示例)。M32 的协作尾行和其他 scale 格式见[矩阵边界示例](MatrixRules.md#更多形状与格式示例)。

## 公共规则与相关接口

本接口同时遵守 [Matrix 公共参数、类型、形状、别名及示例](MatrixRules.md)。该页中的规则与本页声明共同构成调用合同。

**Tile 生命周期：** [矩阵与 Shared 操作边界](StorageBoundaries.md)。

[返回算子索引](README.md)
