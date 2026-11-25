# TMOV_SHARED_ND_TO_CUBE

将已发布的 Shared RowMajor ND 转换为 Local CUBE_M16/M32；每个参与 PE 得到独立的完整结果。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <int PEMask = 15, is_local_tile_v D, SharedReadable S>
void TMOV_SHARED_ND_TO_CUBE(D &dst, const S &src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | `15` |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | is_local_tile_v | 支持 | 不接受 | 不接受 |
| `src` | SharedReadable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

将已发布的 Shared RowMajor ND 转换为 Local CUBE_M16/M32；每个参与 PE 得到独立的完整结果。

## 合法组合与限制

D/S 分别描述目标/源计算视图，必须符合本页方向的存储与布局。PEMask 为编译期参与 PE 位掩码，默认 15。两种方向都要求 dtype 相同；Local 为 M16/M32，Shared 为 unboxed RowMajor。转换保持逻辑坐标及元素原始编码。N8、RCPE6M2 不支持。

ND→CUBE 不支持 M16 b64；M32 b64 使用双 CELL 映射。Shared 源必须已发布。目标有效形状按源描述符及转换规则确定。输出 padding 写原始零，但仍不属于有效区域。该方向 mask=0 为严格 no-op。

目标 D 必须是完整 M16/M32 Tile，不能为 Writer 描述；源 S 可以是已发布 Shared Reader 视图。PEMask 的合法值和位序见 [Shared TMOV 的 PEMask](StorageBoundaries.md#shared-tmov-的-pemask)。默认 15 仅为库约定。

容量、方向与发布要求见 [Local CUBE / Shared ND 转换](TransportRules.md#local-cube--shared-nd-转换)及 [Shared 存储合同](StorageBoundaries.md)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using C = VecTileM16<float, 16, 8>;
using N = Tile<Location::Vec, float, 16, 8>;
using S = SharedTile<N>;
void example(C &dst, S &src) {
  TMOV_SHARED_ND_TO_CUBE(dst, src);
}
```

src 已发布并就绪，容量 512B，目标容量相同；四个 PE 参与。 各参与 PE 得到独立的 16×8 Local CUBE 结果。

### 完整行子视图与尾行

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Parent = Tile<Location::Vec, float, 32, 8, BLayout::RowMajor, 20, 8>;
using Part = Tile<Location::Vec, float, 16, 8>;
using Cube = VecTileM16<float, 16, 8>;
void from_row4(Cube &dst, SharedTile<Parent> &src) {
  TileReader<SharedTile<Parent>> reader(src);
  TMOV_SHARED_ND_TO_CUBE<8>(dst, reader.read<Part>(1, 16, 8));
}
void tail_from_row8(Cube &dst, SharedTile<Parent> &src) {
  TileReader<SharedTile<Parent>> reader(src);
  TMOV_SHARED_ND_TO_CUBE<8>(dst, reader.read<Part>(2, 12, 8));
}
using WideND = Tile<Location::Vec, uint64_t, 32, 2>;
using WideCube = VecTileM32<uint64_t, 32, 2>;
void b64(WideCube &dst, SharedTile<WideND> &src) {
  TMOV_SHARED_ND_TO_CUBE<8>(dst, src);
}
```

src已完整发布。FP32 parent有效20×8、物理32×8，src[r,c]=100*r+c。每行32B，CELL偏移1/2分别为第4/8行起点；两片均覆盖16个完整物理行且容量512B。from_row4结果有效16×8，dst[r,c]=100*(r+4)+c；tail_from_row8结果有效12×8，值为100*(r+8)+c，其余物理位置写raw零并保持在有效域外。静态dst getter仍为16，后续消费者显式选择12行。b64源与目标容量均512B，M32每逻辑列采用两个CELL，值原位复制。

mask8只选择PE0，mask0不读取Shared或分配Local；完整来源沿用前例，四PE mask15各得独立结果。子视图要求起点对齐物理行且覆盖完整16/32行，源物理行不足时拒绝。以上为固定规范推导，未编译或运行。

## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

固定依据：[Shared ND→CUBE完整dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tmov-nd-to-cube.asl)；源码核对与边界见[Shared读取转换](../TileOpContractEvidence.md#shared-读取转换)。

[返回算子索引](README.md)
