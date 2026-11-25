# TIMG2COL

从 GM feature-map 提取卷积窗口，输出 Local CUBE 或 Shared ND。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 重载 | 输出 | 参数形式 | 核级有效行数 |
| --- | --- | --- | --- |
| Local 隐式行数 | 完整 Local CUBE | 三个参数字 | dst 的 ValidRow |
| Local 显式行数 | 完整 Local CUBE | 三个参数字及 groupRows | groupRows |
| 四 PE Shared | Shared Writer 阶段描述 | TIMG2COLParams | Parent 的 ValidRow |
| 单 PE Shared | 完整 SharedTile | TIMG2COLParams | 目标的 ValidRow |

```cpp
struct TIMG2COLParams { uint64_t param0, param1, param2; };

template <LayoutCvtEnum SourceOrder = NORM,
          is_tile_data_v D, GlobalMemoryView G>
void TIMG2COL(D &dst, const G &src,
              uint64_t param0, uint64_t param1, uint64_t param2);

template <LayoutCvtEnum SourceOrder = NORM,
          is_tile_data_v D, GlobalMemoryView G>
void TIMG2COL(D &dst, const G &src, uint64_t param0,
              uint64_t param1, uint64_t param2, size_t groupRows);

template <LayoutCvtEnum SourceOrder = NORM,
          SharedAssemblyOutput D, GlobalMemoryView G>
void TIMG2COL(D &&dst, const G &src, TIMG2COLParams params);

template <LayoutCvtEnum SourceOrder, unsigned PEMask,
          is_tile_data_v Shape, GlobalMemoryView G>
void TIMG2COL(SharedTile<Shape> &dst, const G &src, TIMG2COLParams params);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `SourceOrder` | GM 图像顺序 NORM=NHWC、DN2ND=NCHW | Local 与四 PE Shared 重载默认 `NORM`；单 PE Shared 重载显式指定 |
| `D` | Local 目标 Tile 类型或四 PE Shared 输出描述类型 | 由实参推导 |
| `G` | src 的 GlobalMemoryView 类型 | 由实参推导 |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | 显式指定 |
| `Shape` | 完整 Shared 形状类型 | 由实参推导 |

| 输出形式 | dst | 执行方式 |
| --- | --- | --- |
| Local CUBE | 完整 Local M16/M32 Tile | 直接产生完整 Local 输出 |
| 四 PE Shared ND | Shared Writer 阶段描述 | 必须显式组装，阶段固定对应 PE 身份，见下文 |
| 单 PE Shared ND | 完整 SharedTile | 单次发布完整 Shared 输出 |

`D` 在 Local 重载中必须是完整 Local CUBE；`Shape` 是完整 Shared RowMajor 的形状类型。`SharedAssemblyOutput` 是仅接受 Shared Writer 输出描述的协议约束，是 SharedWritable 的子集。四 PE 重载的参与掩码固定为 15。单 PE 重载的 PEMask 必须显式为 1、2、4 或 8（PE0 对应 bit3）。

`SourceOrder` 指定 GM 存储顺序：NORM 表示 NHWC，DN2ND 表示 NCHW。库按源顺序和目标布局选择 ISA 布局码，映射见[合法组合与限制](#合法组合与限制)。

### 参数字

| 字 | 位段 | 字段与范围 |
| --- | --- | --- |
| param0 | 15:0 / 31:16 / 47:32 | input_h / input_w / cin，各 1..65535 |
| param0 | 55:48 / 63:56 | kernel_h / kernel_w，各 1..255 |
| param1 | 7:0 / 15:8 / 23:16 / 31:24 | pad_top / left / bottom / right，各 0..255 |
| param1 | 36:32 / 41:37 | dilation_h / w，各 1..31 |
| param1 | 47:42 / 53:48 | stride_h / w，各 1..63 |
| param1 | 54 / 58:55 / 62:59 / 63 | 保留位 / ParamVersion / ExtensionClass / 保留位，基础合同全部为 0 |
| param2 | 31:0 / 63:32 | row_start / col_start，各 0..2^32−1 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义源或可读 GM 视图，依重载 | 必填 |
| `param0` | in | TIMG2COL 输入与核形状参数字 | 必填 |
| `param1` | in | TIMG2COL padding、stride、dilation 参数字 | 必填 |
| `param2` | in | TIMG2COL 窗口/列起点参数字 | 必填 |
| `groupRows` | in | TIMG2COL 核级输出行数，元素单位 | 必填 |
| `params` | in | TIMG2COL 三个参数字的集合 | 必填 |

表中“必填”适用于声明中包含该参数的重载。

## 操作语义

LB0、LB1、LB2 分别绑定 ValidCol、核级 ValidRow、TotalCol，各一次。Local 的显式 groupRows 重载用 groupRows 作为核级 ValidRow；省略时 dst 的 ValidRow 直接作为核级 ValidRow；若 dst 类型描述每 PE 的 16/32 行分片，应显式传 groupRows，避免把分片行数误当核级总行数。Shared 使用 Parent 的 ValidRow、ValidCol 和物理列数 TotalCol；各 PE 的协作描述使用相同的公共元数据。

Shared 的 TotalCol 是持久化 ND 行距。Local 的 TotalCol 取 dst 的物理列数，表示等价 ND 中间矩阵的行距；最终 CUBE 几何按 ValidCol 推导。

### 窗口展开

令元素位宽为 B，`C0 = 256 / B`，`C1 = ceil(Cin / C0)`。支持 8/16/32 位数据时，C0 分别为 32/16/8 个元素。

```text
EffectiveKH = (KH - 1) * dilation_h + 1
EffectiveKW = (KW - 1) * dilation_w + 1
Hout = H + pad_top + pad_bottom < EffectiveKH
       ? 0 : floor((H + pad_top + pad_bottom - EffectiveKH) / stride_h) + 1
