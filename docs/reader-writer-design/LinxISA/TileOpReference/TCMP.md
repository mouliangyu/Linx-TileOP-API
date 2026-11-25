# TCMP

对每个有效位置按 Mode 比较 src0 与 src1，将布尔结果写入 Predicate 输出。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <CmpMode Mode, PredicateWritable D,
          Readable A, Readable B>
void TCMP(D &&dst, A &&src0, B &&src1);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Mode` | 比较枚举 EQ/NE/LT/GT/LE/GE | 显式指定 |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | PredicateWritable | 支持 | 不接受 | 支持 |
| `src0` | Readable | 支持 | 支持 | 不接受 |
| `src1` | Readable | 支持 | 支持 | 不接受 |

Mode 是必填编译期枚举：EQ(==)、NE(!=)、LT(<)、GT(>)、LE(≤)、GE(≥)。dst 为 out，src0/src1 为 in，无普通参数默认值。A/B 为数值输入载体，D 为合法谓词载体。输出每个逻辑位置表示对应的比较结果。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |

## 操作语义

对每个有效位置按 Mode 比较 src0 与 src1，将布尔结果写入 Predicate 输出。

## 合法组合与限制

Predicate 使用架构定义的谓词布局，物理存储规则见 [Predicate](Predicate.md)。浮点NaN比较仅NE为true；signaling NaN记录invalid，正负零比较相等。Mode编码EQ/NE/LT/GT/LE/GE为0..5，6/7保留。输入快照先于谓词、padding和状态的原子发布，默认Null padding未定义。

src0、src1 使用 Readable 数值计算视图，dst 使用 PredicateWritable 谓词计算视图。Mode 为编译期比较枚举。具体 basis、容量及分片约束见 [Predicate](Predicate.md)。

两个数值源的计算几何须匹配；谓词输出与数值源匹配逻辑有效行列、布局和比较 basis。谓词自身的物理列数、容量及 packing 按 Predicate 布局独立推导。数值源允许等位宽非 packed backing 重解释；比较的操作数值类型由源合同确定。输入类型为 FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、16、32、64；packed 4-bit 不参与等位宽重解释规则。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<float, 32, 8>;
using P = PredicateTile<V>;
void example(P &dst, V &a, V &b) {
  TCMP<CmpMode::LT>(dst, a, b);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 a 全为 1、b 全为 2 时，各有效谓词为 true。

## 公共规则与相关接口

本接口同时遵守 [CompareConvert 公共参数、类型、形状、别名及示例](CompareConvertRules.md)。该页中的规则与本页声明共同构成调用合同。

**谓词类型和分片：** [Predicate](Predicate.md)。

[返回算子索引](README.md)
