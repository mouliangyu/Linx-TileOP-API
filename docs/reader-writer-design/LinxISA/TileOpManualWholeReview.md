# TileOP 全册复审（2026-11-24）

后续逐重载状态见 [核对表](TileOpContractLedger.md)，证据及闭合规则见 [核对流程](TileOpContractReview.md)。W01–W06 已关联到对应重载，正文修复与证据复核完成后更新台账。

## 范围与方法

本轮覆盖 TileOpReference 的 135 个操作页和 21 个公共、导航页。全量检查六节结构、参数名覆盖、示例调用、代码围栏和本地链接；逐页阅读操作语义及合法组合，按族交叉阅读公共合同，并检查声明和示例清单。复杂重载另行展开核对。覆盖表记录本轮范围，未列问题表示本轮未确认新问题。

审查结论分为手册内部可确认的问题和待进一步核对的设计项。ISA 对照使用已保存的 LinxISA 0.59.1 引用版本：PTO 规范 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`；源码对照使用 PTO-C 0.59 `ae2984c5fdfd1586cacf74ffa61ec3dd528ce5f8`。本轮对 TFMA、TCMPS、TSELS 额外查阅了该版本生成的指令合同。

结构检查通过（135 个操作页），示例未编译执行。此次全册文档审查尚不等于全部指令、全部重载与 ISA 逐字段验证。原始发现保留如下；正文修订与证据状态见 [合同核对更新](TileOpContractReviewUpdate.md)。

## 原始发现与修订依据

### W01：TFMA 缺少封闭的 dtype 集合及已定义的数值行为

[TFMA](TileOpReference/TFMA.md) 将类型要求交给 [ElementwiseRules](TileOpReference/ElementwiseRules.md#tfma三个输入)，后者只要求四个载体 dtype 一致。前面的双输入算术集合包含 U32、S16、TF32 等，未明确它与 TFMA 的关系。

固定 ISA 的 TFMA 明确仅允许 FP64、S64、U64、FP16、FP32、BF16。读者用四个同形 U32 Tile 调用时，现有条文无法给出正确的合法性判断。此外 ISA 已明确浮点一次融合舍入、整数按元素位宽取模，手册仍只给出乘加数学公式和泛化的数值保留说明。

修订：在 TFMA 唯一合同位置列出六种类型、M16/M32 的 b64 限制及融合/取模行为，操作页精确引用。依据：[TFMA.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl)。

### W02：TCMPS 的 Predicate 输出重载缺少类型合同

[TCMPS](TileOpReference/TCMPS.md#合法组合与限制) 完整列出了 GPR 形式，却仅为 Predicate 形式链接 [Predicate](TileOpReference/Predicate.md)。该公共页定义存储与 basis，没有定义每个比较操作的 dtype 集合；CompareConvertRules 又回链 TCMPS。因此 Predicate 重载的类型查询链未闭合。

例如 CUBE E4M3 输入的 Predicate 输出比较与 GPR 输出比较，合法类型范围不同，不能沿用 GPR 的表。固定 ISA 为 PredicateCell 形式明确列出了 E4M3/E5M2/S8 等类型。

修订：分别列出 RowMajor Predicate、CUBE PredicateCell、GPR 的类型和布局合同；保留公共 Predicate 页作为存储定义。依据：[TCMPS.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TCMPS.asl)。

### W03：TAND/TOR/TXOR 的 U8 条款作用域错误

三页的重载表同时包含 Numeric/Numeric 和谓词组合，随后统一写“各输入按本页 U8 几何合同校验”。这与普通整数重载及本页 U32 示例冲突。后文 PredicateCell 专节虽限定了范围，页首仍给出了无条件要求。

修订：普通数值重载使用其数值 dtype 几何；包含 Predicate 的重载使用 U8 存储几何。三页一起修订，并将专节中遗留的“按下表选择”改为明确链接页首表。

### W04：矩阵 Options 有编码表，缺少计算合同

[Options](TileOpReference/Options.md#descriptor-与-vector-参数) 列出量化 scale、offset、shift 字段，[Numerics](TileOpReference/Numerics.md) 没有补齐其运算。读者即使持有合法 FP19 编码，也无法根据手册计算 QF322S8Pre 的结果：scale、offset、舍入、钳制的先后次序未给出。SHIFT 模式也只有字段位置。

同样缺少量化与激活的流水顺序、各模式的舍入/溢出规则和可查询的固定规范链接。该缺口影响全部 TMATMUL/TGEMV 后处理调用。

修订：为各 mode 家族列出输入 accumulator、输出 dtype、计算公式、舍入及饱和规则；定义与激活、辅助规约的执行顺序。需要 numeric profile 的部分链接到具体规范。至少给出一个非单位 scale、非零 offset 的数值例子，避免仅验证位域拼装。

### W05：TMATMUL_MX 的 groupM 与缺省 scale 组合无法照手册写完整调用

[TMATMUL_MX](TileOpReference/TMATMUL_MX.md)、[TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md)、[TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md) 的 groupM 重载都保留两个 scale 实参；省略一侧或两侧 scale 的便利重载没有 groupM。

MatrixRules 同时允许 FP16/BF16 无 scale，以及 Local-A/Shared-B 显式 groupM。以 FP16 的 Local A、Shared B 和核级 groupM=20 为例，读者无法从已公布接口构造无 scale 的调用。设置 ScaleMask=0 后，签名仍要求两个实参，手册未定义应填的占位对象。

源码含内部 `pto_matmul_detail::NoScaleOperand`；Options 中的 `fixp::NoOperand` 用于后处理可选 operand，两者不能直接等同。源码细节不构成公开调用合同。

修订：为 groupM 组合补充无 scale/单侧 scale 重载，或定义公开的 scale 占位值与关闭位的参数规则。三种 TMATMUL_MX 入口同步，并提供 Local-A/Shared-B 示例。

### W06：专用合同仍存在多份完整定义

按结构规范应有唯一归属，但下列页面仍重复维护专用合同：

| 合同 | 重复位置 |
| --- | --- |
| TCVT 舍入表、round-integral、几何 | TCVT、CompareConvertRules；Numerics 另有舍入定义 |
| TPACK/TUNPACK 控制字段与输出公式 | 同名操作页、LayoutRules |
| TPERMUTE 查表几何 | TPERMUTE、LayoutRules |
| TGATHER/TSCATTER 专用行为 | 同名操作页、IrregularRules |
| GMOV peer 与 collective 规则 | GMOV、TransportRules |
| 单片 SizeCode 容量 | Reader、Writer、FragmentGeometry |

其中 TCVT 的 RMode 表、TPACK/TUNPACK 的 control 字段仍放在“合法组合与限制”。这使参数查询依赖读完整页，也让后续修改容易只更新一份。TSHUF 已完成的归属整理应同样应用到这些页面。

修订：共享规则留公共页，操作专有字段和公式留同名页；其他位置使用精确链接。结构验收除标题顺序外，增加重复规范段落检查及归属人工检查。

## 待核对项

- **TPREFETCH 的公开范围。** 声明接受 GlobalMemoryView，专节限定静态 global_tensor 本体并排除 view，而 CommonTypes 将 global_tensor 本身及 subview 都定义为视图。需要明确静态形状/步长是否为新库有意保留的限制，并将约束写进可判断的接口合同。暂不据此扩展动态支持。
- **TSELS 的封闭类型集合。** 页内与 ScalarRules 仅写 dtype 相同、布局匹配。需要列明各布局支持类型，并决定新库是否保留同 dtype 限定；固定 ISA 允许部分等宽原始位载体。ISA 的 GPR 形式不自动意味着本库必须新增该重载。
- **Shared Writer 的身份构造。** 当前正文给出了跨 PE 绑定同一 Sx 的 lowering 合同；多个并存 Writer 和分支创建时如何标识同一协作输出，仍需实现设计验证。此次不据此新增用户限制。

## 逐页覆盖记录

下表的“全册检查”包含结构、参数名和示例清单扫描，以及操作语义/合法组合与公共规则交叉阅读；“公共合同”表示公共页交叉阅读。单项 ISA 深核仅对上文明确给出依据的条款成立。问题栏使用本轮编号，待核对项保持单独状态。

| 页面 | 本轮覆盖 | 问题或待核对项 |
| --- | --- | --- |
| [AtomicsRules](TileOpReference/AtomicsRules.md) | 公共合同/导航 | 本轮未确认新问题 |
| [BroadcastRules](TileOpReference/BroadcastRules.md) | 公共合同/导航 | 本轮未确认新问题 |
| [CommonTypes](TileOpReference/CommonTypes.md) | 公共合同/导航 | 本轮未确认新问题 |
| [CompareConvertRules](TileOpReference/CompareConvertRules.md) | 公共合同/导航 | W02、W06 |
| [ElementwiseRules](TileOpReference/ElementwiseRules.md) | 公共合同/导航 | W01、W03 |
| [FragmentGeometry](TileOpReference/FragmentGeometry.md) | 公共合同/导航 | W06 |
| [GMOV](TileOpReference/GMOV.md) | 全册检查 | W06 |
| [IndexedMemoryRules](TileOpReference/IndexedMemoryRules.md) | 公共合同/导航 | 本轮未确认新问题 |
| [IrregularRules](TileOpReference/IrregularRules.md) | 公共合同/导航 | W06 |
| [LayoutRules](TileOpReference/LayoutRules.md) | 公共合同/导航 | W06 |
| [MGATHER](TileOpReference/MGATHER.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_ADD](TileOpReference/MGATHER_ADD.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_AND](TileOpReference/MGATHER_AND.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_CAS](TileOpReference/MGATHER_CAS.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_DEC](TileOpReference/MGATHER_DEC.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_EXCH](TileOpReference/MGATHER_EXCH.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_INC](TileOpReference/MGATHER_INC.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_MASK](TileOpReference/MGATHER_MASK.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_MAX](TileOpReference/MGATHER_MAX.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_MIN](TileOpReference/MGATHER_MIN.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_OR](TileOpReference/MGATHER_OR.md) | 全册检查 | 本轮未确认新问题 |
| [MGATHER_XOR](TileOpReference/MGATHER_XOR.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER](TileOpReference/MSCATTER.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_ADD](TileOpReference/MSCATTER_ADD.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_AND](TileOpReference/MSCATTER_AND.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_DEC](TileOpReference/MSCATTER_DEC.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_INC](TileOpReference/MSCATTER_INC.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_MASK](TileOpReference/MSCATTER_MASK.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_MAX](TileOpReference/MSCATTER_MAX.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_MIN](TileOpReference/MSCATTER_MIN.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_OR](TileOpReference/MSCATTER_OR.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_POPC](TileOpReference/MSCATTER_POPC.md) | 全册检查 | 本轮未确认新问题 |
| [MSCATTER_XOR](TileOpReference/MSCATTER_XOR.md) | 全册检查 | 本轮未确认新问题 |
| [MatrixRules](TileOpReference/MatrixRules.md) | 公共合同/导航 | W04、W05 |
| [Numerics](TileOpReference/Numerics.md) | 公共合同/导航 | W04、W06 |
| [OperandRoles](TileOpReference/OperandRoles.md) | 公共合同/导航 | 本轮未确认新问题 |
| [Options](TileOpReference/Options.md) | 公共合同/导航 | W04 |
| [Predicate](TileOpReference/Predicate.md) | 公共合同/导航 | W02 |
| [README](TileOpReference/README.md) | 公共合同/导航 | 本轮未确认新问题 |
| [Reader](TileOpReference/Reader.md) | 公共合同/导航 | W06 |
| [ReductionRules](TileOpReference/ReductionRules.md) | 公共合同/导航 | 本轮未确认新问题 |
| [ScalarRules](TileOpReference/ScalarRules.md) | 公共合同/导航 | TSELS 类型集合待核对 |
| [StorageBoundaries](TileOpReference/StorageBoundaries.md) | 公共合同/导航 | Shared 身份待验证 |
| [TABS](TileOpReference/TABS.md) | 全册检查 | 本轮未确认新问题 |
| [TADD](TileOpReference/TADD.md) | 全册检查 | 本轮未确认新问题 |
| [TADDS](TileOpReference/TADDS.md) | 全册检查 | 本轮未确认新问题 |
| [TAND](TileOpReference/TAND.md) | 全册检查 | W03 |
| [TANDS](TileOpReference/TANDS.md) | 全册检查 | 本轮未确认新问题 |
| [TCI](TileOpReference/TCI.md) | 全册检查 | 本轮未确认新问题 |
| [TCI_2D](TileOpReference/TCI_2D.md) | 全册检查 | 本轮未确认新问题 |
| [TCI_COL](TileOpReference/TCI_COL.md) | 全册检查 | 本轮未确认新问题 |
| [TCI_ROW](TileOpReference/TCI_ROW.md) | 全册检查 | 本轮未确认新问题 |
| [TCMP](TileOpReference/TCMP.md) | 全册检查 | 本轮未确认新问题 |
| [TCMPS](TileOpReference/TCMPS.md) | 全册检查 | W02 |
| [TCOLARGMAX](TileOpReference/TCOLARGMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLARGMIN](TileOpReference/TCOLARGMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPAND](TileOpReference/TCOLEXPAND.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDADD](TileOpReference/TCOLEXPANDADD.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDDIV](TileOpReference/TCOLEXPANDDIV.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDEXPDIF](TileOpReference/TCOLEXPANDEXPDIF.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDMAX](TileOpReference/TCOLEXPANDMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDMIN](TileOpReference/TCOLEXPANDMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDMUL](TileOpReference/TCOLEXPANDMUL.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLEXPANDSUB](TileOpReference/TCOLEXPANDSUB.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLMAX](TileOpReference/TCOLMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLMIN](TileOpReference/TCOLMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLPROD](TileOpReference/TCOLPROD.md) | 全册检查 | 本轮未确认新问题 |
| [TCOLSUM](TileOpReference/TCOLSUM.md) | 全册检查 | 本轮未确认新问题 |
| [TCVT](TileOpReference/TCVT.md) | 全册检查 | W06 |
| [TDIV](TileOpReference/TDIV.md) | 全册检查 | 本轮未确认新问题 |
| [TDIVS](TileOpReference/TDIVS.md) | 全册检查 | 本轮未确认新问题 |
| [TEXP](TileOpReference/TEXP.md) | 全册检查 | 本轮未确认新问题 |
| [TEXPANDS](TileOpReference/TEXPANDS.md) | 全册检查 | 本轮未确认新问题 |
| [TEXPDIF](TileOpReference/TEXPDIF.md) | 全册检查 | 本轮未确认新问题 |
| [TFMA](TileOpReference/TFMA.md) | 全册检查 | W01 |
| [TGATHER](TileOpReference/TGATHER.md) | 全册检查 | W06 |
| [TGEMV](TileOpReference/TGEMV.md) | 全册检查 | 本轮未确认新问题 |
| [TGEMV_ACC](TileOpReference/TGEMV_ACC.md) | 全册检查 | 本轮未确认新问题 |
| [TGEMV_BIAS](TileOpReference/TGEMV_BIAS.md) | 全册检查 | 本轮未确认新问题 |
| [TGEMV_MX](TileOpReference/TGEMV_MX.md) | 全册检查 | 本轮未确认新问题 |
| [TGEMV_MX_ACC](TileOpReference/TGEMV_MX_ACC.md) | 全册检查 | 本轮未确认新问题 |
| [TGEMV_MX_BIAS](TileOpReference/TGEMV_MX_BIAS.md) | 全册检查 | 本轮未确认新问题 |
| [TGPR2T](TileOpReference/TGPR2T.md) | 全册检查 | 本轮未确认新问题 |
| [TIMG2COL](TileOpReference/TIMG2COL.md) | 全册检查 | 本轮未确认新问题 |
| [TLEA](TileOpReference/TLEA.md) | 全册检查 | 本轮未确认新问题 |
| [TLOAD](TileOpReference/TLOAD.md) | 全册检查 | 本轮未确认新问题 |
| [TLOAD_CUBE](TileOpReference/TLOAD_CUBE.md) | 全册检查 | 本轮未确认新问题 |
| [TLOG](TileOpReference/TLOG.md) | 全册检查 | 本轮未确认新问题 |
| [TMATMUL](TileOpReference/TMATMUL.md) | 全册检查 | 本轮未确认新问题 |
| [TMATMUL_ACC](TileOpReference/TMATMUL_ACC.md) | 全册检查 | 本轮未确认新问题 |
| [TMATMUL_BIAS](TileOpReference/TMATMUL_BIAS.md) | 全册检查 | 本轮未确认新问题 |
| [TMATMUL_MX](TileOpReference/TMATMUL_MX.md) | 全册检查 | W05 |
| [TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md) | 全册检查 | W05 |
| [TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md) | 全册检查 | W05 |
| [TMAX](TileOpReference/TMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TMAXS](TileOpReference/TMAXS.md) | 全册检查 | 本轮未确认新问题 |
| [TMIN](TileOpReference/TMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TMINS](TileOpReference/TMINS.md) | 全册检查 | 本轮未确认新问题 |
| [TMOV](TileOpReference/TMOV.md) | 全册检查 | 本轮未确认新问题 |
| [TMOV_CUBE_TO_SHARED_ND](TileOpReference/TMOV_CUBE_TO_SHARED_ND.md) | 全册检查 | 本轮未确认新问题 |
| [TMOV_SHARED_ND_TO_CUBE](TileOpReference/TMOV_SHARED_ND_TO_CUBE.md) | 全册检查 | 本轮未确认新问题 |
| [TMUL](TileOpReference/TMUL.md) | 全册检查 | 本轮未确认新问题 |
| [TMULS](TileOpReference/TMULS.md) | 全册检查 | 本轮未确认新问题 |
| [TNEG](TileOpReference/TNEG.md) | 全册检查 | 本轮未确认新问题 |
| [TNOT](TileOpReference/TNOT.md) | 全册检查 | 本轮未确认新问题 |
| [TOR](TileOpReference/TOR.md) | 全册检查 | W03 |
| [TORS](TileOpReference/TORS.md) | 全册检查 | 本轮未确认新问题 |
| [TPACK](TileOpReference/TPACK.md) | 全册检查 | W06 |
| [TPERMUTE](TileOpReference/TPERMUTE.md) | 全册检查 | W06 |
| [TPREFETCH](TileOpReference/TPREFETCH.md) | 全册检查 | 公开范围待核对 |
| [TRECIP](TileOpReference/TRECIP.md) | 全册检查 | 本轮未确认新问题 |
| [TRELU](TileOpReference/TRELU.md) | 全册检查 | 本轮未确认新问题 |
| [TREM](TileOpReference/TREM.md) | 全册检查 | 本轮未确认新问题 |
| [TREMS](TileOpReference/TREMS.md) | 全册检查 | 本轮未确认新问题 |
| [TROWARGMAX](TileOpReference/TROWARGMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TROWARGMIN](TileOpReference/TROWARGMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPAND](TileOpReference/TROWEXPAND.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDADD](TileOpReference/TROWEXPANDADD.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDDIV](TileOpReference/TROWEXPANDDIV.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDEXPDIF](TileOpReference/TROWEXPANDEXPDIF.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDMAX](TileOpReference/TROWEXPANDMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDMIN](TileOpReference/TROWEXPANDMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDMUL](TileOpReference/TROWEXPANDMUL.md) | 全册检查 | 本轮未确认新问题 |
| [TROWEXPANDSUB](TileOpReference/TROWEXPANDSUB.md) | 全册检查 | 本轮未确认新问题 |
| [TROWMAX](TileOpReference/TROWMAX.md) | 全册检查 | 本轮未确认新问题 |
| [TROWMIN](TileOpReference/TROWMIN.md) | 全册检查 | 本轮未确认新问题 |
| [TROWPROD](TileOpReference/TROWPROD.md) | 全册检查 | 本轮未确认新问题 |
| [TROWSUM](TileOpReference/TROWSUM.md) | 全册检查 | 本轮未确认新问题 |
| [TRSQRT](TileOpReference/TRSQRT.md) | 全册检查 | 本轮未确认新问题 |
| [TSCATTER](TileOpReference/TSCATTER.md) | 全册检查 | W06 |
| [TSEL](TileOpReference/TSEL.md) | 全册检查 | 本轮未确认新问题 |
| [TSELS](TileOpReference/TSELS.md) | 全册检查 | 类型集合待核对 |
| [TSHL](TileOpReference/TSHL.md) | 全册检查 | 本轮未确认新问题 |
| [TSHLS](TileOpReference/TSHLS.md) | 全册检查 | 本轮未确认新问题 |
| [TSHR](TileOpReference/TSHR.md) | 全册检查 | 本轮未确认新问题 |
| [TSHRS](TileOpReference/TSHRS.md) | 全册检查 | 本轮未确认新问题 |
| [TSHUF](TileOpReference/TSHUF.md) | 全册检查 | 本轮未确认新问题 |
| [TSQRT](TileOpReference/TSQRT.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE](TileOpReference/TSTORE.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_ADD](TileOpReference/TSTORE_ATOMIC_ADD.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_AND](TileOpReference/TSTORE_ATOMIC_AND.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_INC](TileOpReference/TSTORE_ATOMIC_INC.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_MAX](TileOpReference/TSTORE_ATOMIC_MAX.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_MIN](TileOpReference/TSTORE_ATOMIC_MIN.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_OR](TileOpReference/TSTORE_ATOMIC_OR.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_ATOMIC_XOR](TileOpReference/TSTORE_ATOMIC_XOR.md) | 全册检查 | 本轮未确认新问题 |
| [TSTORE_PART](TileOpReference/TSTORE_PART.md) | 全册检查 | 本轮未确认新问题 |
| [TSUB](TileOpReference/TSUB.md) | 全册检查 | 本轮未确认新问题 |
| [TSUBS](TileOpReference/TSUBS.md) | 全册检查 | 本轮未确认新问题 |
| [TTRI](TileOpReference/TTRI.md) | 全册检查 | 本轮未确认新问题 |
| [TUNPACK](TileOpReference/TUNPACK.md) | 全册检查 | W06 |
| [TXOR](TileOpReference/TXOR.md) | 全册检查 | W03 |
| [TXORS](TileOpReference/TXORS.md) | 全册检查 | 本轮未确认新问题 |
| [TransportRules](TileOpReference/TransportRules.md) | 公共合同/导航 | W06；TPREFETCH 待核对 |
| [Writer](TileOpReference/Writer.md) | 公共合同/导航 | W06；Shared 身份待验证 |
