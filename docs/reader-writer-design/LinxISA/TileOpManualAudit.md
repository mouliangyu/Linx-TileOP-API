# TileOP 手册全量复审记录

日期：2026-11-24。状态：下列 11 项已完成文档修正；原发现保留为审核记录，处理结果见修正记录。

## 范围与证据

审核清单覆盖 TileOpReference 的全部 155 个 Markdown 页面：134 个操作页、21 个公共与导航页。按声明、参数角色、合法组合、语义、示例及公共规则之间的关系进行跨族检查，并对下列问题逐项回读确认。逐页清单记录问题关联及机械检查范围。

本次结论属于接口文档内部一致性与信息完整性审核。ISA 来源沿用既有固定版本核对记录；本次没有逐条重新验证全部指令的 ISA 语义。示例没有编译或执行。清单中未列出问题的页面仍需后续 ISA 对照和实现验证。

结构检查命令 `python .work/tileop-manual-structure/check.py` 输出 `[]`、`ops 134`。该检查覆盖标题、围栏、示例入口及链接等机械条件。下文的空节、错误示例类型与重载合同问题说明：机械检查通过仍需内容审核。

## 原始发现（修正前快照）

P1 表示影响公共调用语义或示例合法性；P2 表示合同查询、信息完整性或结构一致性问题。每项修正应同时检查相关公共页及全部关联操作。

### R01 · P1 · 两个 mask 示例使用错误类型

两页合法组合分别要求普通 Numeric U8 mask；示例却将 mask 声明为 uint32_t 的 V。直接照抄示例违反本页类型合同。证据：MGATHER_MASK 第 58、65–67 行；MSCATTER_MASK 第 55、62–64 行。

文档内部冲突。为 mask 单独定义 U8 类型，同时核对物理容量与有效形状；保留 payload 和 offset 的独立类型。

涉及：[MGATHER_MASK](TileOpReference/MGATHER_MASK.md)、[MSCATTER_MASK](TileOpReference/MSCATTER_MASK.md)。

### R02 · P1 · 双谓词位运算的默认维度没有来源

TAND/TOR/TXOR 的双 PredicateReadable 重载允许省略 UserValidCol/Row，第 74 行沿用数值重载的维度规则；CommonTypes 第 114 行规定零值取第一数值输入。这一重载没有数值输入，因此 TAND(dst,p0,p1) 的计算范围缺少定义。参数表还将两个源统一称为数值输入。

公共规则与专用重载之间的合同缺口。逐重载定义维度来源，明确双谓词及两种混合输入次序；同步角色与参数表。

涉及：[TAND](TileOpReference/TAND.md)、[TOR](TileOpReference/TOR.md)、[TXOR](TileOpReference/TXOR.md)、[CommonTypes](TileOpReference/CommonTypes.md)、[Predicate](TileOpReference/Predicate.md)。

### R03 · P2 · 原子 TSTORE 的参数表缺少重载适用范围

八页将 active 统一列为必填，声明中仅 active 重载包含该参数。以 ADD 第 20、42、50 行为例：active 仅用于 Local CUBE，但合并角色表没有表达该关联。正文已有范围说明，查询表仍会误导调用者。

重载整理错误。按重载列出参数存在性、源存储和 active 约束，避免将三个重载解释成一个参数集合。

涉及：[TSTORE_ATOMIC_ADD](TileOpReference/TSTORE_ATOMIC_ADD.md)、[TSTORE_ATOMIC_AND](TileOpReference/TSTORE_ATOMIC_AND.md)、[TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md)、[TSTORE_ATOMIC_INC](TileOpReference/TSTORE_ATOMIC_INC.md)、[TSTORE_ATOMIC_MAX](TileOpReference/TSTORE_ATOMIC_MAX.md)、[TSTORE_ATOMIC_MIN](TileOpReference/TSTORE_ATOMIC_MIN.md)、[TSTORE_ATOMIC_OR](TileOpReference/TSTORE_ATOMIC_OR.md)、[TSTORE_ATOMIC_XOR](TileOpReference/TSTORE_ATOMIC_XOR.md)。

### R04 · P2 · TGPR2T 缺少可以直接使用的位映射

