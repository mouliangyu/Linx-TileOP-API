# TMATMUL

以零为初值，加上乘积之和，再执行 options 选定的后处理。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

无 options 重载使用 Attr；需额外后处理操作数时选择 options 重载。带 groupM 重载用于 Local-A/Shared-B 的核级行分配。

```cpp
template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b>
void TMATMUL(tile_shape_c &c, tile_shape_a &a,
                              tile_shape_b &b);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b>
void TMATMUL(tile_shape_c &c, tile_shape_a &a,
                              tile_shape_b &b, size_t groupM);

template <is_tile_data_v tile_shape_d,
          is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b, fixp::is_options_v Options>
void TMATMUL(tile_shape_d &d, tile_shape_a &a,
                               tile_shape_b &b, const Options &options,
                               size_t groupM);

template <is_tile_data_v tile_shape_d, is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b, fixp::is_options_v Options>
void TMATMUL(tile_shape_d &d, tile_shape_a &a,
                                    tile_shape_b &b, const Options &options);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Attr` | 不需额外 operand 的 FixpAttr 后处理配置 | `FixpAttr{}` |
| `tile_shape_c` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_a` | 由对应实参推导的类型，满足 `is_local_or_shared_left` 约束 | 由实参推导 |
| `tile_shape_b` | 由对应实参推导的类型，满足 `is_local_or_shared_right` 约束 | 由实参推导 |
| `tile_shape_d` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `Options` | 后处理与累加选项类型 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `c` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `a` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `b` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `d` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `c` | out | 新矩阵结果输出 | 必填 |
| `a` | in | 矩阵 Left 输入，逻辑 M×K | 必填 |
| `b` | in | 矩阵 Right 输入，逻辑 K×N；Shared 物理排列见矩阵合同 | 必填 |
| `groupM` | in | 四 PE 核级行数，非单 PE 行数 | 必填 |
| `d` | out | 新结果输出 | 必填 |
| `options` | in | 后处理及累加选项，字段见 Options | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

以零为初值，加上乘积之和，再执行 options 选定的后处理。有效输出为当前 PE 的 M×N。

## 合法组合与限制

本页各重载按声明接受完整 Left/Right/Acc/Bias/Scale 角色对象。K 分片使用已完成 C 输入与独立 D 输出形成累加链；raw_acc 结果为完整可读 Tile。groupM 指定核级行分配，options 提供后处理及累加控制。

布局、dtype 配对、协作行分配与累加链见 [矩阵公共规则](MatrixRules.md)，后处理字段见 [Options](Options.md)。

## 示例

### Local 输入与逐重载调用

<!-- audit-example: tmatmul_local -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_local {
using D = CubeAccumulatorM16<float, 16, 8, 16, 8>;
using Row = VecTileM16<float, 16, 2, 16, 1>;
using A16 = CubeTileM16<__half, 16, 64, 16, 35>;
using B16 = CubeTileN8<__half, 64, 8, 35, 8>;

void product(D &by_attr, D &by_options, Row &row, A16 &a, B16 &b) {
  TMATMUL(by_attr, a, b);
  TMATMUL(by_options, a, b, fixp::keep_acc().row_max(row));
}

}
```
输入的有效 K=35，物理 K=64；有效 M=16、N=8。所有 primary 的有效元素取数值1。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 1 | `product` 中的 `by_attr` 调用 |
| 4 | `product` 中的 `by_options` 调用 |

### Local A 与 Shared B：显式 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；A 使用 `(validM, 35)` 构造并准备对应核级行块；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_mixed -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_mixed {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = CubeTileM16<__half, 16, 64, DYNAMIC, 35>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;

void product(D &by_attr, D &by_options, Row &row, A16 &a, B16 &b) {
  TMATMUL(by_attr, a, b, size_t{20});
  TMATMUL(by_options, a, b, fixp::keep_acc().row_max(row), size_t{20});
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；所有 primary 的有效元素取数值1。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 2 | `product` 中的 `by_attr` 调用 |
| 3 | `product` 中的 `by_options` 调用 |

### Shared A 与 Shared B：推导 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_shared -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_shared {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = SharedTile<SharedMatrixLeft<__half, 32, 64, 20, 35>>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;

void product(D &by_attr, D &by_options, Row &row, A16 &a, B16 &b) {
  TMATMUL(by_attr, a, b);
  TMATMUL(by_options, a, b, fixp::keep_acc().row_max(row));
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；Shared A 有效20×35、物理32×64；所有 primary 的有效元素取数值1。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 1 | `product` 中的 `by_attr` 调用 |
| 4 | `product` 中的 `by_options` 调用 |

### 后处理与辅助输出

完整的转换、RowMax/GroupMax、CScale、raw_acc、acc_hint、量化和转置函数见 [Options 组合示例](Options.md#完整组合示例)。M32 的协作尾行和其他 scale 格式见[矩阵边界示例](MatrixRules.md#更多形状与格式示例)。

## 公共规则与相关接口

本接口同时遵守 [Matrix 公共参数、类型、形状、别名及示例](MatrixRules.md)。该页中的规则与本页声明共同构成调用合同。

**Tile 生命周期：** [矩阵与 Shared 操作边界](StorageBoundaries.md)。

[返回算子索引](README.md)
