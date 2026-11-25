# TileWriter

本页定义新接口的调用合同。完整生命周期和编译绑定说明见 [设计记录](../TileReaderWriterDesign.md)。

## 声明

```cpp
template <class Parent> class TileWriter {
public:
  TileWriter(); // 全静态有效形状
  TileWriter(size_t valid_rows, size_t valid_cols); // 指定 Parent 有效形状
  TileWriter(const TileWriter &) = delete;
  TileWriter(TileWriter &&) = delete;
  template <class Part> auto first(size_t cell_offset);
  template <class Part> auto first(size_t cell_offset, size_t valid_rows,
                                    size_t valid_cols);
  template <class Part> auto middle(size_t cell_offset);
  template <class Part> auto middle(size_t cell_offset, size_t valid_rows,
                                    size_t valid_cols);
  template <class Part> auto last(size_t cell_offset);
  template <class Part> auto last(size_t cell_offset, size_t valid_rows,
                                    size_t valid_cols);
  template <class Part> auto single(size_t cell_offset);
  template <class Part> auto single(size_t cell_offset, size_t valid_rows,
                                    size_t valid_cols);
  template <class Part> auto fragments(size_t count);
  Parent finish();
};
```

## 输入输出角色

| 对象 | Readable 输入 | Writable 输出 |
| --- | --- | --- |
| 已定义普通 Tile | 是 | 是 |
| Reader.read 返回描述 | 是 | 否 |
| Writer.first/middle/last/single 返回描述 | 否 | 是 |
| Reader/Writer 本身 | 否 | 否 |

Reader 只借用已完成 parent；read 不复制数据，消费描述的计算绑定 B.SUBVIEW。可重读、重叠读取，借用不可超出 parent 生命周期。未完成 Writer 无法构造 Reader，也不能转换为输入 Tile。

Writer 的方法只产生输出描述，计算消费描述时才执行对应阶段。以下保存 INIT 结果及对象状态机的规则适用于 Local Writer。first 绑定 INIT 并保存唯一 parent；middle/last 引用该 parent，不产生新真实 Tile 输出；last 完成发布。single 绑定 INIT_LAST。finish 只交出已保存的 first/single 结果，不生成结束指令，也不为之前的计算补 LAST。

Local Writer 状态为 Empty→first→Open→middle*→last→Complete→finish→Finished，single 从 Empty 直接到 Complete。描述仅消费一次；不允许重复 first、跳过未消费描述、提前/重复 finish、LAST 后写入。析构不隐式完成。

## Shared Writer：目标身份与阶段透传

`TileWriter<SharedTile<Shape>>` 保存 Shared 目标身份、Parent 几何及输出描述所需的信息。同一协作输出在各 PE 上的对象须绑定同一个 Core-wide Sx；这是库与 lowering 的目标身份合同，不能由各 PE 独立分配成不同 Sx；各 PE 通过本地对象引用该共同身份。

first/middle/last/single 构造阶段描述，由消费描述的 TileOP 透传到底层。first 生成分配目标的 B.IOS 与 INIT；middle/last 通过同一个 Sx 的 source-form B.IOS（保留 .reuse）和紧邻的 B.ASSEMBLE 选择正在组装的 generation。合法性由整个 generation 的阶段、覆盖及发布规则决定，不要求每个 PE 的 Writer 对象独立经历 first 到 last。

因此，一个 PE 可以只消费 middle 或 last，而 first 由另一个 PE 执行。描述仍只能消费一次，不能遗漏协议要求的参与阶段；single 表示 INIT_LAST，是否允许由具体操作及 generation 合同决定，不能解释为“每个 PE 各写一次”。

Shared finish 交出指向同一 Sx 的 SharedTile 句柄，不需要读取另一个 PE 保存的 INIT 结果，也不要求当前 PE 的对象执行过 last。它不发指令、不补 LAST、不等待或完成同步，也不证明 generation 已发布。句柄的 payload 只能按 Shared 发布、就绪和消费规则读取，不能借 finish 绕过未完成 generation 的输入限制。阶段执行与消费者的顺序仍须满足底层合同。

