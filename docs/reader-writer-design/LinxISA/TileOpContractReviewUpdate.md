# TileOP 合同核对更新（2026-11-24）

## 范围与状态

全册135个操作、274条重载、156页参考文档。271条重载八维闭合，3条未闭合。2192个核对维度中2186项已核实，6项保留缺口，待核对与仅登记均为0。

## 本批修正

以 LinxISA 锁定的硬件数值规范裁定矩阵行为，补充递增K、逐项融合舍入、ACC初值、点积后BIAS、MX scale解码、异常值及状态发布。90条矩阵重载完成语义核实和公共依赖绑定，M-NUM阻塞解除。模型测试覆盖在核对证据中单列。

手册正文使用行为描述；MatrixRules、Numerics、Options、TMATMUL_ACC、TCVT、TMOV、Writer及总览中的核对过程说明已整理。TCVT补齐完整配对集合；Shared ND Writer明确两步展开并补充完整例。

## 剩余核对项

| 范围 | 重载数 | 待完成内容 |
| --- | ---: | --- |
| Shared TLOAD、Local→Shared TMOV、CUBE→Shared专用入口 | 3 | Shared continuation与每PE单次加入generation已核实；跨调用点first/middle/last的请求与arrival关系待明确 |

## 依据与验证

LinxISA提交 `7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27` 的锁定文件引用 PTO提交 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`，硬件数值profile为 `pto-hardware-numeric-0.59.1-ieee-v1`，下载文件的SHA-256与锁定值一致。具体来源和历史分析见[核对证据](TileOpContractEvidence.md#linxisa-规范裁定当前)。

本批检查全册结构、链接、声明清单及证据指纹。既有37个示例代码块、156个映射调用、90条矩阵声明的模拟检查记录保留。完整库编译、ASL测试执行和硬件运行均未执行。

## 五条余项复核结果

TCVT与Shared→Local ND TMOV各闭合一条。前者补齐11种普通浮点、10种整数及特殊类型配对表；后者定义Shared读取到完整Local临时值、Local TMOV提交Writer的两步库展开。三条Shared生产重载保留同一个规范映射问题，具体条文与结论见[五条复核证据](TileOpContractEvidence.md#剩余五条重载复核)。
