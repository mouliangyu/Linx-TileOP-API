# TPACK

对每个 raw 32-bit word，从 src0 的低位取 W0 字节，再在更高位置拼接 src1 的低 W1 字节，其余高位清零。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A, Readable B>
void TPACK(D &&dst, A &&src0, B &&src1, uint64_t control);
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
| `control` | in | 控制字；字段见本节 | 必填 |

control[7:0] 为 W0，[15:8] 为 W1，单位为字节；各为 1..3 且 W0+W1≤4。[63:32] 须为零，[31:16] 不参与字段选择。

## 操作语义

对每个 raw 32-bit word，从 src0 的低位取 W0 字节，再在更高位置拼接 src1 的低 W1 字节，其余高位清零。

## 合法组合与限制

两源使用 Local Numeric CUBE_M16/M32 的非 packed 8/16/32 位 backing，M32 另支持64位 backing。两源的布局、有效行数和每行 raw-word 数相同。每个 word 仅选取各自低 W0/W1 字节；选中字节必须在对应源的逻辑有效字节范围内，且其包含元素已定义。目标 dtype 为 U8/U16/U32，M32 另支持 U64。目标与源布局和有效行数相同；每个源 raw word 生成一个32位完整结果 word，目标有效列数为 `raw_words * 4 / sizeof(element_type_t<D>)`。U64 将相邻低/高 word 合成一个元素，要求每行 raw-word 数为偶数。所有字段及源验证在发布前完成，非法时整次操作拒绝。

物理有效区域外使用 Null padding，其值保持未定义；只将本次有效输出作为已定义输入使用。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM16<uint32_t, 16, 32>;
void example(V &dst, V &a, V &b) {
  TPACK(dst, a, b, uint64_t{0x0202});
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 a 的每个 word 为 0x44332211、b 为 0x88776655 时，输出 word 为 0x66552211。

### 边界核对

0x0202将0x44332211和0x88776655组为0x66552211；0x0302非法。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Layout 公共参数、类型、形状、别名及示例](LayoutRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

依据：[TileOperandsLegal_TPACK](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/layout-rearrangement.asl)。

固定依据：[TPACK 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TPACK.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
