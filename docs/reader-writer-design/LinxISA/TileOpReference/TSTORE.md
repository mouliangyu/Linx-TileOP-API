# TSTORE

把已定义 Local 或已发布 Shared 源的有效矩形写入 GM；CUBE 源按逻辑元素转换为 GM ND 排列。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

本页按下列顺序列出全部重载；实参类型与参数列表共同决定选择。各重载的存储角色和专用要求见后文。

```cpp
template <GlobalMemoryView G, Readable S>
void TSTORE(G &dst, S &&src);

// Shared 形式见下方带 PEMask 的重载。
```

```cpp
template <int PEMask = 15, GlobalMemoryView G, SharedReadable S>
void TSTORE(G &dst, S &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | `15` |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `src` | Readable/SharedReadable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out（GM 内存） | 可写 GlobalMemoryView；其指向的 GM 内存接收结果 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |

## 操作语义

把已定义 Local 或已发布 Shared 源的有效矩形写入 GM；CUBE 源按逻辑元素转换为 GM ND 排列。

## 合法组合与限制

src 是已定义 Local/已发布 Shared 输入；dst 是 GM 内存写目标。写入有效矩形，GM 地址与行距来自 global_tensor，写入元素数由有效矩形确定。CUBE 形式按逻辑元素转换到 GM ND 布局；不能把 CUBE 原始 CELL 排列当作普通连续矩阵。GM dtype、可访问范围与源有效矩形必须匹配；不承诺把 padding 写入 GM。Shared重载的PEMask为编译期参与PE选择，默认15；各参与者使用自己的GM基址和行距。

`G` / `gm_shape` 满足 [GlobalMemoryView](CommonTypes.md#globalmemoryview)。目标 GM 必须可写，元素类型与存储源匹配。GM 形状和步长约束仍按本页传输规则检查，不能仅凭满足类型协议省略地址、范围和权限要求。

Local Reader 以 Part 有效形状写 GM，CELL 偏移不自动移动 GM 目标；调用者通过 GM subview 选择目标区域。

Shared 分片与发布的完整要求见 [Shared 存储合同](StorageBoundaries.md)。

Shared重载的PEMask可为0、1、2、4、8、12、14、15；0为严格no-op。每个参与 PE 写所选源视图，mask 不自动切分源。源为已发布、非 boxed RowMajor Shared，容量 128 B..256 KiB；dtype 与 GM 一致。完整 Shared 形式是同一合同的完整区域读取。

规则地址原子写回见 [TSTORE_ATOMIC_ADD](TSTORE_ATOMIC_ADD.md) 及其同族入口。

CUBE↔GM 布局转换采用 `BundleCubeTransportDataTypeSupported` 的类型域：HiF4X2 排除；M32 的 FP64/S64/U64 使用双 CELL；N8 的 U64 只用于 ND2N8 加载参数载体。普通 RowMajor 传输按普通 TLSU 类型域检查。固定依据：[CUBE transport dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-layout-conversion.asl)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32>;
using G = global_tensor<float, RowMajor<32, 32>>;
void example(float *output, V &src) {
  G dst(output);
  TSTORE(dst, src);
}
```

output 指向可写的 32×32 连续 float 区域，src 已定义。 src 全为 3 时，GM 的 1024 个元素均写为 3。

### Shared 写回与故障边界

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Shape = Tile<Location::Vec, uint32_t, 16, 8>;
using Published = SharedTile<Shape>;
using GM = global_tensor<uint32_t, RowMajor<16, 8>>;
void store_shared(uint32_t *output, Published &src) {
  GM dst(output);
  TSTORE<8>(dst, src);
}
```

src为已发布512B Shared值，有效元素均为7，output为可写且U32对齐的128元素数组；仅PE0写出128个7。Shared Reader的CELL偏移选择源，GM视图基址单独选择目标。普通TSTORE在首个内存故障处停止，先前完成的写入和事件可保留；Shared未发布时等待且无内存效果。

传输dtype同[TLOAD的类型表](TLOAD.md#合法组合与限制)，Local支持普通RowMajor及合法M16/M32/N8转换，b64按各布局专用规则检查；Shared为RowMajor。GM视图元素行距转换为字节B.IOR。源只读、目标只写有效矩形，padding不写回。此例按规范推导。


## 公共规则与相关接口

本接口同时遵守 [Transport 公共参数、类型、形状、别名及示例](TransportRules.md)。该页中的规则与本页声明共同构成调用合同。

[返回算子索引](README.md)
