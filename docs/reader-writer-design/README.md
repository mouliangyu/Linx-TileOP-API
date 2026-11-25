# TileOP 新接口：网站更新材料

关联：[LinxISA/Linx-TileOP-API#335](https://github.com/LinxISA/Linx-TileOP-API/issues/335)。快照日期：2026-11-25。

## 当前接口正文

- [全量接口手册与操作索引](LinxISA/TileOpReference/README.md)：135个操作页、21个公共页。
- [Reader](LinxISA/TileOpReference/Reader.md)、[Writer](LinxISA/TileOpReference/Writer.md)：公开声明、阶段、动态形状、迭代器、Shared合同。
- [参数角色](LinxISA/TileOpReference/OperandRoles.md)、[分片几何](LinxISA/TileOpReference/FragmentGeometry.md)、[存储边界](LinxISA/TileOpReference/StorageBoundaries.md)。
- [公共类型](LinxISA/TileOpReference/CommonTypes.md)、[Options](LinxISA/TileOpReference/Options.md)。

## 核对与勘误

- [覆盖清单](LinxISA/TileOpManualCoverage.md)。
- [逐重载核对表](LinxISA/TileOpContractLedger.md)及[机器可读台账](LinxISA/TileOpContractLedger.json)：274条重载、271条闭合，3条Shared提交映射搁置。
- [证据记录](LinxISA/TileOpContractEvidence.md)及[核对流程](LinxISA/TileOpContractReview.md)。
- [全册复核](LinxISA/TileOpFullReview20261125.md)、[第二轮复核及三项修正](LinxISA/TileOpFullReview20261125Round2.md)。
- [验证脚本](LinxISA/audit/)；示例和重载检查使用声明/type mock。

## 网站迁移约定

最终交付目标为 https://linxisa.github.io/PTO-C/ 。网页沿用现有“简介、数学语义、C++接口、约束与默认值、示例、Bundle对照、参考”的结构。将本快照接口内容映射到网站各节，具体迁移与验收要求见issue #335。本快照的六节Markdown结构供内容审阅，网站格式以issue中的最新要求为准。

`LinxISA/TileOpReference/`为当前接口正文。目录外文件保留设计推导、历次审查和验证证据；其中早期接口指南、编写计划、builtin研究以及独立BEGIN/END方案作为历史或备选设计阅读。接口查询优先使用当前正文；独立BEGIN/END方案单独记录，当前Writer仍将INIT/LAST绑定到计算操作。

材料为完整文档快照，尚未部署网站。台账中的实现验证边界和三项搁置问题继续保留。
