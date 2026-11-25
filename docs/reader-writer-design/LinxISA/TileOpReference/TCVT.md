# TCVT

按 RMode 将 src 的元素数值转换为目标 dtype；同类型浮点的显式舍入模式按舍入到整数值的专用规则执行。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <int RMode = LINX_RNONE, Writable D, Readable S>
void TCVT(D &&dst, S &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `RMode` | 舍入模式编码 | `LINX_RNONE` |
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

| RMode | 作用 |
| --- | --- |
| LINX_RNONE=0 | float→integer 为 RTZ，其他需要舍入的转换为 RNE |
| LINX_RNE=1 | 最近偶数 |
| LINX_RTZ=2 | 向零 |
| LINX_RDN=3 | 向负无穷；E8M0 scale 的 floor 路径 |
| LINX_RUP=4 | 向正无穷 |
| LINX_RNA=5 | 最近，平局远离零 |
| LINX_RTO=6 | 按转换的 round-to-odd 合同；同类型 FP16/BF16/FP32/FP64 禁止 |
| LINX_RHB=7 | 最近，平局向正无穷（half-up）；例如−1.5→−1、1.5→2 |

## 操作语义

按 RMode 将 src 的元素数值转换为目标 dtype。

同类型 FP16/BF16/FP32/FP64 使用显式非零合法模式时，执行“舍入到整数值”，结果仍是同一浮点 dtype。比如 FP32 的 1.75 经过 RTZ 为 FP32 的 1.0，不会变为 S32；有限非整数置 NX，负数舍入到零保留负零。RNONE 不等于强制该路径。

## 合法组合与限制

源目标 dtype 可以不同，分别推导 Part 物理容量；逻辑有效形状和转换类型配对必须合法。Reader 与 Writer 各自使用相应 Part 的容量及几何。

D/S 分别决定目标/源 dtype；dst(out) 接收转换结果，src(in) 提供已定义数值，无普通参数默认值。元素数值按目标类型转换，不能作为 raw bitcast 使用。

| 布局 | 必须相同 | 允许不同 |
| --- | --- | --- |
| 普通布局 | 容量推导的物理 Row、Col、有效 R/C | dtype 对应的容量和 packing |
| CUBE_M16/M32 | 同一 M 布局和逻辑有效 R/C，Local数值存储 | 各 dtype 的物理 Cols、CELL 数和容量 |

普通布局按物理列数区分容量规则：

- 二次幂列数沿用满容量推导物理行数。窄化到1字节类型时，最小128B分配可能扩大推导行数，应为两侧选择相同物理行列及各自容量。例如FP32→U8的1×32有效区，可共同使用4×32物理形状，容量分别512B/128B。
- RowMajor的非二次幂列数 profile 接受FP32、FP16、BF16、E2M1X2、E1M2X2，并继续检查类型配对。两侧保留相同物理Rows/Cols；容量只须容纳逐行存储。packed行的末尾半byte属于本行padding，每行分别向整byte取整。库为完整Tile选择容纳存储的最小合法二次幂容量，空余容量保留在逻辑矩形之外。32×17 FP16需要1088B存储、2048B容量；32×17 E2M1X2需要288B存储、512B容量。

完整Local载体和Reader/Writer的Part均按B.IOT及范围编码的128B..64KiB校验。Reader/Writer还需满足各自子视图与组装几何，非二次幂列数的完整Tile转换示例只验证完整目标分支。CUBE_N8 不属于该路径。

底层维度绑定：LB0/1分别为有效列/行；普通布局的LB2提供物理列数。CUBE_M16/M32省略LB2，由目标dtype与TSize推导物理几何。CUBE预检通过后，目标TSize不足产生Fault_TileAllocation，目标payload保持无效果。

源目标 dtype 按类型配对规则选择；E8M0、E6M2、RCPE6M2、packed 格式各有额外转换规则。普通同类型目标与源alias时读取完整旧源快照。默认Pad为Null、Sat=0、Canonicalize=0；类型/容量/编码预检后一起发布payload、状态和描述符。特殊格式的完整配对表与默认舍入见 [数值参考](Numerics.md#tcvt-类型配对)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using F32 = Tile<Location::Vec, float, 32, 32>;
using F16 = Tile<Location::Vec, __half, 32, 32>;
void narrow(F16 &dst, F32 &src) { TCVT(dst, src); }
void truncate(F32 &dst, F32 &src) { TCVT<LINX_RTZ>(dst, src); }
```

src 全为 1.75 时 narrow 输出 1.75，truncate 输出 1.0；源已定义，输出独立。

### 不同容量的 Reader 与 Writer

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Source = VecTileM32<float, 32, 8>;
using SrcPart = VecTileM32<float, 32, 4>;
using Target = VecTileM32<uint8_t, 32, 8>;
using DstPart = VecTileM32<uint8_t, 32, 4>;
Target convert_parts(Source &source) {
  TileReader<Source> reader(source);
  TileWriter<Target> writer;
  TCVT(writer.first<DstPart>(0), reader.read<SrcPart>(0));
  TCVT(writer.last<DstPart>(1), reader.read<SrcPart>(4));
  return writer.finish();
}
```

source为已定义的M32 32×8 FP32，每项1.75；Source/Target容量分别1024B/256B，每片为512B/128B。第一片源偏移0、目标0，第二片源偏移4 CELL、目标1 CELL，均对应各自逻辑列4起点。默认float→integer取RTZ，全部输出为U8的1并置NX。两侧M32保持32行，Part有效32×4，窄化后目标每CELL可容纳更多列，因此源/目标CELL偏移分别计算。此例为接口及规范推导，未编译或运行。特殊格式的配对与编码见[数值参考](Numerics.md#tcvt-类型配对)。

### RowMajor 非二次幂列数与 packed 尾部

<!-- audit-example: tcvt_odd_columns -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tcvt_odd_columns {
using Half = Tile<Location::Vec, __half, 32, 17>;
using Packed = Tile<Location::Vec, __fp4_e2m1x2, 32, 17>;
void encode(Packed &dst, Half &src) { TCVT(dst, src); }
void decode(Half &dst, Packed &src) { TCVT(dst, src); }
}
```

源均已定义，目标独立，物理与有效形状均为32×17。Half逐行34B，容量2048B；Packed逐行9B，容量512B。`encode` 输入全为1.0时，17个逻辑元素各得到4位编码`0x2`；每行最后一个byte的另一半为Null padding，保持未定义。`decode` 只读取17个有效元素，输出全为FP16的1.0，两次转换均不新增数值异常。容量空余区域不参与转换。固定测试 `PTO-AVS-TILE-TCVT-NORM-PHYSICAL-SHAPE-006` 同时检查直接转换和bundle目标分配；本例完成模拟声明编译及源码对照，ASL执行另行记录。

### E8M0 指数 scale 的双向转换

<!-- audit-example: tcvt_e8m0 -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tcvt_e8m0 {
using F32 = VecTileM32<float, 32, 8>;
using E8M0 = VecTileM32<__fp8_e8m0, 32, 8>;
void encode(E8M0 &dst, F32 &src) {
  TCVT<LINX_RNE>(dst, src);
}
void decode(F32 &dst, E8M0 &src) {
  TCVT<LINX_RNE>(dst, src);
}
}
```

两个载体的有效形状均为32×8，物理容量分别为1024B和256B。输入已定义，输出独立。`encode` 的源全为2.0时，目标各元素编码为 `0x80`；`decode` 输入各元素编码为 `0x80` 时输出2.0，两次转换均精确。`encode` 的源为零、负数或NaN时，目标为 `0xff` 并置NV；`decode` 的源为 `0xff` 时输出canonical quiet NaN，该转换不新增NV。状态为sticky，已有状态位继续保留。

### E6M2 与 RCPE6M2

<!-- audit-example: tcvt_e6m2 -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tcvt_e6m2 {
using F16 = VecTileM32<__half, 32, 8>;
using E6M2 = VecTileM32<__fp8_e6m2, 32, 8>;
using RcpE6M2 = VecTileM32<__fp8_rcpe6m2, 32, 8>;
void encode(E6M2 &dst, F16 &src) {
  TCVT<LINX_RNE>(dst, src);
}
void decode(F16 &dst, E6M2 &src) {
  TCVT<LINX_RNA>(dst, src);
}
void reciprocal_decode(F16 &dst, RcpE6M2 &src) {
  TCVT<LINX_RNE>(dst, src);
}
}
```

F16容量512B，两种scale载体容量均为256B，均为M32、有效32×8。E6M2编码 `0xc4` 表示2，RCPE6M2相同编码表示1/2。因此 `encode` 输入2.0得到 `0xc4`；`decode` 输入 `0xc4` 得到2.0；`reciprocal_decode` 输入 `0xc4` 得到0.5。这三个值均可精确表示，RCPE6M2按其精确倒数语义进行一次目标舍入。

| 函数与输入 | 结果 | 本次新增状态 |
| --- | --- | --- |
| `encode`，FP16 +0或−0 | `0x00`，表示2^-48 | UF、NX |
| `encode`，FP16 −1 | `0xff` | NV |
| `encode`，FP16 +∞，默认Sat=0 | `0xff` | OF、NX |
| `decode`，`0xff` | FP16 canonical quiet NaN | 无 |
| `reciprocal_decode`，`0xff` | FP16 canonical quiet NaN | 无 |

### 两种 packed 浮点格式

<!-- audit-example: tcvt_packed -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tcvt_packed {
using F32 = VecTileM32<float, 32, 8>;
using E2M1 = VecTileM32<__fp4_e2m1x2, 32, 8>;
using E1M2 = VecTileM32<__fp4_e1m2x2, 32, 8>;
void encode_e2m1(E2M1 &dst, F32 &src) {
  TCVT<LINX_RNE>(dst, src);
}
void decode_e2m1(F32 &dst, E2M1 &src) {
  TCVT<LINX_RNE>(dst, src);
}
void encode_e1m2(E1M2 &dst, F32 &src) {
  TCVT<LINX_RNE>(dst, src);
}
void decode_e1m2(F32 &dst, E1M2 &src) {
  TCVT<LINX_RNE>(dst, src);
}
}
```

这里的32×8统计逻辑元素。F32容量1024B，每种packed目标容量128B，两个4位元素共享一个byte。输入全为1.0时，E2M1逐元素编码为 `0x2`，E1M2为 `0x4`；成对元素在载体中分别为 `0x22`、`0x44`。对应decode函数输出1.0，两次转换均精确。所有函数使用已初始化源和独立输出。

| 编码函数与FP32输入 | 4位元素编码与数值 | 本次新增状态 |
| --- | --- | --- |
| `encode_e2m1`，1.25，RNE | `0x2`，1.0 | NX |
| `encode_e1m2`，1.125，RNE | `0x4`，1.0 | NX |
| 任一编码函数，−0 | `0x8`，−0 | 无 |
| 任一编码函数，quiet NaN | `0x0`，+0 | 无 |
| 任一编码函数，signaling NaN | `0x0`，+0 | NV |

上表给出的编码以单个逻辑元素为单位；相邻元素通过packed存储规则组合。特殊值规则按[专用转换执行函数](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/tcvt-conversion.asl)推导，平局选择依据[packed舍入函数](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/packed-conversion.asl)。

### Packed 整数的扩展和截断

<!-- audit-example: tcvt_integer -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tcvt_integer {
using S4 = VecTileM32<__int4x2, 32, 8>;
using S8 = VecTileM32<int8_t, 32, 8>;
void widen(S8 &dst, S4 &src) { TCVT(dst, src); }
void narrow(S4 &dst, S8 &src) { TCVT(dst, src); }
}
```

S4/S8的容量分别为128B/256B。`widen` 输入4位编码 `0xf` 时，按有符号−1扩展为S8的 `0xff`；`narrow` 输入S8的−9（`0xf7`）时，Sat=0保留低4位，得到 `0x7`，即+7。按整数转换路径，这两个操作不新增数值异常位。来源为[TileConvertIntegerValue与NormalizeTileInteger](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/numeric/formats.asl)。

这些函数补充专用格式的调用、容量和数值边界；结论依据固定规范推导。实际库编译、ASL执行及硬件测试分别记录于[示例核对证据](../TileOpContractEvidence.md#接口示例补齐)。

## 公共规则与相关接口

本接口同时遵守 [CompareConvert 公共参数、类型、形状、别名及示例](CompareConvertRules.md)。该页中的规则与本页声明共同构成调用合同。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。

[返回算子索引](README.md)

固定依据：[TileOperandsLegal_TCVTToValue](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/tcvt-value-operands.asl)。Local完整载体与Part分别经过B.IOT及范围字段的SizeCode 1..10检查，上限均为64KiB。
