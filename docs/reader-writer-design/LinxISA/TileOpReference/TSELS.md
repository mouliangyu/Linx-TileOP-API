# TSELS

计算 `dst[r,c] = predicate[r,c] ? src_true[r,c] : false_scalar`，不读取旧 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, PredicateReadable P, Readable S>
void TSELS(D &&dst, P &&predicate, element_type_t<S> false_scalar,
           S &&src_true);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `P` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `predicate` | PredicateReadable | 支持 | 支持 | 不接受 |
| `src_true` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `predicate` | in | Predicate 输入 | 必填 |
| `false_scalar` | in | 谓词为 false 时使用的标量 | 必填 |
| `src_true` | in | 谓词为 true 时的数值输入 | 必填 |

## 操作语义

predicate 为 true 时复制 src_true 的原始载体位；为 false 时复制 false_scalar 规范化后的低位载体编码。选择保留选中编码，包括 NaN payload；数值状态保持不变。谓词、数值源与标量在目标发布前快照，payload、padding definedness 和描述符共同发布。默认 PadValue=Null。

依据：固定 PTO 规范 [TSELS.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TSELS.asl) 的 defaults、ordering、state_effects。


## 合法组合与限制

操作 dtype 为 FP64、FP32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、S/U16、S/U32、S/U64。布局支持 Local RowMajor、CUBE_M16/M32；b64 CUBE 使用 M32。源计算 dtype 与目标相同，等宽 backing 解释通过 reinterpret_tile 显式表达。类型依据 [TileSelectDataTypeSupported](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/comparison.asl) 及 [CUBE Predicate 合法性](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)。

数值输入与谓词输入分别使用 Readable 和 PredicateReadable；数值输出为 Writable。具体 basis、容量及分片约束见 [Predicate](Predicate.md)。标量和控制枚举不接受片段。

`dst[r,c] = predicate[r,c] ? src_true[r,c] : false_scalar`。[TSEL](TSEL.md) 的 false 输入为 Tile/Readable，TSELS 的 false 输入为显式标量。D/P/S 独立推导；谓词逻辑有效形状和布局与 payload 匹配；比较 basis 不限制 payload 位宽，数值源目标 dtype 相同。输入 predicate 须具有合法谓词描述符及已定义的规范值；比较及支持谓词输出的逻辑操作均可生产它。普通同 dtype 数值载体不自动获得谓词角色。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<float, 32, 8>;
using P = PredicateTile<V>;
void example(V &dst, V &src, P &predicate) {
  TSELS(dst, predicate, 0.0f, src);
}
```

src 和 predicate 均已定义，predicate 的 basis 与 V 匹配，dst 独立。 谓词为 true 的位置取 src，其余位置为 0。

## 公共规则与相关接口

本接口同时遵守 [Scalar 公共参数、类型、形状、别名及示例](ScalarRules.md)。该页中的规则与本页声明共同构成调用合同。

**谓词类型和分片：** [Predicate](Predicate.md)。

[返回算子索引](README.md)
