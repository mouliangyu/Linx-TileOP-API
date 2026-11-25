# TMOV_CUBE_TO_SHARED_ND

将 Local CUBE_M16/M32 按逻辑元素转换为 Shared RowMajor ND，不进行数值转换。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <int PEMask, SharedWritable D, Readable S>
void TMOV_CUBE_TO_SHARED_ND(D &&dst, const S &src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | 显式指定 |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | SharedWritable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

将 Local CUBE_M16/M32 按逻辑元素转换为 Shared RowMajor ND，不进行数值转换。

## 合法组合与限制

多 PE CUBE→ND 通过统一 TMOV 的 Shared Writer 目标表达，遵守完整行转换和发布合同。

D/S 分别描述目标/源计算视图，必须符合本页方向的存储与布局。PEMask 为必填编译期参与 PE 位掩码，无默认值。两种方向都要求 dtype 相同；Local 为 M16/M32，Shared 为 unboxed RowMajor。转换保持逻辑坐标及元素原始编码。N8、RCPE6M2 不支持。

容量、方向与发布要求见 [Local CUBE / Shared ND 转换](TransportRules.md#local-cube--shared-nd-转换)及 [Shared 存储合同](StorageBoundaries.md)。

### Writer 的容量与放置

完整输出要求源和 Shared parent 容量相等。Writer 输出要求源与 Part 容量相等；parent 可大于 Part。源 M16/M32 的物理列数必须等于由源容量和 dtype 推导的精确列数，Shared parent 保持此列距。cell_offset 使用128B单位，插入范围须完全落在 parent 内。有效源元素按逻辑坐标转换；padding 写 raw 零并保留未定义状态。

例如 FP32 M16 源16×8占512B，Part也为512B；Shared parent32×8占1024B。偏移0、4分别选择parent的前、后16行。这验证片段几何。跨PE阶段、调用位置及发布还受[Shared提交核对项](../TileOpContractEvidence.md#shared-提交身份)约束。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using C = VecTileM16<float, 16, 8>;
using N = Tile<Location::Vec, float, 16, 8>;
using S = SharedTile<N>;
void example(S &dst, C &src) {
  TMOV_CUBE_TO_SHARED_ND<8>(dst, src);
}
```

src 已定义且容量为 512B，Shared 目标也是 512B；仅 PE0 由掩码 8 参与。 PE0 将 16×8 的 Local CUBE 结果转换为 Shared ND 并发布。

## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
