# TileOP 合同核对证据

## LinxISA 规范裁定（当前）

本手册以 LinxISA 0.59.1 的[规范锁定文件](https://github.com/LinxISA/linx-isa/blob/7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27/isa/v0.59/pto-spec.lock.json)及其引用的操作条款为依据。数值行为采用锁定的 [pto-hardware-numeric-0.59.1-ieee-v1](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/hardware-conformance-profile.json)。各操作的专用类型、布局和编码条款与公共数值规则共同构成接口合同。Reader/Writer 和便利重载属于库设计，其参数映射按各操作页说明。

锁定的硬件 profile SHA-256 为 `843d4c2c76823af57dc80f4b134c00e0166c0ba262f6924585854bdc44214325`，已与下载文件核对一致。其 reference_model_relation 将 pto-v0 定位为 raw-carrier 参考测试 profile。下文保留的原始 Word 运算推导用于记录该模型的测试覆盖；矩阵接口的数值合同由 hardware profile 的 matrix/arithmetic 条款确定。此前 M-NUM 对90条矩阵重载的阻塞结论在本批撤销。

以下历史章节中涉及 M-NUM、95条未闭合及“需对齐模型才能关闭”的结论由本节和当前台账替代。TCVT仍需完成完整接受类型域到公开配对表的核实；Shared继续核对每PE单次加入generation条款与库多阶段接口的映射。实际编译、ASL和硬件运行状态分别保留。


本页保存跨重载共享的查证路径。逐重载的结论、适用分支、公共依赖和状态以 [台账](TileOpContractLedger.md) 为准。验证方法为声明审阅与固定规范推导；编译及硬件运行分别记录。

## 剩余五条重载复核

TCVT：逐项核对已分配类型、HardwareTCVTTypePairSupported及HardwareTCVTRoundingModeSupported。普通集合含11种浮点与10种整数类型，集合内配对遵循公共数值规范；E8M0、E6M2、RCPE6M2、E2M1X2/E1M2X2采用专用配对表。类型表已补齐，类型与语义维度闭合。

Shared→Local ND TMOV：按[TMOV](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TMOV.asl)的payload/definedness复制合同处理完整目标；库Writer形式明确展开为Shared读取到完整Local Part、Local TMOV写入Writer两步。局部临时值承载片段形状，Local B.ASSEMBLE承载parent分配及阶段。完整例给出16×16 parent、两个8×16 Part、0/4 CELL偏移与期望结果，几何、语义和示例设计维度闭合。完整实现编译和运行验证保持未执行。

Shared生产三条：已核实[B.ASSEMBLE](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/operands/B.ASSEMBLE.asl)的source-form B.IOS SizeCode=0 continuation，以及[PTO-B-ASSEMBLE-SHARED-GENERATION-001](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/shared-generation.asl)的每PE一次加入、同ordinal/metadata、完整无重叠覆盖和原子发布。跨调用点阶段序列需要进一步明确每次请求与一次参与者arrival的关系；当前保持S-SUBMIT三条映射缺口。该结论依据规范条款，下一步需明确该关系后再完成多阶段库映射。

本节为当前结论，下方历史诊断按各自审阅时间保留。正文使用规范行为及库展开合同。

## 固定版本

PTO 规范固定于 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，由 LinxISA 0.59.1（`7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27`）引用。下列源码链接均固定到该 PTO 提交。PTO-C 基线为 `ae2984c5fdfd1586cacf74ffa61ec3dd528ce5f8`。C++ 角色协议、借用、默认参数和便利重载属于本库设计，分别对照指令能表达的行为。

## 公共依赖

公共依赖按范围记录。`C01.local` 等带后缀的结论只闭合 Local 分支；Shared、矩阵角色及其专用几何分别核对。范围和逐项推导保存于 JSON 的 `public_contracts`。

- C01.local：Tile 模板默认值、静态/动态 getter、CUBE 别名、容量。M32 FP32 的32×4片段为512 B，即4 CELL。
- C02：GM 视图保留 const、步长和底层存储生命周期。64×128、stride160 的 `(16,32,32,32)` 子视图起点2592、末元素7583，均以元素计。
- C03.local：reinterpret_tile 借用输入，等宽 carrier 与操作 dtype 分别检查；先 Reader 选择 backing Part，再解释类型。
- C04.local：Reader 的偏移单位为128 B，单片 SizeCode 1..10；32×8 FP32 parent 中32×4 Part偏移0或4合法，5越界。空迭代、重复读取及提前退出可用。
- C05.local：Writer 首次调用保存真实 parent，后续阶段绑定同一目标，finish交出该 parent。单片选single，多片按first/middle/last推进；提前退出行为未定义。依据 [range-modifiers](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/range-modifiers.asl) 与库状态机。编译器顺序实现单独验证。
- C11.local：Numeric 输入/输出与 Predicate、Shared、GM 角色分开；临时片段保存 parent 借用，普通 Tile 输入使用已定义左值。

这些局部闭合支持已核对 Local 操作，公共清单的完整项仍须包含其余存储和操作分支。

## 逐元素、标量、归约与广播

61条重载的八项结论分别指向各自固定操作 ASL、操作页及公共规则。关键执行路径：

| 合同 | 固定源码与核对点 |
| --- | --- |
| 整数/浮点算术 | [elementwise.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/elementwise.asl)：TileProfileBinaryWithFlags、TileIntegerDivRemValue、TileSignedModulo；DIV向零截断，REM为floor modulo |
| MIN/MAX | [minmax.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/minmax.asl)：调用格式profile，NaN及符号零遵守对应选择规则 |
| 类型解释 | [dtype-layout.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/dtype-layout.asl)：操作类型/等宽carrier/布局独立校验 |
| 标量 | 各操作 B.IOR.RegSrc0 的低元素位宽；TEXPANDS 从目标取维度，其余从输入取维度 |
| 归约 | 各操作固定 ASL ordering/state_effects：SUM/PROD索引递增左折叠，逐步操作dtype；ARG保留最早获胜索引；ROW CUBE输出保持源物理列 |
| 广播 | 各操作合法性与执行：ROW按字节slot选择列，COL读第0行；COPY原始位，EXPDIF允许FP16/BF16→FP32 |

边界例包括 U32加法回绕、S32最小值NEG、count33的U32移位、负数REM、FP32数学函数特殊值、归约单元素/ARG平局、ROW偏移2与非法偏移1、COL多行源。边界结果由规范推导，完整函数保留于操作页。

TSUB/TMUL/TDIV/TREM 的指令注释部分仍只列Pad；固定版本的操作元数据 `datr_contract.allowed_nonzero_fields` 含 Layout，生成器据此构造合法性检查。手册按实际布局检查保留CUBE分支，审查时同时读取元数据和dispatch。

## 索引内存与原子族

23个操作的46条声明分别核对有/无range。每页都有独立完整函数和输入初值、结果；重复执行原子函数前须恢复初值。

| 合同 | 固定源码与核对点 |
| --- | --- |
| dtype、布局、packed | [indexed-layout.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/indexed-layout.asl)：index为S/U32/64；普通传输允许packed4整字节，payload列数两倍；物理几何独立 |
| mask | [predicate-carriers.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)：IndexedTLSUPredicateDescriptorLegal、IndexedTLSUPredicateValuesLegal接受Numeric U8以及CUBE PredicateCell，检查0/1 |
| gather | [gather-scatter-values.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gather-scatter-values.asl)：先probe，再构造完整物理结果并标为定义 |
| padding | [elements.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/definedness/elements.asl)：TilePadValueForDataType的Null/Zero返回零位模式；gather调用方明确标记defined |
| scatter | [gather-scatter.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gather-scatter.asl)：所有地址probe与源值保存后调用CommitIndexedScatterTransactions；重复地址赢家未指定 |
| 原子类型/数值 | [gm-atom-red.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red.asl)：GMAtomicOperationDataTypeLegal、GMReductionOperationDataTypeLegal、GMIncValue、GMDecValue、GMFloatingAddPTX；ADD不含S64，CAS含U16 |
| 原子执行 | [gm-atom-red-execution.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red-execution.asl)：探测所有读写地址后提交单lane事件，最后发布旧值；POPC逐地址加1 |
| 原子独立几何 | [gm-atom-red-values.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red-values.asl)：same dtype/effective shape，同布局、独立物理容量 |
| 范围编码 | [indexed-tlsu-range-schema.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/indexed-tlsu-range-schema.asl)及各操作legality：RegSrc1/2的selector区分有无描述符，S64闭区间起点包络由软件保证覆盖且无回绕 |

规范推导：U32偏移0,4,…,124对应128 B；反序范围在本请求效果前fault；32个重复POPC从5得到37；CAS旧值6与expected5不等时返回6且保持6。MASK Numeric与CUBE PredicateCell均有示例。ExecutionMask扩展保持原先暂缓的接口范围。

## 比较与选择的来源差异

TCMPS/TSEL 指令注释中的八位GPR域仍有U8-only文字。固定版本 `TileCubePredicateGPRDataTypeSupported`、最终 [comparison-schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/comparison-schema.asl)、[tile-scalar-schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tile-scalar-schema.asl)及八位测试覆盖U8/S8/E4M3/E5M2。手册已按实际执行路径补齐。这一修复只证明该类型与编码分支，其余维度继续各自核对。

## Local 工具操作

逐项核对 TCI/TCI_2D/TCI_ROW/TCI_COL、TTRI、TLEA、TPACK/TUNPACK、TPERMUTE、TSHUF、TGPR2T 的11条声明。各自 dtype、几何、控制字和边界推导见逐重载记录及操作页。

- [layout-rearrangement.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/layout-rearrangement.asl)：PACK/UNPACK 的原始字节选取、尾word与U64偶数word；PERMUTE局部字节表；SHUF分段和控制值。
- [rearrangement-values.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/rearrangement-values.asl)：各输出先在临时值中构造，再发布；PACK/UNPACK/PERMUTE/SHUF 使用 `TileWithPadding(..., TilePad_Null)`。
- [generation.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/generation.asl)：序列按目标位宽回绕，二维行列步长独立。
- [lea.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/lea.asl)：先按源符号扩展，再乘元素字节数，保留低64位。
- [predicate-carriers-value.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/predicate-carriers-value.asl)：TGPR2T 的GPR plane映射及固定U8输出。

验证范围为规范和声明审阅；完整函数及边界结果均由上述固定版本推导，编译和硬件运行未执行。

## MX 重载选择

旧单scale声明在scale具有Right角色时同时匹配两条便利重载，Clang C++20诊断 `call to TMATMUL_MX is ambiguous`。所有72条MX声明现以primary dtype推导的 `mx_scale_mask_v` 约束选择；GEMV按Vec、Mtx顺序查询。

运行 `python clang/docs/LinxISA/audit/check_mx_overloads.py`，使用手册实际声明及模拟角色/类型，覆盖396个选择案例：mask0/1/2/3、Attr/Options、scale的Vec/Left/Right角色，以及Matrix的Local/Shared组合。此测试验证声明消歧；真实库实例化、lowering及硬件数值仍分别验证。

## Local 索引重排

TSCATTER源与索引形状一致，目标行数独立；固定 [合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/indexed-rearrangement.asl)及 [2行输入到4行输出测试](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/tile/irregular-and-complex/layout/TSCATTER/tile-exec-tscatter-rows-001.asl)直接支持这一点。重复目标在发布前拒绝。原手册“全部同有效行数”已撤销。

TGATHER的生成器在 [generate-asl-decoders](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/scripts/generate-asl-decoders) 将操作路由到 `TileOperandsLegal_TGATHERToValue`/`TGATHERToValue`；该路径明确接受CUBE输出，而source/index仍通过普通 `TileDescriptorLegal`。直接旧值入口的目标限制与新值入口有差异，手册按实际新值路由说明。TSCATTER保留其直接合法性路径。raw零初始化依据 [indexed-rearrangement.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/indexed-rearrangement.asl)，E8M0的raw零与数学零分别解释。

## 规则地址原子存储

8个操作各有Local、Shared、Local谓词三种声明，合计24条。各页补齐三类完整函数及谓词反选、mask0、INC/DEC边界。类型/算术以 `GMReductionOperationDataTypeLegal` / `GMReductionResult` 为准，ADD排除S64，浮点ADD采用固定RN-even与渐进下溢。

Local B.IOT和Shared B.IOS共用三位PEMode解码，实际可表达的mask均为0、1、2、4、8、12、14、15。操作helper接收四位语义mask，其参数域还须与指令可编码集合取交集。mask默认15是库选择。

关于故障范围，TSTORE指令注释的“complete selected-PE footprint”与实际执行存在差异。固定 `ExecuteBundleAtomicTSTOREOperation` 仅处理当前选中PE，`TSTOREAtomic` 在该PE内调用 `PreflightAtomicTStore`；原生测试明确规定Shared未发布先等待，发布后PE0的地址4096失败，而PE1对0x200的原子加仍成功。因此手册将预检范围明确为本PE请求，其他PE已提交效果保持。请求重入使用捕获的地址、源snapshot及generation，避免重复提交坐标；源last-use由完成路径释放。

证据：[tlsu-atomic-tstore.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl)、[atomic-tstore.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/atomic-tstore.asl)、[gm-atom-red.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red.asl)、[block-exec-tstore-atomic-shared-fault-001.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/block/model/dispatch/tlsu-atomic-tstore/block-exec-tstore-atomic-shared-fault-001.asl)。测试源码经过审阅，本轮没有运行该ASL测试或真实硬件。

## 指令编码与模型容量

最终可调用合同同时受操作语义与指令字段约束。固定 [PEMaskOfPEMode](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/schema/bundle-encoding.asl)将8种PEMode映射为0、8、4、2、1、12、14、15；B.IOT和B.IOS共用该映射。GMOV等操作注释中的任意非零四位mask还须经过此编码限制。

[LocalTileSizeCodeIsLegal](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/state/descriptors.asl)仅允许1..10，B.IOT完整Local目标和INIT parent均走这一检查；Local单PE完整值和Part上限均为64KiB。Shared使用1..12，上限256KiB。模型TileInfo的262144容量类型上界不直接构成Local指令的可分配上界。原先手册混用了两层容量，已修正公共合同和所有受影响操作/证据；现有示例均在64KiB内。

## 矩阵来源差异

固定 [cube-tmatmul.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/cube-tmatmul.asl)在M=1的GEMV分支后统一调用 [matrix-operands.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl)。`TileMatrixLocalAScaleSchemaLegal`、`TileMatrixLocalBScaleSchemaLegal`要求CUBE_M32，A有效M×G、B有效N×G；实际几何检查将其主维限制在32。TGEMV_MX元数据中的RowMajor scale与此不一致，手册按最终bundle执行路径说明。

数值项仍有可定位的未闭合问题：[matrix-scale.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/matrix-scale.asl)的普通有限浮点分支调用ReferenceMatrixOrdinaryFloatingAccumulate，而普通特殊值及带scale的MX路径可能进入原始Word乘加；[cube.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/cube.asl)实际调用这些helper。数学公式、低精度解码和逐位profile之间的映射尚需对照完整规范，不能据现有无scale有限值示例确认全部数值分支。台账对受影响语义标记有缺口并保留具体查证路径。

Options已对照matrix-postprocess、matrix-quantization和B.FPATR的计算顺序与位域；完整builder组合、特殊值、RowMax/GroupMax辅助输出案例已在[接口示例补齐](#接口示例补齐)完成。72条MX声明选择已验证，矩阵数值profile问题分别记录。

## 加载参数与传输

WeightTLOADParams按固定weight-to-shared-parameters及PTO-C pto_tile.hpp构造器核对，已补两word位域、保留位和数值打包例。TIMG2COL三word字段与紧邻两条B.IOR逐项核对，公共项C08/C09闭合。Shared Writer发布、Local尾片消费者及各重载完整调用还需分别完成操作级验证。

传输示例补齐TLOAD的返回值/指定Shared目标/权重形式、TLOAD_CUBE的Null尾部、Shared TSTORE和TGATHER的CUBE目标。所有新增完整函数按固定规范推导；真实库编译和硬件执行未运行。

## 图像展开与尾片

四条TIMG2COL声明均已配完整函数与参数构造；固定parameters/schema/execution逐项核对。20行FP16案例验证隐式/显式核级行数的区别、Reader显式4行消费、单PE完整Shared发布、四PE阶段与零行LAST。128B库offset固定0，内部32B条带推导范围独立；1024B parent最后覆盖20..32条带且只定义20行payload。此为规范推导，真实库/lowering/硬件均未运行。

矩阵BIAS顺序复核：固定cube.asl先MatrixProductResult，再MatrixBiasResult，最后后处理；四个BIAS操作页及公共表已统一。新增FP32 K=2案例，乘积项16777216和−16777216先抵消为0，bias1使最终结果1。

## Shared 读取转换

固定 [shared-tmov-nd-to-cube.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tmov-nd-to-cube.asl)逐项要求完整16/32物理行、源parent行距、容量推导精确列数以及正有效交集；子视图起点只须对齐物理行。B.IOT/B.IOS mask一致，禁止Local/Shared两侧B.ASSEMBLE。已补第4行与第8行起始的完整例，后者得到12行有效尾片；b64 M32双CELL单独给例。对应专用接口和TMOV统一CUBE重载两条合同闭合。padding写raw零，源保持，输出每PE独立。验证为固定规范推导，未编译或运行。

## Shared 放置与加载维度

逐条对照固定版本的[转换schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tmov-cube-to-nd.asl)、[转换payload](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/shared-cube-to-nd.asl)、[普通Shared dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tlsu.asl)和[TLOADShared](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/shared-movement.asl)：

- CUBE→ND：Writer源容量=Part容量；完整输出源容量=parent容量。parent保持源精确物理列距。FP32 M16 16×8的512B源可放入32×8的1024B parent，偏移0或4 CELL。
- RowMajor Local→Shared：源容量=parent容量，提交片段从源起点取值，保留parent几何。此路径与CUBE转换的容量公式不同。
- Shared TLOAD：维度和候选描述符来自parent，Part只限定目标范围。32×8 FP32 parent、四PE、256B Part时，每PE源区间为其四分之一；GM基址无需再次按该区间移动。singleton探测整个parent源有效区，需与目标覆盖分开核对。
- CUBE↔GM：`BundleCubeTransportDataTypeSupported` 排除HiF4X2；N8 U64仅TLOAD，M32 b64另有双CELL加载/存储路径。相关TLOAD/TLOAD_CUBE/TSTORE已闭合条目的类型证据同步收窄到对应方向，普通RowMajor类型域保持。

以上为源码逐分支推导，未执行ASL或硬件。

## Shared 提交身份

固定[实际PE提交owner](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/shared-generation-pe-requests.asl)的 `SharedGenerationCoreIdentityMatches` 除Sx、容量、mask之外还检查invocation、producer_site/ReadBPC、start_instruction、operation_form与selector。同一open generation按PE保存arrival token，重复PE到达会等待。`CommitBundleSharedGenerationCandidateForCurrentPE` 在普通Shared TLOAD/TMOV路径上负责提交。

现有库Writer描述将first/middle/last交给不同调用点，尚无将这些调用点映射到上述同一生产身份的完整lowering合同。例如PE0在调用点A执行first、PE1在调用点B执行last，即使Sx相同，ReadBPC仍可能不同。先前建议的同一PE连续first/last还会命中重复arrival路径。须明确采用何种实际提交序列或由规范提供何种跨site续写规则，才能把这些完整Writer示例标为已验证。容量与地址推导不受此项阻塞。

TIMG2COL使用其专用 `CommitBundleSharedGenerationCandidateRangeWithPayloadElements` 路径，按专用PE分片和参数合同核对；上述普通TLSU owner差异不直接外推到它。

本次继续区分预检与提交：`ValidateBundleSharedGeneration` 对INIT走实际PE身份检查，对后续阶段走通用范围检查；实际提交仍统一进入 `CommitBundleSharedGenerationCandidateForCurrentPE`。open generation中的新PE还须通过 `SharedGenerationCoreRequestMatches`，其中包含上述生产身份检查。已到达的PE则走request waiting分支。后续阶段通过预检，只能证明预检条件成立，提交身份还须独立匹配。

已审阅的测试范围如下，均为固定提交的测试源码审阅，ASL执行状态为未运行：

| 固定测试 | 执行上下文与覆盖 | 对库设计的支持范围 |
| --- | --- | --- |
| [block-exec-shared-generation-001](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/block/model/operands/shared-generation/block-exec-shared-generation-001.asl) | ResetProfileState后直接执行bundle，未建立实际PE上下文；覆盖顺序INIT/LAST | 支持聚合模型的阶段序列；实际PE生产身份另由owner检查 |
| [PTO-AVS-BLOCK-SHARED-TMOV-COPIED-VIEW-021](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/block/model/operands/shared-generation-pe-requests/block-exec-shared-tmov-copied-view-021.asl) | LaunchKernelInvocation及四个实际PE；同一BPC、每PE一个INIT_LAST、不同offset，先到请求在STOP等待，发布后消费token | 支持TMOV的协作single、完整覆盖、padding和再次执行的ordinal；[完整库调用](TileOpReference/TMOV.md#四pe各提交一次的-shared-single)已补齐 |

S-SUBMIT的关闭条件：为普通Shared TLOAD、RowMajor TMOV和CUBE→Shared转换分别给出first/middle/last到实际PE生产身份及token的映射，并验证同一PE多次写入、跨PE到达和发布后的消费。当前可直接利用的single路径限定每PE一次请求；它为便利接口提供一个已对照的分支。

## Shared ND读取与发布

S-READ已完成完整Local目标分支的发布追踪：

1. [shared-tlsu](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tlsu.asl)在has_subview且writer_found=false时调用 [TMOVSharedToLocalPerPE](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/shared-movement.asl)。实际PE只写自己的Local bank。
2. payload逐元素写入后，该helper仅在mask=15时设置 `contents_defined=true` 并调用MarkTileValidRegionDefined。mask=8留下false；逐元素写入函数更新payload及逐元素defined位，汇总字段仍保持该值。
3. 完整ND目标没有CUBE Writer effect；FinishBundleLocalGenerationCubeWriterEffects处理空列表。[FinalizeBundleTileAttempt](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/operands/tile-bindings.asl)调用 [PublishRelativeTileDestination](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/state/descriptors.asl)，后者只更新相对索引顺序及有效位。
4. 外层tile-execution的CommitBundleLocalGenerationWithWriterEffects只处理带destination_assemble的目标，完整目标跳过；[TileSourceContentsDefined](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/descriptor-shape.asl)仍要求汇总contents_defined。由此，普通mask8子视图读取的输出无法通过这类消费者检查。

正向证据为 [PTO-AVS-BLOCK-SHARED-LOCAL-SUBVIEW-FOURSTREAM-011](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/block/model/dispatch/shared-tlsu/block-exec-shared-local-subview-fourstream-011.asl)：Shared U8 1×512中四个CELL分别填0x10..0x13，四个实际PE用mask15与offset=PE读取独立1×128目标，测试断言每个目标contents_defined及数据正确。手册已补mask15正向函数、mask8问题输入及ND Writer完整问题函数。该测试的审阅覆盖mask15；mask8结论来自上述可达源码路径推导。

普通ND Writer几何反例：目标parent16×16 FP32为1024B，Shared Reader片段8×16为512B。`BundleLocalDestinationAllocationBytes`在INIT取parent容量，`ResolveBundleTileDestinationsWithShapeAndTypeAndWriterEffects`只为M16/M32创建writer值视图；普通目标物理Rows仍按1024B推导为16。shared-tlsu与8行源视图比较后回滚分配并设置Fault_TileLegality，first阶段即失败。[手册完整问题函数](TileOpReference/TMOV.md#shared-reader-到-local-writer-的几何问题输入)列出两片偏移0/4及预期16×16结果。

关闭条件分别为：对齐非零PEMask下复制结果的定义状态；为普通ND Writer建立可匹配源片段的目标视图及正确范围提交。补实际PE的mask8→消费、mask15→消费、两片Writer→LAST→消费测试后，才能闭合该重载的几何、语义及端到端示例。PEMask编码集合继续按架构保留。

## 矩阵逐重载核对

本轮逐声明处理全部90条矩阵重载。18条普通声明按参数数量和受约束Options/size_t区分，72条MX声明按primary dtype派生0/1/2/3 ScaleMask区分；矩阵、GEMV、ACC、BIAS、Attr/Options、groupM均在JSON逐条记录。

依据链：

1. [matrix-functions](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-functions.asl)：12个function selector、ACC/BIAS/MX/GEMV分类、Local/Shared输入组数量、scale组长及carrier。
2. [matrix-cube-primary](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-cube-primary.asl)与[matrix-operands](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl)：A=M16/M32、B=N8、C/D同M布局、scale=M32、Bias=N8、CScale=U8 M32及精确有效形状。
3. [shared-cube-matrix](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-cube-matrix.asl)与[cube-tmatmul](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/cube-tmatmul.asl)：Shared左右组、转置、groupM、四PE有效行、零行PE、C/D独立和原子发布。
4. [B.FPATR](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/attributes/B.FPATR.asl)及[matrix-postprocess合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-postprocess.asl)：27个PreQuant编码、输入类别、输出dtype、scalar/vector参数、辅助输入输出和位域；Options是新库builder，字段映射按此核对。
5. [cube-value](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/cube-value.asl)、[cube](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/cube.asl)、[matrix-scale](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/matrix-scale.asl)：先乘积/显式C累加，BIAS在K循环后添加，再后处理。

具体数值缺口：E4M3的1编码为0x38，E8M0的1为0x7f，FP16的1为0x3c00。K=1、仅左scale、初值0时，当前 `TileProfileMatrixScaledAccumulate` 的scale-present分支按Word算得 `0x38*0x7f*0x3c00=0x0682e000`；将低32位作为FP32约为4.92297034e-35，而数学缩放乘积为1。调用者在 `MatrixMXProductResultFromTiles` 中直接保存该返回值，keep_acc无激活路径也直接返回该值。此为源码手工代入并用Python核算，不是ASL执行结果或硬件测量。普通浮点遇非有限值也会离开finite reference路径；其特殊值和状态合同同样须对齐。

已核实声明/角色/形状/参数保留相应证据。数值差异登记为有缺口；各重载的完整调用、scale组合、Shared尾PE及辅助输出示例已在后续的[接口示例补齐](#接口示例补齐)中核对。示例中的数学预期与固定profile的执行差异继续在语义维度跟踪。

### M-NUM分支与已有测试的证据范围

| helper与分支 | 输入编码 | 源码代入结果 | 数学合同要求 |
| --- | --- | --- | --- |
| ScaledAccumulate，左scale存在 | acc=0，E4M3左1=`0x38`，E8M0 scale1=`0x7f`，FP16右1=`0x3c00` | Word乘积`0x0682e000` | FP32 1=`0x3f800000` |
| Accumulate，非有限输入 | acc=0，FP16左+∞=`0x7c00`，FP16右1=`0x3c00`，目标FP32 | Word乘积`0x1d100000` | FP32 +∞=`0x7f800000` |
| Bias，非有限输入 | FP32值+∞=`0x7f800000`，FP32 bias1=`0x3f800000` | Word和`0xbf000000`，作为FP32为−0.5 | FP32 +∞=`0x7f800000` |

三项均为固定helper源码代入；普通有限浮点分支继续使用ReferenceMatrixOrdinaryFloatingAccumulate。普通矩阵与无scale MX仍受非有限分支影响；带scale MX还受第一项影响；BIAS另受第三项影响。该分类对应90条记录各自的语义证据。

[PTO-AVS-BLOCK-TMATMULMX-BIAS-EXEC-001](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/block/execution/BSTART.TMATMULMX.BIAS/block-exec-bstart-tmatmulmx-bias-add-001.asl)向E4M3输入写raw整数2/3，向E8M0 scale写raw2/3，向FP32 bias写raw5，并断言raw结果1157。这组位模式按各自浮点格式解码后具有不同的数学值，测试断言直接覆盖编码字乘加路径。[tile-exec-concrete-tile-006](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/tile/model/execution/elementwise/tile-exec-concrete-tile-006.asl)也以raw `5+2*4*3*6=149`检查scale helper。两份测试均已审阅源码，执行状态为未运行。

M-NUM的关闭条件是为这些已接受输入对齐数值profile与执行函数，并用正确格式编码的输入检查解码后结果及异常状态。应分别覆盖普通非有限乘加、BIAS非有限加法、MX各scale存在位及其数值格式；Options、声明和完整调用示例已完成的证据继续有效。

## TCVT 执行覆盖

核对[配对与舍入](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/e8m0-conversion.asl)、[统一转换](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/reference-conversion.asl)、[目标/源几何](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/tcvt-value-operands.asl)及[实际TCVTToValue](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/formats.asl)。默认RNONE在数值控制层解析；同类型显式浮点round-integral优先；E8M0/packed/E6M2/RCPE6M2走专用路径；普通reference以外的浮点仍可能走raw回退。

例如FP32的1（0x3f800000）转换到HiF8：配对helper接受，该目标不属于common集合且不命中特殊格式分支，`TileProfileConvert` 返回原始Word；HiF8编码1在 `ReferenceFP8FiniteValue` 中为0x08。由此可见，接受编码与数学转换覆盖尚未一致。该例限定helper/TCVTToValue源码路径，未执行ASL或硬件。需补齐此类格式profile或澄清规范，而不能把reference集合之外全部写成ISA禁止。


### TCVT几何及字段补正

[PTO-TCVT-CONTRACT-001](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/format-conversion/TCVT.asl)规定CUBE_M16/M32省略LB2；[tcvt-schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tcvt-schema.asl)检查内部默认值1。原台账“CUBE LB2=1”已改为省略字段并说明内部值。`PTO-AVS-TILE-TCVT-CUBE-LB2-001`和source-view-boundary-009检查显式非默认LB2的拒绝；字段发射遵循NDF的省略合同。

同一条款允许RowMajor非二次幂列数profile以TSize作为容量上界。schema的odd_physical_profile分支按TileStorageFitsCapacity检查，destination-shape的ordinary_tcvt分支保留源行数。[PTO-AVS-TILE-TCVT-NORM-PHYSICAL-SHAPE-006](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/tile/elementwise-tile-tile/format-conversion/TCVT/tile-fault-tcvt-norm-physical-shape-006.asl)用32×17 FP16（1088B存储、2048B容量）与E2M1X2（288B存储、512B容量）检查双向结果、物理行数、packed尾部及容量不足。TCVT正文补完整encode/decode函数；CommonTypes记录库选择最小合法二次幂容量的规则。审阅范围为完整RowMajor目标，分片路径继续独立校验。

C-NUM保持类型及语义缺口：HiF8等接受域中的数值转换需要明确profile及执行覆盖，关闭时须同时检查合法配对、正确编码结果、异常状态与实际TCVT入口。几何和LB2的文档修复已完成，不依赖这一数值问题。

## 接口示例补齐

本批完成可独立补写的示例内容，覆盖12个矩阵操作的90条重载和TCVT的专用格式分支。逐重载调用映射保存在 [example_cases.json](audit/example_cases.json)，每条记录包含操作页、代码块、函数名、完整调用及预期声明序号。核对时读取手册的实际声明与实际代码块。

### 矩阵逐声明覆盖

- 每页Local例子明确A/Left、B/Right、D、ACC的C或BIAS、scale和RowMax类型及形状。Attr与Options各有实际调用；Options例子包含独立RowMax输出。GEMV的实参顺序保持mtx在前、vec在后，数学运算为vec×mtx。
- MX四种scale存在位各有完整函数，另为完整Options重载补0/1/2的NoOperand占位调用。K=35、物理K=64，E8M0组0取1、组1取2，覆盖32+3的尾组。数学输出为35/38/38/44，ACC初值2及BIAS后加2分别使结果增加2。
- 六个TMATMUL页面各自提供Local-A/Shared-B的显式groupM和Shared-A/Shared-B的推导groupM调用。groupM=20覆盖16/4/0/0有效行；MatrixRules的六个完整函数以groupM=70覆盖32/32/6/0有效行。两种情况分别使用M16/M32、匹配的C/D与辅助输出，并明确Shared已发布、Local输入已定义及零行PE没有有效结果。
- MatrixRules补packed E2M1的group32及HiF4的group64例子。K=34/68，各有尾组，给出scale dtype、位编码、容量和数学结果。

几何依据为本文件“矩阵逐重载核对”所列的matrix-cube-primary、matrix-operands、shared-cube-matrix及cube-tmatmul。零行PE在Shared预检后返回、跳过Local状态处理的分支对应cube-tmatmul中 `cooperative && valid_m == 0`。Shared消费例子的前提是已发布输入；普通Shared Writer生产身份仍由S-SUBMIT跟踪。

### Options 组合覆盖

[Options完整组合](TileOpReference/Options.md#完整组合示例)提供转换/ReLU、fresh和合并RowMax、GroupMax/max_abs、标量及向量量化、LReLU/PReLU、CScale/raw_acc/acc_hint链和Shared转置函数。FP16/FP32辅助输出均按各自CELL几何分配128B，逐项核对有效M×1或M×ceil(N/GroupN)。U64向量参数采用N8 2×8物理、1×8有效形状。

数学代入包括：16/32的列分组规约、旧RowMax=40的合并、16×2+3=35的量化、−16×0.5=−8的激活、8×2^-1+16=20再加16=36的累加链。Shared转置例子分别给出primary的K×groupM/K×N轴及scale的groupM×groups/N×groups轴。每个参与对象在函数参数或局部声明中定义，预期结果在代码后的输入条件中给出。

### TCVT 专用格式覆盖

[TCVT示例](TileOpReference/TCVT.md#示例)保留普通窄化、同类型round-integral及Reader/Writer例子，新增以下完整函数：

| 分支 | 具体输入与预期 | 直接依据 |
| --- | --- | --- |
| E8M0双向 | FP32 2↔0x80；零/负值/NaN编码为0xff、NV；0xff解码为quiet NaN | e8m0-conversion.asl、tcvt-conversion.asl |
| E6M2双向 | FP16 2↔0xc4；零→0x00并置UF/NX、负值→0xff并置NV | tcvt-conversion.asl、formats/e6m2.asl |
| RCPE6M2 | 0xc4→FP16 0.5；0xff→quiet NaN | tcvt-conversion.asl、formats/rcpe6m2.asl |
| E2M1X2/E1M2X2 | 1↔0x2/0x4；平局RNE、负零、quiet/signaling NaN | tcvt-conversion.asl、packed-conversion.asl |
| S4X2/S8 | 0xf符号扩展为0xff；−9低位截断为+7 | formats.asl的TileConvertIntegerValue |

所有新增转换载体使用M32、逻辑32×8；FP32/FP16/8位/4位分别为1024B/512B/256B/128B。检查以逻辑位宽计算packed容量，解释每个元素的编码及新增sticky状态位。HiF8等扩展格式的通用转换执行差异保留在TCVT语义/类型项。

固定文件入口：[tcvt-conversion](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/tcvt-conversion.asl)、[packed-conversion](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/packed-conversion.asl)、[E6M2](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/arch/data-types/formats/e6m2.asl)、[RCPE6M2](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/arch/data-types/formats/rcpe6m2.asl)、[HiF4X2](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/arch/data-types/formats/hif4x2.asl)。

### 验证边界与状态变更

`python clang/docs/LinxISA/audit/check_examples.py` 对37个标记代码块执行C++20模拟声明/类型检查，其中156个明确映射的调用覆盖全部90条矩阵声明，并逐调用断言所选声明序号。类型模拟检查基本角色、物理容量、静态维度及Local scale布局/形状；新增TCVT非二次幂列数示例按限定profile计算逐行存储及二次幂容量。Options模拟只核对调用形式，实际字段与Shared转置后的形状由上述规范审阅确认。原有MX的396个模拟选择用例继续单独运行。TMOV新增的四个函数按固定源码审阅，编译和执行均另记为未运行。

新增示例的数学/编码预期已按上述固定函数和接口合同推导；完整库实现编译、ASL执行及硬件运行均未执行。带scale数学结果明确作为库合同预期，固定profile差异仍保留。矩阵90条及TCVT一条的“示例”维度改为已核实，示例缺失问题M-EX解除；C07的builder组合缺项补齐。语义、类型及Shared提交等原有未闭合项继续保留。

## 全册复核修正20261125

按[全册复核报告](TileOpFullReview20261125.md#修正记录)修正F01–F09。F01依据固定GMDecValue（old=5大于limit=1，返回limit）；F02依据reduction-and-expansion的列结果物理几何；F03依据TileSignedModulo与浮点profile；F04依据TCVT各侧独立容量推导；F05依据硬件profile的saturation及float_to_integer_invalid；F06/F07依据本库已经定义的TMOV展开及MX重载合同。

F08将已闭合条目的source_candidates整理为checks中已存在的具体references；来源正文辨析保留在本证据文件，手册直接描述固定规范与库设计行为。F09为全册措辞整理，保留实际禁止项和运行时边界。此次修正未改动公开声明及三个搁置的Shared映射协议。结构、声明和示例mock检查分别验证文档格式、签名登记、已标记调用的声明匹配；数值例子的修正通过规范推导，未执行ASL或硬件测试。

## 2026-11-25 第二轮文档一致性修正

依据[第二轮报告](TileOpFullReview20261125Round2.md)完成R01–R03。MX ACC/BIAS完整Options槽的类型、角色和参数说明与MatrixRules及explicit_slots示例对齐；公共页操作声明改为链接唯一声明；六个页面的反驳式句子改为直接描述合同。复核涉及的角色、参数、有效形状与故障边界，未修改操作声明或闭合状态。三条S-SUBMIT继续搁置。验证为文档检查及声明/type mock。