TGPR2T 第 35 行要求按规范 plane 映射，页面和 LayoutRules 未给出 gpr 编号、bit 编号到输出行列/字节位的对应公式。示例四个 GPR 全为零，无法解释任何排列差异。用户无法据手册构造一个指定位置为真的输入。

语义说明遗漏。核对固定版本 ISA 后写出 M16/M32 映射，并提供非零输入和确定输出位置的例子。

涉及：[TGPR2T](TileOpReference/TGPR2T.md)、[LayoutRules](TileOpReference/LayoutRules.md)。

### R05 · P2 · TLEA 缺少输入输出 dtype 配对

TLEA 第 34 行定义符号/零扩展，第 38 行仅要求目标按 64 位 dtype 推导。没有列出源整数位宽和目标有符号性配对。读者无法判断 S32→U64 等调用是否被接口接受。

合法组合信息遗漏。补来源可追溯的 dtype 配对表；在完成核对前保留此项，不推导新的类型禁令。

涉及：[TLEA](TileOpReference/TLEA.md)。

### R06 · P2 · 部分类型合同仍由验证范围代替定义

TSHUF 第 41 行以当前 wrapper 验证范围描述 dtype；TEXPDIF 的公共合同（ElementwiseRules 第 79 行）要求按类型转换合同选择跨 dtype 组合，却缺少具体配对入口。同类型 FP32 示例不能回答其他组合是否合法。

新设计定义不完整。将支持集合与配对明确写入接口合同；实现验证记录放在手册外。

涉及：[TSHUF](TileOpReference/TSHUF.md)、[TEXPDIF](TileOpReference/TEXPDIF.md)、[LayoutRules](TileOpReference/LayoutRules.md)、[ElementwiseRules](TileOpReference/ElementwiseRules.md)。

### R07 · P2 · 公共类型表混淆两种谓词布局

CommonTypes 第 76 行将 TCMP/TCMPS 的 Tile 结果统一列为 PredicateCell；Predicate 明确 RowMajor 结果为 packed predicate、CUBE 为 PredicateCell。按公共类型表理解 RowMajor 时会获得错误的表示信息。

公共文档内部冲突。按布局描述结果表示，并引用 Predicate 的唯一定义。

涉及：[CommonTypes](TileOpReference/CommonTypes.md)、[Predicate](TileOpReference/Predicate.md)。

### R08 · P2 · TCI 系列的 Matrix 存储名称含义不明确

IrregularRules 第 13 行将目标描述为 Matrix CUBE_M16/M32；三个操作示例采用 VecTileM16，CommonTypes 将其 Location 定义为 Vec。Matrix 在这里究竟是布局概念还是存储角色缺少说明。

术语歧义。核对目标位置后使用已定义的 Location 与布局名称。此项仅确认文字歧义，尚未判定示例违反 ISA。

涉及：[TCI_2D](TileOpReference/TCI_2D.md)、[TCI_ROW](TileOpReference/TCI_ROW.md)、[TCI_COL](TileOpReference/TCI_COL.md)、[IrregularRules](TileOpReference/IrregularRules.md)、[CommonTypes](TileOpReference/CommonTypes.md)。

### R09 · P2 · 公开名称 TLOAD_CUBE 缺少独立查询入口

TLOAD 第 29 行公开声明 TLOAD_CUBE；目录中没有 TLOAD_CUBE.md，README 没有该名称入口。结构规范要求每个公开操作名有同名页面。用户按名称检索索引会漏掉该接口。

导航与结构规范不一致。按既定规范提供同名操作页和索引入口，明确公共合同归属。

涉及：[TLOAD](TileOpReference/TLOAD.md)、[README](TileOpReference/README.md)。

### R10 · P2 · 内容整理仍有空节、过期引导与复制残留

MGATHER、MSCATTER、MSCATTER_POPC、TGPR2T 的合法组合与限制节为空。ElementwiseRules 第 5 行和 AtomicsRules 第 19 行仍称下面列出声明；BroadcastRules、ReductionRules 保留无声明的声明节。六个 TGEMV 页面提及未出现在签名中的 groupM。

结构整理残留。空节补适用公共规则的精确链接；公共页修正引导；逐页删除无对应参数的复制内容。现有结构脚本无法识别这些语义残留。

