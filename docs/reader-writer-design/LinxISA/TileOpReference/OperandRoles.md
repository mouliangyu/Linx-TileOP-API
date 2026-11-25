# Tile、Readable 与 Writable

本手册定义新的 TileOP 库接口。普通 Tile、Reader 片段和 Writer 输出描述遵守同一套逐参数角色合同；实现是否已经落地不影响接口定义。

## 三类参数

| 角色 | 接受的值 | 不接受的值 |
| --- | --- | --- |
| Readable | 已定义普通 Tile；该操作支持的 Reader 片段 | Writer、Writer 输出描述、未完成 parent |
| Writable | 普通目标 Tile；该操作支持的 Writer 输出描述 | Reader、Reader 片段 |
| 完整 Tile | 满足角色、存储、发布和形状合同的实际 Tile | 未明确开放的片段描述 |

Readable/Writable 是操作数协议。Reader 对象先通过 read 或迭代器选择输入片段；Writer 对象先通过阶段方法或输出迭代器选择目标片段，二者本身均不直接作为计算参数。

普通 Tile 可在不同调用中扮演输入或输出。TSEL 显式提供 true/false 两个 Readable 源，dst 为 Writable，不要求已有值。GM 描述遵守 [GlobalMemoryView](CommonTypes.md#globalmemoryview) 协议，逐操作规定 GM 读写权限；它与标量、控制字、options 和 GPR 返回值均不属于这两类 Tile 协议。

## 接口签名的记法

```cpp
template <Writable D, Readable A, Readable B>
void add_into(D &&dst, A &&src0, B &&src1) {
  TADD(dst, src0, src1);
}
```

此调用示例用 D/A/B 展示逐参数协议；输入须已定义，三者须满足 [TADD 的合法组合](TADD.md#合法组合与限制)。完整操作声明和默认参数见 [TADD 声明与重载](TADD.md#声明与重载)。转发引用用于接收普通 Tile 左值以及临时片段描述，以借用方式传递 Tile payload。普通 Tile 临时值不能据此作为有效借用输入；接口同时约束值类别、生命周期和 descriptor 单次消费。

D/A/B 分别推导，算子再校验三者的**计算视图** dtype、布局和形状。普通 Tile 取自身几何，Reader 取选中的 Part，Writer 取输出 Part 的物理几何；有效计算区域按消费操作选择，见 [维度与范围绑定](Writer.md#维度与范围绑定)。Parent 提供目标存储、最终有效形状和偏移边界。标量参数的 dtype 同样由计算视图决定。

角色约束与操作几何共同决定调用是否合法。“支持”表示本设计允许该形式；“禁止”表示违反接口合同；具体支持边界由各操作页及 [存储边界](StorageBoundaries.md) 定义，不能用实现进度代替设计结论。支持分片的操作必须为每个相应输入/输出绑定 subview/assemble，并遵守各页的布局、类型和覆盖要求。

## finish 与输入合法性

Local Writer 首次计算保存 INIT 的真实 parent；MIDDLE/LAST 复用它，没有新的真实 Tile 输出。finish 只能在 LAST 或 SINGLE 完成后交出这个 parent。输出描述不能作为 Readable，因而不能对正在组装的 parent 做 subview。

Shared Writer 透传同一 Sx 的身份及阶段，跨 PE 的对象不必各自经历 first 到 last；finish 只交出句柄，不完成发布或同步。Shared 消费仍受 generation 就绪规则约束，详见 [Shared Writer](Writer.md#shared-writer目标身份与阶段透传)。

完整接口见 [Reader](Reader.md)、[Writer](Writer.md)。类型检查解决输入输出角色混淆；执行顺序、动态控制流和相对索引生命周期仍需编译器落实，不能用 C++ concept 替代这些保证。

Predicate 输入/输出分别使用 [PredicateReadable / PredicateWritable](Predicate.md)，与数值协议分开；不会把 Writer 本身作为输入。

## IndexedMaskReadable

索引内存操作使用此只读掩码协议。它接受 RowMajor Numeric U8，以及 CUBE_M16/M32 的 Numeric U8 或 PredicateCell 普通对象/Reader 片段。每个有效掩码字节须为 0 或 1；PredicateCell basis 不约束 payload dtype。mask 与 index 的布局类和有效形状一致。RowMajor packed Predicate 使用其独立位存储协议。Writer 和输出阶段描述均不能作为此协议的输入。