具体协作方式见 [Shared 存储合同](StorageBoundaries.md#shared-writer) 与 [TIMG2COL](TIMG2COL.md)。下述迭代器是同一调用者完整消费一个输出序列的便利接口，不自动分派跨 PE 阶段。

### 普通 Shared TLSU 的提交映射

Shared generation 按参与 PE 集合和 ordinal 识别。每个匹配参与者加入一次；完整且无重叠的覆盖与所有参与者就绪共同决定发布。库阶段描述的提交映射记录在[Shared 提交核对](../TileOpContractEvidence.md#shared-提交身份)。

普通Shared TMOV已有明确的协作single路径：四PE在同一生产位置各提交一次INIT_LAST，使用相同Sx、parent和mask，每PE使用独立offset；owner收齐参与者与合法覆盖后统一发布。完整输入、调用和输出见[TMOV四PE single](TMOV.md#四pe各提交一次的-shared-single)。single编码在到达顺序下由owner归并为一次generation；此分支的证据范围是每PE一次请求。普通 Shared TLSU 的跨调用点 first/middle/last 映射仍在接口设计核对范围中，详见[核对表](../TileOpContractLedger.md#剩余问题分组)。

## 顺序迭代器

`fragments<Part>(count)` 从 CELL 0 开始。begin/end、解引用、前置 ++ 和同范围比较构成便利遍历接口；不承诺随机访问或全部标准 iterator concept。每次 ++ 推进 Part 的物理 CELL 数。

Reader count 可为 0，允许提前 break、continue、重复解引用和复制迭代位置。Writer count≥1，须在开始前确定，消费每项一次后才能 ++，必须完整遍历；动态 count 不允许循环结束后才确定 LAST。单项自动 single，多项首项 first、中项 middle、末项 last。在消费全部输出项之前提前退出（如 break、return 或异常离开）属于未定义行为，即使之后不调用 finish 也一样；跳过当前项消费的 continue 同样属于未定义行为。不要求运行时检测，也不隐式补 LAST。已消费全部项后退出不属于提前退出。

## 示例：不同大小、非顺序写入

```cpp
using Parent = VecTileM32<float, 32, 8>;
using Large = VecTileM32<float, 32, 4>;
using Small = VecTileM32<float, 32, 2>;
// x/y 是已定义 Parent；以下使用新接口。
TileReader<Parent> xr(x), yr(y);
TileWriter<Parent> output;
TADD(output.first<Large>(4), xr.read<Large>(4), yr.read<Large>(4));
TADD(output.middle<Small>(0), xr.read<Small>(0), yr.read<Small>(0));
TADD(output.last<Small>(2), xr.read<Small>(2), yr.read<Small>(2));
auto result = output.finish();
```

三次写入覆盖 [4,8)、[0,2)、[2,4) CELL，阶段不由位置决定。FIRST 不必位于零，LAST 不必位于物理末端。范围须不重叠、在 parent 内并满足最终合法前缀覆盖；片段 dtype、布局、容量和更强对齐按架构校验。

动态参数不代表任意非法位置都会被运行时捕获。静态可判定错误应诊断；动态检查策略仍待实现。所有 TileOP 顺序副作用必须在 IR 与机器层落实；C++ 成员保存 parent 不能自行阻止 use 越过 LAST。循环内 INIT 的 PHI/相对索引分析也需后端支持，推荐 lowering 做首尾 peeling。

相关：[Reader](Reader.md)。

## 动态有效形状

带 valid_rows/valid_cols 的重载以元素为单位提供本次 Part 有效形状，两轴均以显式值为准，即使 Part 模板对应轴已有静态有效维度。省略这两个参数的重载使用 Part 模板的有效维度，要求两轴均非 DYNAMIC；若任一轴为 DYNAMIC，须使用显式维度重载并传入两轴。这是省略参数的重载没有运行时 Part 对象可提供维度所需的接口规则，不限制动态片段本身。不从 Parent 有效形状或 CELL 偏移猜测 Part 形状。显式维度的合法性由 assemble 和消费操作检查，不额外要求与模板中的有效维度逐轴相等。Writer 的动态 Parent 在构造时确定最终有效形状；各次写入不能改变它。现有 fragments<Part>(count) 使用固定静态 Part，有动态尾片时全程使用显式 first/middle/last 阶段，并以 last<Part>(offset, rows, cols) 写尾片；仅一片时使用 single。不能在迭代器自动 LAST 后追加尾片。物理容量及迭代步长仍由 Part 类型决定。

## 维度与范围绑定

消费 Writer 描述时分别绑定下列信息：

| 信息 | 来源与用途 |
| --- | --- |
| Parent | 构造时确定的 dtype、布局、物理容量与最终有效形状；INIT 分配、后续阶段引用同一个目标 |
| Part 物理几何 | Part 类型决定本次输出布局、行距与物理容量；容量编码为 B.ASSEMBLE 的 WriterSizeCode |
| 插入位置与阶段 | cell_offset 按 128 B 换算，first/middle/last/single 选择组装阶段 |
| Part 有效维度 | 描述中显式传入的 rows/cols，或 Part 静态默认值；供按目标区域工作的操作选择维度 |
| 本次结果区域 | 由消费操作的维度来源和结果形状公式确定，按该操作绑定 B.DIM 或专用参数 |

TADD 等按输入选择计算维度的操作使用输入视图及 UserValidCol/Row；Local TLOAD 等按目标选择区域的操作使用输出描述的 Part 有效维度；Shared TLOAD 按 parent 有效形状和列距绑定维度，Part 提供输出范围容量；归约、转换、TIMG2COL 等使用各自的结果形状规则。每次计算的实际结果须满足 Part 的物理几何、容量和该操作的写入规则。Part 的有效维度元数据与计算结果允许不同；padding 和实际写入范围按消费操作及 assemble 合同处理。最终 parent 的覆盖与发布还须通过整个组装序列的检查。

例如 `Part = VecTileM16<float,16,2>`，`first<Part>(0,4,2)` 保存有效形状 4×2。若 TADD 的两个输入视图有效形状均为 16×2，省略维度实参时计算 16×2；传入 `UserValidCol=2, UserValidRow=4` 时计算 4×2。两种调用的 WriterSizeCode 均来自相同 Part 物理容量。换成按目标选区的 Local TLOAD 时，输出描述提供 4×2 的目标区域。整个序列的其他片段仍须满足对应操作的覆盖与发布条件。

编译绑定与上述来源保持一致：有效计算维度进入操作参数；Part 容量与偏移进入范围修饰；Parent 身份由 INIT 保存并供后续阶段及 finish 使用。

## 单片容量

Part 的容量编码、范围和 Parent 边界统一见 [分片几何：单片容量](FragmentGeometry.md#单片容量)。
