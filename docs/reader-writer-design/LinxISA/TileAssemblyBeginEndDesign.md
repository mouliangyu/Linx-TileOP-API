# 独立 BEGIN/END 的 Tile assembly 与 C++ Writer 设计

统一接口入口及与当前阶段方案的对比见 [TileOP 接口指南](TileOpInterfaceGuide.md)。本文是依赖 ISA 修改的备选专题。

本文记录将 INIT/LAST 从计算 TileOP 拆为独立指令的候选方案，以及对应的 C++ 库接口。尚未修改 ISA、builtin 或库实现。指令和 intrinsic 名称均为语义示意，编码未定。

现有绑定阶段的方案见 [Reader/Writer 设计](TileReaderWriterDesign.md)。本方案替换其中的 first/middle/last/single 阶段接口；整数 CELL 偏移、片段类型和 Readable/Writable 分工保持适用。

## 动机

当 INIT/LAST 必须绑定计算时，动态输出迭代器需要选择首项、中间项和末项的静态阶段。INIT 在循环内还会带来 parent 的循环数据流；计算后才决定 break 时，已经执行的计算无法补上 LAST。

将开始和结束拆为独立操作后，库可以明确构造 Writer、执行任意合法写入序列，再显式 finish。执行次数不再决定每笔计算的阶段，循环无需为此做首尾 peeling。

## 架构语义提案

| 操作 | 职责与结果 |
| --- | --- |
| ASSEMBLE.BEGIN | 分配唯一 parent，建立 OPEN generation，产生 parent 身份 |
| 计算 TileOP 的 assembly 写入 | 使用 parent 引用及片段范围写入，不新增真实 tile 结果 |
| ASSEMBLE.END | 验证最终覆盖/描述符，关闭 generation，按就绪规则发布结果，不新增 tile 队列项 |

BEGIN 必须取得分配所需的容量、dtype/layout、参与范围等信息。原先由首笔计算携带的 writer 信息，需明确哪些属于 BEGIN 的 parent 描述符，哪些由第一次写入提供；具体操作数合同尚待 ISA 设计。

每次计算仍须表达 parent 身份、片段偏移和 writer 大小，但不再携带 INIT/LAST 阶段。片段可大小不同、按非地址顺序写入，须满足最终选定的覆盖合同。

END 不等于此前写入已全部执行完成。它关闭新的写入、检查已注册贡献的合法性，并使 generation 在贡献完成等条件满足后发布。后续消费者通过硬件依赖/就绪机制等待，不要求 CPU 同步等待。

BEGIN 引入“已分配但尚无 writer”的状态。零写入时 END 是否合法、错误后的取消和资源释放、异常或控制流离开时如何处理，均需明确；不能由库自行假设。首版建议拒绝零写入完成，除非 ISA 明确定义空结果。

## C++ Writer 接口

Writer 是有状态、不可复制的构建对象。显式 finish 交出此前不可读的结果。

```cpp
using Parent = VecTileM32<float, 32, 8>;
using Large  = VecTileM32<float, 32, 4>;
using Small  = VecTileM32<float, 32, 2>;

TileWriter<Parent> writer; // BEGIN

TADD(writer.write<Large>(4), a, b); // CELL [4,8)
TADD(writer.write<Small>(0), c, d); // CELL [0,2)
TADD(writer.write<Small>(2), e, f); // CELL [2,4)

Parent result = writer.finish();   // END
```

位置参数统一为整数 `cell_offset`，单位 128 B，相对于 parent 起点，支持运行时值。不提供 cells 包装、元素坐标或二维坐标。Fragment 指定每次写入的类型和大小。CELL 单位不免除边界、布局更强对齐、完整片段、编码和覆盖检查。

接口骨架（设计示意）：

```cpp
template<class Parent>
class TileWriter {
public:
    TileWriter();
    TileWriter(const TileWriter&) = delete;
    TileWriter& operator=(const TileWriter&) = delete;
    TileWriter(TileWriter&&) = delete;
    TileWriter& operator=(TileWriter&&) = delete;

    template<class Part>
    auto write(size_t cell_offset);

    template<class Part>
    auto fragments(size_t count);

    Parent finish();
};
```

write 返回 Writable 描述，计算实际消费时才注册并执行写入。Writer 和输出描述都不能作为 Readable 输入，也不能产生可读取未完成 parent 的 Reader。Writer 不公开可绕过完成协议的 parent/data 转换。

Reader 采用对称构造和片段选择：

```cpp
TileReader<Parent> reader(source);
TileWriter<Parent> writer;

TADD(writer.write<Small>(0), reader.read<Small>(2), rhs);
// ... 其他合法写入 ...
auto result = writer.finish();
```

Reader 借用完整 tile，不需要 finish。Writer 创建新结果，需要显式结束；不人为消除这一生命周期差异。

## 生命周期和完成策略

构造成功后处于 OPEN；计算写入期间保持 OPEN；finish 发出 END 并交出结果后进入 FINISHED。

