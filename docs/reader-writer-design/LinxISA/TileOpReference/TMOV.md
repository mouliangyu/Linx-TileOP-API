# TMOV

复制源 payload 及 definedness 到新目标；Local 与 Shared 方向按对应重载执行布局转换及发布。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 重载方向 | 选择条件 | `PEMask` |
| --- | --- | --- |
| Local→Local | Local 输入与输出 | 无此参数 |
| Local→Shared | Shared 目标 | 显式指定 |
| Shared→Local ND | Shared 源、非 CUBE Local 目标 | 默认 `15` |
| Shared→Local CUBE | Shared 源、完整 Local CUBE 目标 | 默认 `15` |

```cpp
template <Writable D, Readable S>
void TMOV(D &&dst, S &&src);
```

```cpp
template <int PEMask, SharedWritable D, Readable S>
void TMOV(D &&dst, S &&src);

template <int PEMask = 15, Writable D, SharedReadable S>
  requires (!is_cube_layout_v<D>)
void TMOV(D &&dst, S &&src);

template <int PEMask = 15, is_local_tile_v D, SharedReadable S>
  requires is_cube_layout_v<D>
void TMOV(D &dst, S &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | dst 的目标计算视图类型 | 由实参推导 |
| `S` | src 的源计算视图类型 | 由实参推导 |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | Local→Shared 显式指定；Shared→Local 默认 `15` |

| 重载方向 | 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- | --- |
| Local→Local | `dst` | Writable | Local | — | Local Writer |
| Local→Local | `src` | Readable | Local | Local Reader | — |
| Local→Shared | `dst` | SharedWritable | Shared | — | Shared Writer |
| Local→Shared | `src` | Readable | Local | Local Reader | — |
| Shared→Local ND | `dst` | Writable | Local | — | Local Writer |
| Shared→Local CUBE | `dst` | is_local_tile_v | 完整 Local CUBE | — | — |
| Shared→Local ND / CUBE | `src` | SharedReadable | 已发布 Shared | Shared Reader | — |

表中“—”表示该参数角色不适用。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

复制源 payload 及 definedness 到新目标；Local 与 Shared 方向按对应重载执行布局转换及发布。

## 合法组合与限制

### Local→Local

源与目标类型分别推导，location、dtype、物理形状、有效形状、布局和容量一致。支持 unboxed RowMajor、CUBE_M16/M32。复制保留 padding 的 definedness；目标分配遵循 [Transport 规则](TransportRules.md)。

### Shared 方向

整块发布显式指定单 bit PEMask；组装调用显式指定参与集合。源/目标布局决定 RowMajor 复制、CUBE→ND 或 ND→CUBE，源与目标 dtype 保持一致。Shared 组装的 Local 源和目标 Part 的容量关系按 [Shared 存储合同](StorageBoundaries.md)。

`is_cube_layout_v<O>` 查询计算视图是否为 CUBE 布局；Shared→Local CUBE 的目标使用完整 Local M16/M32 Tile。PEMask 的合法值、位序和零值行为见 [Shared TMOV 的 PEMask](StorageBoundaries.md#shared-tmov-的-pemask)。

### Shared ND 读取与 Local Writer

每个参与 PE 从已发布 Shared parent 读取自己选择的视图，得到独立 Local 结果。复制保留源 payload 及 definedness。完整 Local 目标与选中视图具有相同 dtype、布局、物理形状、有效形状和容量。

本库将 Shared→Local ND 的 Writer 形式展开为两次 TMOV：先把 Shared 视图复制到完整 Local 临时 Tile，再以 Local→Local TMOV 写入 Writer。临时 Tile 使用 Part 的类型、形状和容量；第二次调用携带 Writer 的 parent 身份、阶段、偏移与范围。两步在同一参与 PE 内按数据依赖执行，临时值存活至第二步完成。PEMask=0 时整个调用按严格 no-op 处理；其他掩码只在选中的 PE 执行这两步。

例如 16×16 FP32 parent 容量为1024B，8×16 Part 容量为512B。每次先读取512B的 Shared 片段，再向 parent 的指定 CELL 区间写入512B。LAST 完成组装后，finish 交出完整 parent。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32>;
void example(V &dst, V &src) {
  TMOV(dst, src);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src 有效元素全为 3 时，dst 有效元素全为 3；padding 的 definedness 按复制合同保持。

### Shared→Local CUBE

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using ND = Tile<Location::Vec, float, 16, 8>;
using Cube = VecTileM16<float, 16, 8>;
void shared_to_cube(Cube &dst, SharedTile<ND> &src) {
  TMOV<8>(dst, src);
}
```

