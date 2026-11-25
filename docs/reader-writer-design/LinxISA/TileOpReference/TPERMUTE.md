# TPERMUTE

按局部字节表索引，从两个 CUBE 输入选择字节组成输出。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A,
          Readable B, Readable I>
void TPERMUTE(D &&dst, A &&src0, B &&src1, I &&indices);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `I` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src0` | Readable | 支持 | 支持 | 不接受 |
| `src1` | Readable | 支持 | 支持 | 不接受 |
| `indices` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |
| `indices` | in | 逐字节局部表索引 | 必填 |

## 操作语义

每个 CUBE 行片中的表独立：M32 的每源表宽为 4 字节，索引 0..3 选 src0、4..7 选 src1；M16 每源为 8 字节，0..7 选 src0、8..15 选 src1。索引有效列数按每个目标元素的字节数扩展；例如 M16 U32 16×32 数据对应 U8 16×128 索引。目标有效维度为正，按本次操作的维度绑定确定，越界索引在发布前拒绝。

## 合法组合与限制

D/A/B 为同 dtype、几何和布局的数值载体，I 为 U8 字节索引。dst(out) 从 src0/src1(in) 按 indices(in) 为每个有效目标字节选值。四者必须同为 CUBE_M16 或 CUBE_M32；源可互相 alias，indices 不得与数值源 alias。

数据域覆盖该布局已分配的4/8/16/32位数值类型，M32另含FP64/S64/U64；packed元素按raw字节/word参与，目标dtype保持。

物理有效区域外使用 Null padding，其值保持未定义；只将本次有效输出作为已定义输入使用。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM16<uint32_t, 16, 32>;
using I = VecTileM16<uint8_t, 16, 128>;
void example(V &dst, V &a, V &b, I &indices) {
  TPERMUTE(dst, a, b, indices);
}
```

a/b/indices 已定义，indices 与数值源不 alias，dst 独立。 indices 全为 0 时，每个输出字节取对应行片中 a 的局部表第 0 字节。

### 边界核对

M16索引8选择src1第0字节，索引16越界；M32索引4选src1第0字节，8越界。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Layout 公共参数、类型、形状、别名及示例](LayoutRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

固定依据：[TPERMUTE 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TPERMUTE.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
