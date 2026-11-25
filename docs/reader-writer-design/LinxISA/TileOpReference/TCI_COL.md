# TCI_COL

生成序列 `dst[r,c] = s+c`，不读取旧 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, typename T> void TCI_COL(D &&dst, T s);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `T` | 起始标量类型，由 s 推导 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |

s 为必填起点；类型、步长取值及布局见 [序列合同](IrregularRules.md#tcitci_2dtci_rowtci_col)。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `s` | in | 标量值，类型与声明中的计算元素类型匹配 | 必填 |

动态目标/Part须预先提供本次有效行列；起点标量T与目标计算元素类型一致。输出有效维度按目标描述绑定。

## 操作语义

生成序列 `dst[r,c] = s+c`，不读取旧 dst。

## 合法组合与限制

b64 CUBE 序列使用 M32 的双 CELL 映射；M16 支持 16/32 位序列。

类型、布局及数值要求见 [Irregular 公共规则](IrregularRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = CubeTileM16<uint32_t, 16, 8>;
void example(V &dst) {
  TCI_COL(dst, uint32_t{10});
}
```

输出无需预先初始化。 每行第 c 列为 10+c。

### 边界核对

U32起点UINT32_MAX，第0/1列分别为UINT32_MAX/0。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

[Irregular 公共规则](IrregularRules.md) · [操作数协议](OperandRoles.md)。

固定依据：[TCI 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/irregular-and-complex/initialization/TCI.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
