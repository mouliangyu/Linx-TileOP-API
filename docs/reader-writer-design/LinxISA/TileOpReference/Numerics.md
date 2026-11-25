# 数值、舍入与编码参考

本手册以 LinxISA 0.59.1 的[规范锁定文件](https://github.com/LinxISA/linx-isa/blob/7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27/isa/v0.59/pto-spec.lock.json)及其引用的操作条款为依据。数值行为采用锁定的 [pto-hardware-numeric-0.59.1-ieee-v1](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/hardware-conformance-profile.json)。各操作的专用类型、布局和编码条款与公共数值规则共同构成接口合同。Reader/Writer 和便利重载属于库设计，其参数映射按各操作页说明。

## TCVT 类型配对

普通类型集合为 FP64、FP32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E3M2、E2M3，以及 S8/S16/S32/S64、U8/U16/U32/U64、S4X2/U4X2。集合内源与目标可独立选择，并满足 [TCVT 形状和布局](CompareConvertRules.md#tcvt)。S4X2/U4X2 按逻辑4位元素转换。下表列出其余类型的完整配对规则。

| 特殊类型 | 合法另一侧 | 限制 |
| --- | --- | --- |
| E8M0 | FP16/BF16/FP32 | 双向 |
| E6M2 | FP16/BF16 | 双向，仅 RNE/RNA |
| RCPE6M2 | FP16/BF16 | 仅作源，仅 RNE/RNA |
| E2M1X2/E1M2X2 | FP16/BF16/FP32 | 恰好一侧为 packed |
| HiF4X2 | 无 | TCVT 排除此类型 |

配对依据：[HardwareTCVTTypePairSupported](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/e8m0-conversion.asl)、[TCVT 类型与布局合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/format-conversion/TCVT.asl)。数值按源格式解码、目标格式舍入和编码；HiF8 的数值 1 编码为 `0x08`，FP32 的数值 1 编码为 `0x3f800000`。

舍入模式编码、默认值及同类型 round-integral 行为见 [TCVT 参数与操作数角色](TCVT.md#参数与操作数角色)。

公共 TCVT 使用 Sat=0，通过 RMode 选择舍入。整数转整数溢出时保留目标位宽的低位；无效浮点转整数返回目标类型的 indefinite 值并记录 NV：有符号类型为最小值，无符号类型为最大值。例如 NaN→S32 返回 `0x80000000`，NaN→U32 返回 `0xffffffff`。浮点输出的溢出遵守目标格式规则。

ISA 的 Sat=1 将整数算术及转换钳制到目标最小/最大值，NaN 转整数为0，浮点溢出钳制到最大有限值。公共 TCVT 的模板参数列表见[声明](TCVT.md#声明与重载)。

## E8M0、E6M2 与 HiF4 scale

E8M0 是指数 scale，代码 0..254 表示 `2^(code-127)`，255 为 NaN，无数学零编码。转 E8M0 时零、负数、NaN 产生 0xff 并置 NV；正有限值按舍入模式量化二进制指数。E8M0 的 0xff 转浮点产生 canonical quiet NaN，不额外置 NV。不能用原始全零 padding 表示该格式的数学零。

HiF4 的 U32 scale 字：[7:0] 为 E6M2，[15:8] 为 E1_8，[31:16] 为 E1_16。E6M2 00..FE 为有限值（指数偏置 48、两位小数），FF 为 quiet NaN。组内 lane q 的指数另外加 E1_8[floor(q/8)] 与 E1_16[floor(q/4)]。该字服务于每 64 个 K 元素的 HiF4X2 Matrix-MX，不能当普通 float scale。

CScale 与上述两者不同：U8 code 直接表示 C 乘 `2^-code`，见 [Options](Options.md)。

## 异常值、状态和精度

TCVT 发布时汇总各有效元素的 NV/DZ/OF/UF/NX 状态；padding 与无效 mask 元素不等于数学输入。转换的零/NaN/无穷处理须按具体格式解释，不按 backing uint8_t 的整数含义解释。

TEXP/TLOG/TRECIP/TSQRT/TRSQRT 的近似精度、NaN 传播、浮点规约次序和融合细节依赖其规范与 numeric profile。接口文档中的 exp/sum 等公式描述数学意图，不承诺逐位 libm 等价。若算法需要误差或逐位保证，应固定目标 profile 并使用该 profile 的数值约束；本次未运行数值测试。

## 固定版本规范

- [TCVT 类型、默认舍入、状态和错误](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/docs/tile/elementwise-tile-tile/format-conversion/TCVT.md)
- [矩阵 scale、CScale 与后续修订](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/docs/status/decisions/ADR-CUBE-0012-matrix-scale-and-cscale.md)
- [数值格式](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/docs/arch/data-types/numeric-formats.md)

## 逐元素执行合同

下列定义以本页固定 PTO 提交为准。逐元素及标量操作采用相同的元素函数；广播仅改变源坐标。计算使用所选操作 dtype；整数加减乘按该位宽取模，逻辑运算保留低位且不产生数值状态。浮点加减乘除由 `TileProfileBinaryWithFlags` 调用 `ScalarFPBinaryProfile`，默认控制使用 RNE。浮点 REM 采用 `ReferenceTileFloatingModulo`。MIN/MAX 通过 `TileFloatingMinMaxValue` 使用 `HardwareNumericFloatingMinMax` 的 NaN、符号零和 invalid 选择规则。

这些函数同时定义结果与状态位，具体 profile 的编码规则构成本接口的逐位数值依据。低精度计算逐元素使用其操作 dtype，不隐式提升为 FP32；TEXPDIF 的显式混合精度配对单独规定。

依据：[TileProfileBinaryWithFlags、TileIntegerDivRemValue、TileSignedModulo](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/elementwise.asl)；[TileFloatingMinMaxValue](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/minmax.asl).

## 数学函数边界

| 操作 | 已定义的特殊输入结果 |
| --- | --- |
| TEXP | ±0→+1，+∞→+∞，−∞→+0；NaN→quiet NaN，signaling NaN记录invalid |
| TLOG | +1→+0，±0→−∞并记录divide-by-zero；负非零→quiet NaN并记录invalid；signaling NaN记录invalid |
| TRECIP | ±0→同号∞并记录divide-by-zero，±∞→同号0；NaN→quiet NaN，signaling NaN记录invalid |
| TSQRT | 保留±0和+∞；负非零→quiet NaN并记录invalid；signaling NaN记录invalid |
| TRSQRT | ±0→同号∞并记录divide-by-zero，+∞→+0；负非零→quiet NaN并记录invalid |
| TRELU | signaling NaN产生profile quiet NaN并记录invalid；其他值按同类型rectifier定义 |

无穷结果使用该格式可表示的编码；误差界和其余逐位规则由固定指令的numeric profile确定。状态在完整合法性预检后与结果一起发布。

- [TRELU exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/logical/TRELU.asl)
- [TEXP exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TEXP.asl)
- [TLOG exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TLOG.asl)
- [TRECIP exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TRECIP.asl)
- [TRSQRT exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TRSQRT.asl)
- [TSQRT exceptions/state_effects](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/transcendental/TSQRT.asl)

## 浮点公共行为

浮点运算遵守 IEEE 754-2019 及各低精度格式的专用规则。融合运算对精确乘加表达式只舍入一次；默认舍入为 RNE。支持次正规数的格式保留次正规输入，结果采用渐进下溢，在舍入后判定微小值。

结果格式具有 NaN 编码时，产生的 NaN 使用该格式的 canonical NaN。支持双符号零的格式保留 IEEE 符号零；HiF8 使用单一零编码。invalid、divide-by-zero、overflow、underflow、inexact 按操作规定汇总到架构状态。矩阵累加顺序见[矩阵公共规则](MatrixRules.md#数值规则)。

依据：[硬件数值规范 arithmetic、subnormal_policy、b_datr](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/hardware-conformance-profile.json)。
