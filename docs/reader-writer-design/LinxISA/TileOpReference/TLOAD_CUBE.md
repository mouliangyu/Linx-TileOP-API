# TLOAD_CUBE

将 GM 数据加载为 Local CUBE Tile，支持选择 padding，默认 Zero。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <TmaPadValue Pad = TmaPadValue::Zero, Writable D, GlobalMemoryView G>
void TLOAD_CUBE(D &&dst, const G &src);
```

## 参数与操作数角色

| 模板参数 | 含义 | 默认值 / 推导 |
| --- | --- | --- |
| Pad | Zero、Max、Min、Null padding | TmaPadValue::Zero |
| D | Local CUBE 目标计算视图 | 由 dst 推导 |
| G | 可读 GlobalMemoryView | 由 src 推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| dst | Writable | Local CUBE | 不接受 | Local CUBE Writer |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| dst | out | CUBE 目标；目标视图提供有效行列 | 必填 |
| src | in | 可读 GM 视图；行距按元素提供 | 必填 |

## 操作语义

按目标有效区域从 GM 加载并执行 ND→CUBE 布局转换。地址计算与传输规则见 [TLOAD](TLOAD.md#操作语义)。目标有效区域外按 Pad 处理；Zero 写零，Max/Min 使用 dtype 对应的 padding 值，Null 保留未定义 padding。

## 合法组合与限制

目标为 Local CUBE_M16/M32/N8，类型、地址、容量和几何条件沿用 [TLOAD 的合法组合](TLOAD.md#合法组合与限制)。Writer 输出描述按 Part 绑定本次加载区域、物理容量及 assemble 阶段，parent 遵守最终覆盖要求。GM 视图须提供本次有效区域的可读数据。

CUBE↔GM 布局转换采用 `BundleCubeTransportDataTypeSupported` 的类型域：HiF4X2 排除；M32 的 FP64/S64/U64 使用双 CELL；N8 的 U64 只用于 ND2N8 加载参数载体。普通 RowMajor 传输按普通 TLSU 类型域检查。固定依据：[CUBE transport dispatch](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-layout-conversion.asl)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<float, 32, 8>;
using G = global_tensor<const float, RowMajor<32, 8>>;
void example(V &dst, const float *input) {
  G source(input);
  TLOAD_CUBE(dst, source);
}
```

input 指向满足加载对齐条件的 32×8 连续可读 FP32 元素。调用后 dst 的有效逻辑元素等于对应 GM 元素，存储采用 M32 布局。

### 尾部与 Null

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Tail = VecTileM32<float, 32, 8, 20, 5>;
using Source = global_tensor<const float, RowMajor<20, 5>>;
void load_tail(Tail &dst, const float *input) {
  Source src(input);
  TLOAD_CUBE<TmaPadValue::Null>(dst, src);
}
```

input为100个连续可读FP32值，结果有效20×5逐元素相等；物理M32 32×8为1024B，其余位置为未定义Null padding。Pad=Zero时尾部写原始零，Max/Min分别使用dtype对应的极值padding。GM故障的部分读取/定义状态沿用TLOAD合同，完整输出尚未发布。此例按规范推导。


## 公共规则与相关接口

[TLOAD](TLOAD.md) · [传输规则](TransportRules.md) · [Writer](Writer.md) · [操作数角色](OperandRoles.md)。

[返回算子索引](README.md)
