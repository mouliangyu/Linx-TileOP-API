# TROWEXPAND

计算 `dst[r,c] = v`；v=src[r,slot]。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <unsigned BroadcastByteOffset = 0, Writable D, Readable S>
void TROWEXPAND(D &&dst, S &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `BroadcastByteOffset` | ROW 广播字节偏移 | `0` |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

BroadcastByteOffset 为编译期字节偏移，默认 0；可选列及布局关系见 [广播偏移](BroadcastRules.md#广播偏移)。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

计算 `dst[r,c] = v`；v=src[r,slot]。slot 由 BroadcastByteOffset 选择。

## 合法组合与限制

类型、布局及数值要求见 [Broadcast 公共规则](BroadcastRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using D = Tile<Location::Vec, float, 32, 32>;
using B = Tile<Location::Vec, float, 32, 1>;
void example(D &dst, B &src) {
  TROWEXPAND(dst, src);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 广播源全为 2时，有效输出全为 2。

### 边界核对

FP16 M16 使用 BroadcastByteOffset=2 选择第1列；偏移1违反元素对齐，应诊断。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Broadcast 公共规则](BroadcastRules.md) · [操作数协议](OperandRoles.md)。


依据：[TROWEXPAND 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-expansion/TROWEXPAND.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
