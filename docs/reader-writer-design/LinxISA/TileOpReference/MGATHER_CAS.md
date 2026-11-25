# MGATHER_CAS

在每个 lane 指定的 GM 地址执行原子比较交换，将观察到的旧值写入结果 Tile。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

范围未知时选第一式。已知全部访问起点的上下界时选第二式；range 位于 validCol 后、validRow 前。

本页按下列顺序列出全部重载；实参类型与参数列表共同决定选择。各重载的存储角色和专用要求见后文。

```cpp
template <Writable DstTile, Readable IndexTile,
          Readable ExpectedTile, Readable ReplacementTile>
void MGATHER_CAS(DstTile &&observedOld, uint64_t base,
                 IndexTile &&byteDisplacements, ExpectedTile &&expected,
                 ReplacementTile &&replacement,
                 uint32_t validCol, uint32_t validRow = 1);

template <Writable DstTile, Readable IndexTile,
          Readable ExpectedTile, Readable ReplacementTile>
void MGATHER_CAS(DstTile &&observedOld, uint64_t base,
                 IndexTile &&byteDisplacements, ExpectedTile &&expected,
                 ReplacementTile &&replacement,
                 uint32_t validCol, IndexedByteRange range,
                 uint32_t validRow = 1);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `DstTile` | 由对应实参推导的类型，满足 `Writable` 约束 | 由实参推导 |
| `IndexTile` | 由对应实参推导的类型，满足 `Readable` 约束 | 由实参推导 |
| `ExpectedTile` | 由对应实参推导的类型，满足 `Readable` 约束 | 由实参推导 |
| `ReplacementTile` | 由对应实参推导的类型，满足 `Readable` 约束 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `observedOld` | Writable | 支持 | 不接受 | 支持 |
| `byteDisplacements` | Readable | 支持 | 支持 | 不接受 |
| `expected` | Readable | 支持 | 支持 | 不接受 |
| `replacement` | Readable | 支持 | 支持 | 不接受 |

```cpp
IndexedByteRange range{min, max};
```

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `observedOld` | out | 每 lane 一个交换前的 GM 值；不读取旧输出 | 必填 |
| `base` | in（GM 内存读写） | 64 位 GM 字节地址 | 必填 |
| `byteDisplacements` | in | 每 lane 相对 base 的字节位移 | 必填 |
| `expected` | in | 与旧值进行整数相等比较的值 | 必填 |
| `replacement` | in | 比较成功时写入 GM 的值 | 必填 |
| `validCol` | in | 动态列维度，单位为元素；静态列类型使用类型维度 | 必填 |
| `validRow` | in | 动态行维度，单位为元素；静态行类型使用类型维度 | 1 |
| `range` | in | 相对 base 的有符号 64 位最小/最大访问起点 | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

每个有效 lane 独立执行：

```text
address = base + byteDisplacements[r,c]
atomically:
    old = memory[address]
    if old == expected[r,c]:
        memory[address] = replacement[r,c]
