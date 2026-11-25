# TEXPANDS

将目标有效区域的每个元素设为 s，不读取旧 dst；这是标量填充。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D>
void TEXPANDS(D &&dst, element_type_t<D> s,
              unsigned UserValidCol = 0, unsigned UserValidRow = 0,
              unsigned UserPhysicalCol = 0);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |

没有数值输入；默认有效维度取目标计算视图。非零 UserValidCol/UserValidRow 分别指定本次列数、行数。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `s` | in | 标量值，类型与声明中的计算元素类型匹配 | 必填 |
| `UserValidCol` | in | 本次计算列数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserValidRow` | in | 本次计算行数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserPhysicalCol` | in | 本次物理列数，元素单位；0 保留计算视图物理列 | 0 |

## 操作语义

将目标有效区域的每个元素设为 s，不读取旧 dst；这是标量填充。

## 合法组合与限制

类型、布局及数值要求见 [Scalar 公共规则](ScalarRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 32, 32>;
void example(V &dst) {
  TEXPANDS(dst, uint32_t{7});
}
```

输出无需预先初始化。 有效输出全为 7。

### 边界核对

M16 的有效行数上限为16；静态17行调用应诊断。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Scalar 公共规则](ScalarRules.md) · [操作数协议](OperandRoles.md)。


依据：[TEXPANDS 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/initialization/TEXPANDS.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