涉及：[MGATHER](TileOpReference/MGATHER.md)、[MSCATTER](TileOpReference/MSCATTER.md)、[MSCATTER_POPC](TileOpReference/MSCATTER_POPC.md)、[TGPR2T](TileOpReference/TGPR2T.md)、[ElementwiseRules](TileOpReference/ElementwiseRules.md)、[AtomicsRules](TileOpReference/AtomicsRules.md)、[BroadcastRules](TileOpReference/BroadcastRules.md)、[ReductionRules](TileOpReference/ReductionRules.md)、[TGEMV](TileOpReference/TGEMV.md)、[TGEMV_ACC](TileOpReference/TGEMV_ACC.md)、[TGEMV_BIAS](TileOpReference/TGEMV_BIAS.md)、[TGEMV_MX](TileOpReference/TGEMV_MX.md)、[TGEMV_MX_ACC](TileOpReference/TGEMV_MX_ACC.md)、[TGEMV_MX_BIAS](TileOpReference/TGEMV_MX_BIAS.md)。

### R11 · P1 · Writer 输出 Part 与计算维度的绑定仍未闭合

既有 TileOpManualCompletenessReview 已记录：Writer 输出 Part 为 4 行，而操作按输入默认选择 16 行时，两个维度分别绑定何处尚待统一。CommonTypes 给出了计算维度选择，但不足以回答 assemble 片段范围与实际写入结果如何关联。该问题影响所有消费 Writer 描述的相关操作。

已记录的公共设计待决项。先核对底层 assemble 绑定，定义 Part 几何、计算区域和输出元数据的关系，再检查各操作的适用性。不要逐页自行增加相等限制。

涉及：[Writer](TileOpReference/Writer.md)、[CommonTypes](TileOpReference/CommonTypes.md)、[OperandRoles](TileOpReference/OperandRoles.md)。

## 修正记录

| 项目 | 已落实的修改 | 验证 |
| --- | --- | --- |
| R01 | 两个 mask 示例使用独立 U8 128 B 载体，有效形状 1×32 | 对照 Numeric U8 合同及容量规则 |
| R02 | 三个操作增加逐重载维度来源表；双谓词取 src0 U8 存储视图 | 同步 CommonTypes 与参数表 |
| R03 | 八个原子 TSTORE 增加重载选择表及逐重载源/active 角色 | 检查全部八页 |
| R04 | TGPR2T 增加 M16/M32 位映射和非零示例；公共页链接唯一定义 | 固定 ISA predicate-carriers 执行函数 |
| R05 | TLEA 列出 S32/S64→S64、U32/U64→U64 | 固定 ISA 类型及符号扩展合同；核对 wrapper |
| R06 | TEXPDIF 列全六个配对；TSHUF 写明 M32 64 位双 word 控制 | 固定 ISA tile manual 与 TSHUF ASL |
| R07 | 公共类型表区分 RowMajor packed 与 CUBE PredicateCell | 对照 Predicate 页 |
| R08 | TCI 公共规则明确 Location::Left，三个示例使用 CubeTileM16 | 核对 TCI_2D_Impl 的角色条件；此为库角色命名 |
| R09 | 新增 TLOAD_CUBE 独立页；声明从 TLOAD 移出；补分类与名称索引 | 135 个操作页结构检查通过 |
| R10 | 四个空节补合同入口；修正公共页引导和六页 GEMV 参数残留 | 全族文本检查 |
| R11 | Writer 分别定义 Parent、Part 物理范围及操作结果区域的绑定 | 同步 CommonTypes、OperandRoles、设计与完整性记录 |

R02 的默认维度选择和 R11 的库侧参数来源属于本次新接口设计定义；硬件范围字段含义沿用固定版本 B.ASSEMBLE。示例仍未编译，完整 ISA 逐操作复核仍为独立工作。

