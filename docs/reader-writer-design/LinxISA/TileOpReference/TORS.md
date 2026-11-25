# TORS

计算 `dst[r,c] = x | s`，其中 x=src[r,c]；标量 s 应用于每个有效元素，不读取旧 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S>
void TORS(D &&dst, S &&src, element_type_t<S> s);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |
| `s` | in | 标量值，类型与声明中的计算元素类型匹配 | 必填 |

## 操作语义

计算 `dst[r,c] = x | s`，其中 x=src[r,c]；标量 s 应用于每个有效元素，不读取旧 dst。

## 合法组合与限制

类型、布局及数值要求见 [Scalar 公共规则](ScalarRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 32, 32>;
void example(V &dst, V &src) {
  TORS(dst, src, uint32_t{2});
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src 全为 6 时，有效输出全为 6。

### 边界核对

U32 源0xffffffff、标量0，AND结果0，OR/XOR结果0xffffffff；使用本页对应运算。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Scalar 公共规则](ScalarRules.md) · [操作数协议](OperandRoles.md)。


依据：[TORS 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/logical/TORS.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
