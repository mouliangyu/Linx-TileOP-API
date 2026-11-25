# TFMA

逐元素计算 `dst[r,c] = src0[r,c]*src1[r,c]+src2[r,c]`，不读取旧 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A, Readable B, Readable C>
void TFMA(D &&dst, A &&src0, B &&src1, C &&src2);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `C` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src0` | Readable | 支持 | 支持 | 不接受 |
| `src1` | Readable | 支持 | 支持 | 不接受 |
| `src2` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |
| `src2` | in | 第三数值输入 | 必填 |

## 操作语义

逐元素计算 `dst[r,c] = src0[r,c]*src1[r,c]+src2[r,c]`，不读取旧 dst。

## 合法组合与限制

类型、布局及数值要求见 [Elementwise 公共规则](ElementwiseRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32>;
void example(V &dst, V &src0, V &src1, V &src2) {
  TFMA(dst, src0, src1, src2);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src0/src1/src2 分别全为 2/3/4 时，输出全为 10。

### 边界核对

U64 输入 UINT64_MAX、1、1，结果为 0；U32 不在本操作类型集合。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Elementwise 公共规则](ElementwiseRules.md) · [操作数协议](OperandRoles.md)。


依据：[TFMA 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TFMA.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