固定 ISA 版本：`PTO-ISA/pto-spec@a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，对应 LinxISA 0.59.1 引用：

- [TGPR2T 执行与位映射](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/predicate-carriers.asl)
- [TEXPDIF](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TEXPDIF.asl)
- [TLEA](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TLEA.asl)
- [TSHUF](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TSHUF.asl)
- [B.ASSEMBLE](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/operands/B.ASSEMBLE.asl)

修正后目录为 156 页：135 个操作页与 21 个公共/导航页。结构检查输出 `[]`、`ops 135`。下方清单保留问题关联用于回归核对。

## 修正顺序与收敛条件

1. 统一 R11、R02 的公共合同，给出能区分合法与非法调用的具体例子。
2. 修正 R01、R03、R07 的内部冲突，检查同族全部重载与示例。
3. 对照固定 ISA 版本补齐 R04、R05、R06、R08，逐项记录依据；仅有旧 wrapper 证据的项目继续标明证据边界。
4. 整理 R09、R10 的索引和结构，再运行机械检查。

每项关闭需记录改动页面、关联页面核对结果和验证方式。后续审查按清单推进，避免只复查最近修改的几个操作。全量 ISA 复核及示例编译分别保留独立状态。

## 逐页覆盖清单

“基础结构”记录当前脚本范围内的检查；“问题关联”列出本报告涉及的项目。“未列出”表示本轮没有在该页记录具体发现。公共页的结构规则与操作页不同，统一列为公共参考检查范围。所有页面的完整 ISA 复核及示例编译均未在本轮完成。

| 页面 | 基础结构 | 问题关联 |
| --- | --- | --- |
| [AtomicsRules](TileOpReference/AtomicsRules.md) | 公共参考 | R10 |
| [BroadcastRules](TileOpReference/BroadcastRules.md) | 公共参考 | R10 |
| [CommonTypes](TileOpReference/CommonTypes.md) | 公共参考 | R02、R07、R08、R11 |
| [CompareConvertRules](TileOpReference/CompareConvertRules.md) | 公共参考 | 未列出 |
| [ElementwiseRules](TileOpReference/ElementwiseRules.md) | 公共参考 | R06、R10 |
| [FragmentGeometry](TileOpReference/FragmentGeometry.md) | 公共参考 | 未列出 |
| [GMOV](TileOpReference/GMOV.md) | 操作页脚本通过 | 未列出 |
| [IndexedMemoryRules](TileOpReference/IndexedMemoryRules.md) | 公共参考 | 未列出 |
| [IrregularRules](TileOpReference/IrregularRules.md) | 公共参考 | R08 |
| [LayoutRules](TileOpReference/LayoutRules.md) | 公共参考 | R04、R06 |
| [MGATHER](TileOpReference/MGATHER.md) | 操作页脚本通过 | R10 |
| [MGATHER_ADD](TileOpReference/MGATHER_ADD.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_AND](TileOpReference/MGATHER_AND.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_CAS](TileOpReference/MGATHER_CAS.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_DEC](TileOpReference/MGATHER_DEC.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_EXCH](TileOpReference/MGATHER_EXCH.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_INC](TileOpReference/MGATHER_INC.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_MASK](TileOpReference/MGATHER_MASK.md) | 操作页脚本通过 | R01 |
| [MGATHER_MAX](TileOpReference/MGATHER_MAX.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_MIN](TileOpReference/MGATHER_MIN.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_OR](TileOpReference/MGATHER_OR.md) | 操作页脚本通过 | 未列出 |
| [MGATHER_XOR](TileOpReference/MGATHER_XOR.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER](TileOpReference/MSCATTER.md) | 操作页脚本通过 | R10 |
| [MSCATTER_ADD](TileOpReference/MSCATTER_ADD.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_AND](TileOpReference/MSCATTER_AND.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_DEC](TileOpReference/MSCATTER_DEC.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_INC](TileOpReference/MSCATTER_INC.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_MASK](TileOpReference/MSCATTER_MASK.md) | 操作页脚本通过 | R01 |
| [MSCATTER_MAX](TileOpReference/MSCATTER_MAX.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_MIN](TileOpReference/MSCATTER_MIN.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_OR](TileOpReference/MSCATTER_OR.md) | 操作页脚本通过 | 未列出 |
| [MSCATTER_POPC](TileOpReference/MSCATTER_POPC.md) | 操作页脚本通过 | R10 |
| [MSCATTER_XOR](TileOpReference/MSCATTER_XOR.md) | 操作页脚本通过 | 未列出 |
| [MatrixRules](TileOpReference/MatrixRules.md) | 公共参考 | 未列出 |
| [Numerics](TileOpReference/Numerics.md) | 公共参考 | 未列出 |
| [OperandRoles](TileOpReference/OperandRoles.md) | 公共参考 | R11 |
| [Options](TileOpReference/Options.md) | 公共参考 | 未列出 |
| [Predicate](TileOpReference/Predicate.md) | 公共参考 | R02、R07 |
| [README](TileOpReference/README.md) | 公共参考 | R09 |
| [Reader](TileOpReference/Reader.md) | 公共参考 | 未列出 |
| [ReductionRules](TileOpReference/ReductionRules.md) | 公共参考 | R10 |
| [ScalarRules](TileOpReference/ScalarRules.md) | 公共参考 | 未列出 |
| [StorageBoundaries](TileOpReference/StorageBoundaries.md) | 公共参考 | 未列出 |
| [TABS](TileOpReference/TABS.md) | 操作页脚本通过 | 未列出 |
| [TADD](TileOpReference/TADD.md) | 操作页脚本通过 | 未列出 |
| [TADDS](TileOpReference/TADDS.md) | 操作页脚本通过 | 未列出 |
| [TAND](TileOpReference/TAND.md) | 操作页脚本通过 | R02 |
| [TANDS](TileOpReference/TANDS.md) | 操作页脚本通过 | 未列出 |
| [TCI](TileOpReference/TCI.md) | 操作页脚本通过 | 未列出 |
| [TCI_2D](TileOpReference/TCI_2D.md) | 操作页脚本通过 | R08 |
| [TCI_COL](TileOpReference/TCI_COL.md) | 操作页脚本通过 | R08 |
| [TCI_ROW](TileOpReference/TCI_ROW.md) | 操作页脚本通过 | R08 |
| [TCMP](TileOpReference/TCMP.md) | 操作页脚本通过 | 未列出 |
| [TCMPS](TileOpReference/TCMPS.md) | 操作页脚本通过 | 未列出 |
| [TCOLARGMAX](TileOpReference/TCOLARGMAX.md) | 操作页脚本通过 | 未列出 |
| [TCOLARGMIN](TileOpReference/TCOLARGMIN.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPAND](TileOpReference/TCOLEXPAND.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDADD](TileOpReference/TCOLEXPANDADD.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDDIV](TileOpReference/TCOLEXPANDDIV.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDEXPDIF](TileOpReference/TCOLEXPANDEXPDIF.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDMAX](TileOpReference/TCOLEXPANDMAX.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDMIN](TileOpReference/TCOLEXPANDMIN.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDMUL](TileOpReference/TCOLEXPANDMUL.md) | 操作页脚本通过 | 未列出 |
| [TCOLEXPANDSUB](TileOpReference/TCOLEXPANDSUB.md) | 操作页脚本通过 | 未列出 |
| [TCOLMAX](TileOpReference/TCOLMAX.md) | 操作页脚本通过 | 未列出 |
| [TCOLMIN](TileOpReference/TCOLMIN.md) | 操作页脚本通过 | 未列出 |
| [TCOLPROD](TileOpReference/TCOLPROD.md) | 操作页脚本通过 | 未列出 |
| [TCOLSUM](TileOpReference/TCOLSUM.md) | 操作页脚本通过 | 未列出 |
| [TCVT](TileOpReference/TCVT.md) | 操作页脚本通过 | 未列出 |
| [TDIV](TileOpReference/TDIV.md) | 操作页脚本通过 | 未列出 |
| [TDIVS](TileOpReference/TDIVS.md) | 操作页脚本通过 | 未列出 |
| [TEXP](TileOpReference/TEXP.md) | 操作页脚本通过 | 未列出 |
| [TEXPANDS](TileOpReference/TEXPANDS.md) | 操作页脚本通过 | 未列出 |
| [TEXPDIF](TileOpReference/TEXPDIF.md) | 操作页脚本通过 | R06 |
| [TFMA](TileOpReference/TFMA.md) | 操作页脚本通过 | 未列出 |
| [TGATHER](TileOpReference/TGATHER.md) | 操作页脚本通过 | 未列出 |
| [TGEMV](TileOpReference/TGEMV.md) | 操作页脚本通过 | R10 |
| [TGEMV_ACC](TileOpReference/TGEMV_ACC.md) | 操作页脚本通过 | R10 |
| [TGEMV_BIAS](TileOpReference/TGEMV_BIAS.md) | 操作页脚本通过 | R10 |
| [TGEMV_MX](TileOpReference/TGEMV_MX.md) | 操作页脚本通过 | R10 |
| [TGEMV_MX_ACC](TileOpReference/TGEMV_MX_ACC.md) | 操作页脚本通过 | R10 |
| [TGEMV_MX_BIAS](TileOpReference/TGEMV_MX_BIAS.md) | 操作页脚本通过 | R10 |
| [TGPR2T](TileOpReference/TGPR2T.md) | 操作页脚本通过 | R04、R10 |
| [TIMG2COL](TileOpReference/TIMG2COL.md) | 操作页脚本通过 | 未列出 |
| [TLEA](TileOpReference/TLEA.md) | 操作页脚本通过 | R05 |
| [TLOAD](TileOpReference/TLOAD.md) | 操作页脚本通过 | R09 |
| [TLOAD_CUBE](TileOpReference/TLOAD_CUBE.md) | 操作页脚本通过 | R09 |
| [TLOG](TileOpReference/TLOG.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL](TileOpReference/TMATMUL.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL_ACC](TileOpReference/TMATMUL_ACC.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL_BIAS](TileOpReference/TMATMUL_BIAS.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL_MX](TileOpReference/TMATMUL_MX.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md) | 操作页脚本通过 | 未列出 |
| [TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md) | 操作页脚本通过 | 未列出 |
| [TMAX](TileOpReference/TMAX.md) | 操作页脚本通过 | 未列出 |
| [TMAXS](TileOpReference/TMAXS.md) | 操作页脚本通过 | 未列出 |
| [TMIN](TileOpReference/TMIN.md) | 操作页脚本通过 | 未列出 |
| [TMINS](TileOpReference/TMINS.md) | 操作页脚本通过 | 未列出 |
| [TMOV](TileOpReference/TMOV.md) | 操作页脚本通过 | 未列出 |
| [TMOV_CUBE_TO_SHARED_ND](TileOpReference/TMOV_CUBE_TO_SHARED_ND.md) | 操作页脚本通过 | 未列出 |
| [TMOV_SHARED_ND_TO_CUBE](TileOpReference/TMOV_SHARED_ND_TO_CUBE.md) | 操作页脚本通过 | 未列出 |
| [TMUL](TileOpReference/TMUL.md) | 操作页脚本通过 | 未列出 |
| [TMULS](TileOpReference/TMULS.md) | 操作页脚本通过 | 未列出 |
| [TNEG](TileOpReference/TNEG.md) | 操作页脚本通过 | 未列出 |
| [TNOT](TileOpReference/TNOT.md) | 操作页脚本通过 | 未列出 |
| [TOR](TileOpReference/TOR.md) | 操作页脚本通过 | R02 |
| [TORS](TileOpReference/TORS.md) | 操作页脚本通过 | 未列出 |
| [TPACK](TileOpReference/TPACK.md) | 操作页脚本通过 | 未列出 |
| [TPERMUTE](TileOpReference/TPERMUTE.md) | 操作页脚本通过 | 未列出 |
| [TPREFETCH](TileOpReference/TPREFETCH.md) | 操作页脚本通过 | 未列出 |
| [TRECIP](TileOpReference/TRECIP.md) | 操作页脚本通过 | 未列出 |
| [TRELU](TileOpReference/TRELU.md) | 操作页脚本通过 | 未列出 |
| [TREM](TileOpReference/TREM.md) | 操作页脚本通过 | 未列出 |
| [TREMS](TileOpReference/TREMS.md) | 操作页脚本通过 | 未列出 |
| [TROWARGMAX](TileOpReference/TROWARGMAX.md) | 操作页脚本通过 | 未列出 |
| [TROWARGMIN](TileOpReference/TROWARGMIN.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPAND](TileOpReference/TROWEXPAND.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDADD](TileOpReference/TROWEXPANDADD.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDDIV](TileOpReference/TROWEXPANDDIV.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDEXPDIF](TileOpReference/TROWEXPANDEXPDIF.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDMAX](TileOpReference/TROWEXPANDMAX.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDMIN](TileOpReference/TROWEXPANDMIN.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDMUL](TileOpReference/TROWEXPANDMUL.md) | 操作页脚本通过 | 未列出 |
| [TROWEXPANDSUB](TileOpReference/TROWEXPANDSUB.md) | 操作页脚本通过 | 未列出 |
| [TROWMAX](TileOpReference/TROWMAX.md) | 操作页脚本通过 | 未列出 |
| [TROWMIN](TileOpReference/TROWMIN.md) | 操作页脚本通过 | 未列出 |
| [TROWPROD](TileOpReference/TROWPROD.md) | 操作页脚本通过 | 未列出 |
| [TROWSUM](TileOpReference/TROWSUM.md) | 操作页脚本通过 | 未列出 |
| [TRSQRT](TileOpReference/TRSQRT.md) | 操作页脚本通过 | 未列出 |
| [TSCATTER](TileOpReference/TSCATTER.md) | 操作页脚本通过 | 未列出 |
| [TSEL](TileOpReference/TSEL.md) | 操作页脚本通过 | 未列出 |
| [TSELS](TileOpReference/TSELS.md) | 操作页脚本通过 | 未列出 |
| [TSHL](TileOpReference/TSHL.md) | 操作页脚本通过 | 未列出 |
| [TSHLS](TileOpReference/TSHLS.md) | 操作页脚本通过 | 未列出 |
| [TSHR](TileOpReference/TSHR.md) | 操作页脚本通过 | 未列出 |
| [TSHRS](TileOpReference/TSHRS.md) | 操作页脚本通过 | 未列出 |
| [TSHUF](TileOpReference/TSHUF.md) | 操作页脚本通过 | R06 |
| [TSQRT](TileOpReference/TSQRT.md) | 操作页脚本通过 | 未列出 |
| [TSTORE](TileOpReference/TSTORE.md) | 操作页脚本通过 | 未列出 |
| [TSTORE_ATOMIC_ADD](TileOpReference/TSTORE_ATOMIC_ADD.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_AND](TileOpReference/TSTORE_ATOMIC_AND.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_INC](TileOpReference/TSTORE_ATOMIC_INC.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_MAX](TileOpReference/TSTORE_ATOMIC_MAX.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_MIN](TileOpReference/TSTORE_ATOMIC_MIN.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_OR](TileOpReference/TSTORE_ATOMIC_OR.md) | 操作页脚本通过 | R03 |
| [TSTORE_ATOMIC_XOR](TileOpReference/TSTORE_ATOMIC_XOR.md) | 操作页脚本通过 | R03 |
| [TSTORE_PART](TileOpReference/TSTORE_PART.md) | 操作页脚本通过 | 未列出 |
| [TSUB](TileOpReference/TSUB.md) | 操作页脚本通过 | 未列出 |
| [TSUBS](TileOpReference/TSUBS.md) | 操作页脚本通过 | 未列出 |
| [TTRI](TileOpReference/TTRI.md) | 操作页脚本通过 | 未列出 |
| [TUNPACK](TileOpReference/TUNPACK.md) | 操作页脚本通过 | 未列出 |
| [TXOR](TileOpReference/TXOR.md) | 操作页脚本通过 | R02 |
| [TXORS](TileOpReference/TXORS.md) | 操作页脚本通过 | 未列出 |
| [TransportRules](TileOpReference/TransportRules.md) | 公共参考 | 未列出 |
| [Writer](TileOpReference/Writer.md) | 公共参考 | R11 |

## 后续复审三项修正

- TLOAD_CUBE 恢复 `Pad = TmaPadValue::Zero`，参数表和示例同步；TLOAD 页引用该入口。依据：0.59 源码 `include/jcore/template_asm.hpp` 的 TLOAD_CUBE 声明。
- CommonTypes 增加 reinterpret_tile 的声明、参数、等宽与 carrier 约束、借用生命周期和完整 TEXPDIF 示例；Reader 与索引补入口。普通 Local Tile 解释视图依据源码 `include/common/pto_tile.hpp`；Reader 片段组合是本手册定义的新库协议扩展，尚未验证实现。
- TSHUF 专用控制字段移至参数节，计算规则放在语义节，几何及合法性放在限制节；LayoutRules 保留入口与共享合同。实际读取元素的 definedness 条件按固定 ISA TSHUF 语义保留。

验证：135 个操作页结构、代码围栏和本地链接检查通过；复核默认值与控制表的重复残留。新增示例未编译执行。
