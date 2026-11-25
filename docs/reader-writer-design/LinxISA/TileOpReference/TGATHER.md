# TGATHER

计算 `dst[r,c] = src[off[r,c],c]`；off 的单位是 Local 逻辑行号。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S, Readable I>
void TGATHER(D &&dst, S &&src, I &&off);
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

计算 `dst[r,c] = src[off[r,c],c]`；off 的单位是 Local 逻辑行号。

## 合法组合与限制

D/S 是数值载体，I 是行索引载体。dst(out) 接收 `src[off[r,c],c]`；src(in) 持久不变；off(in) 的单位是**逻辑行号**。没有 stride、标量偏移或默认参数。dst/off 有效形状相同，src 的有效列数至少覆盖 dst；索引必须非负且小于 src.ValidRow。

TGATHER的源和索引使用普通Local描述；输出可使用普通Local或合法CUBE_M16/M32布局。布局转换只改变输出物理位置，行索引及列坐标仍按源逻辑域解释。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 32, 32>;
void example(V &dst, V &src, V &rows) {
  TGATHER(dst, src, rows);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src[r,c]=100*r+c、rows[r,c]=31-r 时，dst[r,c]=100*(31-r)+c。

### CUBE 输出与索引边界

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Input = Tile<Location::Vec, uint32_t, 32, 4>;
using Result = VecTileM32<uint32_t, 32, 4>;
void gather_cube(Result &dst, Input &src, Input &index) {
  TGATHER(dst, src, index);
}
```

src[r,c]=100*r+c，index[r,c]=31-r时，dst的逻辑结果为100*(31-r)+c，物理存储采用M32，输入及输出容量均512B。index=32或负的signed索引在输出发布前拒绝；输出padding为Null。此例按固定规范推导。


## 公共规则与相关接口

本接口同时遵守 [Irregular 公共参数、类型、形状、别名及示例](IrregularRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