src已发布、512B、有效16×8且全为3，PE0得到相同逻辑元素的独立M16结果。Shared Reader从第4行起读取完整16行、尾行以及M32 b64的完整例子见[专用入口](TMOV_SHARED_ND_TO_CUBE.md#完整行子视图与尾行)；将其中调用名替换为TMOV，参数、角色与结果相同。

### Shared Reader 到完整 Local ND

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace shared_nd_read {
using Parent = Tile<Location::Vec, uint8_t, 1, 512>;
using Part = Tile<Location::Vec, uint8_t, 1, 128>;
void all_pe(Part &dst, SharedTile<Parent> &src, size_t pe) {
  TileReader<SharedTile<Parent>> reader(src);
  TMOV<15>(dst, reader.read<Part>(pe));
}
void pe0(Part &dst, SharedTile<Parent> &src) {
  TileReader<SharedTile<Parent>> reader(src);
  TMOV<8>(dst, reader.read<Part>(0));
}
}
```

前提：src已发布，四个128B区间分别填入`0x10`、`0x11`、`0x12`、`0x13`；dst为各PE的独立Local对象。`all_pe`由四PE调用，pe分别为0..3，offset按CELL计，各PE应得到对应的128个字节。输出有效区已定义，源保持原值。

`pe0` 由 PE0 调用，得到 128 个 `0x10`；输出可作为后续操作的 Local 输入。

### Shared Reader 到 Local Writer 的几何问题输入

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace shared_nd_assemble {
using Parent = Tile<Location::Vec, float, 16, 16>;
using Part = Tile<Location::Vec, float, 8, 16>;
Parent copy(SharedTile<Parent> &src) {
  TileReader<SharedTile<Parent>> reader(src);
  TileWriter<Parent> writer;
  TMOV<15>(writer.first<Part>(0), reader.read<Part>(0));
  TMOV<15>(writer.last<Part>(4), reader.read<Part>(4));
  return writer.finish();
}
}
```

src 已发布、有效形状为 16×16、元素全为 3。四 PE 各自请求独立 Local parent；两片各 512B，覆盖 CELL 区间 [0,4)、[4,8)。库接口通过 finish 返回完整的 16×16 Local Tile，元素全为 3。

### Shared ND Writer 的展开示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace shared_nd_expanded {
using Parent = Tile<Location::Vec, float, 16, 16>;
using Part = Tile<Location::Vec, float, 8, 16>;
Parent copy(SharedTile<Parent> &src) {
  TileReader<SharedTile<Parent>> reader(src);
  TileWriter<Parent> writer;
  Part first, last;
  TMOV<15>(first, reader.read<Part>(0));
  TMOV(writer.first<Part>(0), first);
  TMOV<15>(last, reader.read<Part>(4));
  TMOV(writer.last<Part>(4), last);
  return writer.finish();
}
}
```

src 已发布、有效16×16且元素全为3。四个 PE 各自得到完整 Local 16×16结果，元素全为3。两个512B临时值分别覆盖 Shared 源及 Local parent 的 CELL 区间[0,4)、[4,8)。该展开是 Shared ND Writer 重载的库实现合同。

### 四PE各提交一次的 Shared single

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace shared_single {
using Shape = Tile<Location::Vec, uint64_t, 4, 16,
                   BLayout::RowMajor, 4, 8>;
using Part = Tile<Location::Vec, uint64_t, 1, 16,
                  BLayout::RowMajor, 1, 8>;
SharedTile<Shape> publish(Shape &local, size_t pe) {
  TileWriter<SharedTile<Shape>> writer;
  TMOV<15>(writer.single<Part>(pe), local);
  return writer.finish();
}
}
```

四PE在同一调用位置执行，pe分别为0..3，同一次协作输出须映射到同一个Sx与生产身份。各Local源容量512B、有效4×8，元素`(r,c)`初始化为`0x1000 + pe*0x100 + r*16 + c`。本次只复制每个源第一物理行的128B范围，目标offset分别为0/1/2/3 CELL；发布后Shared有效4×8，第r行第c列为`0x1000 + r*0x100 + c`，列8..15保留未定义padding。

每个请求编码INIT_LAST；实际PE提交owner将首个到达请求建立为generation，其余请求加入同一generation，收齐参与者及覆盖后发布。先到请求停留在各自STOP处等待，随后消费完成token。固定测试 `PTO-AVS-BLOCK-SHARED-TMOV-COPIED-VIEW-021` 覆盖该提交序列及再次执行的ordinal；C++到同一生产位置、Sx和动态offset的lowering仍需实现验证。跨调用点first/middle/last另由S-SUBMIT跟踪。

## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
