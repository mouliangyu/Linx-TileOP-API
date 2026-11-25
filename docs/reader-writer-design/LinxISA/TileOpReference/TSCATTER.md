# TSCATTER

先将目标物理存储初始化为全零位，再执行 `dst[off[r,c],c] = src[r,c]`；不读取旧 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S, Readable I>
void TSCATTER(D &&dst, S &&src, I &&off);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `I` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |
| `off` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |
| `off` | in | Local 逻辑行索引，非字节偏移 | 必填 |

## 操作语义

先将目标物理存储初始化为全零位，再执行 `dst[off[r,c],c] = src[r,c]`；不读取旧 dst。

## 合法组合与限制

源和索引有效形状相同；目标有效行数独立指定且为正，目标有效列数等于源。B.DIM 的有效行列取目标计算视图，Reader 输入各自保持其有效形状。

先以全零 carrier 初始化本次目标计算视图，再执行 `dst[off[r,c],c] = src[r,c]`。dst 为 out，**不读取旧值**；src/off 为 in，二者有效形状相同。目标列数等于源有效列数，索引必须小于目标有效行数；同一列中两个源元素不能指向同一目标行。不同列的同一个行号不构成冲突。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 32, 32>;
void example(V &dst, V &src, V &rows) {
  TSCATTER(dst, src, rows);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src[r,c]=100*r+c、rows[r,c]=31-r 时，dst[r,c]=100*(31-r)+c；每列索引为排列，无重复目标。

### 不同行数与重复索引

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Source = Tile<Location::Vec, uint32_t, 2, 32>;
using Output = Tile<Location::Vec, uint32_t, 4, 32>;
void expand_rows(Output &dst, Source &src, Source &index) {
  TSCATTER(dst, src, index);
}
```

src[0,c]=10+c、src[1,c]=20+c，index[0,c]=2、index[1,c]=3 时，输出前两行全零，后两行分别为10+c、20+c。若同列两个index都为2，重复目标预检拒绝整次操作。两侧物理容量分别256B和512B；索引按目标Part局部行号解释。此例按固定规范推导。

## 公共规则与相关接口

本接口同时遵守 [Irregular 公共参数、类型、形状、别名及示例](IrregularRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
