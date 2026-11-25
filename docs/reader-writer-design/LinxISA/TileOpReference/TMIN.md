# TMIN

对有效区域逐元素计算 `dst[r,c] = min(x,y)`，其中 x=src0[r,c]、y=src1[r,c]。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A, Readable B>
void TMIN(D &&dst, A &&src0, B &&src1,
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
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src0` | Readable | 支持 | 支持 | 不接受 |
| `src1` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |
| `UserValidCol` | in | 本次计算列数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserValidRow` | in | 本次计算行数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserPhysicalCol` | in | 本次物理列数，元素单位；0 保留计算视图物理列 | 0 |

## 操作语义

对有效区域逐元素计算 `dst[r,c] = min(x,y)`，其中 x=src0[r,c]、y=src1[r,c]。不读取旧 dst，不广播。

## 合法组合与限制

类型、布局及数值要求见 [Elementwise 公共规则](ElementwiseRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32>;
void example(V &dst, V &src0, V &src1) {
  TMIN(dst, src0, src1);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src0 全为 6、src1 全为 2 时，有效输出全为 2。

### 边界核对

FP32 一个输入为 quiet NaN、另一个为2，结果为2；两输入均为NaN时返回canonical quiet NaN。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Elementwise 公共规则](ElementwiseRules.md) · [操作数协议](OperandRoles.md)。


依据：[TMIN 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TMIN.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
