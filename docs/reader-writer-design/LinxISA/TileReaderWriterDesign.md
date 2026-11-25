# TileOP 库 Reader / Writer 接口设计

面向 kernel 作者的统一入口见 [TileOP 接口指南](TileOpInterfaceGuide.md)，调研来源与章节组织见 [文档调研记录](TileOpInterfaceResearch.md)。本文保留具体状态机与编译绑定细节。

本文记录已确认的上层 TileOP 库接口方向，尚未实现。它与底层 C builtin 接口分层：Reader/Writer 是简化编程和限制操作数角色的库对象，不要求底层 builtin 引入同名对象。示例为拟议 C++ 用法。

本文以 INIT/LAST 绑定计算 TileOP 为前提。后续讨论的独立开始/结束指令及显式 finish 构建器方案另见 [独立 BEGIN/END 设计](TileAssemblyBeginEndDesign.md)；两种方案的阶段接口和提前退出规则不能混用。

## 已确定的接口

```cpp
TileWriter<Parent> out;

TADD(out.first <Large>(4), a, b);
TADD(out.middle<Small>(0), c, d);
TADD(out.last  <Small>(2), e, f);

auto parent = out.finish();

TileReader<Parent> reader(parent);
auto part = reader.read<Small>(2);
```

所有位置参数均命名为 `cell_offset`，单位固定为 **128 B CELL**，相对于 parent 起点；整数 `2` 表示 256 B 偏移。直接接受整数，支持运行时值。**不使用 `cells(...)` 包装，不提供元素列、二维坐标或 fragment 编号重载。** 参数不是 tile 队列相对索引；队列索引由后端生成。

`Parent` 显式指定 parent 类型及容量，INIT 前即可确定分配信息。每次调用的 `<Fragment>` 独立指定本次片段形状、dtype、layout 和物理大小，不要求所有片段等大，也不要求提前声明片段列表。

例如上述代码可以采用这些类型：

```cpp
using Parent = VecTileM32<float, 32, 8>; // 8 CELL
using Large  = VecTileM32<float, 32, 4>; // 4 CELL
using Small  = VecTileM32<float, 32, 2>; // 2 CELL
```

三次写入依次覆盖 `[4,8)`、`[0,2)`、`[2,4)` CELL。输入 a/b 为 Large，c/d/e/f 为 Small，且均已定义。片段位置与执行阶段独立，地址不要求递增。

## Writer 方法与阶段

| 方法 | 绑定到消费该输出描述的计算 TileOP 的阶段 |
| --- | --- |
| `first<Fragment>(cell_offset)` | INIT：分配唯一 parent，写入片段 |
| `middle<Fragment>(cell_offset)` | MIDDLE：复用 parent，写入片段 |
| `last<Fragment>(cell_offset)` | LAST：复用 parent，写入片段并结束组装 |
| `single<Fragment>(cell_offset)` | INIT_LAST：一次计算创建并完成 parent |
| `finish()` | 交出完整 parent；不发独立 TileOP、不创建新 tile |

first/middle/last/single 返回输出描述，携带所属 Writer、片段类型、静态阶段和位置。调用方法本身不执行 INIT/LAST；实际消费描述的 TADD 等计算才执行对应阶段并推进状态。单次写入仍必须满足最终覆盖规则。

Local Writer 内部保存唯一 parent 载体。first 的计算将 INIT 结果记录到所属 Writer；middle/last 的计算引用同一载体，没有新的真实 tile 寄存器结果；finish 返回该载体所代表的 parent。输出描述中的 owner 引用将计算与 Writer 联系起来，finish 不需要反向搜索 first。

本设计沿用所有 TileOP 的副作用顺序由编译链保持的执行契约。必须在 IR 和机器层落实该契约，不能仅凭 C++ 成员读写或一个泛化的 side-effect 标记推断顺序正确。底层 builtin 怎样接收目标或交付 INIT 结果仍属独立契约，本文不把此前的目标指针草案当作已解决方案。

## Reader 与操作数角色

