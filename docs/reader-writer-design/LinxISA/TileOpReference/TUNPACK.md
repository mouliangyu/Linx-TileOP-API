# TUNPACK

从每个源 raw word 的 byte offset 处取 byte count 个字节，右对齐并零扩展到输出 word。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S>
void TUNPACK(D &&dst, S &&src, uint64_t control);
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
| `control` | in | 控制字；字段见本节 | 必填 |

control[7:0] 为 byte offset（0..3），[15:8] 为 byte count（1..4），offset+count≤4。[63:32] 须为零，[31:16] 不参与字段选择。

## 操作语义

从每个源 raw word 的 byte offset 处取 byte count 个字节，右对齐并零扩展到输出 word。

## 合法组合与限制

源使用 Local Numeric CUBE_M16/M32 的非 packed 8/16/32 位 backing，M32 另支持64位 backing。每个 raw word 的选中区间必须落在该 word 的逻辑有效字节范围内，且包含元素已定义。尾 word 可不足四个有效字节，只要所选区间完整有效。目标 dtype 为 U8/U16/U32，M32 另支持 U64。目标与源布局和有效行数相同；每个源 raw word 生成一个32位完整结果 word，目标有效列数为 `raw_words * 4 / sizeof(element_type_t<D>)`。U64 将相邻低/高 word 合成一个元素，要求每行 raw-word 数为偶数。所有字段及源验证在发布前完成，非法时整次操作拒绝。

物理有效区域外使用 Null padding，其值保持未定义；只将本次有效输出作为已定义输入使用。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM16<uint32_t, 16, 32>;
void example(V &dst, V &src) {
  TUNPACK(dst, src, uint64_t{0x0201});
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 src 的每个 word 为 0x44332211 时，输出 word 为 0x00003322。

### 边界核对

0x0201将0x44332211变为0x3322；offset3/count2非法。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Layout 公共参数、类型、形状、别名及示例](LayoutRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

依据：[TileOperandsLegal_TUNPACK](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/layout-rearrangement.asl)。

固定依据：[TUNPACK 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TUNPACK.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
