# TileOP 算子接口手册：参考调研与编写规范

> 当前结构以 [TileOP 接口手册结构规范](TileOpManualStructure.md) 为准。本文保留调研与历史决定；其中早期条目模板、角色表位置及样章组织不再作为排版规范。


> 0.59 修订说明：本文早期审查记录中的三参数 TSEL、118 项目录及 Shared 分片禁用结论已被更新。当前合同以 [接口参考](TileOpReference/README.md) 为准：TSEL 显式传入 true/false；119 项活动操作；Shared Reader/Writer 按存储合同使用；矩阵使用完整角色声明。


本文件研究如何编写可用于查询和编程的算子接口手册，不修改 TileOP API，不宣布新重载成立，也不以它替代手册正文。调研日期：2026-11-23。

## 1. 手册需要完成的任务

读者通常已经有计算任务，要查清一个操作如何调用，而不是从头学习全部编程模型。一份可用的参考条目应使读者无需打开编译器或 ISA 源码，就能回答：

1. 这个操作是否完成我要的计算？参数顺序是什么？
2. 应选择哪个重载？哪些参数可省略，省略后做什么？
3. 每个输入输出应是什么类型、位置、布局、物理及有效形状？
4. 是否读取目标旧值，能否 alias，是否有额外输出或内存效果？
5. Reader/Writer 能用于哪一个参数，哪些组合合法？
6. 可以直接照用的最小示例是什么，其结果是什么？

“118 个操作名均出现”只说明目录完整，不说明接口合同完整。

## 2. 实际查阅的参考

### cuBLAS GEMM：硬件数值库的合同深度