Wout = W + pad_left + pad_right < EffectiveKW
       ? 0 : floor((W + pad_left + pad_right - EffectiveKW) / stride_w) + 1
K = KH * KW * C1 * C0
```

输出行按窗口的 `(oh, ow)` 行优先顺序展开；列顺序为 `(kh, kw, c1, c0)`，即 `(((kh*KW + kw)*C1 + c1)*C0 + c0)`。row_start 以窗口为单位，col_start 以展开后的列元素为单位。

窗口访问落在输入 H/W 之外，或通道落在 Cin..C1*C0−1 时，产生定义明确的 raw zero，不访问 GM。有效矩形之外的物理存储尾部不写入、不保证有定义值。目标容量仍须满足布局及 Shared 发布覆盖要求。

## 合法组合与限制

ValidCol、TotalCol 均须为 1..65535，且 ValidCol≤TotalCol。ValidCol、TotalCol、col_start 都必须是 C0 的整数倍；`row_start + ValidRow <= Hout*Wout` 且 `col_start + ValidCol <= K`，使用足够宽的整数检查，不能回绕。有效窗口空间为空时不能提交非空输出。

GM 与目标 dtype 匹配，支持 FP32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E8M0、S/U8/16/32。源顺序与目标布局按下表映射到 ISA 布局码。

| SourceOrder | Shared RowMajor | Local CUBE_M16 | Local CUBE_M32 |
| --- | --- | --- | --- |
| NORM | NORM / ND2ND | ND2M16 | ND2M32 |
| DN2ND | DN2ND | DN2M16 | DN2M32 |

GM 从 src.base 开始保存一个连续的 H×W×Cin feature-map；NCHW 元素地址索引为 `(c*H+h)*W+w`，NHWC 为 `(h*W+w)*Cin+c`。GM 寻址使用上述连续布局公式。

| 目标 | 核级 ValidRow | 每 PE 行块大小 M |
| --- | --- | --- |
| Local M16 | 1..64 | 16 |
| Local M32 | 1..128 | 32 |
| Shared ND | 1..128 | ValidRow≤64 时为 16，否则为 32 |

PE i 的有效行数为 `clamp(ValidRow - i*M, 0, M)`，源窗口起点为 `row_start + min(i*M, ValidRow)`。Local dst 必须能容纳该 PE 的结果，最终有效行数为此分配值。零行 PE 仍须参加 collective，但不分配 Local Tile、不访问 GM 或写 payload。参与 PE 必须使用一致的 GM base、参数字及公共目标元数据。

例如 FP16、M16、ValidCol=TotalCol=16、groupRows=20 时，PE0/1/2/3 的实际有效行数分别为 16/4/0/0。非零行 PE 的硬件 Tile 描述符记录实际结果形状；零行 PE 没有本次 Local 输出可读。C++ 目标对象的库侧有效维度保持原值。例如静态目标为 16 行时，PE1 的 GetValidRow() 仍返回 16，硬件结果的有效行数则为 4。后续消费者须按实际结果绑定维度，例如通过 Reader 显式描述 4 行片段，或使用消费操作的显式有效维度参数。零行 PE 不得以构造 Reader 等方式读取不存在的 Local 输出。

### Shared Writer 协作

这是固定四 PE 发布协议：PE0 消费 `first`，PE1、PE2 消费 `middle`，PE3 消费 `last`。这些阶段跨四个 PE 共同构成同一个 Shared generation。

每个描述的显式 `cell_offset` 必须为 0；硬件按上述 PE 行分配与 TotalCol 推导实际写入位置。Parent 容量、Part 的合法 SizeCode 及四 PE 覆盖须满足 Shared generation 合同；最后一个阶段还负责关闭物理尾部覆盖。PE3 在有效行数为零时仍执行 LAST。无效 payload 的 definedness 按存储合同保持。

各 PE 的 Shared Writer 透传同一个 Sx 目标身份与对应阶段。PE0 的 INIT 建立 generation；PE1/2/3 通过同一个 Sx 的 `.reuse` binder 与 B.ASSEMBLE 继续写入。`finish()` 交出该 Sx 的 SharedTile 句柄；LAST 由 PE3 的阶段调用完成，消费者按 generation 发布和就绪规则执行同步。库与 lowering 必须保持各 PE 的目标身份一致，以及底层要求的阶段和消费顺序。单 PE 重载直接发布完整 SharedTile。

库的cell_offset仍为128B单位且此四PE重载固定填0。硬件内部的覆盖计数以32B条带计算：`derived_offset = row_start_for_PE * TotalCol / C0`、`writer_stripes = PEValidRow * TotalCol / C0`。例如FP16、TotalCol16、groupRows20、1024B parent时，四PE的内部起点为0/16/20/20，payload条带为16/4/0/0；LAST从条带20覆盖到32，关闭尾部覆盖但只保留有效payload的定义状态。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using D = VecTileM16<__half, 16, 16>;
using G = global_tensor<const __half, RowMajor<20, 16>>;
void example(D &dst, const __half *image) {
  G src(image);
  constexpr uint64_t p0 = uint64_t{4} | (uint64_t{5} << 16)
    | (uint64_t{16} << 32) | (uint64_t{1} << 48) | (uint64_t{1} << 56);
  constexpr uint64_t p1 = (uint64_t{1} << 32) | (uint64_t{1} << 37)
    | (uint64_t{1} << 42) | (uint64_t{1} << 48);
  constexpr uint64_t p2 = 0;
  TIMG2COL(dst, src, p0, p1, p2, 20);
}
```

