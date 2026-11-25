# TADD

将两个 Local Tile 的对应有效元素相加，写入目标 Tile。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

```cpp
template <Writable D, Readable A, Readable B>
void TADD(D &&dst, A &&src0, B &&src1,
          unsigned UserValidCol = 0, unsigned UserValidRow = 0,
          unsigned UserPhysicalCol = 0);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `D` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `A` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `B` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `dst` | Writable | 支持 | 不接受 | 支持 |
| `src0` | Readable | 支持 | 支持 | 不接受 |
| `src1` | Readable | 支持 | 支持 | 不接受 |

维度选择、计算区域校验及输出元数据遵守 [公共有效维度规则](CommonTypes.md#有效维度与输出元数据)。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | out | 目标，结果存储与布局按本页合同 | 必填 |
| `src0` | in | 第一数值输入 | 必填 |
| `src1` | in | 第二数值输入 | 必填 |
| `UserValidCol` | in | 本次计算列数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserValidRow` | in | 本次计算行数，元素单位；0 使用该操作默认维度来源 | 0 |
| `UserPhysicalCol` | in | 本次物理列数，元素单位；0 保留计算视图物理列 | 0 |

## 操作语义

使用 `TADD` 计算；可选有效维度参数不改变元素类型或物理形状。

对 `0 ≤ r < R`、`0 ≤ c < C`：

```text
dst[r,c] = src0[r,c] + src1[r,c]
```

不读取旧 dst，不广播，也不进行隐式类型提升。输出有效区域外的值不可依赖。函数返回 `void`，结果位于 dst。

## 合法组合与限制

D/A/B 独立推导，允许普通 Tile 与片段混用；三者计算视图具有相同 dtype 和布局，输入有效区域须覆盖本次计算区域，输出有效区域为本次结果形状。Writer 取 Part 的几何，不取 Parent 总容量。

| 项目 | 可用组合 |
| --- | --- |
| 元素类型 | FP64、FP32、TF32、HF32、FP16、BF16、E4M3、E5M2；S/U 8、16、32、64 |
| 三个操作数 | 独立类型；计算视图的 dtype、物理形状、布局和容量匹配 |
| 存储 | Local；不接受 Shared 作为普通逐元素输入 |
| 布局 | 普通 RowMajor 或持久 Local CUBE_M16/M32，三个参数必须一致 |
| 容量 | 有效区域装入物理载体；Local活动分配容量128B..64KiB |
| 别名 | 普通源/目标同名读取操作前快照；Reader 借用须保持到读取结束 |

整数加法按操作位宽取模；浮点加法与状态位遵守 [逐元素执行合同](Numerics.md#逐元素执行合同)。padding、别名和发布见 [Elementwise 公共规则](ElementwiseRules.md#readerwriter-与别名)。

操作几何由 Part 决定，不由 Writer Parent 的总容量决定。两个读取片段和写入片段须有相同 dtype、布局和计算形状。CELL 偏移可以不同，位置不决定阶段。分片重载分别推导输入和输出类型，并按 Part 校验计算形状。

物理列覆写见 [公共物理列规则](CommonTypes.md#物理列覆写)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using AddTile = Tile<Location::Vec, float, 32, 32, BLayout::RowMajor>;
using AddGM = global_tensor<float, RowMajor<32, 32>>;
using AddGMInput = global_tensor<const float, RowMajor<32, 32>>;

void add32(float *out, const float *left, const float *right) {
  AddGMInput gx(left), gy(right);
  AddGM gz(out);
  AddTile x, y, z;
  TLOAD(x, gx);
  TLOAD(y, gy);
  TADD(z, x, y);
  TSTORE(gz, z);
}
```

调用者提供三个至少包含 1024 个 float 的 GM 区域。若 left 全为 1、right 全为 2，则 out 的 1024 个元素全为 3。

### 边界核对

U32 输入 UINT32_MAX 与 1，结果为 0。 这些结果由固定规范推导；编译和硬件运行未执行。

## 公共规则与相关接口

**相关：** [TLOAD](TLOAD.md)、[TSEL](TSEL.md)、[TROWSUM](TROWSUM.md)、[Reader/Writer 状态与偏移](../TileReaderWriterDesign.md)。


依据：[TADD 指令合同](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/elementwise-tile-tile/arithmetic/TADD.asl)（类型、形状、顺序、异常及数值状态）；C++ 角色和分片绑定遵守本库公共协议。

[返回算子索引](README.md)
