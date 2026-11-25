# TPREFETCH

请求 GM 矩形预取，不产生 Tile，不代替加载或同步。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <GlobalMemoryView G>
void TPREFETCH(const G &src, uint32_t valid_col, uint32_t valid_row);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `src` | in | 可读 GlobalMemoryView；提供 GM 基址和元素类型 | 必填 |
| `valid_col` | in | 有效列数，元素单位 | 必填 |
| `valid_row` | in | 有效行数，元素单位 | 必填 |

## 操作语义

请求 GM 矩形预取，不产生 Tile，不代替加载或同步。

## 合法组合与限制

dtype为已分配的非packed数值载体，含64位；packed4不属于本路径。为四个 PE 请求 GM 矩形预取，没有 Tile 输出，也不更新有效区元数据。新库接受可读 RowMajor GlobalMemoryView，包括 global_tensor 的动态视图及 subview；按视图绑定基址、物理列数和元素行距。物理列数须为非零二次幂且覆盖 valid_col，行距须覆盖所访问列。valid_col、valid_row 均为元素数量，无默认值，正值且不超过源形状。调用不替代 TLOAD 或同步；不能把预取完成当作数据已装入 Tile。

`G` / `gm_shape` 满足 [GlobalMemoryView](CommonTypes.md#globalmemoryview)。源 GM 必须可读；预取不产生 Tile 值。GM 形状和步长约束仍按本页传输规则检查，不能仅凭满足类型协议省略地址、范围和权限要求。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using G = global_tensor<const float, RowMajor<32, 32>>;
void example(const float *input) {
  G src(input);
  TPREFETCH(src, 32, 16);
}
```

input 指向可读的 32×32 连续 float 区域。 请求前 16 行、每行 32 个 float 的预取；不产生 Tile。

### 边界核对

物理列数32、有效列数17合法，物理列数24不满足二次幂要求。四PE各有自己的基址与元素行距；任一PE的地址或权限预检失败时，本次四PE预取不产生访问事件。缓存驻留与保留时间由实现决定。

## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

依据：固定 PTO 规范 [TPREFETCH.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TPREFETCH.asl) 的动态 B.DIM 与 B.IOR 绑定。GlobalMemoryView 覆盖范围属于新库设计；各 PE 提供自己的基址和行距，四 PE 的地址及权限全部预检查后才产生访问事件。

[返回算子索引](README.md)