Reader 与 Writer 统一使用显式类型构造：`TileReader<Parent> in(parent)` 借用已有 tile，`TileWriter<Parent> out` 创建组装对象。两者均提供 `fragments<Part>(count)`、解引用和自增的遍历形式。Reader 不需要 finish；Writer 必须完成后才能通过 finish 交出结果。这个生命周期差异保留，不人为给读取添加 assemble 阶段。

```cpp
TileReader<Parent> xs(x);
TileReader<Parent> ys(y);
TileWriter<Parent> out;

TADD(out.first<Large>(4), xs.read<Large>(4), ys.read<Large>(4));
TADD(out.middle<Small>(0), xs.read<Small>(0), ys.read<Small>(0));
TADD(out.last<Small>(2), xs.read<Small>(2), ys.read<Small>(2));

auto result = out.finish();
```

Reader 借用已定义的 parent，read 返回只读片段描述，不复制 payload；消费该描述的 TileOP 绑定相应 B.SUBVIEW。借用不得超出 parent 生命周期或跨越使该内容失效的覆写。

### 直接读取

```cpp
TileReader<Parent> reader(parent);
auto small = reader.read<Small>(2); // 从 parent 的 256 B 偏移开始
auto large = reader.read<Large>(4); // 从 parent 的 512 B 偏移开始

TADD(dst0, small, rhs0);
TADD(dst1, small, rhs1); // 可以重复读取同一片段
```

`read<Fragment>(cell_offset)` 接受整数 CELL 偏移，可为运行时值；Fragment 的类型、物理大小和编码在编译期确定。可在不同调用点选择不同片段类型及任意合法位置。read 不发独立复制指令，不改变 parent，也没有 first/middle/last 阶段。每个消费者独立生成其 source binder 的 subview；输入编号由该描述在计算操作数中的位置决定。

Reader、读取范围、读取迭代器和片段描述均为借用对象，不拥有或延长 parent 生命周期。允许复制描述、重复读取和重叠读取，前提是 parent 内容仍有效；这不表示复制 tile 寄存器或 payload。构造接口仅接受有效 parent 左值，拒绝临时 parent 和未完成 Writer，避免最直接的悬空借用。普通 C++ 不能自动静态验证所有借用或硬件队列生命周期，仍须落实相关合同。

### 顺序读取迭代器

与输出迭代器一样，提供同类型片段的连续遍历便利接口：

```cpp
TileReader<Parent> reader(parent);
auto reads = reader.fragments<Part>(count);

for (auto it = reads.begin(); it != reads.end(); ++it) {
    TADD(dst, *it, rhs);
    if (stop)
        break; // 仅停止读取，不留下未完成的 assembly。
}
```

范围从 CELL 0 开始。`*it` 等价于 `reader.read<Part>(index * PartCellCount)`；`++it` 移动到下一个片段。count 是片段数量，可以为运行时值；允许 count == 0 的空读取范围。必须保证每个实际访问片段都在合法 parent 范围内，且偏移计算不溢出。

读取迭代器不需要阶段分派、首尾 peeling、完整覆盖或 finish。允许跳过片段、continue、提前 break 和重复解引用。复制读取迭代器可保留独立遍历位置，但不在此承诺完整的 C++ 标准 iterator concept 或随机访问运算集合。读范围结束也不会消费 parent。

核心状态只需要 parent 的借用引用和当前片段序号；范围另外保存 count。下面为实现示意，不是已实现的头文件声明：

```cpp
template<class Parent, class Part>
struct ReadIterator {
    const Parent* parent;
    size_t index;

    auto operator*() const {
        return ReadFragment<Parent, Part>(
            *parent, index * PartCellCount);
    }

    ReadIterator& operator++() {
        ++index;
        return *this;
    }
};
```

`PartCellCount` 表示从 Part 的物理布局推导出的编译期 CELL 数，实际实现用相应 trait 获取。这里的 parent 指针指向库层 Tile 对象，不代表硬件 tile 存在可解引用的 payload 内存地址。ReadFragment 仅保存借用和范围信息，不读取或复制 payload。

