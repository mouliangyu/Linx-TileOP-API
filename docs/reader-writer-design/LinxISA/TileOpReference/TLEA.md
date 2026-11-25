# TLEA

将元素索引转换为 64 位字节位移，不访问 GM。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable S>
void TLEA(D &&dst, S &&src, unsigned element_bits);
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
| `element_bits` | in | 目标元素位宽，bit 单位 | 必填 |

## 操作语义

所有参数必填。源为有符号时符号扩展，无符号时零扩展；结果为 `extend64(src[r,c]) * (element_bits / 8)` 的低 64 位，不饱和、不产生溢出 fault。element_bits 必须为 8、16、32、64，不接受 0 或 packed 4-bit。

## 合法组合与限制

| src dtype | dst dtype | 扩展方式 |
| --- | --- | --- |
| S32、S64 | S64 | 符号扩展到 64 位 |
| U32、U64 | U64 | 零扩展到 64 位 |

表中列出全部类型配对，结果保留缩放乘积的低 64 位。

源目标为 Local，相同 RowMajor 或 CUBE_M32 布局、相同有效形状；目标容量和物理几何按 64 位 dtype 独立推导。Shared、M16、N8 不允许。S64/U64 直接 alias 读取旧源；Writer 不可作为输入。输出 padding 按数值 padding 合同。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using I = Tile<Location::Vec, int32_t, 8, 32>;
using O = Tile<Location::Vec, int64_t, 8, 32>;
void offsets(O &dst, I &index) { TLEA(dst, index, 16); }
```

index 为 -1、0、3 时结果分别为 -2、0、6 字节。分片索引保持数值不变，不自动加 parent 偏移。

### 边界核对

S32 -1、element_bits64得到S64 -8；element_bits4非法。 此为固定规范推导；编译及硬件运行未执行。

## 公共规则与相关接口

依据：[PTO-C TLEA](https://linxisa.github.io/PTO-C/#TLEA)。

固定依据：[TLEA 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/tile-scalar-and-immediate/arithmetic/TLEA.asl)；公共证据见 [Local 工具操作](../TileOpContractEvidence.md#local-工具操作)。

[返回算子索引](README.md)