四个 PE 使用同一可读 image 调用；image 为连续 FP16 NHWC 4×5×16，1×1 核、stride=dilation=1、无 padding，起点为零。 四 PE 的实际输出行数依次为 16、4、0、0；PE0/1 对应原图按 NHWC 展开的前 16 行和后 4 行。PE2/3 无 Local 输出可读。

### 隐式行数与尾片消费

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Local = VecTileM16<__half, 16, 16>;
using Image = global_tensor<const __half, RowMajor<20, 16>>;
using Output = global_tensor<__half, RowMajor<20, 16>>;
constexpr TIMG2COLParams image_params() {
  return {uint64_t{4} | (uint64_t{5} << 16) | (uint64_t{16} << 32)
            | (uint64_t{1} << 48) | (uint64_t{1} << 56),
          (uint64_t{1} << 32) | (uint64_t{1} << 37)
            | (uint64_t{1} << 42) | (uint64_t{1} << 48), 0};
}
void implicit_rows(Local &dst, const __half *image) {
  Image src(image);
  auto p = image_params();
  TIMG2COL(dst, src, p.param0, p.param1, p.param2);
}
void tail_to_gm(Local &dst, const __half *image, __half *output,
                unsigned pe) {
  Image src(image);
  auto p = image_params();
  TIMG2COL(dst, src, p.param0, p.param1, p.param2, size_t{20});
  if (pe < 2) {
    size_t rows = pe == 0 ? 16 : 4;
    TileReader<Local> reader(dst);
    Output parent(output);
    auto out = parent.subview(pe * 16, 0, rows, 16);
    TSTORE(out, reader.read<Local>(0, rows, 16));
  }
}
```

各PE均调用，pe实参等于该执行者的Core内PE编号0..3。image为连续FP16 NHWC4×5×16，output提供320个可写元素。implicit_rows取静态dst的16作为核级行数，仅PE0产生16行；tail_to_gm显式20后，PE0/1分别写16/4行，输出20×16等于输入按行展开，PE2/3不读取Local结果。所有源元素预先定义。

### Shared 单PE与四PE组装

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using ParentShape = Tile<Location::Vec, __half, 32, 16,
                         BLayout::RowMajor, 20, 16>;
using PartShape = Tile<Location::Vec, __half, 16, 16>;
using Shared = SharedTile<ParentShape>;
using ImageView = global_tensor<const __half, RowMajor<20, 16>>;
void single_pe(Shared &dst, const __half *image, TIMG2COLParams params) {
  ImageView src(image);
  TIMG2COL<NORM, 8>(dst, src, params);
}
Shared four_pe(const __half *image, TIMG2COLParams params, unsigned pe) {
  ImageView src(image);
  TileWriter<Shared> writer;
  if (pe == 0) TIMG2COL(writer.first<PartShape>(0), src, params);
  else if (pe == 3) TIMG2COL(writer.last<PartShape>(0), src, params);
  else TIMG2COL(writer.middle<PartShape>(0), src, params);
  return writer.finish();
}
```

params由前例image_params()构造。单PE版本由PE0发布全部20×16；四PE版本由同一协作调用中的writer绑定同一个Sx，PE0/1分别写16/4行，PE2/3无payload，PE3仍提交LAST。parent物理容量1024B、Part512B，四PE公共元数据一致。函数按内联设备代码使用，返回句柄的消费遵守发布/就绪合同。输入同前例，Shared有效20×16逐元素等于输入；其余物理尾部保持未定义。params.param1置bit54时，参数预检拒绝；col_start=1不满足FP16的C0=16要求。示例均为规范推导，未编译或运行。

## 公共规则与相关接口

依据：LinxISA 0.59.1 所引用 PTO 规范提交 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2` 的 [TIMG2COL schema](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/timg2col-schema.asl) 与 [执行/组装合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/timg2col-execution.asl)。库的重载和 SourceOrder 映射为本手册定义。

[返回算子索引](README.md)
