# MGATHER_MASK

对每个活动索引，将 `src.base + offset[r,c]` 处的元素读入 dst。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

不提供访问范围时选择无 range 的重载；能给出全部访问起点的字节边界时，选择 IndexedByteRange 重载。范围不改变索引寻址语义。

```cpp
template <Writable D, Readable I, IndexedMaskReadable M, GlobalMemoryView G,
          TmaPadValue Pad = TmaPadValue::Null>
void MGATHER_MASK(D &&dst, const G &src, I &&offset, M &&mask);

template <Writable D, Readable I, IndexedMaskReadable M, GlobalMemoryView G,
          TmaPadValue Pad = TmaPadValue::Null>
void MGATHER_MASK(D &&dst, const G &src, I &&offset, M &&mask,
                  IndexedByteRange range);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `I` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `M` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |
| `Pad` | padding 方式 | `TmaPadValue::Null` |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `offset` | Readable | 支持 | 支持 | 不接受 |
| `mask` | IndexedMaskReadable | 支持 | 支持 | 不接受 |

`G` 满足 [GlobalMemoryView](CommonTypes.md#globalmemoryview)，提供 GM 基址、元素类型和访问属性。`src` 是可读 GM 源；不接受 Reader 片段或 Writer 输出描述。GM 元素类型须与 payload 的 dtype 匹配，不做隐式转换。`const G &` 只约束描述对象，不决定底层内存权限。

GM 地址为 `base + offset[r,c]`，offset 的单位为字节；G 的布局步长不参与本操作的地址计算。非 packed 访问满足元素自然对齐；packed 4-bit 每个索引访问一个完整字节，对应两个相邻 payload 元素。访问须满足相应内存权限。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 可读 GlobalMemoryView；提供 GM 基址和元素类型 | 必填 |
| `offset` | in | 索引 GM 字节位移 | 必填 |
| `mask` | in | 掩码输入；编码按本页重载及谓词合同 | 必填 |
| `range` | in | IndexedByteRange 字节范围，见范围合同 | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

对每个活动索引，将 `src.base + offset[r,c]` 处的元素读入 dst。offset 为字节位移，G 的行列步长不参与索引地址计算；packed 元素映射与掩码语义见 [索引 GM 规则](IndexedMemoryRules.md)。

## 合法组合与限制

mask 满足 IndexedMaskReadable：RowMajor 使用 Numeric U8；CUBE_M16/M32 支持 Numeric U8 或 PredicateCell。每个有效掩码字节为规范 0 或 1，PredicateCell 的比较 basis 独立于 payload dtype。1 执行访问；0 抑制该位置的地址生成与内存访问，gather 按 Pad 处理输出，scatter 保留内存原值。其他掩码字节值在效果前拒绝。packed 4-bit 时每个 mask 项控制同一索引对应的整字节元素对；mask 的有效列数为 payload 的一半，不能分别屏蔽两个 nibble。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 1, 32>;
using Mask = Tile<Location::Vec, uint8_t, 1, 128, BLayout::RowMajor, 1, 32>;
using G = global_tensor<const uint32_t, RowMajor<1, 32>>;
void example(V &dst, const uint32_t *memory, V &offset, Mask &mask) {
  G gm(memory);
  MGATHER_MASK(dst, gm, offset, mask);
}
```

memory 指向对齐的 32 个可读 U32；offset 已按上述公式初始化，mask 全为 1；各访问地址合法，无并发写。 按 offset[0,c]=4*c 访问第 c 个 GM 元素；dst 得到对应 GM 值。

### 范围重载

以下函数是上例的独立调用替代；输入条件和预期结果沿用上例，每次测试从相同初值开始。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 1, 32>;
using Mask = Tile<Location::Vec, uint8_t, 1, 128, BLayout::RowMajor, 1, 32>;
using G = global_tensor<const uint32_t, RowMajor<1, 32>>;
void example_with_range(V &dst, const uint32_t *memory, V &offset, Mask &mask) {
  G gm(memory);
  MGATHER_MASK(dst, gm, offset, mask, IndexedByteRange{0,124});
}

```

### 边界核对

32个U32访问起点为0,4,…,124，包络完整结束于base+128；range{0,123}不覆盖最后一项，违反调用者合同。range{4,0}在本请求效果前拒绝。 mask全0时不访问GM，gather的Null输出为已定义零位模式；mask字节2在效果前拒绝。 验证方式为固定规范推导；示例未编译或运行硬件。

### CUBE 谓词掩码

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = VecTileM32<uint32_t, 32, 4>;
using P = PredicateTile<V>;
using G = global_tensor<const uint32_t, RowMajor<32, 4>>;
void cube_mask(V &dst, const uint32_t *memory, V &offset, V &selector) {
  G gm(memory);
  P mask;
  TCMPS<CmpMode::NE>(mask, selector, uint32_t{0});
  MGATHER_MASK(dst, gm, offset, mask);
}
```

selector全为1、offset[r,c]=4*(4*r+c)，memory指向128个对齐U32时，所有位置参与访问。selector全0时，GM访问全部被抑制。调用者提供已定义的输入，gather输出独立；scatter输入保持已定义。

## 公共规则与相关接口

本接口同时遵守 [IndexedMemory 公共参数、类型、形状、别名及示例](IndexedMemoryRules.md)。该页中的规则与本页声明共同构成调用合同。

固定依据：[MGATHER_MASK 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_MASK.asl)及本页公共规则链接中的执行函数。

[返回算子索引](README.md)
