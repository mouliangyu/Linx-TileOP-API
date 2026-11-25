# TSTORE_PART

由 PEMask 指定的参与 PE 将已发布 Shared 源的有效矩形写入 GM。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <int PEMask = 15, GlobalMemoryView G, SharedReadable S>
void TSTORE_PART(G &dst, const S &src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | `15` |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `src` | SharedReadable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out（GM 内存） | 可写 GlobalMemoryView；其指向的 GM 内存接收结果 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

由 PEMask 指定的参与 PE 将已发布 Shared 源的有效矩形写入 GM。

## 合法组合与限制

src 是已发布的 Shared RowMajor 输入或其 Reader 描述；dst 是 GM 内存写目标。写入有效矩形，GM地址与行距来自global_tensor；构造器的元素行距由库换算为汇编字节行距，GM dtype、可访问范围与源有效矩形必须匹配。写入范围只包含有效元素。TSTORE_PART 的 PEMask 选择参与消费的 PE，可编码值为0、1、2、4、8、12、14、15，默认15；0为严格no-op。每个参与 PE 使用自己的 GM 基址和行距。Reader 明确选择源范围，mask 选择参与者。

普通存储遇到首个地址、权限或对齐错误时停止，先前完成的 GM 写入可能已经可见。Shared 源保持其 payload、描述符和发布状态。

`G` / `gm_shape` 满足 [GlobalMemoryView](CommonTypes.md#globalmemoryview)。目标 GM 必须可写，元素类型与存储源匹配。GM 形状和步长约束仍按本页传输规则检查，不能仅凭满足类型协议省略地址、范围和权限要求。

**发布与分片边界：** [StorageBoundaries](StorageBoundaries.md)。

Shared 分片与发布的完整要求见 [Shared 存储合同](StorageBoundaries.md)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using N = Tile<Location::Vec, float, 16, 8>;
using S = SharedTile<N>;
using G = global_tensor<float, RowMajor<16, 8>>;
void example(float *memory, S &src) {
  G dst(memory);
  TSTORE_PART<8>(dst, src);
}
```

src 已发布并就绪，memory 指向可写的 128 个 float；仅 PE0 参与。 PE0 将 Shared 的有效 16×8 元素写入 GM。

### 边界核对

对同一已发布源调用`TSTORE_PART<0>`不读源或访问GM。若PE0以mask8向两个连续有效行写回，而第二行地址发生权限错误，第一行已经完成的写入可以保留。Shared Reader保持父物理行距，GM的行距与起点由目标视图独立提供。类型域沿用[TSTORE](TSTORE.md#合法组合与限制)的Shared RowMajor分支。


## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