- finish 只能执行一次，之后不能再写入。
- 输出描述只能消费一次；尚有未消费描述时不得 finish。
- 所有借用的输出描述和迭代器在 finish 后失效。
- Writer 首版禁止移动，因为描述和迭代器引用它。禁止复制避免重复拥有同一 OPEN generation。
- 析构不自动 finish，不隐式发出 END，也不隐式返回结果。未完成销毁应有明确诊断或取消策略；没有硬件取消合同就不能声称 RAII 已释放 generation。
- 动态非法使用的检测方式、检查开销和失败处理尚待确定；接口示意不承诺所有错误都能静态拒绝。

保留简洁的 `writer.finish()`。可以选择 `Parent finish() &&`、要求 `std::move(writer).finish()` 来强调结果移交，但 std::move 本身不会防止后续使用或重复完成，仍需状态规则，因此当前提案不要求该拼写。

## 顺序迭代器与动态控制流

```cpp
TileWriter<Parent> writer;
auto parts = writer.fragments<Part>(count);

for (auto it = parts.begin(); it != parts.end(); ++it) {
    TADD(*it, a, b);
    if (stop)
        break;
}

auto result = writer.finish();
```

迭代器只负责当前位置和边界。从 CELL 0 开始，解引用产生当前片段输出描述，自增前进 Part 的物理 CELL 数；写入后才能前进，不能跳过尚未消费的输出。count 可为动态值，决定遍历范围，不再决定 INIT/LAST。

提前 break 后能够显式 END，但实际覆盖必须合法。连续前缀能否接受及其最终有效形状取决于 ISA 合同；留下非法孔洞不能靠 END 修复。若实际写入数量改变有效形状，需要结果类型携带动态有效形状；固定 Parent 则要求实际结果与其声明一致。

终止条件可在本次计算后求值，因为 END 尚未执行；这消除了绑定 LAST 的时间限制。若条件需要读取正在 assembly 的 parent，该读取仍属非法；不能把独立 END 当作允许提前消费。

count 范围封装并非唯一写法。基础 write 接口也能表达事先不知道执行次数的循环，但必须有容量/边界约束并最终显式 finish。不依赖自动析构结束，也不提供未定义的取消行为。

## 编译器数据流

在 BEGIN 位于循环外的常见形式中：

```llvm
%parent = call @assemble.begin(...)
; loop / conditional writes
call void @tadd.write(%parent, ...)
call void @tadd.write(%parent, ...)
call void @assemble.end(%parent)
call void @consume(%parent)
```

Writer 保存 BEGIN 的结果；finish 对该身份发出 END，再将同一身份包装成完整 Tile。write/END 不增加真实 tile 寄存器或相对索引队列项。END 不需要再产生一个假 tile 输出来串联阶段。

本提案依赖 BEGIN、写入、END 和消费的顺序副作用合同，必须在 LLVM IR 和机器层落实；仅有 parent 的 def-use 仍不能让消费等待 END。已有的“所有 TileOP 有序”约定需扩展到新增操作，不能仅假定泛化的 hasSideEffects 标记已足够。

独立 BEGIN/END 消除了为了阶段选择所需的分派和 peeling，不消除任意控制流的 tile PHI、相对索引生命周期或异常边问题。若 BEGIN 分别位于两个分支，汇合后仍可能需要处理 parent PHI。

## C++ 先例与借鉴边界

| 实际 API | 写入与完成 | 对本设计的启示 |
| --- | --- | --- |
| [Apache Arrow ArrayBuilder](https://arrow.apache.org/docs/cpp/arrays.html) | Append → Finish → Array | 可变 builder 完成后交出不可变结果；Arrow builder 可重置复用，我们的 Writer 首版只完成一次 |
| [ParquetFileWriter](https://github.com/apache/arrow/blob/main/cpp/src/parquet/file_writer.h) | 写 row group → Close | 显式结束负责尾部/元数据收尾；不等同于仅销毁局部句柄 |
| [gRPC ClientWriter](https://grpc.github.io/grpc/cpp/classgrpc_1_1_client_writer.html) | Write → WritesDone → Finish | 关闭写入与取得最终完成状态可以是不同步骤；tile finish 不必承担 CPU 同步等待 |
| [FlatBufferBuilder](https://flatbuffers.dev/tutorial/) | 构建对象 → Finish(root) → 完整 buffer | 显式完成标记可消费的完整结果；不是所有构建器都返回新对象 |

这些例子说明显式完成是常见的 builder/写入流设计，不代表它们具有 tile 的硬件生命周期、控制流或相对索引语义。

## 代价与待定项

相比绑定 INIT/LAST，独立 BEGIN/END 增加指令与控制开销，单次写入也需要独立开始和结束。硬件需处理 OPEN 空 generation、END 的验证和发布、错误/取消/资源回收。后续可以研究将 BEGIN 与首笔计算、END 与末笔计算融合为优化，但不能在尚无对应 ISA 支持时承诺零额外开销。

落地前需确定 BEGIN/END 的操作数和编码、parent 初始描述符、写入引用形式、空结果与提前结束规则、动态结果类型、同步与发布、诊断/取消，以及编译器顺序和生命周期建模。本文不将已有 ASL 对绑定阶段的验证视为新指令已通过验证。