来源：[cuBLAS cublas<t>gemm](https://docs.nvidia.com/cuda/cublas/index.html#cublas-t-gemm)。已读取官方页面的 GEMM 条目。

条目先列 S/D/C/Z/H 等具体函数声明，再给出 `C = α op(A) op(B) + βC`、矩阵存储顺序和逻辑维度。参数表明确区分 Memory、In/out、Meaning，并按 transa/transb 写出 lda/ldb 的下界。beta 为零时 C 不需要作为有效输入，这个影响调用合法性的条件直接写在参数说明里。最后按错误码列出触发条件。

**采用：** 完整声明、输入/输出方向、逻辑与物理存储分开、条件化约束、可判断的错误条件。TileOP 的 TSEL 旧 dst、matmul C、Shared-B 物理形状都需要这种精度。

**不照搬：** TileOP 未定义 cuBLAS 式状态码，不能凭空增加；LLVM 内部细节也不应占据用户参数表。

### Triton dot：短条目仍需精确到参数

来源：[triton.language.dot](https://triton-lang.org/main/python-api/generated/triton.language.dot.html)。已读取官方 API 页面。

页面直接给出带默认值的签名，说明 2D/3D 的 shape 规则、batch 维度、acc 的累加用途以及输入/acc 类型。input_precision 参数写明设备相关的枚举、默认值和何时忽略；allow_tf32 写明弃用和互斥关系。精度风险紧邻操作说明。

**采用：** 参数默认值、互斥与生效条件必须与签名一起可查；数值精度是调用合同的一部分。

**不照搬：** 一个参数名出现在签名里但说明不足，不能成为我们省略说明的理由。我们的参数表应覆盖每个公开参数。

### PyTorch add：简单算子的最小完整条目

来源：[torch.add 页面](https://docs.pytorch.org/docs/stable/generated/torch.add.html)、[官方 docstring 源码](https://github.com/pytorch/pytorch/blob/main/torch/_torch_docs.py)。网页访问返回 403，实际读取的是官方源码中的 add 条目。

add 条目含带默认值的签名、精确公式、broadcast/type promotion 支持、位置和关键字参数，以及可观察输出的例子。

**采用：** 简单 op 可以很短，但必须说明 shape/type 行为；具体结果示例比只列 `TADD(d,a,b)` 更有帮助。

**不照搬：** TileOP 不自动继承 Tensor 库的 broadcasting 或类型提升。若不支持，条目要明确说明，不让用户猜测。

### OpenCL vloadn：单位和对齐是接口正文

来源：[官方 OpenCL C 规范源码，Vector Data Load and Store Functions](https://github.com/KhronosGroup/OpenCL-Docs/blob/main/OpenCL_C.txt)。单独 man page 返回 403，实际读取官方规范源码。

规范先定义 gentype 与向量宽度 n 的合法集合，再列不同地址空间的声明；读取地址明确写为 `p + offset × n`，随后按元素类型给出对齐要求。generic address space 的重载有明确版本/feature 条件。

**采用：** 单位、地址公式、对齐、类型集合及 feature 条件直接构成接口定义。MGATHER 的字节位移、Reader 的 CELL 偏移都应这样写。

**不照搬：** 不用一个含糊的 generic type 掩盖不合法的类型组合，也不使用用户已拒绝的宏式签名压缩。

### MLIR Linalg：算子结构化数据的参考

来源：[Linalg dialect](https://mlir.llvm.org/docs/Dialects/Linalg/)，实际读取 matmul 和 pack 条目。

条目包含操作语义、示例、属性、操作数、结果。pack 进一步定义 shape 关系、padding、动态形状下的非法条件和反例。页面也包含 traits/interfaces 等 IR 开发者信息。

**采用：** 属性、操作数和结果应作为独立信息维护；shape 关系应可检查，必要时给反例。

**不照搬：** TileOP 面向 C++ 用户，不应把 IR traits、编码、binder 结构自动附在每个页面的主体里。

## 3. 对 TileOP 的结论

以 **cuBLAS 的参数与约束深度**为主要参考，借用 **PyTorch/Triton 的单操作查询入口**和 **OpenCL 的单位、对齐表述**。MLIR 的结构适合后台组织合同数据，不能直接替代面向用户的 C++ 条目。

手册按操作提供可独立阅读的页面。分类页只负责查找，不用大表中的一句描述承担整个操作定义。Reader/Writer 位于公共类型参考；每个算子页仍需明确它们在哪个参数上可用。

## 4. 信息架构

```text
TileOP API Reference
├── 首页：版本、检索、分类与字母索引
├── 公共类型
│   ├── Tile / SharedTile / global_tensor
│   ├── Shape、layout、valid region
│   ├── Reader / Writer / fragment / iterator
│   ├── Predicate 与 element view
│   └── Options、枚举、范围描述符
├── 算子参考
│   ├── 逐元素算术、逻辑、比较与转换
│   ├── 标量与初始化
│   ├── 归约与广播
│   ├── 布局与不规则 Tile 访问
│   ├── 加载、存储、搬运、预取
│   ├── Indexed GM 与原子操作
│   └── 矩阵与矩阵向量运算
└── 接口状态与限制
```

每个公开操作有唯一可链接的条目。共享同一合同的重载放同页，实质不同的操作有独立条目。别名指向同一个权威说明，并明确兼容状态。排序、名称及交叉链接保持稳定。

教程、完整 kernel、ISA 提案、编译器 lowering 和工程验收记录放在不同文档。手册可以链接它们，但不能要求读者先阅读这些材料才知道参数怎么填。

## 5. 单操作条目模板

### 5.1 标题与摘要

操作名，加一句明确的计算描述。顶部附 namespace、header、接口版本与状态。正文描述一个确定版本的接口；不在同一声明块混入已实现接口和未经确认的重设计。

### 5.2 C++ 声明与重载选择

列出完整声明，包括模板参数、普通参数、返回类型和默认值。允许省略内部实现 attribute，但不得省略影响可调用性的约束；复杂约束在紧随的表格展开。

多个重载先给“何时选这个重载”的小表，再逐一声明。不能用 `OP(d,x,...)` 或一句“其余类似”代替完整签名。名字和表达式来自真实头文件或已确认的新 API 规格。

### 5.3 操作定义

用公式、索引关系或简短伪代码定义结果。明确输入逻辑形状、输出逻辑形状，以及与物理布局的关系。说明是否广播、是否类型提升、是否读取目标旧值。

返回类型为 void 仍需说明修改了哪些对象，产生什么结果；不能把“无 C++ 返回值”写成“无输出”。

### 5.4 模板参数与函数参数

模板参数单独列说明。普通参数表至少包含：

| 参数 | 类型/角色 | 输入输出方向 | shape/单位/范围 | 默认值及含义 |
| --- | --- | --- | --- | --- |
| 每个形参各一行 | 精确到载体类别 | in / out / in-out | 具体关系或枚举 | 无默认值也明确 |

参数存在相互约束时直接说明，例如 dtype 与 accumulator 的配对、转置条件下的物理形状。不能只给每个参数一个宽泛类型集合，让读者误认为其笛卡尔积都合法。

### 5.5 支持组合与前提

列允许的 dtype 组合、layout/location 组合、shape 关系、容量、对齐、PE 条件以及 alias 规则。数学 shape 与物理容量不得混成一列。

这一节给出本操作的具体条件。共用规则可以链接一次，但“满足 ISA 要求”“类型必须匹配”不能替代决定能否调用的实际约束。

### 5.6 Subview / assembly 支持

逐参数写支持情况及条件，不给整个算子贴一个含糊的“支持 Reader/Writer”标签。

| 参数 | 普通 Tile | Reader 片段 | Writer 片段 | 专用条件 |
| --- | --- | --- | --- | --- |
| 根据实际操作填写 | 支持状态 | 支持状态 | 支持状态 | 具体布局与 shape |

in-out 参数、多结果、predicate、Shared 和不规则索引要分别处理。未确定项进入设计问题列表，不能靠编写手册擅自增加重载。

### 5.7 数值、内存与错误行为

只写本操作相关的规则：舍入、溢出、NaN、精度；访问范围、原子性、冲突地址；同步与生命周期。分别说明编译期拒绝、运行时 fault、前置条件违反或尚未规定，不能一概称为“会报错”。

一个简单加法无需空置的内存原子章节；原子操作则必须说明哪些位置被修改、返回的旧值和顺序保证。

### 5.8 最小示例

声明具体的 operand 类型、输入数据/来源、调用与结果。至少一个基本示例；额外重载只补充有差别的例子。Subview/assembly 示例放在已核实支持它的条目中。

示例应独立可读，不使用正文未定义的 a/b/d。库未实现时明确标为设计示例；已实现后将示例变成编译和结果检查用例。不能声称通过未执行的检查。

### 5.9 相关接口与版本差异

链接直接相关的操作、类型和 options。不收录旧接口兼容与迁移；按目标接口描述调用方式。ISA 名称与实现映射可作为末尾补充，不占主体。

## 6. 用六种操作检验模板

这里检验模板是否容纳真实差异，不在研究阶段发明尚未批准的新 API。

| 操作 | 必须直接回答的问题 | 模板要承载的信息 |
| --- | --- | --- |
| TADD | 支持哪些 dtype/layout？动态 ValidCol/ValidRow 的 0 是什么？两个 Reader 和一个 Writer 能否同用？ | 完整重载、默认值、shape、逐参数范围支持 |
| TSEL | dst 是否必须预先定义？false 值来自哪里？为何不能把 Writer 当旧 dst 读取？ | in-out 参数、旧值语义、专用分片限制；显式 false 新重载若未确认不得写成正式接口 |
| TROWSUM | R×C 归约后是什么逻辑 shape？物理 carrier 多大？分片会不会改变归约范围？ | 数学定义、逻辑/物理分离、归约轴与分片条件 |
| TLOAD | GM 的 dtype/pitch 如何匹配目标？Local 和 Shared 选哪个重载？Writer 目标按 Parent 还是 Part 加载？ | 重载选择、地址单位、转换、目标形状与发布 |
| MGATHER_CAS | offsets 是元素还是字节？范围如何计算？返回旧值与内存更新如何对应？ | 地址公式、完整参数顺序、对齐、range、原子性及返回结果 |
| TMATMUL_ACC | C/D 类型如何选择？Shared B 物理形状是什么？groupM、CScale、raw_acc、acc_hint 分别做什么？ | 类型配对矩阵、形状表、options 生效条件、C/D alias 与缓存透明性 |

若这六种条目都能在统一框架下精确描述，才能推广到其余操作。先制作少量完整条目，检查能否据其独立写出合法调用，再批量扩展。

## 7. 完整性的验收方式

### 单条目验收

- 每个公开模板参数、形参和返回值都有说明，参数顺序与声明一致。
- dtype/layout/shape 的合法组合能判断，不靠读者查 ISA 猜测。
- 所有默认值、单位、运行时/编译期要求明确。
- 目标旧值、alias、输入输出生命周期和副作用明确。
- 分片能力逐参数说明，不从“Readable/Writable”推断任意操作可用。
- 示例使用已声明类型，数值或效果可检查。
- 没有未经确认的新重载，没有将缺失合同用空泛句子填满。

### 全手册验收

用“公开接口及重载”建立清单，逐项跟踪声明、合同、示例和验证状态。118 项 ISA catalog 只用作交叉核对：它不能替代 C++ 接口清单，也不能遗漏别名、辅助方法、范围重载和 options。

自动化只用于检查名称/重载遗漏、链接、格式、默认值同步及已实现示例的编译。不能自动复制旧说明后宣称语义写作完成。

## 8. 当前文档的处置与下一步

当前 TileOpUserManual.md 是不合格草稿，不能作为这套规范下的成品。暂不继续扩大正文，也不重新批量搬运页面。

六个代表操作的首版条目已写入 [TileOP 算子接口参考](TileOpReference/README.md)：TADD、TSEL、TROWSUM、TLOAD、MGATHER_CAS、TMATMUL_ACC。正文区分当前声明、实现限制与拟议 Reader/Writer 适配，含具体类型的设备函数示例。已检查本地链接和代码围栏；示例尚未编译或执行。

样章仍有明确的合同缺口：低精度数值细则、权重 C0 表、CScale 编码及完整 options 模式。应先补齐这些资料，再按同一结构扩展全量接口；不将六页样章视为全手册已完成。

## 9. 范围更新

手册不要求现有接口兼容。算子页不列旧 range carrier、阶段专用 `_ASS` 或专用 assembly writer 的兼容用法；组装按新的 Reader/Writer 设计描述。普通 Tile 声明仍以核实的接口为依据，不为移除兼容章节而虚构已实现重载。

## 10. 已确认的接口收录原则

本节记录 2026-11-23 的手册评审结论，适用于后续所有条目。

1. 交付物是所有 TileOP 的接口参考，不是基本编程教程。以算子查询为中心，Reader/Writer 是公共操作数协议，不能占据全手册重心。
2. 不需要现有接口兼容。正文不列旧 range carrier、`_ASS`、专用 assembly writer 或迁移路径。组装统一使用算子名，阶段由 Writer 输出描述表达。
3. 头文件用于核实参数与实现，不等于公开 API 清单。收录接口必须有公开接口文档或已确认设计依据；仅在实现中发现的便利函数、宏展开辅助入口不能直接提升为公开接口。
4. `TADD_U` 不收录。它来自实现宏展开，原 TADD 文档没有这个入口。`TLOAD(ElementTile&, pointer, valid_elements)` 同样不作为本手册的新增重载。`TREDUCEPREFIXVIEW` 虽有旧文档依据，也不作为新取片接口保留。
5. 保留 TADD/TSEL/TROWSUM 的普通操作、TLOAD 的 Local/Shared/权重公开重载、MGATHER_CAS 的范围重载和 TMATMUL_ACC 的 options/groupM 公开重载。`raw_acc`、`acc_hint` 有已讨论设计依据，不能与未经确认的实现辅助接口一起删除。
6. 不新增四参数 TSEL，不凭“Readable/Writable”推定所有 opcode 都支持 subview/assembly。每个参数的角色与 binder 支持分别核对。
7. 声明必须完整，不用宏、占位省略号或一张操作名表代替接口正文。示例必须有明确类型、输入前提和可观察结果。
8. 不复制旧页面后声称重写完成。旧文档、头文件、ISA 分别作为接口范围、实现和语义来源；矛盾要核查，未决事项明确记录，不能把实现缺陷写成目标接口设计。
9. 新设计和已实现能力明确区分。去掉兼容要求不代表可以宣称拟议重载已经实现、示例已经编译或硬件已经验证。

### 全量补写的完成条件

维护按公开操作及重载列出的覆盖清单。每项至少完成声明、参数/默认值/单位、语义、合法类型与形状组合、输入输出与别名、分片支持、示例和核对状态。完成名称索引不等于完成条目。公共类型与 options 的缺口同样计入未完成项。

## 11. 全量手册交付记录

用户确认补完整本。新版入口为 [接口参考](TileOpReference/README.md)，覆盖 118 个活动 TileOP 的声明与分类合同，另列公开辅助入口、公共类型、options、数值编码及 Reader/Writer 目标协议。旧 TileOpUserManual 草稿改为入口页。第 8 节的六个样章状态是历史记录，现由本节及 [覆盖清单](TileOpManualCoverage.md) 更新。

补查并写入权重 C0 表、CScale 精确公式、全部 pre-quant mode 与 descriptor 位域、MX Shared scale 不随转置变化、特殊 TCVT 配对和原子 preflight 边界。没有恢复未经确认的实现辅助接口，也没有增加兼容迁移层。示例没有编译或硬件执行，目标 Reader/Writer 尚未实现。

## 12. 打平目录

按用户确认，手册不创建分类子目录。每个公开算子在 TileOpReference 下有同名 Markdown 文件；README 提供分类与名称索引。共享合同保留在同层的 *Rules.md，Reader/Writer 分页。覆盖清单移至 TileOpManualCoverage.md，与设计/评审记录一起位于手册目录之外。此变更重组文档，不改变 API 合同。

## 13. 操作数角色显式化

评审指出多数算子页未区分 Reader/Writer/Tile。所有 124 个操作入口现增加逐参数角色表，放在普通 Tile 基线声明之前；明确目标协议、完整 Tile 限制、非 Tile 参数及未确定的 binder 适配。基础逐元素操作给出独立 Readable/Writable 模板的目标签名。TSEL 保留完整 Tile 读写目标，矩阵 C/D 不混入 assemble，GM 副作用不推导为 Writer 支持。新增 OperandRoles.md 统一说明协议；没有将未定义适配标为已实现。

## 14. 按新设计表述接口

用户明确手册是在定义新设计，不使用“拟议支持”或以未实现作为接口限制。算子角色表中“支持/禁止”直接表示设计合同；真正未决的 API 标为“设计待定”。实现与编译验证状态保留在独立覆盖记录，不作为 Reader/Writer 合同的前缀。

## 15. 索引 GM 操作的分片角色

MGATHER/MSCATTER 全族不以未核实旧实现适配为由标记设计待定。Local 输入统一为 Readable，MGATHER Local 结果统一为 Writable，MSCATTER 的 GM 目标不作为 Writer。各 Part 独立推导；索引保持 GM 字节位移语义；原子结果组装不扩大原子性，不延迟 GM 更新到 finish。

## 16. 完整性修正

移除并列旧签名；统一独立操作数协议、GM 视图构造与权限、动态维度元数据规则。补 PredicateTile 的 basis 与分片协议、逐类局部坐标、GMOV 的绝对 PE 编号。本版矩阵及 Shared 接口选择完整角色 Tile，明确为库设计边界，不声称 ISA 无法支持分片。相关记录见 TileOpManualCompletenessReview.md。


## 17. 统一操作页结构

全量操作页已按 [结构规范](TileOpManualStructure.md) 整理。当前页首先声明，再列参数及操作数角色；早期“角色表置于声明前”的安排已停止使用。整理范围与检查结果见 [覆盖记录](TileOpManualCoverage.md#2026-11-24按统一结构整理全量参考)。
