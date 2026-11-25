# TROWSUM

将输入 Tile 的每一行沿列方向求和，产生每行一个结果。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable tile_shape_out, Readable tile_shape_in>
void TROWSUM(tile_shape_out &&dst, tile_shape_in &&src);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `tile_shape_out` | 由对应实参推导的类型，满足 `Writable` 约束 | 由实参推导 |
| `tile_shape_in` | 由对应实参推导的类型，满足 `Readable` 约束 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src` | Readable | 支持 | 支持 | 不接受 |

例如 `VecTileM32<float,32,256,32,1>` 可以承载 32 个行结果，有效输出列数为1。后续消费者必须按有效列数 1 使用结果，不能将整个物理载体视为有效数据。使用 Reader 选取归约结果时，还需满足消费算子对片段布局和有效形状的要求。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 能容纳 R 个归约结果；普通结果描述有效列为 1 | 必填 |
| `src` | in | 已定义的 R×C 区域；R、C 均为正且不超过物理形状 | 必填 |

## 操作语义

普通 Tile 输出与 Writer 输出描述统一使用 TROWSUM。

输入有效形状为 R×C：

```text
dst[r,0] = sum(src[r,c], c = 0..C-1),  r = 0..R-1
```

逻辑输出为 R×1，dtype 与输入相同，不做广播、不读取旧 dst。归约范围由 **源的有效列数**决定。padding 不参与求和。

## 合法组合与限制

Part 表示输出结果几何，不能复用输入的大小。Reader 选择范围会改变归约域；部分列的行归约、部分行的列归约不会自动合并为完整结果。

| 项目 | 可用组合 |
| --- | --- |
| dtype | 输入输出相同：FP64、FP32、TF32、HF32、FP16、BF16、E4M3、E5M2；S/U 8、16、32、64 |
| 普通 Local | RowMajor 输入及相应行结果载体 |
| CUBE Local | 保持 M16/M32 CELL 布局；结果的数学形状仍为 R×1 |
| 物理容量 | Local为128B..64KiB，归约按该编码容量校验 |
| 别名 | 目标与源使用不同 Tile |

每行从同类型零开始，按列号递增逐项执行该dtype的加法；整数按位宽取模，浮点逐步舍入并汇总状态。物理结果几何、padding和发布见 [归约公共合同](ReductionRules.md#合法组合)。

Reader 输入以选中 Part 作为完整归约域。动态 R/C 从 src 读取；调用者需保证合法范围，不能认为所有动态错误都会先由 C++ wrapper 捕获。输出 padding 不应读取。

使用 Reader 输入时，选中列范围会改变求和范围：两段分别归约不会自动合并为整行结果。仅按行切分且每段保留完整有效列，才保持原来每行的完整归约。不能将逐元素 TADD 的分片等价性直接套在归约上。

Writer 的输出 Part 可以有比逻辑 R×1 更宽的物理形状。写入范围由 Part 的物理大小决定，不能用 Parent 总容量代替；first 分配 Parent，middle/last 复用同一 Parent。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Input = Tile<Location::Vec, float, 32, 32, BLayout::RowMajor>;
using Output = Tile<Location::Vec, float, 32, 1, BLayout::RowMajor>;
using InputGM = global_tensor<float, RowMajor<32, 32>>;
using InputGMInput = global_tensor<const float, RowMajor<32, 32>>;
using OutputGM = global_tensor<float, RowMajor<32, 1>>;

void row_sum(float *out, const float *in) {
  InputGMInput gi(in);
  OutputGM go(out);
  Input x;
  Output y;
  TLOAD(x, gi);
  TROWSUM(y, x);
  TSTORE(go, y);
}
```

输入 1024 个 float 全为 1 时，输出 32 个 float 全为 32。输出载体恰好 128 B。

### 边界核对

沿归约轴仅有一个有效元素2时，结果为2；其余物理padding不参与计算。 RowMajor行结果物理列为1；M16/M32行结果物理列保持源物理列。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

**相关：** [TADD](TADD.md)、[TLOAD](TLOAD.md)、[Reader/Writer](../TileReaderWriterDesign.md)。

**分片坐标与形状：** [分片几何合同](FragmentGeometry.md)。


依据：[TROWSUM 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/reduce-and-expand/row-reduction/TROWSUM.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
