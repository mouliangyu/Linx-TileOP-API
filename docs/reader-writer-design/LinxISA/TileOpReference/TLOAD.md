# TLOAD

将 GM 数据加载到 Local 或 Shared Tile；目标为 Local CUBE 时同时完成 ND→CELL 布局转换。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

本页按下列顺序列出全部重载；实参类型与参数列表共同决定选择。各重载的存储角色和专用要求见后文。

```cpp
template <Writable D, GlobalMemoryView G>
void TLOAD(D &&dst, const G &src);

template <is_tile_data_v shp, int PEMask, GlobalMemoryView gm_shape>
SharedTile<shp> TLOAD(const gm_shape &src);

template <WeightLayoutEnum WeightLayout, int PEMask = 1,
          is_tile_data_v shp, GlobalMemoryView gm_shape>
void TLOAD(SharedTile<shp> &dst, const gm_shape &src,
           WeightTLOADParams params);
```

```cpp
template <int PEMask, SharedWritable D, GlobalMemoryView G>
void TLOAD(D &&dst, const G &src);

```

### 权重参数构造

```cpp
struct WeightTLOADParams {
  uint64_t shape_word = 0;
  uint64_t start_word = 0;
};
constexpr WeightTLOADParams make_weight_tload_params(
    uint16_t cin, uint16_t cout, uint8_t kernel_h, uint8_t kernel_w,
    uint32_t n_start = 0, uint32_t k_start = 0);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |
| `shp` | Shared 形状类型 | 返回值形式须显式指定；目标实参形式可推导 |
| `PEMask` | 编译期参与PE位掩码 | 普通Shared显式指定；权重重载为1 |
| `gm_shape` | GlobalMemoryView 类型 | 由实参推导 |
| `WeightLayout` | 权重源布局 | 显式指定 |

| 重载 | 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- | --- |
| Local TLOAD | `dst` | Writable | Local | — | Local Writer |
| Shared 目标形式 | `dst` | SharedWritable | Shared | — | Shared Writer |
| 权重加载 | `dst` | SharedTile<shp> | 完整 Shared | — | — |

表中“—”表示该参数角色不适用。返回值形式 `TLOAD<shp, PEMask>(src)` 直接返回完整 SharedTile。

| 参数 | 适用重载 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- | --- |
| `dst` | Local、Shared 目标、权重加载 | out | 目标，存储与布局按对应重载确定 | 必填 |
| `src` | 全部加载重载 | in | 可读 GM 视图 | 必填 |
| `params` | 权重加载 | in | WeightTLOADParams 权重形状与 N/K 元素窗口参数 | 必填 |

### 权重参数字段

`cin`/`cout` 为输入/输出通道数；`kernel_h`/`kernel_w` 为核高/宽，均为必填。`n_start`/`k_start` 为 N/K 元素起点，默认均为 0。返回 WeightTLOADParams，不执行加载。

构造器按下表打包，无内存或加载副作用。窄类型实参在C++转换后打包，调用者须在转换前保证数值可表示。

| 字 | 位段 | 字段 |
| --- | --- | --- |
| shape_word | 15:0 / 31:16 | cin / cout |
| shape_word | 39:32 / 47:40 | kernel_h / kernel_w |
| shape_word | 63:48 | 保留，构造器写0 |
| start_word | 31:0 / 63:32 | n_start / k_start |

例如 `make_weight_tload_params(20, 64, 3, 3, 2, 32)` 得 `shape_word=0x0000030300400014`、`start_word=0x0000002000000002`。正通道/核维度、窗口和C0对齐在加载时按本页要求检查。源基址、shape_word、start_word依次绑定同一条三源B.IOR，目标selector为0。

显式选择 CUBE padding 的入口见 [TLOAD_CUBE](TLOAD_CUBE.md)；TLOAD 的 CUBE 路径使用 Zero padding。

## 操作语义

普通 RowMajor、非 packed 元素的地址关系为：

```text
dst[r,c] = load(src.base + r * row_stride_bytes + c * sizeof(element))
```

## 合法组合与限制

返回 SharedTile 的重载直接返回完整 Tile，没有 Writer 参数。每次分片的 GM 起点由调用者给出，cell_offset 只定位目标。

| 需求 | 入口 |
| --- | --- |
| GM 矩形 → 普通 Local | `TLOAD(dst, src)`，非 CUBE 重载 |
| GM 矩形 → Local CUBE | `TLOAD(dst, src)`，CUBE 重载自动选择转换 |
| 创建静态形状 Shared 结果 | `TLOAD<Shape, PEMask>(src)` |
| 写入指定 Shared 描述 | `TLOAD<PEMask>(dst, src)`，Shared目标重载；动态有效区域预先设置在dst上 |
| 卷积权重 → Shared NK | `TLOAD<OHWI2NK/ OIHW2NK>(dst, src, params)` |

Local 的 R/C 来自目标计算视图；Shared 的 R/C 来自 parent 有效区域，物理列距也由 parent 提供。GM 必须覆盖实际访问的地址集合。CUBE 重载保持逻辑元素坐标，同时改变物理排列。加载不读取旧 dst，不修改 GM。

`global_tensor` 构造器的 stride 按**元素**表达，wrapper 的 `GetStrideBytes(3)` 换算为汇编所需**字节**跨度。传入 pitched 子矩阵时不能提前再乘一次元素字节数。packed 类型的地址关系按其存储格式计算，不能直接套用上面的 `sizeof(element)` 公式。

| 项目 | 要求 |
| --- | --- |
| dtype | 同类型传输；FP64/32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E3M2、E2M3、E8M0；E2M1X2、E1M2X2、HiF4X2、S4X2、U4X2；S/U 8、16、32、64 |
| 类型转换 | 普通 TLOAD 没有目标转换 dtype 参数，不用于数值 cast；CUBE 路径显式要求源目标 dtype 相同 |
| 容量 | Local活动容量128B..64KiB，Shared为128B..256KiB；CUBE CELL 存储必须装入目标容量 |
| 有效区域 | 正行列数且不超过物理形状，GM 对应地址可访问 |
| Local CUBE | CubeM16→ND2M16，CubeM32→ND2M32，CubeN8→ND2N8 |
| Shared完整目标 / 返回值 mask | 显式单bit：1、2、4、8 |
| Shared Writer mask | 显式1、2、4、8、12、14、15，按组装阶段及覆盖规则使用 |
| Shared 权重 mask | 此公开重载仅接受单 bit：1、2、4、8 |

统一 CUBE 入口使用默认 Zero padding；普通加载的有效区外数据不作为已定义结果使用。Local 输出接受普通 Tile 或 Writer 输出描述，按计算视图选择普通/CUBE 布局转换；Reader 片段不能作为目标。

cin/cout 为正通道数，kernel_h/kernel_w 为 1..255；n_start/k_start 分别是 N/K 元素窗口起点。OHWI 源为 `[Cout,Kh,Kw,Cin]`，OIHW 源为 `[Cout,Cin,Kh,Kw]`。输出为非 boxed、非 CUBE 的 RowMajor Shared `[N,K]`；K 规范顺序是 `[kh,kw,c1,c0]`，c0 最快，补齐通道写 raw zero 且不读取 GM。K 起点和有效 K 必须按 dtype 的 C0 对齐。

C0 为 32 字节中的元素数，不以 128B CELL 对齐代替。

| dtype | C0（元素） |
| --- | --- |
| FP32/TF32/HF32/S32/U32 | 8 |
| FP16/BF16/S16/U16 | 16 |
| HiF8/E4M3/E5M2/E8M0/S8/U8 | 32 |

其余 dtype 不属于该权重加载模式。`C1=ceil(cin/C0)`，完整 K 为 `kernel_h*kernel_w*C1*C0`；要求 n_start+有效N≤cout、k_start+有效K≤完整K，物理列数为非零二次幂。例：FP16、Cin=20、3×3 kernel 得 C0=16、C1=2、K=288；k_start=32、有效K=64 合法，k_start=40 不合法。当前扩展不提供 grouped/depthwise、batch>1 或 OHWI2KN/OIHW2KN。

Shared generation 必须完成发布才能被消费者使用。分片加载的每次 GM 起点由调用者传入，Writer 的 CELL 偏移只定位目标，不会自动推进 GM 指针。

`G` / `gm_shape` 满足 [GlobalMemoryView](CommonTypes.md#globalmemoryview)。源 GM 必须可读，元素类型与加载目标匹配。GM 形状和步长约束仍按本页传输规则检查，不能仅凭满足类型协议省略地址、范围和权限要求。

Shared 分片与发布的完整要求见 [Shared 存储合同](StorageBoundaries.md)。

[TLOAD_CUBE](TLOAD_CUBE.md) 支持选择 CUBE padding，默认 Zero；普通 TLOAD 的 CUBE 路径使用 Zero。关联写入仍使用同名入口和 Writer 阶段，不增加 `_ASS` 名称。Shared 首次 producer 建立 generation，后续阶段引用它；Shared mask 及物理范围须满足发布合同。

完整Shared目标与返回值形式由一个显式选择的PE发布整个parent；多PE写入由Shared Writer提供B.ASSEMBLE范围和阶段。此规则与[Shared发布合同](StorageBoundaries.md#shared-writer)一致，默认调用不会隐式重叠写同一个parent。

普通加载在首个GM故障处停止；先前完成的读取事件及部分目标数据可能保留，部分Local结果或Shared generation尚未构成完整就绪结果。CUBE有效区按目标坐标加载、尾部按Pad；普通模式的padding不作为有效输入。依据[TLOAD固定合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/regular/TLOAD.asl)。

CUBE↔GM 布局转换采用 `BundleCubeTransportDataTypeSupported` 的类型域：HiF4X2 排除；M32 的 FP64/S64/U64 使用双 CELL；N8 的 U64 只用于 ND2N8 加载参数载体。普通 RowMajor 传输按普通 TLSU 类型域检查。固定依据：[CUBE transport dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-layout-conversion.asl)。

### Shared Writer 的源地址与维度

Shared TLOAD 的 LB0/LB1/LB2 分别绑定 parent 有效列数、有效行数、物理列数。Part 的容量绑定 WriterSizeCode，cell_offset 定位 Shared 目标；Part 的有效行列不覆盖上述 parent 维度。

Shared 组装按 parent 的物理元素容量分成四个源区间。多PE时，PE i 从其自己的GM基址读取第 i 个四分之一区间与 parent 有效域的交集，并受 writer payload容量限制；单PE时源地址按整个parent有效矩形探测。源在候选片段内从零放置，再按目标cell_offset提交。

例：FP32 parent32×8、1024B，四PE、Part8×8/256B，各PE使用同一个32×8 GM基址及32B行距；源行区间分别为[0,8)、[8,16)、[16,24)、[24,32)，目标偏移0/2/4/6 CELL。若调用者再把每PE基址前移8*i行，实际源地址将被重复前移。该例核实地址及容量；完整阶段到实际PE提交身份的lowering仍由[Shared提交核对项](../TileOpContractEvidence.md#shared-提交身份)跟踪。

依据：[TLOADShared](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/shared-movement.asl)、[Shared dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/shared-tlsu.asl)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Matrix = VecTileM32<float, 32, 32>;
using GM = global_tensor<float, RowMajor<32, 32>>;
using GMInput = global_tensor<const float, RowMajor<32, 32>>;

void load_matrix(Matrix &dst, const float *input) {
  GMInput src(input);
  TLOAD(dst, src);
}
```

