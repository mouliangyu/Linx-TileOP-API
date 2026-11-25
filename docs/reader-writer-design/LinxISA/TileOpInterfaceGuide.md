# TileOP 库接口指南：Tile、Subview 与 Assembly

查询已编写的 TileOP 签名、参数和约束，请阅读 [TileOP 接口参考](TileOpReference/README.md)。目录覆盖 118 个活动 TileOP，并列出公共扩展和 options。本文作为公共接口合同与设计边界的参考。

本文面向编写 kernel 的用户，整理现有 TileOP 库的接口组织，并给出 Reader/Writer 改造后的编程契约。**Reader/Writer 是拟议接口，尚未实现；示例不是当前头文件可直接编译的承诺。** 普通算子、数据传输和矩阵 options 以现有库为基础。

## 1. 阅读范围与版本

| 层次 | 本文职责 | 状态 |
| --- | --- | --- |
| TileOP C++ 库 | Tile 类型、操作数角色、分片、组装、迭代器和用法 | 本文主体 |
| C builtin / LLVM intrinsic | 承接库的操作和控制信息 | 独立设计，不要求有 Reader/Writer 对象 |
| ISA | subview、assembly、发布和相对索引的实际语义 | 合法性的依据 |

调研基线：

- TileOP 库：[Linx-TileOP-API `5f764847`](https://github.com/LinxISA/Linx-TileOP-API/tree/5f764847b707fabf998c93fb4725787bcd2d6417)。其使用指南声明 API/spec 基线为 0.58.7；个别 assembly 章节引用更早的规范。
- ISA：[pto-spec `a89a53d`](https://github.com/PTO-ISA/pto-spec/tree/a89a53d48f5708328be609fe2e6296ac8bdb4bc2)。本文关于 Local M16/M32 assembly 和 InternalAcc 的解释以此提交为准，不把库的旧几何规则混入新设计。
- 本文主方案：INIT/LAST 仍绑定计算操作的 Reader/Writer。独立 BEGIN/END 方案在第 10 节单独说明，尚未选定为替代实现。

建议先阅读第 2–6 节编写分片计算；需要动态循环时读第 7 节；接口范围见第 9 节。逐算子的声明、参数与约束查询 [接口手册](TileOpReference/README.md)。

## 2. 对象、类型与参数单位

### 2.1 Tile 与存储对象

| 对象 | 表达什么 | 使用约束 |
| --- | --- | --- |
| 普通 Local Tile | 类型化的 tile 值，包含 dtype、layout、物理容量和有效形状合同 | 输入必须已定义；不承诺普通 C++ 函数 ABI 或标量下标访问 |
| SharedTile | Shared tile 句柄及其类型信息 | 发布、参与 PE 和消费者可见性遵守 Shared 合同 |
| global_tensor | GM 地址及布局/步长描述 | 由 TLOAD/TSTORE 等使用，不是 Local tile |
| TileReader | 借用已完成 parent 的读取对象 | 不分配 tile，不延长 parent 生命周期 |
| TileWriter | 拥有尚在组装中的 parent 的库对象 | 完成前不能读取或建立 subview |
| 片段描述 | 一次输入或输出操作的范围与类型 | 不复制 payload，不是新分配的普通 tile |

库继续使用已有 Tile 类型，例如：

```cpp
using Parent = VecTileM32<float, 32, 8>; // 1024 B，8 CELL
using Large  = VecTileM32<float, 32, 4>; //  512 B，4 CELL
using Small  = VecTileM32<float, 32, 2>; //  256 B，2 CELL
```

Parent 显式指定；不会根据最后一次写入的位置自动推导分配容量。每笔写入独立选择片段类型，因此允许不同大小的片段。物理容量、物理形状与有效形状是不同概念；有效范围变小不等于分配变小。

底层采用向量 carrier 不自动赋予 Tile 普通向量下标的语义。现有 `ElementTile`、`TPARTELEMENT` 和 element-loop 有自己的强类型映射合同，本次 Reader/Writer 改造不替代这些接口。

### 2.2 单位表

| 参数 | 单位 / 含义 | 示例 |
| --- | --- | --- |
| `cell_offset` | 相对 parent 起点的 128 B CELL 数 | `2` 表示 256 B 偏移 |
| `fragments<Part>(count)` 的 count | Part 片段个数 | Part 为 2 CELL 时，4 个片段覆盖 8 CELL |
| Part 的 shape | 按该 Tile 类型定义的行列与布局 | 不能把列号直接当 CELL 偏移 |
| GM stride | 按具体传输接口的合同；现有规则矩形 TLSU 行 stride 为字节 | 不与 CELL 混用 |
| `groupM` | cooperative matmul 的整个核的 M 行数 | 不是单 PE 的 M，也不是 PE mask |

Subview/assembly 直接接收整数 CELL 偏移，不提供 `cells()` wrapper、二维坐标或 fragment 编号重载。偏移也不是 tile 队列的相对索引。CELL 粒度避免表达低于 128 B 的偏移，但不能自动满足更强布局对齐、编码大小或边界要求。

## 3. 统一操作数角色

计算仍使用已有操作名和参数次序，例如 `TADD(dst, lhs, rhs)`。拟议适配让输出接受 Writable 描述、输入接受 Readable 描述，不要求业务代码选择 `TADD_ASS`。

| 对象 | 可作为 tile 输入 | 可作为 tile 输出 |
| --- | --- | --- |
| 普通 Tile | 已定义且满足操作要求时可以 | 满足该操作目标要求时可以 |
| `reader.read<Part>(offset)` | 可以 | 不可以 |
| `writer.first/middle/last/single<Part>(offset)` | 不可以 | 可以，仅消费一次 |
| Reader / Writer 对象本身 | 不可以 | 不可以 |

Readable/Writable 是角色约束，不是对所有算子的通行许可。每个操作还必须检查 dtype、layout、形状、PE、alias 和是否支持对应 binder modifier。多输出操作必须逐个输出角色适配，不能仅修改第一个参数就宣称完成。

例如，下列用法必须拒绝；诊断文字是设计目标，不是当前编译器的实际输出：

```cpp
TADD(dst, writer.middle<Small>(0), rhs);
// 输入要求 Readable；assembly 输出描述仅为 Writable。

TileReader<Parent> reader(writer);
// 构造要求已完成的 Parent；Writer 不是 Parent。
```

## 4. Reader 接口参考

以下是拟议声明的语义骨架；`ReadFragment`、`ReadRange` 是说明返回类型角色的名称，实现命名未定。

```cpp
template<class Parent>
class TileReader {
public:
    explicit TileReader(const Parent& parent);
    TileReader(Parent&&) = delete;
    TileReader(const Parent&&) = delete;

    template<class Part>
    ReadFragment<Parent, Part> read(size_t cell_offset) const;

    template<class Part>
    ReadRange<Parent, Part> fragments(size_t count) const;
};
```

| 接口 | 前提 | 结果与效果 |
| --- | --- | --- |
| 构造 | parent 是有效、已完成的左值 | 借用 parent，不分配或复制 |
| `read<Part>(offset)` | 类型兼容、范围和对齐合法 | 返回 Readable；消费时生成 source subview |
| `fragments<Part>(count)` | 所有访问位置合法 | 从 CELL 0 开始的同大小连续片段范围 |

`read` 可使用运行时偏移；Part 类型和物理尺寸在编译期确定。重复读取与重叠读取允许。每个消费者根据输入位置绑定自己的 B.SUBVIEW，不由用户填写输入寄存器编号。

Reader、读取范围、片段与迭代器均借用 parent，不拥有硬件 payload。拒绝临时对象只能消除一类悬空使用，普通 C++ 类型检查不能证明任意控制流下的硬件 tile 生命周期。Reader 不需要 `finish()`。

## 5. Writer 接口参考：阶段绑定计算

以下同样是拟议声明骨架，描述符类型不是当前公开实现：

```cpp
template<class Parent>
class TileWriter {
public:
    TileWriter();
    TileWriter(const TileWriter&) = delete;
    TileWriter& operator=(const TileWriter&) = delete;
    TileWriter(TileWriter&&) = delete;
    TileWriter& operator=(TileWriter&&) = delete;

    template<class Part> auto first(size_t cell_offset);
    template<class Part> auto middle(size_t cell_offset);
    template<class Part> auto last(size_t cell_offset);
    template<class Part> auto single(size_t cell_offset);
    template<class Part> auto fragments(size_t count);

    Parent finish();
};
```

| 方法 | 消费前状态 | 消费描述的计算行为 | 消费后状态 |
| --- | --- | --- | --- |
| `first<Part>(offset)` | Empty | INIT 分配 parent，并写片段 | Open |
| `middle<Part>(offset)` | Open | MIDDLE 写同一个 parent | Open |
| `last<Part>(offset)` | Open | LAST 写片段并完成 assembly | Complete |
| `single<Part>(offset)` | Empty | INIT_LAST 创建并完成 parent | Complete |
| `finish()` | Complete | 返回保存的 parent；不发独立指令 | Finished |

构造库对象和创建输出描述都不执行 INIT。描述引用所属 Writer；计算实际消费 first 描述时，把 INIT 的结果保存到 Writer。middle/last 引用同一 parent，没有新的真实 tile 输出；finish 返回保存的身份。因此 finish 能指向首次计算的输出，无需反向搜索计算历史。

阶段与位置独立：first 不要求 offset 0，last 不要求最高地址。允许在不同调用中使用不同 Part 类型。当前基线对 Local M16/M32 检查边界、参与 PE、同 PE 写入不重叠、可编码的物理 envelope、writer 数量及最终合法前缀覆盖。当前物理形状由 parent 容量决定，最终有效列前缀由覆盖确定；不能套用旧版“覆盖缩小 parent 物理形状”的说明。

首版使用明确最终有效形状的 Parent，每条成功路径必须产生匹配结果。动态偏移不代表动态类型；如果实际覆盖导致有效形状随路径变化，需要另外支持动态有效形状结果。

Writer 不公开 parent/data 转换。输出描述仅消费一次；有未消费描述时不能请求另一描述或 finish。拒绝未初始化 continuation、重复 first、LAST 后继续写以及提前/重复 finish。析构不自动补 LAST，也不隐式取消硬件状态。

这些是接口要求。静态角色错误可以编译期拒绝；动态状态、范围和覆盖错误如何检查、是否 trap、检查开销及诊断模式尚未实现，不能承诺每种错误都会得到固定报错。

## 6. 完整的分片计算示例

以下是拟议的内联计算区域。x、y 已加载为完整 Parent；示例省略 GM 传输，避免把 GM 布局转换与 CELL 范围选择混在一起。它不表示允许通过普通非内联 C++ ABI 传递 Tile。

```cpp
using Parent = VecTileM32<float, 32, 8>;
using Large  = VecTileM32<float, 32, 4>;
using Small  = VecTileM32<float, 32, 2>;

// x、y：已定义的 Parent。
TileReader<Parent> xs(x);
TileReader<Parent> ys(y);
TileWriter<Parent> out;

TADD(out.first<Large>(4), xs.read<Large>(4), ys.read<Large>(4));
TADD(out.middle<Small>(0), xs.read<Small>(0), ys.read<Small>(0));
TADD(out.last<Small>(2), xs.read<Small>(2), ys.read<Small>(2));

auto result = out.finish();
// result 是完整 Parent，可以传给后续 TileOP 或 TSTORE。
```

三笔输出分别覆盖 `[4,8)`、`[0,2)`、`[2,4)` CELL，完整覆盖 parent。它同时展示不同片段大小和非地址递增的写入顺序；没有把 INIT/LAST 绑定到固定空间位置。

只有一笔写入时使用 single：

```cpp
TileWriter<Parent> out;
TADD(out.single<Parent>(0), x, y);
auto result = out.finish();
```

同一个 Reader 片段可复用：

```cpp
auto part = xs.read<Small>(2);
Small d0, d1;
TADD(d0, part, ys.read<Small>(0));
TADD(d1, part, ys.read<Small>(2));
```

## 7. 迭代器与动态控制流

### 7.1 对称的顺序遍历

```cpp
TileReader<Parent> xs(x);
TileReader<Parent> ys(y);
TileWriter<Parent> out;

auto xr = xs.fragments<Small>(4);
auto yr = ys.fragments<Small>(4);
auto wr = out.fragments<Small>(4);
auto xi = xr.begin();
auto yi = yr.begin();

for (auto wi = wr.begin(); wi != wr.end(); ++wi, ++xi, ++yi)
    TADD(*wi, *xi, *yi);

auto result = out.finish();
```

解引用产生片段描述，自增前进一个 Part 的物理 CELL 数。范围从 CELL 0 开始，不提供随机写计划。不同大小片段和任意偏移使用直接接口。

| 行为 | Reader 迭代器 | Writer 迭代器 |
| --- | --- | --- |
| count | 可运行时；可为 0 | 可运行时；开始前确定且至少为 1 |
| `*it` | 可重复读取 | 对应项只能被计算消费一次 |
| `++it` | 推进位置 | 当前项消费后才能推进 |
| 提前 break | 可以 | 未执行 LAST 时不能 finish |
| continue 跳过当前计算 | 可以 | 不可以 |
| 复制 | 可保留独立读取位置 | 单遍输出语义，不承诺可复制遍历 |
| 完成 | 不需 finish | 显式 finish |

仅承诺这里列出的解引用、自增和同范围比较操作，不宣称满足完整的 C++ 标准 iterator concept。end 不可解引用。

### 7.2 动态 count 的真实含义

Writer 的消费者按 `count == 1`、首项、中间项、末项选择 INIT_LAST、INIT、MIDDLE、LAST。阶段必须落到静态编码的调用点；不能把动态 phase 当作立即数直接传给 builtin。

动态 count 需要边界和形状检查，固定 Parent 不允许任意 count 改变结果合同。普通 C++ 循环可能保留阶段分支和 parent PHI；不能承诺优化器自动完成首尾 peeling。分支 INIT、循环相对索引与跨迭代生命周期需要后端验证。

若终止条件在本次计算后才知道，当前绑定阶段的 ISA 无法给已经执行的计算补 LAST。finish 和析构都不能修复它。需要这种控制流时，评估第 10 节的独立 END 方案，并继续满足最终覆盖要求。

## 8. 其他 TileOP 接口与适配范围

### 8.1 算子目录

本次改变的是分片操作数的表达，不重新命名全部算子。完整逐操作签名、dtype、边界与后端状态继续由现有操作参考承载；不能把某个 wrapper 已存在解释为新 Reader/Writer 已适配。

以下路径均位于 [固定版本的使用指南](https://github.com/LinxISA/Linx-TileOP-API/tree/5f764847b707fabf998c93fb4725787bcd2d6417/docs/tileop-usage)：

| 类别 | 典型入口 | 查阅位置 | 新描述符适配要求 |
| --- | --- | --- | --- |
| 数据传输 | TLOAD、TSTORE、TMOV | `tlsu/load-store-move/` | 逐角色确认 GM/Local/Shared、布局转换和范围支持 |
| 逐元素双输入 | TADD、TSUB、TMUL | `elementwise-tile-tile/` | 检查每个输入 subview 与目标 assembly 的组合 |
| 标量/立即数 | TADDS 等 | `tile-scalar-and-immediate/` | 保留标量类型和立即数限制 |
| 比较与选择 | TCMP、TSEL 等 | 逐操作页及 `predicate-adapters.md` | Predicate 角色不可自动等同普通 Readable tile |
| 归约与广播 | TROWSUM、TROWMAX、TROWEXPAND 等 | `reduce-and-expand/` | 输入输出形状不同，需专门约束 |
| 布局与转换 | TCVT、TPERMUTE、TSHUF、TPACK、TUNPACK | `elementwise-tile-tile/format-conversion/`、`layout-and-rearrangement/` | 按转换前后类型和布局检查 |
| 不规则/原子传输 | MGATHER、MSCATTER 及 variants | `tlsu/memory/`、`indexed-tlsu-range.md` | byte displacement、范围和原子语义独立保留 |
| 矩阵计算 | TMATMUL、TMATMUL_ACC、BIAS/MX、TGEMV | `cube/`、`options.md` | 核对主输入、C、scale/bias、辅助输出各角色 |
| PE/Shared 传输 | GMOV、Shared TLOAD/TMOV | `tlsu/` | 独立发布与参与 PE 合同，不直接套 Local Writer |
| 逻辑元素编程 | ElementTile、TPARTELEMENT | `README.md`、`element-if.md` | 保留元素映射，不机械改为 CELL 偏移 |

此表是文档导航与适配清单，**不是全量算子已支持 Reader/Writer 的声明**。现有操作及后端覆盖以 [support-status.md](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/docs/tileop-usage/support-status.md) 为准。首版 Reader/Writer 合法性分析聚焦 Local M16/M32；Shared、其他布局和每个算子的组合仍需逐项验收。

每个算子适配页应固定提供：完整重载、每个操作数角色、支持类型/布局、输入 subview 支持、输出 assembly 支持、辅助输出、alias 限制、动态参数、正例/负例、编译与模型验证状态。没有记录的组合不得由通用角色模板默认为支持。

### 8.2 Matmul 保留显式 accumulator 与 options

现有 cooperative Local-A/Shared-B 调用包括：

```cpp
TMATMUL(d, a, shared_b, groupM);
TMATMUL(d, a, shared_b, options, groupM);
TMATMUL_ACC(d, c, a, shared_b, groupM);
TMATMUL_ACC(d, c, a, shared_b, options, groupM);
```

`fixp::Options` 除最终后处理外，还承载输入变换与 CCTRL：

| 配置 | 语义 |
| --- | --- |
| `keep_acc()` | 不进行输出类型转换，本身不设置 CCTRL |
| `.raw_acc()` | 原始 accumulator 类型的 D，并提供缓存替换提示 |
| `.acc_hint()` | 对显式 C 的缓存使用/预取提示，ACC 形式才合法 |
| `f16()/bf16()/s8(...)`、激活、辅助输出 | 最终后处理，具体组合按已有合同 |
| 转置、CScale | 输入解释/变换，不等同于最终后处理 |

三步 K 累加的调用示意（输入与输出 Tile 类型已匹配）：

```cpp
TMATMUL(c0, a0, b0, fixp::keep_acc().raw_acc(), groupM);
TMATMUL_ACC(c1, c0, a1, b1,
            fixp::keep_acc().raw_acc().acc_hint(), groupM);
TMATMUL_ACC(result, c1, a2, b2,
            fixp::f16().relu().acc_hint(), groupM);
```

InternalAcc 是透明实现缓存。每步显式 C 是架构输入，每步 D 都分配并发布，raw D 可以供满足其类型/布局要求的其他 TileOP 使用。当前 C 与 D 索引必须不同。不能把 raw D 描述成只能给下一次 matmul 的不可读句柄，也不能引入当前 ISA 不存在的独立 spill 指针参数。

`MatmulAccumulator` 和独立 FIXP 是另外的候选接口/ISA 扩展，不作为本次 assemble/subview 改造的已确认 API。当前 finish 不能代替一条不存在的独立后处理指令。

## 9. 接口范围

本设计不要求现有接口兼容。旧 range、TileArray slot、阶段专用算子及元素 profile 入口不作为新接口承诺；分片统一由 Reader/Writer 描述，计算继续使用原算子名。Parent 显式描述容量和最终有效形状，不由数组位置推断 INIT/LAST。

普通 Tile 的公开算子、完整重载与实现限制见 [接口手册](TileOpReference/README.md)。这不意味着现有 wrapper 已接受新 Reader/Writer 类型。

## 10. 备选：独立 BEGIN/END 的简化接口

如果 ISA 将开始与结束从计算拆开，同一个 Writer 可以简化为：

```cpp
TileReader<Parent> xs(x);
TileReader<Parent> ys(y);
TileWriter<Parent> out; // 拟议 BEGIN

TADD(out.write<Large>(4), xs.read<Large>(4), ys.read<Large>(4));
TADD(out.write<Small>(0), xs.read<Small>(0), ys.read<Small>(0));
TADD(out.write<Small>(2), xs.read<Small>(2), ys.read<Small>(2));

auto result = out.finish(); // 拟议 END
```

| 问题 | 当前 ISA 对应的阶段方案 | 独立 BEGIN/END 候选 |
| --- | --- | --- |
| parent 何时分配 | 首次计算 INIT | BEGIN |
| 每笔输出方法 | first/middle/last/single | write |
| finish 是否发结束操作 | 否 | 是 |
| 动态循环阶段分派 | 需要 | 不需要 |
| 计算后决定 break | 未提前发 LAST 则不能完成 | 可随后 END，但实际覆盖必须合法 |
| 新 ISA 支持 | 沿用现有阶段语义 | 需要新增语义与编码 |

两个方案不能在同一 API 中默默混用。Reader 和 CELL 参数规则保持一致；独立 END 仍不允许读取 OPEN parent，不消除边界、覆盖、动态有效形状及发布顺序要求。空 generation、取消和销毁策略尚待确定。

## 11. 编译契约、错误处理与验收边界

parent 的数据依赖只指向首次定义，不能单独保证读取位于 LAST/END 之后。本设计要求编译链在 IR 与机器层保持 TileOP 的顺序副作用契约；仅添加一个泛化 side-effect 标志不能作为已完成实现的证据。

| 检查层 | 必须覆盖的事项 |
| --- | --- |
| 静态类型 | Writer 不能读、Reader 片段不能写、Part 与 Parent 兼容、算子角色合法 |
| 运行路径 | 初始化、一次性描述消费、结束状态、范围/覆盖、借用存活 |
| 编译器 | INIT 的真实结果绑定、continuation 无假 tile 输出、顺序、PHI 与相对索引 |
| 模型/硬件 | 混合片段、非递增偏移、边界和尾部、非法覆盖、动态循环的实际结果 |

实现前仍需明确：新描述符的具体 C++ 类型与约束、所有算子的适配矩阵、运行时检查策略、动态结果形状、Shared 扩展范围，以及是否选择独立 BEGIN/END。本文已完成源码调研与文档一致性检查，未实现新接口，未执行编译或模型数值验收。

## 12. 设计与调研索引

- [Reader/Writer 详细设计](TileReaderWriterDesign.md)：阶段状态机、动态迭代器和编译器绑定。
- [独立 BEGIN/END 详细设计](TileAssemblyBeginEndDesign.md)：显式 finish、生命周期及 ISA 改动。
- [调研记录与文档结构](TileOpInterfaceResearch.md)：来源、差异、章节职责和后续维护方式。
- [Builtin 原型草案](TileBuiltinPrototypes.md)与[映射草案](TileBuiltinMapping.md)：另一层接口，不作为本文 C++ API 的已实现证明。
