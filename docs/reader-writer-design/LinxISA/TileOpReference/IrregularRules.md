# 序列、三角矩阵与 Local 索引重排：公共规则

**算子声明：** [TCI](TCI.md)、[TCI_2D](TCI_2D.md)、[TCI_COL](TCI_COL.md)、[TCI_ROW](TCI_ROW.md)、[TGATHER](TGATHER.md)、[TSCATTER](TSCATTER.md)、[TTRI](TTRI.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。这些操作不访问 GM；GM 索引访问见 [IndexedMemory](IndexedMemoryRules.md)。

## TCI、TCI_2D、TCI_ROW、TCI_COL



D 为输出 Tile 类型，T 为起始标量类型；dst(out) 不需初始化，s(in) 是起始值，**没有默认实参**。descending 默认 0，只能为 0/1，TCI 输出 `s+c` 或 `s−c`。

TCI 目标为 Local RowMajor，ValidRow=1，ValidCol>0，dtype 为 S16/U16/S32/U32/S64/U64。TCI_2D、TCI_ROW、TCI_COL 目标角色为 Location::Left，布局为 CUBE_M16/M32（CubeTileM16/CubeTileM32），同样支持上述六种 dtype；row_step/col_step 是编译期 -1、0 或 1，结果为 `s+r*row_step+c*col_step`。TCI_ROW 等价于步长 (1,0)，TCI_COL 等价于 (0,1)。M16 有效行数≤16，M32 有效区域必须落入合法载体。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Sequence = Tile<Location::Vec, uint32_t, 1, 32>;
void sequence(Sequence &dst) { TCI(dst, uint32_t{10}); }
```

结果依次为 10..41。整数起点按目标宽度解释，结果按目标元素位宽取模。padding 不作为有效序列。示例未编译执行。

## TTRI



D 为 Local RowMajor 输出，dtype 为 FP64、FP32、FP16、S64、S32、S16、U64、U32、U16，有效 R/C 均为正。dst 为 out，无其他参数。该公开入口采用默认 lower、对角线偏移 0：`dst[r,c] = (c <= r ? 1 : 0)`。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Triangle = Tile<Location::Vec, float, 32, 32>;
void triangle(Triangle &dst) { TTRI(dst); }
```

第 0 行为 1,0,…，第 1 行为 1,1,0,…。示例未编译执行。

## TGATHER

参数字段、运算和专用几何由 [TGATHER 操作页](TGATHER.md) 定义。

## TSCATTER

参数字段、运算和专用几何由 [TSCATTER 操作页](TSCATTER.md) 定义。

## Local 索引操作的类型与错误

两种操作的 value 源目标同 dtype，支持非 packed 8/16/32/64 位数值载体；普通公开类型为 FP64/32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E3M2、E2M3、E8M0、S/U8、16、32、64。索引固定为 S16/U16/S32/U32/S64/U64。两种操作的源及索引使用普通非CUBE Local描述。TSCATTER目标沿用普通Local布局；TGATHER的值目标路径另接受合法CUBE_M16/M32目标，按目标布局存放相同逻辑元素。Shared及packed4不属于该类型域。

选择的是原始位，不做数值转换。TGATHER 的 padding 未定义；TSCATTER 的整个物理目标包括 padding 都写全零位并定义，但 E8M0 等无数值零编码的格式不能将全零位称为数学 0。

ISA 在写入前检查所有参与索引；负数、越界、未定义索引或被选中源，以及 scatter 重复目标会拒绝整个对应 Tile 操作，不发布部分结果。此故障处理范围为当前 Local 重排操作。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Data = Tile<Location::Vec, uint32_t, 32, 32>;
using Index = Tile<Location::Vec, uint32_t, 32, 32>;
void reorder(Data &gathered, Data &scattered, Data &x, Index &rows) {
  TGATHER(gathered, x, rows);
  TSCATTER(scattered, x, rows);
}
```

若 x[r,c]=100r+c，rows[r,c]=31−r，两种操作的输出均为 100(31−r)+c。索引是每列的排列，因此 scatter 不产生重复目标。示例未编译执行。

## Reader/Writer

TCI/TTRI 只有 Writable 输出角色。TGATHER/TSCATTER 的输入为 Readable、目标为 Writable；坐标、初始化及索引边界见 [分片几何](FragmentGeometry.md#序列三角形和-local-索引)。

b64 CUBE 序列使用 M32 的双 CELL 映射；M16 支持 16/32 位序列。