begin 的 index 为 0，end 的 index 为 count；迭代比较仅对同一范围定义。不能解引用 end。示意省略范围归属、比较、边界及溢出检查的实现细节。`operator++` 只推进读取位置，不消费 Tile 或改变 parent 身份与完成状态。

动态 index 只影响 subview 的位置；动态 count 只决定遍历终点。因此 Reader 不需要像 Writer 一样区分 INIT/MIDDLE/LAST，不引入 assembly 状态机或因阶段选择而产生的新 parent PHI。后端仍须正确生成动态 subview 偏移，并维持原 parent 在全部消费者处的有效生命周期。

```cpp
TileReader<Parent> xs(x);
TileReader<Parent> ys(y);
auto xr = xs.fragments<Part>(count);
auto yr = ys.fragments<Part>(count);
TileWriter<Parent> out;
auto wr = out.fragments<Part>(count);

auto xi = xr.begin();
auto yi = yr.begin();
for (auto wi = wr.begin(); wi != wr.end(); ++wi, ++xi, ++yi)
    TADD(*wi, *xi, *yi);

auto result = out.finish();
```

组合读写时仍遵守 Writer 的约束：count >= 1，结果形状/容量匹配，完整遍历输出范围。Reader 单独允许提前结束不意味着包含 Writer 的循环也能提前完成。

### 读取合法性

CELL 单位只保证表达 128 B 粒度，仍需验证 Fragment 和 parent 的 dtype/layout/shape 兼容、范围连续、边界、SizeCode、布局的更强对齐及具体 opcode 的 subview 支持。不会仅凭 Reader 对象就允许读取未发布或未完成的 parent。动态合法性检查策略与基础接口保持一致，不能宣称任意动态非法读取都会被库捕获。

| 对象 | Readable 输入 | Writable 输出 |
| --- | --- | --- |
| 普通 Tile | 已定义时可用 | 可用 |
| Reader 本身 | 不可用；先选择片段 | 不可用 |
| Reader 的片段描述 | 可用 | 不可用 |
| Writer 的输出描述 | 不可用 | 可用 |
| Writer 本身 | 不可用 | 不可用 |

计算 TileOP 的输入模板按 Readable 约束，输出模板按 Writable 约束。Writer 和输出描述不能作为普通输入，也不能用来创建 Reader/subview；Writer 不暴露公开 parent/data 转换。只有 finish 后的 Tile 才可读。角色合法不代表所有 opcode 都支持该 dtype/layout/subview/assemble 组合，仍需逐操作检查。

## 顺序输出迭代器（便利封装）

基础 first/middle/last 接口之外，提供同类型片段的连续顺序输出迭代器。迭代器不支持随机写入计划，不承担不同大小片段的通用表达；这些能力保留在基础接口。

```cpp
TileWriter<Parent> out;
auto writes = out.fragments<Part>(/* count = */ 4);

for (auto it = writes.begin(); it != writes.end(); ++it)
    TADD(*it, a, b);

auto parent = out.finish();
```

从 CELL 0 开始，`*it` 返回当前 Writable 片段描述；`++it` 将写入序号加一，并将 CELL 偏移增加 `Part` 的物理 CELL 数。count 表示写入次数，不是 CELL 数；必须至少为 1，且整体覆盖必须符合 Parent 合同。

首项自动选择 INIT，中间项选择 MIDDLE，末项选择 LAST；只有一项时选择 INIT_LAST。TADD 等 producer 实际消费描述后才能递增，不能跳过或重复写入；到达 end 不自动返回 parent，仍由 finish 检查并移交结果。该对象按单遍输出迭代器设计，不承诺随机访问或多遍遍历语义。

### 动态数量与阶段分派

count 可以是运行时值，但必须在创建范围、开始写入前确定；本轮遍历中保持不变。不是等循环结束后才确定数量。

```cpp
TileWriter<Parent> out;
auto writes = out.fragments<Part>(count);

for (auto it = writes.begin(); it != writes.end(); ++it)
    TADD(*it, a, b);

auto parent = out.finish();
```

