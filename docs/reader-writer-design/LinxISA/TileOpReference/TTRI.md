# TTRI

生成下三角矩阵 `dst[r,c] = (c <= r ? 1 : 0)`，对角线偏移为 0。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D> void TTRI(D &&dst);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |

D 为 Local RowMajor 输出，dtype 为 FP64、FP32、FP16、S64、S32、S16、U64、U32、U16，有效 R/C 均为正。dst 为 out，无其他参数。该公开入口采用默认 lower、对角线偏移 0：`dst[r,c] = (c <= r ? 1 : 0)`。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |

## 操作语义

生成下三角矩阵 `dst[r,c] = (c <= r ? 1 : 0)`，对角线偏移为 0。

## 合法组合与限制

第 0 行为 1,0,…，第 1 行为 1,1,0,…。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Triangle = Tile<Location::Vec, float, 32, 32>;
void triangle(Triangle &dst) { TTRI(dst); }
```

### 边界核对

有效2×3结果两行为[1,0,0]、[1,1,0]，物理容量独立满足最小128B。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Irregular 公共参数、类型、形状、别名及示例](IrregularRules.md)。该页中的规则与本页声明共同构成调用合同。

固定依据：[TTRI 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TTRI.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
