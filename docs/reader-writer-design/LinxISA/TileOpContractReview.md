# TileOP 接口合同核对流程

## 入口与当前基线

[逐重载核对表](TileOpContractLedger.md) 已登记 135 个操作的 274 条公开重载声明；[JSON 台账](TileOpContractLedger.json) 保存完整签名、状态、条文入口、来源候选、问题编号和文档指纹。当前闭合数、八维进度、逐操作待办及范围化公共依赖统一见生成的核对表。

本表以新库设计为对象。ISA 决定硬件行为，PTO-C 源码用于查证原有接口和实现；新协议、便利重载和类型约束须记录为库设计决定。三者分别核对到具体条款。来源候选只能作为查证入口。

缺口会跨多个重载重复出现，核对表按公共原因分组并保留逐重载记录。状态由 JSON 台账生成；新的文档缺陷与修正另见[全册复核记录](TileOpFullReview20261125.md)。

## 每个重载的八项核对

| 核对项 | 必须记录的结论 | 闭合证据 |
| --- | --- | --- |
| 声明 | 模板、默认值、返回类型、重载选择条件、值类别 | 正文声明与设计或源码逐项映射；歧义已排除 |
| 角色 | 每个参数的 Tile/Reader/Writer/Shared/GM/Predicate 角色、读写方向 | 逐参数合同与存储、生命周期规则一致 |
| 类型配对 | 封闭类型集合、跨类型配对、backing/操作类型关系 | 固定 ISA 合法性条款及库侧选择理由 |
| 形状 | 物理/有效形状来源、容量、布局、偏移、对齐、尾片及动态情况 | 对应 ISA 字段和库元数据绑定；边界案例 |
| 参数编码 | 单位、默认值、位域、保留值、可选 operand、静态/动态要求 | 参数到指令字段或库行为的逐项映射 |
| 语义 | 公式、舍入、溢出、padding、别名、发布、副作用、错误条件 | 固定语义条款；数值 profile 精确引用；新设计决定 |
| 来源 | 各条结论属于 ISA、现有实现或新库设计 | 仓库、固定提交、文件/章节及具体条款；记录差异的处理 |
| 示例 | 对应本重载的完整输入、调用、预期结果及边界案例 | 逐参数推导及规范对照；单独记录编译/运行状态 |

同一声明覆盖多个语义分支时，在该重载记录中列出分支清单，例如 Local/Shared、RowMajor/CUBE、静态/动态、普通 Tile/片段。逐分支闭合后才允许汇总为已核实。实例化 dtype 无须逐一复制签名，但必须由完整配对表覆盖。

## 状态与证据

- **已登记**：存在声明或查询入口，等待语义核对。
- **待核对**：尚缺逐条结论或依据。
- **有缺口**：有可复述的反例或缺项，关联问题记录。
- **已核实**：记录具体结论、来源条款和适用分支，说明验证方式。
- **不适用**：说明该项为何不适用于本重载。

每项证据应写成“结论；依据；适用范围；验证方式”。例如 TFMA 的类型项应列出六种类型及布局差异，引用固定 TFMA.asl 条款；不能仅写“已看 ISA”。正文修复后重新核对证据，才将“有缺口”改为“已核实”。八项均为已核实或不适用才可将 `closed` 设为 true。

示例的规范推导、模拟声明检查、完整实现编译、ASL执行和硬件运行分别记录。没有实现时可以完成接口设计的规范推导；实际编译及运行仍记为未执行。矩阵逐声明示例映射保存在 `audit/example_cases.json`；`check_examples.py` 从正文提取代码，检查完整函数和所选重载。数值预期按 LinxISA 锁定的硬件数值规范核对，模型执行覆盖另行记录。

## 更新与失效规则

重载 ID 由操作名和规范化完整声明的 SHA-256 前 12 位组成。空白重排保持 ID；签名变化产生新 ID，人工迁移仍然有效的证据，并保留修改原因。序号仅辅助定位。

台账记录全部 156 页的指纹。正文、公共合同、示例或导航变化都会令检查失败，提示复核受影响记录；公共规则的修改沿 `references` 反向查找重载，补查间接依赖。更新指纹前记录此次变更影响及证据处理。指纹只用于发现变化，人工决定哪些证据继续有效。

固定来源版本变化时重新核对受影响条款。现有证据保留原提交号，新增核对结论明确版本差异。

维护命令（仓库根目录）：