迭代器保存 index/count，当前 `cell_offset = index * PartCellCount`。计算消费输出描述时，按下表分派到静态编码的 builtin 调用点，不把运行时 phase 直接作为硬件立即数：

| 条件（按顺序判断） | 阶段 |
| --- | --- |
| `count == 1` | INIT_LAST |
| `index == 0` | INIT |
| `index + 1 == count` | LAST |
| 其他 | MIDDLE |

静态次数与循环展开可以消除分派，动态次数可能保留分支。后端对这些控制流的支持仍需验证。count 必须至少为 1，总物理大小不能超过容量，还须满足架构 writer 数量和最终覆盖限制。动态 count 决定写入次数；最终有效形状与物理覆盖按组装合同判断，不由 count 额外推导“必须使用动态结果类型”的限制。

### INIT 结果绑定与循环 peeling

迭代器解引用出的描述仍引用同一个 Writer。对于 Local Writer，第一笔计算把 INIT 的结果保存为 Writer 的 parent，后续计算引用这个 parent，finish 交出它。绑定机制不依赖 peeling。

若 INIT 分支留在用户循环内，parent 可能成为循环携带的 SSA 值，涉及 PHI 和相对索引分析；不能因为每次都访问同一个 C++ 成员就认为后端自然正确。

推荐的 lowering 是首尾剥离（以下为概念伪代码，假定 count >= 1）：

```text
if count == 1:
    parent = INIT_LAST_TADD(fragment 0)
else:
    parent = INIT_TADD(fragment 0)
    for i in [1, count - 1):
        MIDDLE_TADD(parent, fragment i)
    LAST_TADD(parent, fragment count - 1)
finish returns parent
```

在多片段路径中，INIT 位于循环外，所有 MIDDLE/LAST 直接引用同一个 parent；它们不产生新的 tile 结果。count == 1 与多片段路径汇合处仍可能需要 parent PHI，循环中的相对索引也仍须正确处理。

普通 C++ 迭代器只能实现阶段分派，不能保证优化器自动 peeling 任意用户循环。如果实现必须依赖上述剥离结构，需要编译器专门 lowering，或另设由库控制遍历的回调接口；目前不把后者加入已确认的迭代器 API。变换还必须保持循环体其他运算和副作用的语义。

### 提前退出与 break

这套便利迭代器用于已确定数量、完整执行的组装。**在消费全部输出项之前提前退出属于未定义行为，无论之后是否调用 finish。** 包括 break、return 或异常离开；不要求运行时检测。 提前 break 不会自动发出 LAST，peeling 也不能修复这件事；析构和 finish 都不能追溯修改已执行计算的阶段。

```cpp
for (auto it = writes.begin(); it != writes.end(); ++it) {
    TADD(*it, a, b);
    if (stop)
        break; // 若尚未消费全部输出项，此处即为未定义行为。
}
auto parent = out.finish(); // 未执行 LAST 时属于非法使用。
```

不提供自动取消、隐式完成或自动补写行为。continue 若跳过当前项的实际计算，同样属于未定义行为。只有实际末项已经消费且 Writer 已完成，结束遍历才不会留下未完成组装。

若算法能在最后一次计算之前确定终止，应使用基础 first/middle/last/single 接口显式选择阶段，并确保终止后的覆盖及结果形状合法。若终止条件依赖本次计算完成后的结果，当前接口无法事后给这次计算补 LAST；延迟执行或独立结束机制不属于本设计。

## 生命周期与合法性

状态由计算消费输出描述时推进：Empty → first → Open → middle* → last → Complete → finish → Finished；single 从 Empty 进入 Complete。

Writer 不可复制或移动，输出描述只能消费一次。必须拒绝未初始化的 continuation、重复 first、重复消费输出描述、提前或重复 finish，以及 LAST 后继续写。存在未消费描述时不能申请另一描述或 finish。析构不能自动补 LAST，因为 LAST 必须绑定实际计算。

