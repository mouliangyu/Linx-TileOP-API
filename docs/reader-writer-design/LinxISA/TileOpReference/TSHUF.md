# TSHUF

按 controls 和 control 在每个行 segment 内选择来源行，列及 word 位置不变；越界按 SELF 或 ZERO 处理。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S, Readable C>
void TSHUF(D &&dst, S &&src, C &&controls, uint64_t control);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `C` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |
| `controls` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |
| `controls` | in | 逐 word 控制输入 | 必填 |
| `control` | in | 控制字；字段见下表 | 必填 |

controls 的每个 U32 元素低 5 bit 为 b，高位忽略。

| 标量 control 位 | 含义 |
| --- | --- |
| [7:0] | mode：0 UP，1 DOWN，2 BFLY，3 IDX |
| [15:8] | segment code：0..4 对应宽度 2、4、8、16、32；M16 不允许 32 |
| [23:16] | boundary：0 SELF，1 ZERO |
| [63:32] | 必须为 0；[31:24] 不参与字段选择 |

## 操作语义

lane 为当前行在 M16/M32 CELL 中的行号，segment_base 为该 lane 所在分段的起始行号，local_lane=lane−segment_base。

在每个 segment 内，UP 读取 lane−b，DOWN 读取 lane+b，BFLY 读取 segment_base+(local_lane XOR b)，IDX 读取 segment_base+(b mod width)。越出 segment 或源有效行时，SELF 读取自己的行，ZERO 写零。列/word 位置不变。

同一 raw word 内多个小元素一起移动。FP64/S64/U64 的低、高 32-bit word 分别读取各自控制元素并选择源行，然后共同发布结果。源和控制值在输出发布前读取。

## 合法组合与限制

非法 mode、segment、boundary 和目标 alias 由目标合法性检查拒绝。

D/S 为同 dtype、几何和布局的 Local CUBE_M16/M32 数值视图。C 为同布局、同有效行数、同 CELL 数的 U32 控制视图，每个有效源行的 32-bit word 对应一个控制元素。目标与两个输入分别使用独立存储；实际读取的源元素及控制 word 须已定义。

数据使用 CUBE 数值载体；FP64/S64/U64 使用 M32 双 CELL 映射。M16 接受其合法的非 64 位数值载体。64 位形式的 controls 有效列数为 src 有效列数的两倍。

数据域覆盖该布局已分配的4/8/16/32位数值类型，M32另含FP64/S64/U64；packed元素按raw字节/word参与，目标dtype保持。

物理有效区域外使用 Null padding，其值保持未定义；只将本次有效输出作为已定义输入使用。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM16<uint32_t, 16, 32>;
void example(V &dst, V &src, V &controls) {
  TSHUF(dst, src, controls, uint64_t{0x0302});
}
```

输入 Tile 已初始化，输出与输入使用不同对象。 controls 全为 1 时，宽度 16 的段内相邻两行互换。

### 边界核对

control0x0302为M16宽16 BFLY SELF，b=1交换相邻行；UP在lane0、b1、ZERO输出零。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Layout 公共参数、类型、形状、别名及示例](LayoutRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

固定依据：[TSHUF 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TSHUF.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
