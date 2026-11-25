# TGEMV

以零为初值，加上乘积之和，再执行 options 选定的后处理。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

无 options 重载使用 Attr；需额外后处理操作数时选择 options 重载。

```cpp
template <is_tile_data_v tile_shape_d, is_local_tile_v tile_shape_mtx,
          is_local_tile_v tile_shape_vec, fixp::is_options_v Options>
void TGEMV(tile_shape_d &d, tile_shape_mtx &mtx,
                             tile_shape_vec &vec, const Options &options);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d, is_local_tile_v tile_shape_mtx,
          is_local_tile_v tile_shape_vec>
void TGEMV(tile_shape_d &d, tile_shape_mtx &mtx,
                 tile_shape_vec &vec);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `tile_shape_d` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_mtx` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `tile_shape_vec` | 由对应实参推导的类型，满足 `is_local_tile_v` 约束 | 由实参推导 |
| `Options` | 后处理与累加选项类型 | 由实参推导 |
| `Attr` | 不需额外 operand 的 FixpAttr 后处理配置 | `FixpAttr{}` |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `d` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `mtx` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `vec` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `d` | out | 新结果输出 | 必填 |
| `mtx` | in | Right 矩阵输入，逻辑 K×N | 必填 |
| `vec` | in | Left 向量输入，逻辑 1×K | 必填 |
| `options` | in | 后处理及累加选项，字段见 Options | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

以零为初值，加上乘积之和，再执行 options 选定的后处理。有效输出为 1×N；mtx 为 Right，vec 为 Left。

## 合法组合与限制

本页各重载按声明接受完整 Left/Right/Acc/Bias/Scale 角色对象。K 分片使用已完成 C 输入与独立 D 输出形成累加链；raw_acc 结果为完整可读 Tile。options 提供本页声明所列的控制参数。

布局、dtype 配对、协作行分配与累加链见 [矩阵公共规则](MatrixRules.md)，后处理字段见 [Options](Options.md)。

## 示例

### Local 输入与逐重载调用

<!-- audit-example: tgemv_local -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tgemv_local {
using D = CubeAccumulatorM16<float, 16, 8, 1, 8>;
using Row = VecTileM16<float, 16, 2, 1, 1>;
using A16 = CubeTileM16<__half, 16, 64, 1, 35>;
using B16 = CubeTileN8<__half, 64, 8, 35, 8>;

void product(D &by_attr, D &by_options, Row &row, A16 &a, B16 &b) {
  TGEMV(by_attr, b, a);
  TGEMV(by_options, b, a, fixp::keep_acc().row_max(row));
}

}
```
输入的有效 K=35，物理 K=64；有效 M=1、N=8。所有 primary 的有效元素取数值1。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 2 | `product` 中的 `by_attr` 调用 |
| 1 | `product` 中的 `by_options` 调用 |

### 后处理与辅助输出

完整的转换、RowMax/GroupMax、CScale、raw_acc、acc_hint、量化和转置函数见 [Options 组合示例](Options.md#完整组合示例)。M32 的协作尾行和其他 scale 格式见[矩阵边界示例](MatrixRules.md#更多形状与格式示例)。

## 公共规则与相关接口

本接口同时遵守 [Matrix 公共参数、类型、形状、别名及示例](MatrixRules.md)。该页中的规则与本页声明共同构成调用合同。

**Tile 生命周期：** [矩阵与 Shared 操作边界](StorageBoundaries.md)。

[返回算子索引](README.md)