observedOld[r,c] = old
```

索引单位是**字节**，无隐式元素大小乘法，也不加 `r * row_stride`。输出为旧值；比较 `observedOld == expected` 可判断该 lane 是否交换成功。

min/max 是访问**起点**的闭区间，单位为字节。若 payload 宽度为 W，则整个地址包络为 `[base+min, base+max+W)`。例如 32 个连续 U32 元素的位移为 0,4,…,124，范围是 `{0,124}`。

范围不做逐 lane 越界检查，不缩放索引，不裁剪地址，也不放宽内存顺序。调用者保证每个访问起点落在范围内；允许负边界。`min > max` 会在当前参与 PE 产生副作用前 fault，其他 PE 已发生的副作用不回滚。

## 合法组合与限制

四个模板参数分别指定结果、位移、期望值和替换值的 Local Tile 类型。

| 项目 | 要求 |
| --- | --- |
| payload | observedOld、expected、replacement 同 dtype：U16、U32 或 U64 |
| index dtype | S32、U32、S64 或 U64；不要求与 payload 宽度相同 |
| 形状 | 四个计算视图具有相同逻辑有效行列，所有有效 lane 均有输入；物理列数、容量及各自 LB2 独立，不要求相同 |
| 布局 | 四个计算视图布局类相同：RowMajor、CUBE_M16 或 CUBE_M32；不支持 N8，各自满足 dtype 对应的物理布局约束 |
| 地址 | 每个最终地址满足 payload 自然对齐：U16 为 2 B，U32 为 4 B，U64 为 8 B；完整元素可访问，地址运算不回绕 |
| 输出别名 | 使用独立 observedOld；实现用 early-clobber 输出避免覆盖尚未读取的输入 |

接口按 DstTile 的静态/动态维度选择分支：静态维度直接来自类型，对应的 validCol/validRow 实参不覆写它。动态维度才读取实参。传 `validCol=1` 不会把静态 32 列类型裁剪为 1 列。

原子性针对单次元素比较交换，不针对整个 Tile。多个 lane 或 PE 访问同一地址时，各次 CAS 可以观察到不同旧值；不能假定按行列顺序执行，也不能把返回 Tile 当成同一时刻的 GM 快照。此接口不提供 memory_order 参数；不能仅凭 inline asm 的 memory clobber 推导任意跨设备的 C++ 原子顺序保证。

payload/index dtype 和部分静态布局形状错误由 `static_assert` 拒绝。非法地址、未对齐访问和错误范围声明不能假定由 C++ wrapper 预检。ISA 在提交前探测本请求的所有 active 地址；探测失败时本请求不产生原子事件、不发布旧值。其他 PE 已提交的效果不回滚，成功请求中的 lane 也不构成整体原子事务。

本页支持上述 Reader/Writer 组合。显式 range 指定访问起点位移的闭区间；省略 range 使用无显式包络的重载。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Values = Tile<Location::Vec, uint32_t, 1, 32, BLayout::RowMajor>;
using GM = global_tensor<uint32_t, RowMajor<1, 32>>;
using GMInput = global_tensor<const uint32_t, RowMajor<1, 32>>;

// offsets 指向 {0,4,...,124}；expect/repl 各包含 32 个值。
void cas32(uint32_t *memory, uint32_t *old_out,
           const uint32_t *offsets, const uint32_t *expect,
           const uint32_t *repl) {
  GMInput gi(offsets), ge(expect), gr(repl);
  GM go(old_out);
  Values index, expected, replacement, old;
  TLOAD(index, gi);
  TLOAD(expected, ge);
  TLOAD(replacement, gr);
  MGATHER_CAS(old, reinterpret_cast<uint64_t>(memory), index,
               expected, replacement, 32, IndexedByteRange{0, 124});
  TSTORE(go, old);
}
```

没有并发写入，memory 与 expect 全为 5、repl 全为 9 时，old_out 全为 5，memory 变为 9。若某元素原为 6，则该元素返回 6 且保持 6。

### 范围重载

以下函数是上例的独立调用替代；输入条件和预期结果沿用上例，每次测试从相同初值开始。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Values = Tile<Location::Vec, uint32_t, 1, 32, BLayout::RowMajor>;
using GM = global_tensor<uint32_t, RowMajor<1, 32>>;
using GMInput = global_tensor<const uint32_t, RowMajor<1, 32>>;

// offsets 指向 {0,4,...,124}；expect/repl 各包含 32 个值。
void cas32_without_range(uint32_t *memory, uint32_t *old_out,
           const uint32_t *offsets, const uint32_t *expect,
           const uint32_t *repl) {
  GMInput gi(offsets), ge(expect), gr(repl);
  GM go(old_out);
  Values index, expected, replacement, old;
  TLOAD(index, gi);
  TLOAD(expected, ge);
  TLOAD(replacement, gr);
  MGATHER_CAS(old, reinterpret_cast<uint64_t>(memory), index,
               expected, replacement, 32);
  TSTORE(go, old);
}

```

### 边界核对

32个U32访问起点为0,4,…,124，包络完整结束于base+128；range{0,123}不覆盖最后一项，违反调用者合同。range{4,0}在本请求效果前拒绝。 原值6、expected5、replacement9时返回6且内存保持6。 验证方式为固定规范推导；示例未编译或运行硬件。

## 公共规则与相关接口

**相关：** [TLOAD](TLOAD.md)、[范围扩展原始合同](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/docs/tileop-usage/indexed-tlsu-range.md)。

固定依据：[MGATHER_CAS 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MGATHER_CAS.asl)及本页公共规则链接中的执行函数。

[返回算子索引](README.md)
