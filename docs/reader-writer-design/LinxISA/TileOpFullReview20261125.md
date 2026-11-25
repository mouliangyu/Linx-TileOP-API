# TileOP 全册复核记录（2026-11-25）

## 范围与验证边界

本轮以现有135个操作页、274条重载和21个公共页面为完整文档检查范围。检查声明、参数表、角色表、类型与形状叙述、操作语义、示例及公共规则的一致性；同族重复文本合并阅读，独有声明、公式、限制和例子分别检查。具体发现回查固定LinxISA所锁定的PTO语义。

本记录区分全册文档审阅与逐条ISA重新认证：下表来源入口继承台账，供定位依据；本轮没有重新执行全部ASL、没有逐一重证274条重载的全部八维合同。无新增发现仅表示本轮文档检查未识别新的问题。原台账的closed状态保持原样，本报告中的九组缺陷已按下列修正记录处理。

规范版本：LinxISA `7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27` 锁定 PTO `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，数值采用其硬件profile。三条S-SUBMIT映射按用户要求搁置。

## 修正记录

九组发现均已修正，以下发现段保留修正前的问题，供追溯。

| 编号 | 修正结果 | 正文入口 |
| --- | --- | --- |
| F01 | old=5、limit=1 的结果改为1，并列明正常/反选谓词的更新行与保留行 | [TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md#示例) |
| F02 | 六个列规约页统一为1×C列结果几何，分别说明RowMajor/CUBE物理维度与128B示例容量 | [TCOLMAX](TileOpReference/TCOLMAX.md#示例)及同族五页 |
| F03 | TREM/TREMS 使用mod记号，说明有符号、无符号及浮点合同，增加负除数例子 | [TREM](TileOpReference/TREM.md#操作语义)、[TREMS](TileOpReference/TREMS.md#操作语义) |
| F04 | 两侧独立推导SizeCode，允许结果相同 | [CompareConvertRules](TileOpReference/CompareConvertRules.md) |
| F05 | 区分整数截断、无效浮点转整数与浮点溢出，列明signed/unsigned indefinite及NV | [Numerics](TileOpReference/Numerics.md) |
| F06 | Shared→Local总表分ND与CUBE，列入ND LocalWriter的两次TMOV展开 | [StorageBoundaries](TileOpReference/StorageBoundaries.md) |
| F07 | 六个MX页补全scale Tile/NoOperand类型与角色，明确Attr、Options、便利重载的差别 | [TGEMV_MX](TileOpReference/TGEMV_MX.md#参数与操作数角色)、[TMATMUL_MX](TileOpReference/TMATMUL_MX.md#参数与操作数角色)及各ACC/BIAS页 |
| F08 | 流程页统一引用生成状态；closed条目候选来源替换为已记录的具体依据；清理旧数值待办 | [合同核对表](TileOpContractLedger.md) |
| F09 | 全册同族及公共页改为直接描述行为，保留类型、布局、生命周期和故障边界约束 | [手册索引](TileOpReference/README.md) |

本次修改保持274条声明与271条closed、3条open状态；三条S-SUBMIT继续搁置。修正依据限于报告定位的条文、公共合同及文档一致性；未新增实现编译、ASL执行或硬件运行证据。

## 发现

9组问题：1组P1、7组P2、1组P3。F08/F09为跨册维护问题，独立于操作语义缺陷。

### F01 [P1] TSTORE_ATOMIC_DEC 的 Shared/谓词示例算错

位置：TSTORE_ATOMIC_DEC.md:111。

old=5、src(limit)=1 时满足 old>limit，结果为1。该段却将 shared_source 和 selected_rows 写成4；未选中行保持5。普通例子与 MGATHER_DEC/MSCATTER_DEC 的结果为1。

依据及修正方向：固定 ASL tile/model/memory/gm-atom-red.asl 的 GMDecValue 第249行；修正 Shared、正常谓词和反选谓词预期。

### F02 [P2] 六个列规约页混入行规约物理几何

位置：TCOLMAX.md:56。

六页边界段均写“RowMajor行结果物理列为1；M16/M32行结果物理列保持源物理列”。当前入口输出1×C，这段没有解释列规约自身的物理载体，容易导致按行规约配置目标。

依据及修正方向：ReductionRules.md 的合法组合区分两个方向；改为列结果的物理形状及与该页例子的容量关系。

### F03 [P2] TREM/TREMS 的百分号公式误导 C++ 调用者

位置：TREM.md:3。

正文用 x%y / x%s，公共规则和边界例子却定义有符号结果与除数同号。S32输入−5和3时，本接口得1，C++表达式得−2。

依据及修正方向：固定 ASL tile/model/execution/elementwise.asl 的 TileSignedModulo 第230行；改用明确的模运算公式并写明各类型行为。

### F04 [P2] TCVT 公共规则额外禁止相同 SizeCode

位置：CompareConvertRules.md:36。

“不能复用同一个 SizeCode”把独立推导误写为必须不同。FP32→S32在相同物理形状下容量相同，SizeCode自然相同。

依据及修正方向：TCVT.md 的普通布局规则允许各侧按 dtype 得到容量；保留独立推导，允许推导结果相等。

### F05 [P2] TCVT 溢出说明遗漏无效浮点转整数

位置：Numerics.md:21。

Sat=0概括为“保留舍入值低位”，未区分整数截断与无效浮点转整数。NaN→S32应返回0x80000000并按转换合同记录NV，不能由低位截断说明推得。

依据及修正方向：固定 hardware-conformance-profile.json 的 conversion.float_to_integer_invalid；按源目标类型和异常类别分别描述，明确signed/unsigned indefinite值。

### F06 [P2] Shared→Local 总表遗漏 ND Writer 分支

位置：StorageBoundaries.md:11。

总表将 Shared→Local 的目标概括为完整 Local CUBE Tile。TMOV 的 ND 重载允许 Local Writer，并明确定义两次 TMOV 的展开，读总表会错过这一可用形式。

依据及修正方向：TMOV.md 声明、角色表与 Shared ND 读取与 Local Writer 小节；总表分 ND 与 CUBE 两行。

### F07 [P2] MX 参数表没有表达缺失 scale 的类型

位置：TGEMV_MX.md:86。

GEMV的smtx/svec表一律要求is_local_tile_v，完整Options声明却使用typename并允许NoOperand。矩阵MX表将typename称为“约束”，角色表也只列Tile，未表达ScaleMask清零的槽。

依据及修正方向：MatrixRules.md 的MX重载约束和各页explicit_slots0/1/2例子；按实际scale和NoOperand两类填写，区分Attr、Options及便利重载。

### F08 [P2] 当前核对状态在不同文档中不一致

位置：../TileOpContractReview.md:5。

流程页仍显示179条闭合、95条剩余；当前JSON是271条closed、3条open。多个closed条目的source_candidates仍写待定位/待逐条映射。TCVT页和Options页仍有旧数值覆盖问题的残留说明。

依据及修正方向：状态从JSON统一生成；候选来源保留为历史记录或清理为已解析来源。此次发现的正文问题应单独跟踪，271条closed不能表示本轮没有发现缺陷。

### F09 [P3] 多族正文残留反驳式说明

位置：TTRI.md:35。

TTRI及IrregularRules有“不是只设置对角线”；矩阵页及StorageBoundaries有“这不表示架构禁止分片”；其他公共页仍穿插旧接口、实现或模型差异。

依据及修正方向：按用户要求将正文改为可调用形式与正确行为。实际输入禁用、类型边界等有效约束保留；历史辨析移到手册外的证据记录。

## 修正后的检查结果

- 声明/指纹：check_contracts.py通过，274条。
- 统一六节结构及链接检查：通过，135页。
- 已标记示例：check_examples.py通过，37个块、156个映射调用，覆盖90条矩阵声明。仅声明/type mock。
- 上述三项检查在修正后重新运行通过。检查范围不含文字预期值的自动求值、完整实现编译、ASL执行或硬件运行；F01的预期值已按GMDecValue人工推导修正。

## 逐操作覆盖

各行涵盖该页列出的全部重载；F08/F09另按跨册项处理。来源列为台账已有固定规范入口。

| 操作 | 重载数 | 本轮文档结论 | 规范入口 |
| --- | ---: | --- | --- |
| [GMOV](TileOpReference/GMOV.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/pe-movement/GMOV.asl) |
| [MGATHER](TileOpReference/MGATHER.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER.asl) |
| [MGATHER_ADD](TileOpReference/MGATHER_ADD.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_ADD.asl) |
| [MGATHER_AND](TileOpReference/MGATHER_AND.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_AND.asl) |
| [MGATHER_CAS](TileOpReference/MGATHER_CAS.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_CAS.asl) |
| [MGATHER_DEC](TileOpReference/MGATHER_DEC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_DEC.asl) |
| [MGATHER_EXCH](TileOpReference/MGATHER_EXCH.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_EXCH.asl) |
| [MGATHER_INC](TileOpReference/MGATHER_INC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_INC.asl) |
| [MGATHER_MASK](TileOpReference/MGATHER_MASK.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_MASK.asl) |
| [MGATHER_MAX](TileOpReference/MGATHER_MAX.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_MAX.asl) |
| [MGATHER_MIN](TileOpReference/MGATHER_MIN.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_MIN.asl) |
| [MGATHER_OR](TileOpReference/MGATHER_OR.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_OR.asl) |
| [MGATHER_XOR](TileOpReference/MGATHER_XOR.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_XOR.asl) |
| [MSCATTER](TileOpReference/MSCATTER.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER.asl) |
| [MSCATTER_ADD](TileOpReference/MSCATTER_ADD.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_ADD.asl) |
| [MSCATTER_AND](TileOpReference/MSCATTER_AND.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_AND.asl) |
| [MSCATTER_DEC](TileOpReference/MSCATTER_DEC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_DEC.asl) |
| [MSCATTER_INC](TileOpReference/MSCATTER_INC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_INC.asl) |
| [MSCATTER_MASK](TileOpReference/MSCATTER_MASK.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_MASK.asl) |
| [MSCATTER_MAX](TileOpReference/MSCATTER_MAX.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_MAX.asl) |
| [MSCATTER_MIN](TileOpReference/MSCATTER_MIN.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_MIN.asl) |
| [MSCATTER_OR](TileOpReference/MSCATTER_OR.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_OR.asl) |
| [MSCATTER_POPC](TileOpReference/MSCATTER_POPC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_POPC.asl) |
| [MSCATTER_XOR](TileOpReference/MSCATTER_XOR.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_XOR.asl) |
| [TABS](TileOpReference/TABS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TABS.asl) |
| [TADD](TileOpReference/TADD.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TADD.asl) |
| [TADDS](TileOpReference/TADDS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TADDS.asl) |
| [TAND](TileOpReference/TAND.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TAND.asl) |
| [TANDS](TileOpReference/TANDS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TANDS.asl) |
| [TCI](TileOpReference/TCI.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TCI.asl) |
| [TCI_2D](TileOpReference/TCI_2D.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TCI.asl) |
| [TCI_COL](TileOpReference/TCI_COL.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TCI.asl) |
| [TCI_ROW](TileOpReference/TCI_ROW.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TCI.asl) |
| [TCMP](TileOpReference/TCMP.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TCMP.asl) |
| [TCMPS](TileOpReference/TCMPS.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TCMPS.asl) |
| [TCOLARGMAX](TileOpReference/TCOLARGMAX.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLARGMAX.asl) |
| [TCOLARGMIN](TileOpReference/TCOLARGMIN.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLARGMIN.asl) |
| [TCOLEXPAND](TileOpReference/TCOLEXPAND.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPAND.asl) |
| [TCOLEXPANDADD](TileOpReference/TCOLEXPANDADD.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDADD.asl) |
| [TCOLEXPANDDIV](TileOpReference/TCOLEXPANDDIV.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDDIV.asl) |
| [TCOLEXPANDEXPDIF](TileOpReference/TCOLEXPANDEXPDIF.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDEXPDIF.asl) |
| [TCOLEXPANDMAX](TileOpReference/TCOLEXPANDMAX.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDMAX.asl) |
| [TCOLEXPANDMIN](TileOpReference/TCOLEXPANDMIN.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDMIN.asl) |
| [TCOLEXPANDMUL](TileOpReference/TCOLEXPANDMUL.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDMUL.asl) |
| [TCOLEXPANDSUB](TileOpReference/TCOLEXPANDSUB.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDSUB.asl) |
| [TCOLMAX](TileOpReference/TCOLMAX.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLMAX.asl) |
| [TCOLMIN](TileOpReference/TCOLMIN.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLMIN.asl) |
| [TCOLPROD](TileOpReference/TCOLPROD.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLPROD.asl) |
| [TCOLSUM](TileOpReference/TCOLSUM.md) | 1 | F02 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-reduction/TCOLSUM.asl) |
| [TCVT](TileOpReference/TCVT.md) | 1 | F04；F05 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tcvt-schema.asl) |
| [TDIV](TileOpReference/TDIV.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TDIV.asl) |
| [TDIVS](TileOpReference/TDIVS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TDIVS.asl) |
| [TEXP](TileOpReference/TEXP.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TEXP.asl) |
| [TEXPANDS](TileOpReference/TEXPANDS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/initialization/TEXPANDS.asl) |
| [TEXPDIF](TileOpReference/TEXPDIF.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TEXPDIF.asl) |
| [TFMA](TileOpReference/TFMA.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl) |
| [TGATHER](TileOpReference/TGATHER.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/indexed-rearrangement.asl) |
| [TGEMV](TileOpReference/TGEMV.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGEMV_ACC](TileOpReference/TGEMV_ACC.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGEMV_BIAS](TileOpReference/TGEMV_BIAS.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGEMV_MX](TileOpReference/TGEMV_MX.md) | 8 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGEMV_MX_ACC](TileOpReference/TGEMV_MX_ACC.md) | 8 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGEMV_MX_BIAS](TileOpReference/TGEMV_MX_BIAS.md) | 8 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TGPR2T](TileOpReference/TGPR2T.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TGPR2T.asl) |
| [TIMG2COL](TileOpReference/TIMG2COL.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/timg2col-execution.asl) |
| [TLEA](TileOpReference/TLEA.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TLEA.asl) |
| [TLOAD](TileOpReference/TLOAD.md) | 4 | S-SUBMIT搁置分支保留 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TLOAD.asl) |
| [TLOAD_CUBE](TileOpReference/TLOAD_CUBE.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TLOAD.asl) |
| [TLOG](TileOpReference/TLOG.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TLOG.asl) |
| [TMATMUL](TileOpReference/TMATMUL.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMATMUL_ACC](TileOpReference/TMATMUL_ACC.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMATMUL_BIAS](TileOpReference/TMATMUL_BIAS.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMATMUL_MX](TileOpReference/TMATMUL_MX.md) | 16 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMATMUL_MX_ACC](TileOpReference/TMATMUL_MX_ACC.md) | 16 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMATMUL_MX_BIAS](TileOpReference/TMATMUL_MX_BIAS.md) | 16 | F07 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/matrix-operands.asl) |
| [TMAX](TileOpReference/TMAX.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TMAX.asl) |
| [TMAXS](TileOpReference/TMAXS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TMAXS.asl) |
| [TMIN](TileOpReference/TMIN.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TMIN.asl) |
| [TMINS](TileOpReference/TMINS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TMINS.asl) |
| [TMOV](TileOpReference/TMOV.md) | 4 | F06；S-SUBMIT搁置分支保留 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/execution/BSTART.TMOV.asl) |
| [TMOV_CUBE_TO_SHARED_ND](TileOpReference/TMOV_CUBE_TO_SHARED_ND.md) | 1 | S-SUBMIT搁置分支保留 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tlsu.asl) |
| [TMOV_SHARED_ND_TO_CUBE](TileOpReference/TMOV_SHARED_ND_TO_CUBE.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tmov-nd-to-cube.asl) |
| [TMUL](TileOpReference/TMUL.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TMUL.asl) |
| [TMULS](TileOpReference/TMULS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TMULS.asl) |
| [TNEG](TileOpReference/TNEG.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TNEG.asl) |
| [TNOT](TileOpReference/TNOT.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TNOT.asl) |
| [TOR](TileOpReference/TOR.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TOR.asl) |
| [TORS](TileOpReference/TORS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TORS.asl) |
| [TPACK](TileOpReference/TPACK.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TPACK.asl) |
| [TPERMUTE](TileOpReference/TPERMUTE.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TPERMUTE.asl) |
| [TPREFETCH](TileOpReference/TPREFETCH.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TPREFETCH.asl) |
| [TRECIP](TileOpReference/TRECIP.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TRECIP.asl) |
| [TRELU](TileOpReference/TRELU.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TRELU.asl) |
| [TREM](TileOpReference/TREM.md) | 1 | F03 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TREM.asl) |
| [TREMS](TileOpReference/TREMS.md) | 1 | F03 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TREMS.asl) |
| [TROWARGMAX](TileOpReference/TROWARGMAX.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWARGMAX.asl) |
| [TROWARGMIN](TileOpReference/TROWARGMIN.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWARGMIN.asl) |
| [TROWEXPAND](TileOpReference/TROWEXPAND.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPAND.asl) |
| [TROWEXPANDADD](TileOpReference/TROWEXPANDADD.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDADD.asl) |
| [TROWEXPANDDIV](TileOpReference/TROWEXPANDDIV.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDDIV.asl) |
| [TROWEXPANDEXPDIF](TileOpReference/TROWEXPANDEXPDIF.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDEXPDIF.asl) |
| [TROWEXPANDMAX](TileOpReference/TROWEXPANDMAX.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDMAX.asl) |
| [TROWEXPANDMIN](TileOpReference/TROWEXPANDMIN.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDMIN.asl) |
| [TROWEXPANDMUL](TileOpReference/TROWEXPANDMUL.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDMUL.asl) |
| [TROWEXPANDSUB](TileOpReference/TROWEXPANDSUB.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPANDSUB.asl) |
| [TROWMAX](TileOpReference/TROWMAX.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWMAX.asl) |
| [TROWMIN](TileOpReference/TROWMIN.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWMIN.asl) |
| [TROWPROD](TileOpReference/TROWPROD.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWPROD.asl) |
| [TROWSUM](TileOpReference/TROWSUM.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWSUM.asl) |
| [TRSQRT](TileOpReference/TRSQRT.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TRSQRT.asl) |
| [TSCATTER](TileOpReference/TSCATTER.md) | 1 | 未发现新的页内/公共规则冲突 | [台账](TileOpContractLedger.md) |
| [TSEL](TileOpReference/TSEL.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TSEL.asl) |
| [TSELS](TileOpReference/TSELS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TSELS.asl) |
| [TSHL](TileOpReference/TSHL.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TSHL.asl) |
| [TSHLS](TileOpReference/TSHLS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TSHLS.asl) |
| [TSHR](TileOpReference/TSHR.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TSHR.asl) |
| [TSHRS](TileOpReference/TSHRS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TSHRS.asl) |
| [TSHUF](TileOpReference/TSHUF.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TSHUF.asl) |
| [TSQRT](TileOpReference/TSQRT.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TSQRT.asl) |
| [TSTORE](TileOpReference/TSTORE.md) | 2 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TSTORE.asl) |
| [TSTORE_ATOMIC_ADD](TileOpReference/TSTORE_ATOMIC_ADD.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_AND](TileOpReference/TSTORE_ATOMIC_AND.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_DEC](TileOpReference/TSTORE_ATOMIC_DEC.md) | 3 | F01 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_INC](TileOpReference/TSTORE_ATOMIC_INC.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_MAX](TileOpReference/TSTORE_ATOMIC_MAX.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_MIN](TileOpReference/TSTORE_ATOMIC_MIN.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_OR](TileOpReference/TSTORE_ATOMIC_OR.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_ATOMIC_XOR](TileOpReference/TSTORE_ATOMIC_XOR.md) | 3 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl) |
| [TSTORE_PART](TileOpReference/TSTORE_PART.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TSTORE.asl) |
| [TSUB](TileOpReference/TSUB.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TSUB.asl) |
| [TSUBS](TileOpReference/TSUBS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TSUBS.asl) |
| [TTRI](TileOpReference/TTRI.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TTRI.asl) |
| [TUNPACK](TileOpReference/TUNPACK.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TUNPACK.asl) |
| [TXOR](TileOpReference/TXOR.md) | 4 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TXOR.asl) |
| [TXORS](TileOpReference/TXORS.md) | 1 | 未发现新的页内/公共规则冲突 | [固定条文](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TXORS.asl) |

## 公共页覆盖

| 页面 | 本轮关注点或发现 |
| --- | --- |
| [AtomicsRules](TileOpReference/AtomicsRules.md) | 单lane原子性、INC/DEC和故障边界 |
| [BroadcastRules](TileOpReference/BroadcastRules.md) | ROW/COL方向、offset及EXPDIF类型 |
| [CommonTypes](TileOpReference/CommonTypes.md) | Local/Shared协议、GM视图、单位和元数据 |
| [CompareConvertRules](TileOpReference/CompareConvertRules.md) | F04；谓词与数值转换角色 |
| [ElementwiseRules](TileOpReference/ElementwiseRules.md) | F03对照；dtype、别名和整数模 |
| [FragmentGeometry](TileOpReference/FragmentGeometry.md) | Part容量、局部坐标及不同输入输出几何 |
| [IndexedMemoryRules](TileOpReference/IndexedMemoryRules.md) | 字节索引、packed配对、range与mask |
| [IrregularRules](TileOpReference/IrregularRules.md) | F09；序列、三角形、Local索引 |
| [LayoutRules](TileOpReference/LayoutRules.md) | raw-word重排及固定输出几何 |
| [MatrixRules](TileOpReference/MatrixRules.md) | F07关联；scale存在位、groupM及尾组 |
| [Numerics](TileOpReference/Numerics.md) | F05；数值profile及转换边界 |
| [OperandRoles](TileOpReference/OperandRoles.md) | 输入输出协议及finish |
| [Options](TileOpReference/Options.md) | F08、F09；量化、激活、辅助输出及CScale |
| [Predicate](TileOpReference/Predicate.md) | basis、存储、选择和位运算 |
| [README](TileOpReference/README.md) | 135操作导航及公共页入口 |
| [Reader](TileOpReference/Reader.md) | 借用、显式维度和顺序迭代 |
| [ReductionRules](TileOpReference/ReductionRules.md) | F02对照；行/列结果几何 |
| [ScalarRules](TileOpReference/ScalarRules.md) | F03对照；标量类型及维度来源 |
| [StorageBoundaries](TileOpReference/StorageBoundaries.md) | F06、F09；ND/CUBE方向与发布 |
| [TransportRules](TileOpReference/TransportRules.md) | 复制、转换、预取及存储故障 |
| [Writer](TileOpReference/Writer.md) | 阶段消费、动态维度、提前退出及Shared身份 |
