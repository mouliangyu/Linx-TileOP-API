# TCOLEXPANDSUB

计算 `dst[r,c] = x-v`；x=src0[r,c]，v=src1[0,c]。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A, Readable B>
void TCOLEXPANDSUB(D &&dst, A &&src0, B &&src1);
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

本操作没有 BroadcastByteOffset 参数。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |

## 操作语义

计算 `dst[r,c] = x-v`；x=src0[r,c]，v=src1[0,c]。按列值沿行方向广播。

## 合法组合与限制

类型、布局及数值要求见 [Broadcast 公共规则](BroadcastRules.md)。

维度取得、计算区域校验及输出元数据见 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using D = Tile<Location::Vec, float, 32, 32>;
using B = Tile<Location::Vec, float, 1, 32>;
void example(D &dst, D &src0, B &src1) {
  TCOLEXPANDSUB(dst, src0, src1);
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 广播源全为 2、src0 全为 6时，有效输出全为 4。

### 边界核对

广播源可有两行：第0行全2、第1行全9时，只使用第0行的2；两行均须已定义。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

[Broadcast 公共规则](BroadcastRules.md) · [操作数协议](OperandRoles.md)。


依据：[TCOLEXPANDSUB 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/column-expansion/TCOLEXPANDSUB.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