```sh
python clang/docs/LinxISA/audit/check_contracts.py
python clang/docs/LinxISA/audit/check_contracts.py --render
python clang/docs/LinxISA/audit/check_examples.py
```

先编辑 JSON 状态与证据，再运行检查和渲染。工具检查声明覆盖、ID、状态、证据存在性、闭合条件和文档变更；语义判断由审查者完成。生成的 Markdown 用于阅读，JSON 为维护源。

## 配套公共接口登记

274 条记录覆盖操作页的同名函数。下列公共接口也须核对，作为重载闭合的依赖；各项的本轮处理和剩余证据见 [更新记录](TileOpContractLedger.md#公共依赖)，完整依赖与局部闭合范围分别登记。它们保留在独立清单，避免构造器、builder 和操作声明混算。

| 编号 | 接口与条文入口 | 核对重点 | 状态 |
| --- | --- | --- | --- |
| C01 | [Tile、CUBE 别名、SharedTile](TileOpReference/CommonTypes.md) | 模板默认值、角色、容量推导、有效维度 getter | 已核实 |
| C02 | [global_tensor 构造与 subview](TileOpReference/CommonTypes.md#gm-视图构造与子区域) | const、步长单位、动态形状、packed 起点 | 已核实 |
| C03 | [reinterpret_tile](TileOpReference/CommonTypes.md#reinterpret_tile) | 借用、等宽 carrier、Reader 组合、操作类型 | 已核实 |
| C04 | [TileReader](TileOpReference/Reader.md) | 构造、两种 read、fragments、++、边界与生命周期 | 已核实 |
| C05 | [TileWriter](TileOpReference/Writer.md) | 构造、八种阶段方法、fragments、finish、Local/Shared 状态 | 部分范围已核实；完整项见具体缺口 |
| C06 | [PredicateTile](TileOpReference/Predicate.md)、[GPRMask](TileOpReference/TSEL.md#声明与重载) | basis、存储、掩码位映射 | 已核实 |
| C07 | [Options 与 FixpAttr](TileOpReference/Options.md) | 每个 builder/成员、组合合法性、辅助输入输出、编码；关联 W04 | 已核实；数值行为采用锁定的硬件 numeric profile |
| C08 | [make_weight_tload_params](TileOpReference/TLOAD.md#权重参数构造) | 完整参数、默认值、权重布局 | 已核实 |
| C09 | [TIMG2COLParams](TileOpReference/TIMG2COL.md#参数字) | 位域、范围、布局码、保留位 | 已核实 |
| C10 | [IndexedByteRange](TileOpReference/IndexedMemoryRules.md#indexedbyterange) | 闭区间、字节单位、包络、异常边界 | 已核实 |
| C11 | [操作数协议](TileOpReference/OperandRoles.md)、[Shared 协议](TileOpReference/CommonTypes.md#shared-操作数协议) | 角色互斥、计算视图查询、临时对象、发布 | 部分范围已核实；完整项见具体缺口 |

本轮修订、来源和未闭合项见 [合同核对更新](TileOpContractReviewUpdate.md)。

## 本轮关联问题与执行顺序

[全册复审报告](TileOpManualWholeReview.md) 的 W01–W06 已关联到对应重载；影响全体矩阵调用的 W04 关联全部矩阵声明。W05 挂在现有 groupM 重载，另需补查当前声明集合缺失的组合。W06 在共享规则和同名操作之间确定唯一归属。

先闭合公共类型与协议，再按算子族逐重载核对。每次修复同步检查本操作的其他重载和依赖同一公共合同的操作。全册验收要求：所有重载八项闭合、公共依赖闭合、问题记录已处理、结构检查通过、验证边界明确。

## 规范裁定与正文范围

本手册以 LinxISA 0.59.1 的[规范锁定文件](https://github.com/LinxISA/linx-isa/blob/7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27/isa/v0.59/pto-spec.lock.json)及其引用的操作条款为依据。数值行为采用锁定的 [pto-hardware-numeric-0.59.1-ieee-v1](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/hardware-conformance-profile.json)。各操作的专用类型、布局和编码条款与公共数值规则共同构成接口合同。Reader/Writer 和便利重载属于库设计，其参数映射按各操作页说明。

接口闭合要求声明、参数及行为与上述规范对应。参考模型覆盖、编译与硬件执行分别记录在验证项。正文描述操作行为、前置条件及结果；实现差异与历史纠错保存在核对证据中。规范条款之间尚待裁定的关系、库到指令的映射缺口继续保留为未闭合项。
