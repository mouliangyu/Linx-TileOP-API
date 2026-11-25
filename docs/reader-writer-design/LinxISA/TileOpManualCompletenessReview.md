# 接口信息完整性核查

> 0.59 修订说明：本文早期审查记录中的三参数 TSEL、118 项目录及 Shared 分片禁用结论已被更新。当前合同以 [接口参考](TileOpReference/README.md) 为准：TSEL 显式传入 true/false；119 项活动操作；Shared Reader/Writer 按存储合同使用；矩阵使用完整角色声明。


本轮修正的是新接口手册合同，不表示对应库和编译器已经实现。示例未编译或在硬件执行。

| 项目 | 修正结果 | 正文 |
| --- | --- | --- |
| GM 类型和权限 | 定义 GlobalMemoryView，保留元素 const，明确读写要求 | [公共类型](TileOpReference/CommonTypes.md) |
| GM 构造与子区域 | 补静态/运行时构造、元素行距、subview 和 packed 起点限制 | [公共类型](TileOpReference/CommonTypes.md#gm-视图构造与子区域) |
| 重复旧签名 | 删除已提供独立协议签名的同类型旧声明；同步标量、TFMA 等参数说明 | [操作数协议](TileOpReference/OperandRoles.md) |
| 动态有效维度 | 各轴零值回退到输入计算视图；输出形状与对象元数据按各操作说明，不设静态结果匹配的通用限定 | [有效维度](TileOpReference/CommonTypes.md#有效维度与输出元数据) |
| GMOV peer_tid | 核实绝对 PE 编号 0..3，补重复选择、环形接收及目标 mask 示例 | [GMOV](TileOpReference/GMOV.md) |
| 谓词 | 定义 PredicateTile 及输入输出协议、basis、存储/逻辑形状区别 | [Predicate](TileOpReference/Predicate.md) |
| 分片几何 | 明确归约域、ARG 局部索引、广播轴、转换容量、重排 word/segment、序列原点 | [分片几何](TileOpReference/FragmentGeometry.md) |
| Shared 与矩阵 | 明确本版接口接收完整角色 Tile，Local 分片不替代 Shared 发布；保留真实 C→D 链 | [操作边界](TileOpReference/StorageBoundaries.md) |
| 声明与角色表 | 支持的输入/输出改为对应协议，禁止将输出声明为 Readable；保留 TSEL 完整读写目标 | 各算子页 |

GMOV 及谓词核对依据：PTO-ISA/pto-spec 提交 a89a53d48f5708328be609fe2e6296ac8bdb4bc2 的 BSTART.GMOV 和 predicate-carriers 规范。其余新增库协议是本手册定义的 API，不将旧 wrapper 的实现缺陷作为设计合同。

验证包括本地链接/锚点、代码块闭合、操作入口覆盖、重复同名声明以及输出协议方向检查。数值异常、近似精度及架构 fault 仍引用各操作的数值和 ISA 合同，不将文档检查称为编译或数值验证。


## 2026-11-24：结构整理后的语义待决项

Writer Part 与消费操作的维度绑定已在 [Writer](TileOpReference/Writer.md#维度与范围绑定) 统一：Part 物理容量绑定 WriterSizeCode；有效计算区域由操作的输入、目标或专用形状规则选择；Parent 保留最终形状和目标身份。TADD 的 4 行输出描述与 16 行输入默认值案例已明确说明。索引 GM 的 Null padding 及访问失败原子边界保留为独立 ISA 复核项。
