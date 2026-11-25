# TGPR2T

将四个 GPR 中的谓词位按行打包为 U8 Tile。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D>
void TGPR2T(D &&dst, uint64_t gpr0, uint64_t gpr1,
            uint64_t gpr2, uint64_t gpr3);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `gpr0` | in | 第 0 个 64-bit plane carrier | 必填 |
| `gpr1` | in | 第 1 个 64-bit plane carrier | 必填 |
| `gpr2` | in | 第 2 个 64-bit plane carrier | 必填 |
| `gpr3` | in | 第 3 个 64-bit plane carrier | 必填 |

## 操作语义

输出是普通 Numeric U8，固定使用 ByteOffset0 和 Zero padding。令 `g[0..3]` 依次表示 gpr0..gpr3，`bit(g,k)=(g>>k)&1`：

| 布局与有效形状 | 输出映射 |
| --- | --- |
| M32，32×4 | `dst[r,0] = sum(bit(g[p/2], r+32*(p%2)) << p, p=0..7)` |
| M16，16×8 | `dst[r,j] = sum(bit(g[p/4], r+16*(p%4)) << b, b=0..7)`，其中 `j=0,1`、`p=8*j+b` |

上述除法为整数除法。M32 的其余列 1..3、M16 的其余列 2..7 写零。M32 的每个 GPR 容纳两个 32-bit plane，M16 的每个 GPR 容纳四个 16-bit plane；各 plane 的第 r 位对应第 r 行。四个 GPR 在发布前取值，结果写入独立输出。

## 合法组合与限制

目标为 Local U8，完整有效形状为 M32 32×4 或 M16 16×8；Writer Part 同样须提供该固定输出几何。目标物理容量须容纳完整结果。


## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM16<uint8_t, 16, 8>;
void example(V &dst) {
  TGPR2T(dst, uint64_t{1} << 16, 0, uint64_t{1}, 0);
}
```

该 M16 示例将 plane 1 的第 0 行和 plane 8 的第 0 行设为 1，因此 dst[0,0]=2、dst[0,1]=1，其余元素为 0。这里的下标表示结果的逻辑坐标。

### 边界核对

M16 gpr0=1<<16、gpr2=1，得到[0,0]=2、[0,1]=1，其余零；M32 gpr3 bit63对应[31,0]的bit7。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

本接口同时遵守 [Layout 公共参数、类型、形状、别名及示例](LayoutRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

固定依据：[TGPR2T 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/layout-and-rearrangement/layout/TGPR2T.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
