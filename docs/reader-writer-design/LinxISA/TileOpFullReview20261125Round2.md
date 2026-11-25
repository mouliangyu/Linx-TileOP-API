# TileOP 全册复核第二轮（2026-11-25）

## 范围与方法

覆盖当前135个操作页、274条已登记重载以及21个公共页面。按族比较语义、类型、形状、角色和示例叙述，跨页复核公共协议与操作声明；相同段落合并阅读，独有内容单独检查。对全部登记声明检查函数参数在本页参数区的覆盖，并重跑声明指纹、六节结构和已标记示例检查。

本轮为文档一致性复核，未逐条重新认证274×8项ISA证据，未执行完整实现、ASL或硬件测试。三条S-SUBMIT保持搁置。下列条目记录复核时的发现；修正进度见各条处理记录。

## 确认问题

### R01 [P2] 两个MX操作页的参数表仍遗漏NoOperand分支

位置：[TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md#参数与操作数角色)、[TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md#参数与操作数角色)。

两页的tile_shape_sa/sb仍写“满足typename约束”，scale_a/b角色表仍仅列完整Tile。完整Options重载允许ScaleMask为0/1/2，缺失槽应为NoOperand；本页explicit_slots示例及新增说明已有这一合同，参数表与它们冲突。比如两侧FP16的ScaleMask=0调用要在两个槽传NoOperand，按角色表却会被排除。

前一轮F07修改匹配了ascale/bscale命名，遗漏这两页使用的scale_a/b命名。应按实际声明的参数名修正四个模板类型行及四个角色行，并复查六个MX页的完整槽与便利槽。

依据：本库[MX重载约束](TileOpReference/MatrixRules.md#mx-重载约束)、两页Options声明及explicit_slots0/1/2示例。属于库接口描述遗漏。

处理记录（2026-11-25）：R01已修正。两页的四个模板类型行、四个操作数角色行及四个参数含义行补齐Options缺失槽的NoOperand规则。复查六个MX页面：完整槽按ScaleMask选择，便利槽仅接受实际scale Tile。72条MX声明的396个角色/dtype重载选择检查通过（声明mock）。

### R02 [P2] 公共协议页与TADD页给出不同函数声明

位置：[OperandRoles](TileOpReference/OperandRoles.md#接口签名的记法)。

公共协议页的TADD声明止于UserValidRow；[TADD操作页](TileOpReference/TADD.md#声明与重载)另有UserPhysicalCol=0。读公共页会漏掉六实参调用能力；把两段声明放在同一翻译单元还会形成两个重载，常见三实参调用出现歧义。

应保持一个完整声明来源：公共页给出与操作页一致的声明，或只展示调用表达式并链接完整签名。发现时的声明登记检查仅提取操作页，未覆盖公共页中的重复声明。

处理记录（2026-11-25）：R02已修正。检查全部21个公共页，仅OperandRoles重复声明操作；现改为调用示例并链接TADD声明。结构规范明确同名操作页为声明唯一维护位置，check_contracts.py增加跨页操作声明检查。角色协议和274条操作声明保持原值。R01、R03的后续处理见各条记录。

### R03 [P3] 前一轮反驳式措辞清理仍有遗漏

位置：[AtomicsRules](TileOpReference/AtomicsRules.md#原子性顺序与故障)、[IndexedMemoryRules](TileOpReference/IndexedMemoryRules.md#indexedbyterange)、[CommonTypes](TileOpReference/CommonTypes.md#有效维度与输出元数据)、IrregularRules与TTRI。

仍有“不要把…误读成…”、“不能把旧PTO-C文档…当成…”、“本手册不设…也不据此…”、“不应自行增加参数”。这些句子讨论读者误解或旧文档，未满足正文直接描述正确行为的编写要求。

应分别保留本请求预检与跨PE效果边界、两种range重载、结果描述符与库元数据规则、TCI必填起点和TTRI固定lower/对角线0，删除对应反驳叙述。类型禁止、非法参数及未定义行为约束继续保留。

处理记录（2026-11-25）：R03已修正。AtomicsRules、IndexedMemoryRules、CommonTypes、IrregularRules、TTRI和README改为直接描述行为，保留本请求预检、跨PE已提交效果、range重载、实际有效形状与库侧元数据、TCI必填起点、TTRI的lower及对角线0合同。

## 排除的候选问题

- 广播族按dst/Writer Part决定计算域：台账已明确该库绑定规则，固定TROWEXPANDADD合同要求完整矩形输入与结果有效几何一致；不能据此认定应一律改成按src0取维度。
- MX便利重载中的sa/sb、scale_vec/scale_mtx：这些参数仅存在于实际scale重载，角色写完整Tile成立；需要NoOperand分支的是完整Options槽。
- TSEL明确记录动态输出有效形状，属于CommonTypes允许的逐操作元数据更新约定，不能仅凭公共默认保持元数据判错。

## 验证结果与边界

- check_contracts.py：通过，274条声明及文档指纹一致。
- 六节结构与链接检查：通过，135个操作页。
- check_examples.py：通过，37个完整块、156个映射调用覆盖90条矩阵声明；仅声明/type mock。
- 全部登记声明的函数参数均在对应操作页参数区域出现，无空的必需章节。
- 本轮确认3组文档问题；未确认新的ISA数值行为错误。前一轮F07、F09的“全部修正”结论过宽，上述R01/R03是实际遗漏。台账closed表示已有证据登记，不覆盖这些新增的文档一致性发现。

## 逐页覆盖

下表记录本轮文档复核范围；“未新增发现”仅表示本轮未识别新的冲突。

| 页面 | 本轮结论 |
| --- | --- |
| [AtomicsRules](TileOpReference/AtomicsRules.md) | R03 |
| [BroadcastRules](TileOpReference/BroadcastRules.md) | 未新增发现 |
| [CommonTypes](TileOpReference/CommonTypes.md) | R03 |
| [CompareConvertRules](TileOpReference/CompareConvertRules.md) | 未新增发现 |
| [ElementwiseRules](TileOpReference/ElementwiseRules.md) | 未新增发现 |
| [FragmentGeometry](TileOpReference/FragmentGeometry.md) | 未新增发现 |
| [GMOV](TileOpReference/GMOV.md) | 未新增发现 |
| [IndexedMemoryRules](TileOpReference/IndexedMemoryRules.md) | R03 |
| [IrregularRules](TileOpReference/IrregularRules.md) | R03 |
| [LayoutRules](TileOpReference/LayoutRules.md) | 未新增发现 |
| [MGATHER](TileOpReference/MGATHER.md) | 未新增发现 |
| [MGATHER_ADD](TileOpReference/MGATHER_ADD.md) | 未新增发现 |
| [MGATHER_AND](TileOpReference/MGATHER_AND.md) | 未新增发现 |
| [MGATHER_CAS](TileOpReference/MGATHER_CAS.md) | 未新增发现 |
| [MGATHER_DEC](TileOpReference/MGATHER_DEC.md) | 未新增发现 |
| [MGATHER_EXCH](TileOpReference/MGATHER_EXCH.md) | 未新增发现 |
| [MGATHER_INC](TileOpReference/MGATHER_INC.md) | 未新增发现 |
| [MGATHER_MASK](TileOpReference/MGATHER_MASK.md) | 未新增发现 |
| [MGATHER_MAX](TileOpReference/MGATHER_MAX.md) | 未新增发现 |
| [MGATHER_MIN](TileOpReference/MGATHER_MIN.md) | 未新增发现 |
| [MGATHER_OR](TileOpReference/MGATHER_OR.md) | 未新增发现 |
| [MGATHER_XOR](TileOpReference/MGATHER_XOR.md) | 未新增发现 |
| [MSCATTER](TileOpReference/MSCATTER.md) | 未新增发现 |
| [MSCATTER_ADD](TileOpReference/MSCATTER_ADD.md) | 未新增发现 |
| [MSCATTER_AND](TileOpReference/MSCATTER_AND.md) | 未新增发现 |
| [MSCATTER_DEC](TileOpReference/MSCATTER_DEC.md) | 未新增发现 |
| [MSCATTER_INC](TileOpReference/MSCATTER_INC.md) | 未新增发现 |
| [MSCATTER_MASK](TileOpReference/MSCATTER_MASK.md) | 未新增发现 |
| [MSCATTER_MAX](TileOpReference/MSCATTER_MAX.md) | 未新增发现 |
| [MSCATTER_MIN](TileOpReference/MSCATTER_MIN.md) | 未新增发现 |
| [MSCATTER_OR](TileOpReference/MSCATTER_OR.md) | 未新增发现 |
| [MSCATTER_POPC](TileOpReference/MSCATTER_POPC.md) | 未新增发现 |
| [MSCATTER_XOR](TileOpReference/MSCATTER_XOR.md) | 未新增发现 |
| [MatrixRules](TileOpReference/MatrixRules.md) | 未新增发现 |
| [Numerics](TileOpReference/Numerics.md) | 未新增发现 |
| [OperandRoles](TileOpReference/OperandRoles.md) | R02 |
| [Options](TileOpReference/Options.md) | 未新增发现 |
| [Predicate](TileOpReference/Predicate.md) | 未新增发现 |
| [README](TileOpReference/README.md) | R03 |
| [Reader](TileOpReference/Reader.md) | 未新增发现 |
| [ReductionRules](TileOpReference/ReductionRules.md) | 未新增发现 |
| [ScalarRules](TileOpReference/ScalarRules.md) | 未新增发现 |
| [StorageBoundaries](TileOpReference/StorageBoundaries.md) | 未新增发现 |
| [TABS](TileOpReference/TABS.md) | 未新增发现 |
| [TADD](TileOpReference/TADD.md) | R02 |
| [TADDS](TileOpReference/TADDS.md) | 未新增发现 |
| [TAND](TileOpReference/TAND.md) | 未新增发现 |
| [TANDS](TileOpReference/TANDS.md) | 未新增发现 |
| [TCI](TileOpReference/TCI.md) | 未新增发现 |
| [TCI_2D](TileOpReference/TCI_2D.md) | 未新增发现 |
| [TCI_COL](TileOpReference/TCI_COL.md) | 未新增发现 |
| [TCI_ROW](TileOpReference/TCI_ROW.md) | 未新增发现 |
| [TCMP](TileOpReference/TCMP.md) | 未新增发现 |
| [TCMPS](TileOpReference/TCMPS.md) | 未新增发现 |
| [TCOLARGMAX](TileOpReference/TCOLARGMAX.md) | 未新增发现 |
| [TCOLARGMIN](TileOpReference/TCOLARGMIN.md) | 未新增发现 |
| [TCOLEXPAND](TileOpReference/TCOLEXPAND.md) | 未新增发现 |
| [TCOLEXPANDADD](TileOpReference/TCOLEXPANDADD.md) | 未新增发现 |
| [TCOLEXPANDDIV](TileOpReference/TCOLEXPANDDIV.md) | 未新增发现 |
| [TCOLEXPANDEXPDIF](TileOpReference/TCOLEXPANDEXPDIF.md) | 未新增发现 |
| [TCOLEXPANDMAX](TileOpReference/TCOLEXPANDMAX.md) | 未新增发现 |
| [TCOLEXPANDMIN](TileOpReference/TCOLEXPANDMIN.md) | 未新增发现 |
| [TCOLEXPANDMUL](TileOpReference/TCOLEXPANDMUL.md) | 未新增发现 |
| [TCOLEXPANDSUB](TileOpReference/TCOLEXPANDSUB.md) | 未新增发现 |
| [TCOLMAX](TileOpReference/TCOLMAX.md) | 未新增发现 |
| [TCOLMIN](TileOpReference/TCOLMIN.md) | 未新增发现 |
| [TCOLPROD](TileOpReference/TCOLPROD.md) | 未新增发现 |
| [TCOLSUM](TileOpReference/TCOLSUM.md) | 未新增发现 |
| [TCVT](TileOpReference/TCVT.md) | 未新增发现 |
| [TDIV](TileOpReference/TDIV.md) | 未新增发现 |
| [TDIVS](TileOpReference/TDIVS.md) | 未新增发现 |
| [TEXP](TileOpReference/TEXP.md) | 未新增发现 |
| [TEXPANDS](TileOpReference/TEXPANDS.md) | 未新增发现 |
| [TEXPDIF](TileOpReference/TEXPDIF.md) | 未新增发现 |
| [TFMA](TileOpReference/TFMA.md) | 未新增发现 |
| [TGATHER](TileOpReference/TGATHER.md) | 未新增发现 |
| [TGEMV](TileOpReference/TGEMV.md) | 未新增发现 |
| [TGEMV_ACC](TileOpReference/TGEMV_ACC.md) | 未新增发现 |
| [TGEMV_BIAS](TileOpReference/TGEMV_BIAS.md) | 未新增发现 |
| [TGEMV_MX](TileOpReference/TGEMV_MX.md) | 未新增发现 |
| [TGEMV_MX_ACC](TileOpReference/TGEMV_MX_ACC.md) | 未新增发现 |
| [TGEMV_MX_BIAS](TileOpReference/TGEMV_MX_BIAS.md) | 未新增发现 |
| [TGPR2T](TileOpReference/TGPR2T.md) | 未新增发现 |
| [TIMG2COL](TileOpReference/TIMG2COL.md) | 未新增发现 |
| [TLEA](TileOpReference/TLEA.md) | 未新增发现 |
| [TLOAD](TileOpReference/TLOAD.md) | 未新增发现 |
| [TLOAD_CUBE](TileOpReference/TLOAD_CUBE.md) | 未新增发现 |
| [TLOG](TileOpReference/TLOG.md) | 未新增发现 |
| [TMATMUL](TileOpReference/TMATMUL.md) | 未新增发现 |
| [TMATMUL_ACC](TileOpReference/TMATMUL_ACC.md) | 未新增发现 |
| [TMATMUL_BIAS](TileOpReference/TMATMUL_BIAS.md) | 未新增发现 |
| [TMATMUL_MX](TileOpReference/TMATMUL_MX.md) | 未新增发现 |
| [TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md) | R01 |
| [TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md) | R01 |
| [TMAX](TileOpReference/TMAX.md) | 未新增发现 |
| [TMAXS](TileOpReference/TMAXS.md) | 未新增发现 |
| [TMIN](TileOpReference/TMIN.md) | 未新增发现 |
| [TMINS](TileOpReference/TMINS.md) | 未新增发现 |
| [TMOV](TileOpReference/TMOV.md) | 未新增发现 |
| [TMOV_CUBE_TO_SHARED_ND](TileOpReference/TMOV_CUBE_TO_SHARED_ND.md) | 未新增发现 |
| [TMOV_SHARED_ND_TO_CUBE](TileOpReference/TMOV_SHARED_ND_TO_CUBE.md) | 未新增发现 |
| [TMUL](TileOpReference/TMUL.md) | 未新增发现 |
| [TMULS](TileOpReference/TMULS.md) | 未新增发现 |
| [TNEG](TileOpReference/TNEG.md) | 未新增发现 |
| [TNOT](TileOpReference/TNOT.md) | 未新增发现 |
| [TOR](TileOpReference/TOR.md) | 未新增发现 |
| [TORS](TileOpReference/TORS.md) | 未新增发现 |
| [TPACK](TileOpReference/TPACK.md) | 未新增发现 |
| [TPERMUTE](TileOpReference/TPERMUTE.md) | 未新增发现 |
| [TPREFETCH](TileOpReference/TPREFETCH.md) | 未新增发现 |
| [TRECIP](TileOpReference/TRECIP.md) | 未新增发现 |
| [TRELU](TileOpReference/TRELU.md) | 未新增发现 |
| [TREM](TileOpReference/TREM.md) | 未新增发现 |
| [TREMS](TileOpReference/TREMS.md) | 未新增发现 |
| [TROWARGMAX](TileOpReference/TROWARGMAX.md) | 未新增发现 |
| [TROWARGMIN](TileOpReference/TROWARGMIN.md) | 未新增发现 |
| [TROWEXPAND](TileOpReference/TROWEXPAND.md) | 未新增发现 |
| [TROWEXPANDADD](TileOpReference/TROWEXPANDADD.md) | 未新增发现 |
| [TROWEXPANDDIV](TileOpReference/TROWEXPANDDIV.md) | 未新增发现 |
| [TROWEXPANDEXPDIF](TileOpReference/TROWEXPANDEXPDIF.md) | 未新增发现 |
| [TROWEXPANDMAX](TileOpReference/TROWEXPANDMAX.md) | 未新增发现 |
| [TROWEXPANDMIN](TileOpReference/TROWEXPANDMIN.md) | 未新增发现 |
| [TROWEXPANDMUL](TileOpReference/TROWEXPANDMUL.md) | 未新增发现 |
| [TROWEXPANDSUB](TileOpReference/TROWEXPANDSUB.md) | 未新增发现 |
| [TROWMAX](TileOpReference/TROWMAX.md) | 未新增发现 |
| [TROWMIN](TileOpReference/TROWMIN.md) | 未新增发现 |
| [TROWPROD](TileOpReference/TROWPROD.md) | 未新增发现 |
| [TROWSUM](TileOpReference/TROWSUM.md) | 未新增发现 |
| [TRSQRT](TileOpReference/TRSQRT.md) | 未新增发现 |
| [TSCATTER](TileOpReference/TSCATTER.md) | 未新增发现 |
| [TSEL](TileOpReference/TSEL.md) | 未新增发现 |
| [TSELS](TileOpReference/TSELS.md) | 未新增发现 |
| [TSHL](TileOpReference/TSHL.md) | 未新增发现 |
| [TSHLS](TileOpReference/TSHLS.md) | 未新增发现 |
| [TSHR](TileOpReference/TSHR.md) | 未新增发现 |
| [TSHRS](TileOpReference/TSHRS.md) | 未新增发现 |
| [TSHUF](TileOpReference/TSHUF.md) | 未新增发现 |
| [TSQRT](TileOpReference/TSQRT.md) | 未新增发现 |
| [TSTORE](TileOpReference/TSTORE.md) | 未新增发现 |
| [TSTORE_ATOMIC_ADD](TileOpReference/TSTORE_ATOMIC_ADD.md) | 未新增发现 |
| [TSTORE_ATOMIC_AND](TileOpReference/TSTORE_ATOMIC_AND.md) | 未新增发现 |
| [TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md) | 未新增发现 |
| [TSTORE_ATOMIC_INC](TileOpReference/TSTORE_ATOMIC_INC.md) | 未新增发现 |
| [TSTORE_ATOMIC_MAX](TileOpReference/TSTORE_ATOMIC_MAX.md) | 未新增发现 |
| [TSTORE_ATOMIC_MIN](TileOpReference/TSTORE_ATOMIC_MIN.md) | 未新增发现 |
| [TSTORE_ATOMIC_OR](TileOpReference/TSTORE_ATOMIC_OR.md) | 未新增发现 |
| [TSTORE_ATOMIC_XOR](TileOpReference/TSTORE_ATOMIC_XOR.md) | 未新增发现 |
| [TSTORE_PART](TileOpReference/TSTORE_PART.md) | 未新增发现 |
| [TSUB](TileOpReference/TSUB.md) | 未新增发现 |
| [TSUBS](TileOpReference/TSUBS.md) | 未新增发现 |
| [TTRI](TileOpReference/TTRI.md) | R03 |
| [TUNPACK](TileOpReference/TUNPACK.md) | 未新增发现 |
| [TXOR](TileOpReference/TXOR.md) | 未新增发现 |
| [TXORS](TileOpReference/TXORS.md) | 未新增发现 |
| [TransportRules](TileOpReference/TransportRules.md) | 未新增发现 |
| [Writer](TileOpReference/Writer.md) | 未新增发现 |

## 三项修正验收

R01、R02、R03均已处理。274条操作声明和271条闭合记录保持原值，三条S-SUBMIT继续搁置。本次验证包括声明/指纹、全册结构、已标记示例及MX重载选择；示例与重载选择使用声明/type mock，未运行实现、ASL或硬件。
