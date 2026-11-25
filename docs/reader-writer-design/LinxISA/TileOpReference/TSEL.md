# TSEL

`dst[r,c] = mask[r,c] ? when_true[r,c] : when_false[r,c]`。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 重载 | mask 实参 | 用途 |
| --- | --- | --- |
| 谓词 Tile | PredicateReadable | 按谓词计算视图逐元素选择 |
| 单 word GPR | `uint64_t` | 按单 word 位掩码选择 |
| 双 word GPR | `predicate::GPRMask` | 按 low/high 位掩码选择 8 位元素 |

```cpp
template <Writable D, PredicateReadable P, Readable T, Readable F>
void TSEL(D &&dst, P &&mask, T &&when_true, F &&when_false);

template <Writable D, Readable T, Readable F>
void TSEL(D &&dst, uint64_t mask, T &&when_true, F &&when_false);

template <Writable D, Readable T, Readable F>
void TSEL(D &&dst, predicate::GPRMask mask, T &&when_true, F &&when_false);
```

```cpp
namespace predicate {
struct GPRMask { uint64_t low; uint64_t high; };
}
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | dst 的输出计算视图类型 | 由实参推导 |
| `P` | 谓词 Tile 重载中 mask 的谓词计算视图类型 | 由实参推导 |
| `T` | when_true 的输入计算视图类型 | 由实参推导 |
| `F` | when_false 的输入计算视图类型 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `mask`（谓词 Tile 重载） | PredicateReadable | 支持 | 支持 | 不接受 |
| `when_true` | Readable | 支持 | 支持 | 不接受 |
| `when_false` | Readable | 支持 | 支持 | 不接受 |

所有重载均显式提供 dst、mask、when_true 和 when_false。GPR 重载的 mask 是值传递的标量掩码，分别使用 `uint64_t` 或含 low/high 两个 word 的 `GPRMask`。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `mask` | in | 掩码输入；编码按本页重载及谓词合同 | 必填 |
| `when_true` | in | 谓词为 true 时的输入 | 必填 |
| `when_false` | in | 谓词为 false 时的输入 | 必填 |

## 操作语义

`dst[r,c] = mask[r,c] ? when_true[r,c] : when_false[r,c]`。输出保留选中源元素的原始位，包括NaN payload；选择不产生numeric flags，默认Null padding未定义。完整预检和输入快照先于目标发布。动态输出有效形状从数值源记录。

GPR 掩码按列存放谓词位。`row`、`column` 为计算视图内从零开始的逻辑坐标；M16 的 `row_bits=16`，M32 的 `row_bits=32`。令 `columns_per_word = 64 / row_bits`，则：

```text
word_index = column / columns_per_word
bit_index  = row + (column % columns_per_word) * row_bits
```

单 word 重载从 `mask` 的 bit_index 位取谓词。双 word 重载在 word_index 为 0 时读取 `mask.low`，为 1 时读取 `mask.high`。例如 M16 U8 的 `(row=0, column=4)` 对应 high 的第 0 位；M32 U8 的 `(row=0, column=2)` 同样对应 high 的第 0 位。可用行列范围见下文 GPR 掩码表。

## 合法组合与限制

### 数值操作数与谓词

操作类型取输出计算视图 dtype；两个数值源分别与它等元素位宽，允许异类型原始位载体。数值计算视图的物理形状、布局和有效形状一致。支持非 boxed Local RowMajor、CUBE_M16/M32；元素位宽为 8、16、32、64 位，M16 使用 8、16、32 位。dtype 包括 FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8/16/32/64；RowMajor 源还允许 HiF8、E3M2、E2M3、E8M0 等宽载体。

PredicateCell 与数值源具有相同布局和逻辑有效形状，谓词物理列数可以不同。比较 basis 与所选数值的类型、位宽独立。有效谓词须已定义且为规范 0/1，详见 [谓词](Predicate.md)。

普通 Tile 允许目标与任一数值源 alias，观察写入前的源值。Writer 输出描述用于 dst，parent 的读取遵循 [Writer 生命周期](Writer.md)。

### GPR 掩码

GPR 形式支持 Local CUBE_M16/M32。操作类型取输出计算 dtype：FP32/TF32/HF32/FP16/BF16/S32/S16/U32/U16 使用一个 uint64_t；M32 另允许 FP64/S64/U64。8 位操作类型为 U8、S8、E4M3、E5M2，使用 GPRMask 两个 word。输入 backing 可使用与操作类型等位宽的原始位载体。

| 布局 | 最大有效行 | 8 位列（双 word） | 16 位列 | 32 位列 | 64 位列 |
| --- | --- | --- | --- | --- | --- |
| M16 | 16 | 8 | 4 | 2 | — |
| M32 | 32 | 4 | 2 | 2 | 2 |

表中列数为各操作位宽支持的最大有效列数。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<float, 32, 8>;
using P = PredicateTile<V>;
void choose(V &dst, V &left, V &right) {
  P p;
  TCMP<CmpMode::LT>(p, left, right);
  TSEL(dst, p, left, right);
}
```

输入已定义时，每个输出位置选择较小输入的原始位（NaN 由比较规则决定）。

### 单 word 与双 word GPR 重载

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using F = VecTileM32<float, 32, 2>;
using B = VecTileM16<int8_t, 16, 8>;
void single_word(F &dst, F &yes, F &no) {
  TSEL(dst, uint64_t{1} << 31, yes, no);
}
void two_words(B &dst, B &yes, B &no) {
  TSEL(dst, predicate::GPRMask{0, uint64_t{1} << 15}, yes, no);
}
```

yes全1、no全2，输入已定义、输出独立。single_word仅[31,0]取1；two_words仅[15,4]取1；其他位置取2。单word与双word示例分别覆盖M32的两列FP32和M16的八列S8。四类8位dtype共用双word编码；每个数值输入仍独立满足载体合法性。

## 公共规则与相关接口

公共合同：[操作数角色](OperandRoles.md)、[谓词](Predicate.md)、[Writer 生命周期](Writer.md)。

相关接口：[TCMP](TCMP.md)、[TCMPS](TCMPS.md)。

依据：[PTO-C 0.59 TSEL](https://linxisa.github.io/PTO-C/#TSEL)。

八位 GPR 域依据：[TileCubePredicateGPRDataTypeSupported](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)、[TCMPS/TSELS dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tile-scalar-schema.asl) 及 [四类八位编码测试](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/tests/asl/tile/model/execution/predicate-carriers/tile-exec-gpr-mask-eight-bit-001.asl)。

[返回算子索引](README.md)