若 input[r*32+c] 为 r*32+c，dst 的逻辑元素 `[r,c]` 具有相同值；其物理存储已经变为 CUBE_M32。调用方须保证 GM 生命周期与访问同步；TLOAD 不等于对任意其他生产者完成同步。

### Shared 返回值、指定目标与权重

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Shape = Tile<Location::Vec, __half, 8, 16>;
using Shared = SharedTile<Shape>;
using GMInput = global_tensor<const __half, RowMajor<8, 16>>;
Shared load_shared(const __half *input) {
  GMInput source(input);
  return TLOAD<Shape, 8>(source);
}
void load_into_shared(Shared &dst, const __half *input) {
  GMInput source(input);
  TLOAD<8>(dst, source);
}
void load_weights(Shared &dst, const __half *weights) {
  GMInput source(weights);
  auto params = make_weight_tload_params(16, 8, 1, 1);
  TLOAD<OHWI2NK, 8>(dst, source, params);
}
```

这些函数按内联设备代码使用。每个input/weights指向256B连续可读FP16数据，元素初始化为其线性下标。仅PE0执行整块Shared发布，结果逻辑值为r*16+c。权重例的C0=16、C1=1、K=16、N=8，OHWI地址与输出NK一致。单bit mask为1/2/4/8时分别选择对应PE完成整块发布；多PE的组装另按Writer分支调用。

Local边界：M16排除b64，M32的b64采用双CELL；N8的U64仅用于允许的参数载体加载，后续消费者仍检查自身类型域。CUBE padding可通过TLOAD_CUBE显式选择。以上示例及边界按规范推导，尚未编译或运行硬件。


## 公共规则与相关接口

**相关：** [TADD](TADD.md)、[TMATMUL_ACC](TMATMUL_ACC.md)、[MGATHER_CAS](MGATHER_CAS.md)。

[返回算子索引](README.md)
