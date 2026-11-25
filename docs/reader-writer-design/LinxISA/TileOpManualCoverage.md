# 接口覆盖与核对记录

## 逐重载核对入口

当前语义核对状态由 [逐重载台账](TileOpContractLedger.md) 维护，共登记 135 个操作的 256 条声明。状态与闭合要求见 [核对流程](TileOpContractReview.md)。下文的旧版数量与来源对照保留为历史记录；当前页面集合以台账及其文档指纹为准。

## 目录组织

手册目录打平：119 个活动操作及 15 个额外入口分别使用同名文件。公共参考和 `*Rules.md` 也在同一层；分类仅用于 README 导航。Reader/Writer 分为 Reader.md 与 Writer.md。下面的族统计记录操作归属，不代表仍用族页面集中存放声明。

## 活动 TileOP

119 项 0.59 活动 catalog 均有同名独立页面及声明与合同条目，逐项索引见 [名称目录](TileOpReference/README.md#按名称查询)。每个名称的签名存在性已检查；这项检查不等于示例编译或所有数值组合测试。

| 章节 | 活动操作数 | 合同重点 |
| --- | ---: | --- |
| [Atomics](TileOpReference/AtomicsRules.md) | 18 | 旧值输出、逐 lane 原子性、范围参数与数据类型 |
| [Broadcast](TileOpReference/BroadcastRules.md) | 16 | 声明、参数、形状、效果与调用示例 |
| [CompareConvert](TileOpReference/CompareConvertRules.md) | 3 | 声明、参数、形状、效果与调用示例 |
| [Elementwise](TileOpReference/ElementwiseRules.md) | 22 | 声明、参数、形状、效果与调用示例 |
| [TLEA](TileOpReference/TLEA.md) | 1 | 元素索引转换为字节位移 |
| [IndexedMemory](TileOpReference/IndexedMemoryRules.md) | 4 | 字节位移、普通 U8 mask、范围声明 |
| [Irregular](TileOpReference/IrregularRules.md) | 4 | 声明、参数、形状、效果与调用示例 |
| [Layout](TileOpReference/LayoutRules.md) | 5 | 声明、参数、形状、效果与调用示例 |
| [MGATHER_CAS](TileOpReference/MGATHER_CAS.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [Matrix](TileOpReference/MatrixRules.md) | 11 | 完整基础/options/scale/groupM 重载；primary/scale 布局 |
| [Reduction](TileOpReference/ReductionRules.md) | 11 | 声明、参数、形状、效果与调用示例 |
| [Scalar](TileOpReference/ScalarRules.md) | 14 | 声明、参数、形状、效果与调用示例 |
| [TADD](TileOpReference/TADD.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [TLOAD](TileOpReference/TLOAD.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [TMATMUL_ACC](TileOpReference/TMATMUL_ACC.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [TROWSUM](TileOpReference/TROWSUM.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [TSEL](TileOpReference/TSEL.md) | 1 | 声明、参数、形状、效果与调用示例 |
| [Transport](TileOpReference/TransportRules.md) | 4 | 存储/复制/预取输出与 Shared 发布 |

## 非 catalog 单名对应的公开入口

另新增八种 TSTORE_ATOMIC_* 同名页面及 TIMG2COL 页面；TLOAD_CUBE 的 padding 重载集中在 TLOAD 页。加上原有六个额外入口，共 134 个算子页面。IndexedByteRange 在旧 PTO-C 0.59 文档中列为独立扩展；LinxISA 0.59.1 固定规范已纳入对应 indexed TLSU 范围操作数。本设计保留有范围和无范围两类重载，不要求每个调用都传范围。

| 接口 | 手册位置 | 收录依据 |
| --- | --- | --- |
| TCI_2D、TCI_ROW、TCI_COL | [序列](TileOpReference/IrregularRules.md) | TCI 公开扩展 |
| TSTORE_PART | [传输](TileOpReference/TransportRules.md) | TSTORE Shared 公开重载 |
| TMOV_CUBE_TO_SHARED_ND、TMOV_SHARED_ND_TO_CUBE | [传输](TileOpReference/TransportRules.md) | TMOV 公开布局转换 |
| IndexedByteRange 重载 | [索引](TileOpReference/IndexedMemoryRules.md)、[原子](TileOpReference/AtomicsRules.md)、[CAS](TileOpReference/MGATHER_CAS.md) | LinxISA 0.59.1 indexed TLSU 范围合同 |
| TCMPS GPR 结果 | [比较](TileOpReference/CompareConvertRules.md) | 公开 overload，High 参数单独说明 |
| Matrix 的局部 scale 和 options/groupM 组合 | [矩阵](TileOpReference/MatrixRules.md) | 各 Matrix/GEMV 公开重载 |
| Tile、SharedTile、global_tensor、CUBE 别名 | [公共类型](TileOpReference/CommonTypes.md) | 算子参数所需载体 |
| fixp builders / modifiers | [Options](TileOpReference/Options.md) | 公开 options 及已确认 raw_acc/acc_hint |
| Reader/Writer 与迭代器 | [分片](TileOpReference/Reader.md) | 本次确认的目标设计，非已实现重载 |

## 不收录的接口

| 名称/类别 | 原因 |
| --- | --- |
| TADD_U | 原公开 TADD 页无此接口；实现宏展开不构成公共接口依据 |
| TLOAD 的 ElementTile pointer/valid_elements 形式 | 未经确认的另一编程 profile，不由实现存在直接加入 |
| TREDUCEPREFIXVIEW、旧 range、_ASS、专用 assembly writer | 新分片协议统一 Reader/Writer，无兼容要求 |
| 默认 EQ 的无 Mode 比较 | 旧兼容重载，使用显式 CmpMode |
| TCONCAT/TEXTRACT/TINSERT/THISTOGRAM/TQUANT/TDEQUANT/TSORT/TMRGSORT/TTRANS/TFILLPAD | 不在本基线活动目录，旧文件存在不代表活动 API |
| TMOV_L2S_INSERT/PUBLISH、TMOV_S2L_BROADCAST/EXTRACT | ISA ADR-CUBE-0016 移除了独立 Shared movement；旧 API 页推荐不能覆盖新 ISA |
| 独立 BEGIN/END、MatmulAccumulator、独立 FIXP | 另案候选设计，不混入当前 ISA 接口 |

## 核对方法与边界

声明和默认值对照公开文档及实现，语义冲突补查固定版本 ISA。TGATHER/TSCATTER 的行索引、重复目标拒绝及零初始化，TCVT 特殊类型配对，CScale 指数公式，MX scale 不随 primary 转置，以及权重 C0 表均按规范补查。

旧文档中的通用结果模板不作为依据，例如 TPREFETCH 没有输出 Tile。原子请求先完成地址探测再产生事件，但多个 PE 的已提交事件不整体回滚；不能将两类故障边界混为一谈。

**验证范围：**名称覆盖、Markdown 围栏与本地链接检查；未运行编译器、模型或设备。Reader/Writer 动态控制流 lowering、部分 opcode 的通用分片 binder、numeric profile 的误差上界属于实现/架构验证边界，不能通过文档改写宣称已实现。

## 0.59 修订核对

对照 PTO-C 发布站与 Linx-TileOP-API `ae2984c5fdfd1586cacf74ffa61ec3dd528ce5f8`：补 TLEA、TIMG2COL、八种规则地址原子 TSTORE、TLOAD_CUBE padding、UserPhysicalCol；TSEL 使用显式 true/false 输入，并补 GPRMask。Shared 搬运采用存储合同中的分片及发布要求。动态 Reader/Writer 可传有效行列。矩阵页仍声明完整角色对象，未定义通用矩阵片段重载。

Shared TMOV 另按 LinxISA 0.59.1 手册引用的 a89a53d48f5708328be609fe2e6296ac8bdb4bc2 语义核对：Local→Shared 显式 PEMask；ND→CUBE 不接受 Writer 目标；mask 位序、可编码集合及零 mask 不推进 Writer 的规则见 StorageBoundaries。此项核对不代表全手册已迁移到 0.59.1。

## LinxISA 0.59.1 审查：前五项修正

本轮依据 LinxISA 手册固定引用的 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2` 正式语义更新以下合同；库中的协议类型及模板参数是新接口设计。

| 问题 | 修正位置 | 正式依据 |
| --- | --- | --- |
| 单片容量与 parent 容量混淆 | Reader、Writer、FragmentGeometry、CommonTypes | [B.SUBVIEW](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/operands/B.SUBVIEW.asl)、[B.ASSEMBLE](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/operands/B.ASSEMBLE.asl) 的 Local 1..10 / Shared 1..12 |
| GPR 谓词操作类型错误 | TSEL、TCMPS、CompareConvertRules | 固定版本 TCMP/TCMPS/TSEL 的 GPR carrier 类型域；8 位操作仅 U8，64 位仅 M32 |
| TCMP 强制谓词与数值物理形状相同 | TCMP、CompareConvertRules | PredicateCell 独立 U8 存储几何及 basis 合同 |
| 谓词位运算缺重载 | TAND、TOR、TXOR、Predicate、ElementwiseRules | U8 CUBE 双 PredicateCell / 混合 Numeric U8 合同 |
| 广播缺少字节偏移 | 八个 TROWEXPAND 算子页、广播公共规则及分片几何 | ROW 族 RMode=BroadcastByteOffset，源有效列数至少为 1 |

验证：全手册本地链接/锚点及代码围栏检查通过；八个 ROW 广播声明和三个谓词位运算重载集检查通过。未编译或执行示例。ExecutionMask 与 TIMG2COL 的审查问题不在本轮修正范围。

## LinxISA 0.59.1 后续六项修正

依据同一 PTO 固定提交 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`：

- TIMG2COL 四 PE Shared 输出改为显式 Shared Writer 描述，限定 PE0/1/2/3 的 first/middle/middle/last 与零显式偏移；保留单 PE 完整发布，Local 禁止 assemble。
- packed 4-bit 索引访存改为 payload 列数是 index 的两倍，mask 与 index 同形状，一项控制整字节元素对。
- MGATHER_CAS 区分逻辑有效形状和各自物理列数/容量，不要求四个载体物理形状相同。
- TIMG2COL 补充 C0、窗口/K 边界、核级行分配及 NHWC/NCHW 到 Shared ND/Local M16/M32 的映射。
- CAS 示例的只读 GM 输入使用 const 元素类型。
- IndexedByteRange 按 0.59.1 已纳入的合同描述，旧 feature macro 不作为新设计的接口条件。

本轮未扩展 ExecutionMask 库接口。验证为文档链接、代码围栏与合同一致性检查；没有编译示例或执行硬件测试。

## Shared Writer 生命周期澄清

Shared Writer 为同一 Sx 透传阶段，各 PE 对象不要求独立经历 first 到 last；TIMG2COL 的跨 PE 阶段据此保持原 Writer 接口。finish 只交出句柄，不补 LAST、不同步或证明发布。撤回“必须另设 collective 接口才能表达”的判断；Local INIT 结果保存模型保持原合同。

## 通用限制来源审计与撤回

本轮检索全量操作页及公共规则中的强制性约束，并对静态形状、动态限制、谓词来源、别名及 Writer 状态机进行来源复核。不能把缺少支持证据改写为禁止，也不能把旧 wrapper 的 static_assert 自动变成新接口要求。

| 条目 | 处理与依据 |
| --- | --- |
| 所有静态输出必须等于实际结果；尾片必须换动态类型 | 撤回。此前为手册自行概括，无通用 ISA 依据。TIMG2COL 按硬件描述符记录每 PE 行数。 |
| Reader/Writer 显式 Part 维度必须等于静态轴 | 撤回额外类型相等条件，保留 subview/assemble、容量及操作几何校验。 |
| 动态 count 改变结果就必须换动态 Parent 类型 | 撤回类型强制推论，保留物理容量及最终覆盖要求。 |
| TPERMUTE、TCMPS GPR、TEXPDIF 的“仅静态形状” | 旧 PTO-C wrapper 有静态检查，但固定 ISA 的维度合同不要求 C++ 编译期常量；不作为新接口限制。 |
| TMATMUL_ACC 拒绝动态 A/B/D | 移除旧 wrapper 限制在新接口合同中的表述；保留角色、K、容量及协作行分配规则。 |
| TMOV Shared parent 静态已知、ND→CUBE 静态目标匹配 | PTO-C TMOV 原页有此要求，来源并非杜撰；但属旧 C++ carrier 条件，新设计不继承其静态类型限制。保留 ISA 的实际几何、行距、覆盖及有效区要求。 |
| 谓词必须由比较产生 | 撤回唯一生产者限制；合法谓词逻辑操作也能产生谓词。保留描述符、规范值和有效性要求。 |
| Shared 句柄一律不得作为持久化内存对象 | 撤回泛化禁令，改为本页未定义序列化或跨调用 ABI，不据此声明硬件禁止。 |
| Reader 页的 Writer first/last 状态机 | 删除误复制的规则；Reader 可重复、重叠读取，也可提前结束遍历。 |

保留有依据的约束：TPERMUTE 的新目标及 index/source 别名限制、归约的新分配目标来自固定 ISA；128 B CELL、容量编码、布局、对齐、地址访问、Shared 发布条件按相应 ISA 合同。Reader/Writer 输入输出角色和 Writer 迭代器提前退出为未定义行为来自本次已确认设计，不作为无来源限制删除。

核对源：PTO-C 0.59 的 `template_asm.hpp`（TPERMUTE/TCMPS 静态检查）与 `TMOV_zh.md`；固定 PTO 规范 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2` 的 TPERMUTE、TCMPS、TSELS、归约、TIMG2COL 和 Shared 转换合同。此审计撤回额外限制，不等于声明当前编译器已实现全部新接口。


## 2026-11-24：按统一结构整理全量参考

本轮按 [结构规范](TileOpManualStructure.md) 整理 134 个操作页。每页统一为声明与重载、参数与操作数角色、操作语义、合法组合与限制、示例、公共规则与相关接口六节。完整声明集中在首节，相关链接与返回索引置于页尾；矩阵、TIMG2COL、GPR 与 Predicate 专用内容使用三级标题。

清理逐元素、标量、广播、归约和序列页的跨操作复制残留；按实际签名列模板参数和函数参数，并保留专用参数解释。移除重复角色矩阵及物理列算法，公共维度与物理列规则集中到 CommonTypes。Reader 示例改为实际重读片段。补充各操作自身的具体调用、类型、输入前提及效果，包括矩阵和 GM 原子操作；修正 DEC 示例的回绕结果。

验证范围：134 页的固定标题顺序、各页示例包含对应操作调用、完整签名与整理前逐项一致；LinxISA 文档的本地链接和锚点检查通过。示例用于定义新接口，未进行编译或硬件执行，不据此宣称实现支持。

未决公共绑定和待复核 ISA 语义见 [完整性审查记录](TileOpManualCompletenessReview.md#2026-11-24结构整理后的语义待决项)。本轮结构验收不代替这些语义的确认。
