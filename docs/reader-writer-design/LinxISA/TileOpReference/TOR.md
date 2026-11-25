# TOR

对有效区域逐元素计算 `dst[r,c] = x | y`，其中 x=src0[r,c]、y=src1[r,c]。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 输入组合 | 输出种类 | UserValidCol/Row 为零时的来源 |
| --- | --- | --- |
| Numeric、Numeric | Numeric | src0 |
| Predicate、Predicate | U8-basis Predicate | src0 的 U8 存储视图 |
| Predicate、Numeric U8 | Numeric U8 | src1 |
| Numeric U8、Predicate | Numeric U8 | src0 |

非零维度参数逐轴覆盖表中默认值。Numeric/Numeric 重载按数值 dtype 校验几何；包含 Predicate 的重载按本页 PredicateCell 的 U8 存储几何合同校验。

本页按下列顺序列出全部重载；实参类型与参数列表共同决定选择。各重载的存储角色和专用要求见后文。

```cpp
template <Writable D, Readable A, Readable B>
void TOR(D &&dst, A &&src0, B &&src1,
          unsigned UserValidCol = 0, unsigned UserValidRow = 0,
          unsigned UserPhysicalCol = 0);
```

```cpp
template <PredicateWritable D, PredicateReadable A, PredicateReadable B>
void TOR(D &&dst, A &&src0, B &&src1,
          unsigned UserValidCol = 0, unsigned UserValidRow = 0,
          unsigned UserPhysicalCol = 0);

template <Writable D, PredicateReadable A, Readable B>
void TOR(D &&dst, A &&src0, B &&src1,
          unsigned UserValidCol = 0, unsigned UserValidRow = 0,
          unsigned UserPhysicalCol = 0);

template <Writable D, Readable A, PredicateReadable B>
void TOR(D &&dst, A &&src0, B &&src1,
          unsigned UserValidCol = 0, unsigned UserValidRow = 0,
          unsigned UserPhysicalCol = 0);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable/PredicateWritable | 支持 | 不接受 | 支持 |
| `src0` | Readable/PredicateReadable | 支持 | 支持 | 不接受 |
| `src1` | Readable/PredicateReadable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一个输入，种类由重载确定 | 必填 |
| `src1` | in | 第二个输入，种类由重载确定 | 必填 |
| `UserValidCol` | in | 本次计算列数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserValidRow` | in | 本次计算行数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserPhysicalCol` | in | 本次物理列数，元素单位；0 保留计算视图物理列 | 0 |

## 操作语义

对有效区域逐元素计算 `dst[r,c] = x | y`，其中 x=src0[r,c]、y=src1[r,c]。不读取旧 dst，不广播。

## 合法组合与限制

物理列参数见 [物理列覆写](CommonTypes.md#物理列覆写)。

类型、布局及数值要求见 [Elementwise 公共规则](ElementwiseRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

### PredicateCell 重载

以下限制仅适用于 PredicateCell 重载。仅用于 Local CUBE_M16/M32、U8 操作类型，不接受 RowMajor packed Predicate。两个 PredicateCell 输入产生 PredicateCell 输出，输出 basis 必须为 U8；不继承输入的比较 basis。一个 PredicateCell 与一个 Numeric U8 输入产生 Numeric U8 输出，两种输入顺序都支持。输入谓词必须已定义且字节为规范 0/1，输入原比较 basis 不决定本次位运算类型。

各计算视图须符合 U8 位运算的物理/有效几何与布局要求；谓词按自身 U8 存储几何校验，不能用其原数值 basis 的容量代替。有效维度按「声明与重载」中的重载表选择，物理列覆写沿用本页数值重载的规则。Predicate 输出使用谓词 padding 合同，混合输出使用 Numeric U8 合同。


Writer Part 必须满足结果种类及 basis，未完成 Writer 仍不能作为输入。谓词输出类型示例为 `PredicateTile<VecTileM32<uint8_t, 32, 4>>`；由 FP32 比较得到的谓词输入不会使输出变为 FP32 basis。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 32, 32>;
void example(V &dst, V &src0, V &src1) {
  TOR(dst, src0, src1);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src0 全为 6、src1 全为 2 时，有效输出全为 6。

### PredicateCell 与混合重载

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using N = VecTileM32<uint8_t, 32, 4>;
using F = VecTileM32<float, 32, 4>;
using InputPredicate = PredicateTile<F>;
using OutputPredicate = PredicateTile<N>;
void predicates(OutputPredicate &dst, InputPredicate &p, InputPredicate &q) {
  TOR(dst, p, q);
}
void predicate_numeric(N &dst, InputPredicate &p, N &x) {
  TOR(dst, p, x);
}
void numeric_predicate(N &dst, N &x, InputPredicate &p) {
  TOR(dst, x, p);
}
```

p由合法比较产生且全true，q全false，x全为U8的2；每个函数的输出独立。predicates的结果全true，basis为U8；两个混合函数结果全为3。谓词布局与逻辑有效形状保持32×4，按各自存储几何校验。RowMajor packed谓词不满足这些专用重载。

## 公共规则与相关接口

[Elementwise 公共规则](ElementwiseRules.md) · [操作数协议](OperandRoles.md)。

[返回算子索引](README.md)
