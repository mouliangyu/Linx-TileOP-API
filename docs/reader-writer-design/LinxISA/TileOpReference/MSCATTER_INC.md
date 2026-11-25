# MSCATTER_INC

对 `base + index[r,c]` 处的 GM 元素执行原子更新：`new = old >= limit ? 0 : old+1`。不产生 Local 旧值输出。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

不提供访问范围时选择无 range 的重载；能给出全部访问起点的字节边界时，选择 IndexedByteRange 重载。范围不改变索引寻址语义。

```cpp
template <Readable I, Readable V>
void MSCATTER_INC(uint64_t base, I &&index, V &&limit,
    uint32_t validCol, uint32_t validRow = 1);

template <Readable I, Readable V>
void MSCATTER_INC(uint64_t base, I &&index, V &&limit,
    uint32_t validCol, IndexedByteRange range, uint32_t validRow = 1);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `I` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `V` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `index` | Readable | 支持 | 支持 | 不接受 |
| `limit` | Readable | 支持 | 支持 | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `base` | in（GM 内存读写） | GM 基址，字节地址；原子访问须可读写 | 必填 |
| `index` | in | 索引 GM 字节位移 | 必填 |
| `limit` | in | INC/DEC 的回绕界限输入 | 必填 |
| `validCol` | in | 有效列数，元素单位 | 必填 |
| `validRow` | in | 有效行数，元素单位 | 1 |
| `range` | in | IndexedByteRange 字节范围，见范围合同 | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

对 `base + index[r,c]` 处的 GM 元素执行原子更新：`new = old >= limit ? 0 : old+1`。不产生 Local 旧值输出。

## 合法组合与限制

payload dtype：U32。

范围、访问对齐、原子性与分片规则见 [原子公共规则](AtomicsRules.md)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 1, 32>;
void example(uint64_t base, V &index, V &value) {
  MSCATTER_INC(base, index, value, 32);
}
```

base 指向对齐的 32 个可读写 U32，index[0,c]=4*c；所有输入已定义，各地址不重复，无其他并发访问。 GM 原值均为 5、value 全为 1 时，更新值为 0。

### 范围重载

以下函数是上例的独立调用替代；输入条件和预期结果沿用上例，每次测试从相同初值开始。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 1, 32>;
void example_with_range(uint64_t base, V &index, V &value) {
  MSCATTER_INC(base, index, value, 32, IndexedByteRange{0,124});
}

```

### 边界核对

32个U32访问起点为0,4,…,124，包络完整结束于base+128；range{0,123}不覆盖最后一项，违反调用者合同。range{4,0}在本请求效果前拒绝。 重复地址分别执行原子更新，旧值分配不按lane编号承诺。 验证方式为固定规范推导；示例未编译或运行硬件。

## 公共规则与相关接口

本接口同时遵守 [Atomics 公共参数、类型、形状、别名及示例](AtomicsRules.md)。该页中的规则与本页声明共同构成调用合同。

固定依据：[MSCATTER_INC 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/memory-and-data-movement/irregular/MSCATTER_INC.asl)及本页公共规则链接中的执行函数。

[返回算子索引](README.md)