CELL 单位使起点自然表达 128 B 对齐，但仍须满足片段完整 CELL/更强布局对齐、WriterSizeCode 可编码、边界、dtype/layout/行数兼容、参与 PE、writer 数量及最终覆盖规则。动态位置和次数不意味着允许任意大小、重叠或越界。静态可判断问题应诊断；动态检查的具体开销、调试模式和错误处理策略尚待实现设计，不在这里承诺任意非法动态使用都有运行时保护。

首版建议 Parent 明确最终有效形状，所有合法路径产生与它一致的结果。若支持随路径变化的最终有效形状，需要另行确定结果类型如何保存该信息，不能返回描述不准确的固定 Tile。

控制流可表达动态偏移、middle 循环及分支选择片段类型，但支持范围须通过后端验证；运行路径上的初始化、覆盖和完成检查不能替代 tile PHI、循环生命周期及相对索引正确性验证。不因普通 tile 分支汇合已有修复就默认跨分支 INIT 的 assembly 已支持。

## ISA 核对与已有设计

核对基线为 PTO-spec `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，范围为 Local M16/M32 assembly：

- [逐次结构检查](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/local-generation.asl#L178)不要求 INIT 偏移为零或后续偏移递增；它检查边界、状态和同一 PE 上的范围重叠等条件。
- [最终检查调用](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/local-generation-cube.asl#L385)由 LAST 触发。[最终覆盖及形状检查](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/local-generation-cube-validation.asl#L3)汇总历史与当前 writer；物理末端的 writer 不必是 LAST。中间可有孔洞，最终须满足合法前缀覆盖。
- 当前基线保留由容量决定的完整 parent 物理形状，LAST 推导有效列前缀；不能照搬旧版“覆盖决定最终物理形状”的说明。

[TileOP #301](https://github.com/LinxISA/Linx-TileOP-API/issues/301) 已实现的 LocalCubeAssembly 提供 parent 所有权、ParentRef 和 finish 的参考，但其静态 writer 列表及按序消费不作为本通用接口限制。[#36](https://github.com/LinxISA/Linx-TileOP-API/issues/36) 的 session RFC 提供控制流讨论；本方案显式指定阶段，不要求从 finish 反推 LAST，也不让 TileArray 坐标隐含阶段。

上述核对是 ASL 源码检查，不是新接口的编译或模型运行验证。Shared 及其他布局应分别核对后再扩展。

### LinxISA 0.59.1 单片容量补充

Local Reader/Writer 的每个 Part 仅允许 128 B～64 KiB（SizeCode 1..10），Shared Part 允许 128 B～256 KiB（1..12），均为二次幂。Parent 总容量与单片容量分别校验，不以 Parent 可分配容量代替 Part 的编码上限。


## Shared 跨 PE 阶段透传修正

Local 的 INIT 返回值保存及单对象状态机不适用于 Shared 跨 PE 协作。Shared Writer 保存目标 Sx 身份和几何，各 PE 的阶段描述共同指向同一个 generation；不要求每个对象分别经历 first/middle/last。lowering 必须为同一协作输出保持一致 Sx，续写使用保留 payload 的 source-form B.IOS 与紧邻 B.ASSEMBLE，不在 PE 间传递 Local INIT 结果。

TIMG2COL 的 PE0/1/2/3 分别提供 first/middle/middle/last，属于该透传协议的合法用途，不必另造 collective 入口来绕过 Writer。finish 交出同一 Sx 句柄，不补 LAST、不同步、不证明发布完成；读取必须遵守 Shared 就绪规则。此处修正的是库文档中过强的逐对象生命周期要求，并非判定 ISA 的 generation 绑定缺失。完整合同见 [Writer](TileOpReference/Writer.md#shared-writer目标身份与阶段透传)。

## 2026-11-24：维度绑定补充

Part 物理范围、操作结果区域和 Parent 最终形状分别绑定。按输入选区的操作从输入及显式操作参数取得维度；按目标选区的操作从输出 Part 取得维度；特殊操作使用自己的形状规则。具体合同及 4 行/16 行例子统一维护在 [Writer 维度与范围绑定](TileOpReference/Writer.md#维度与范围绑定)。
