# GMOV

从当前 Core 的 peer_tid 所指定 PE 读取其 Local 源片段，复制到当前参与 PE 的目标；四个 PE 共同提供输入。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <int PEMask = 15, Writable D, Readable S>
void GMOV(D &&dst, uint64_t peer_tid, S &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | `15` |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `peer_tid` | in | Core 内绝对 PE 编号 0..3 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

从当前 Core 的 peer_tid 所指定 PE 读取其 Local 源片段，复制到当前参与 PE 的目标；四个 PE 共同提供输入。

## 合法组合与限制

Local 输入为 Readable，输出为 Writable；两者 Part 几何、dtype 和容量匹配。PEMask 和 peer_tid 是普通控制参数。非零mask的GMOV须四PE共同到达并提供合法且就绪的输入片段。

从 peer 选择的旧 Local fragment 复制到当前目标 fragment。dst 为 out，src 为 collective 提供的 in，peer_tid 是架构 peer 选择值。非零mask时所有四个PE须到达相同collective并使源就绪；PEMask决定目标写入集合，源rendezvous仍覆盖四个PE。

D/S 的计算视图必须为 Local Vec，dtype、物理/有效形状、布局、fractal 和容量完全相同。布局限RowMajor、CUBE_M16/M32，接受架构已分配的非packed及packed类型；N8、Shared不属于本入口。FP64/S64/U64 使用 RowMajor 或 CUBE_M32，M32 每逻辑列采用两个 CELL；CUBE_M16 使用非 b64 backing。C++ PEMask 可取0、1、2、4、8、12、14、15，默认15；0为严格no-op，不读取源或分配输出。Writer阶段须使用非零mask，才能产生对应的组装效果。B.DIM的三个解析值固定为1，传输几何来自持久描述符；库不将矩形有效维度直接填入这些B.DIM。peer_tid 是当前 Core 内绝对 PE 编号 0、1、2、3，各 PE 独立提供；允许重复选择同一源。任一 PE 提供值 ≥4 均在分配/请求前触发 TileLegality fault。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32>;
void example(V &dst, V &src) {
  GMOV(dst, uint64_t{0}, src);
}
```

四个 PE 都调用本函数；各 PE 的 src 已定义且几何一致，输出独立，peer_tid=0。 每个 PE 得到 PE0 的 src。

### 边界核对

mask=0不产生目标；非零mask下任一参与collective的peer_tid=4在分配前拒绝。peer_tid=0允许四PE重复读取PE0，各源payload及definedness先快照再写目标。库接受0的设计与固定ISA保持一致。

## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

依据：[GMOVDataTypeLegal 与 carrier 合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/dtype-layout.asl)。

[返回算子索引](README.md)
