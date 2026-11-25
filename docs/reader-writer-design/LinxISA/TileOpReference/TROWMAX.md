# TROWMAX

沿列归约 src[r,0..C−1]，输出有效形状为 R×1；dst[r,0] 保存最大值。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S> void TROWMAX(D &&dst, S &&src);
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

## 操作语义

沿列归约 src[r,0..C−1]，输出有效形状为 R×1；dst[r,0] 保存最大值。不读取旧目标。

## 合法组合与限制

类型、布局及数值要求见 [Reduction 公共规则](ReductionRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Input = Tile<Location::Vec, float, 32, 32>;
using Output = Tile<Location::Vec, float, 32, 1>;
void example(Output &dst, Input &src) {
  TROWMAX(dst, src);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 输入 src[r,c]=r+c 时，结果为 dst[r,0]=r+31。

### 边界核对

沿归约轴仅有一个有效元素2时，结果为2；其余物理padding不参与计算。 RowMajor行结果物理列为1；M16/M32行结果物理列保持源物理列。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Reduction 公共规则](ReductionRules.md) · [操作数协议](OperandRoles.md)。


依据：[TROWMAX 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWMAX.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
