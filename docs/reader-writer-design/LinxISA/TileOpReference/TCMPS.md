# TCMPS

对每个有效位置按 Mode 比较 src 与标量 s；Tile 重载产生 Predicate 输出，GPR 重载返回编码后的 uint64_t 掩码。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 重载 | 调用形式 | 结果 |
| --- | --- | --- |
| 谓词 Tile | `TCMPS<Mode>(dst, src, s)` | 写入 dst |
| GPR | `TCMPS<Mode, High>(src, s)` | 返回 uint64_t 掩码 |

```cpp
template <CmpMode Mode, PredicateWritable D, Readable S>
void TCMPS(D &&dst, S &&src, element_type_t<S> s);

template <CmpMode Mode, bool High = false, Readable S>
uint64_t TCMPS(S &&src, element_type_t<S> s);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Mode` | 比较枚举 EQ/NE/LT/GT/LE/GE | 显式指定 |
| `D` | 谓词 Tile 重载的目标计算视图类型 | 由实参推导 |
| `S` | 数值源 src 的计算视图类型 | 由实参推导 |
| `High` | GPR 重载中选择 8 位比较结果的高半部 | `false` |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst`（谓词 Tile 重载） | PredicateWritable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 适用重载 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- | --- |
| `dst` | 谓词 Tile | out | 接收逐元素比较结果的谓词计算视图 | 必填 |
| `src` | 全部 | in | 已定义的数值输入计算视图 | 必填 |
| `s` | 全部 | in | 与全部有效元素比较的标量，类型为 element_type_t<S> | 必填 |

## 操作语义

全部有效元素分别与标量 s 按 Mode 比较。浮点 NaN 比较仅 NE 为 true，signaling NaN 记录 invalid；正负零比较相等。谓词 Tile 重载将逐元素结果写入 dst；GPR 重载将结果编码为 uint64_t 返回。

### GPR 返回值编码

`row`、`column` 为输入计算视图内从零开始的逻辑坐标。M16 的 `row_bits=16`，M32 的 `row_bits=32`。令 `columns_per_word = 64 / row_bits`，返回值中的位号为：

```text
bit_index = row + (column % columns_per_word) * row_bits
```

比较成立时对应位为 1，否则为 0。8 位操作类型的 High 选择下表中的逻辑列范围；实际参与比较的位置受输入有效行列限制。

| 布局 | High=false | High=true |
| --- | --- | --- |
| M16 8 位 | 第 0..3 列 | 第 4..7 列 |
| M32 8 位 | 第 0..1 列 | 第 2..3 列 |

其他操作类型使用 High=false，有效列范围见下节。例如 M16 U8 的 `(row=0, column=4)` 编码到 High=true 返回值的第 0 位。两次 8 位比较返回的低、高 word 分别对应 [TSEL 的 GPRMask.low/high](TSEL.md#操作语义)。

## 合法组合与限制

RowMajor packed Predicate 输出的操作类型为 FP64、FP32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、S/U16、S/U32、S/U64。

CUBE PredicateTile 输出形式支持 FP32、TF32、HF32、FP16、BF16、E4M3、E5M2、S32、S16、S8、U32、U16、U8；CUBE_M32 另支持 FP64、S64、U64。其 basis 为操作 dtype，存储为规范 U8 PredicateCell。操作 dtype 与 backing 分别校验；通过 reinterpret_tile 选择跨类型解释时须等位宽且为非四位 carrier。M32 的 b64 backing 使用每逻辑列两个 CELL。


GPR 形式的有效形状按下表限定。有效列数从 1 起，每次调用返回一个 64 位 word。

| 布局 | 有效行数 | 8 位最大有效列数 | 16 位最大有效列数 | 32 位最大有效列数 | 64 位最大有效列数 |
| --- | --- | --- | --- | --- | --- |
| M16 | 1..16 | 8 | 4 | 2 | — |
| M32 | 1..32 | 4 | 2 | 2 | 2 |

表中的位宽适用于下述受支持的操作类型；“—”表示该组合不可用。

数值源 src 使用 Readable；谓词 Tile 重载的 dst 使用 PredicateWritable。具体 basis、容量及分片约束见 [Predicate](Predicate.md)。s 为标量值，Mode 与 High 为编译期控制参数。

GPR 形式要求 Vec 位置、CUBE_M16/M32、正有效区域；操作类型支持 FP32/TF32/HF32/FP16/BF16/S32/S16/U32/U16/U8/S8/E4M3/E5M2；M32 另支持 FP64/S64/U64。操作类型由 src 的计算 dtype 决定。High=true 适用于 U8/S8/E4M3/E5M2；其他操作类型使用 High=false。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<float, 32, 8>;
using P = PredicateTile<V>;
void example(P &dst, V &src) {
  TCMPS<CmpMode::LT>(dst, src, 2.0f);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src 全为 1 时，各有效谓词为 true。

### U8 双 word 掩码与选择

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using U8 = VecTileM16<uint8_t, 16, 8>;
void select_below(U8 &dst, U8 &src, U8 &fallback) {
  predicate::GPRMask mask{
      TCMPS<CmpMode::LT, false>(src, uint8_t{128}),
      TCMPS<CmpMode::LT, true>(src, uint8_t{128})};
  TSEL(dst, mask, src, fallback);
}
```

src 与 fallback 的全部有效元素已初始化，dst 为独立输出对象。每个位置在 src 小于 128 时保留 src，否则选择 fallback；low 覆盖第 0..3 列，high 覆盖第 4..7 列。

## 公共规则与相关接口

本接口同时遵守 [CompareConvert 公共参数、类型、形状、别名及示例](CompareConvertRules.md)。该页中的规则与本页声明共同构成调用合同。

**谓词类型和分片：** [Predicate](Predicate.md)。

形状与编码依据：LinxISA 0.59.1 所引用 PTO 规范的 [GPR 形状检查](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)（TileCubePredicateGPRShapeLegalAs、TileCubePredicateRowBits、TileCubePredicateFieldCount）及 [比较结果编码](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/predicate-carriers.asl)（TileCompareCUBEScalarToGPRAs）。

类型依据：LinxISA 引用的 PTO 规范中 PredicateCell 与 GPR 的类型合法性条款。参考 [TCMPS.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TCMPS.asl) 的 PredicateCell 与 GPR legality 分支。

RowMajor 类型与比较规则依据 [TileCompareDataTypeSupported / TileProfileFloatingCompare](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/comparison.asl)。

八位 GPR 域依据：[TileCubePredicateGPRDataTypeSupported](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)、[TCMPS/TSELS dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tile-scalar-schema.asl) 及 [四类八位编码测试](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/tile/model/execution/predicate-carriers/tile-exec-gpr-mask-eight-bit-001.asl)。

[返回算子索引](README.md)
