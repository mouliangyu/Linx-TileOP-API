# 行列归约与索引归约：公共规则

**算子声明：** [TCOLARGMAX](TCOLARGMAX.md)、[TCOLARGMIN](TCOLARGMIN.md)、[TCOLMAX](TCOLMAX.md)、[TCOLMIN](TCOLMIN.md)、[TCOLPROD](TCOLPROD.md)、[TCOLSUM](TCOLSUM.md)、[TROWARGMAX](TROWARGMAX.md)、[TROWARGMIN](TROWARGMIN.md)、[TROWMAX](TROWMAX.md)、[TROWMIN](TROWMIN.md)、[TROWPROD](TROWPROD.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。[TROWSUM](TROWSUM.md) 单独说明行求和及物理载体；本章列出其他行/列归约。参数均无默认值，输入有效行列须为正。

## 参数约定



D 为结果 Tile 类型，S 为源 Tile 类型。dst(out) 接收结果，不读取旧值；src(in) 提供完整有效 R×C 矩形。有效维度来自 src，物理容量不扩大归约范围。

## 每个操作的结果

| 操作 | 输出有效形状 | 对应结果 |
| --- | --- | --- |
| TROWMAX | R×1 | dst[r,0] = max(src[r,0..C−1]) |
| TROWMIN | R×1 | dst[r,0] = min(src[r,0..C−1]) |
| TROWPROD | R×1 | dst[r,0] = product(src[r,0..C−1]) |
| TCOLSUM | 1×C | dst[0,c] = sum(src[0..R−1,c]) |
| TCOLMAX | 1×C | dst[0,c] = max(src[0..R−1,c]) |
| TCOLMIN | 1×C | dst[0,c] = min(src[0..R−1,c]) |
| TCOLPROD | 1×C | dst[0,c] = product(src[0..R−1,c]) |
| TROWARGMAX | R×1，U32 | 每行最大值的最小列索引 |
| TROWARGMIN | R×1，U32 | 每行最小值的最小列索引 |
| TCOLARGMAX | 1×C，U32 | 每列最大值的最小行索引 |
| TCOLARGMIN | 1×C，U32 | 每列最小值的最小行索引 |

索引从 0 开始，单位为元素位置。索引归约只输出索引，既不额外输出极值，也不将其编码进输入 dtype。

## 合法组合

值归约的源目标 dtype 相同，支持 FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、16、32、64。ARG 的输入为 FP64、FP32、FP16、BF16、S/U8、16、32、64，输出固定 uint32_t；b64 的 CUBE 形式使用 M32。

输入为 Local Tile，输出使用可承载相应行/列结果的 Local 布局。逻辑 R×1 或 1×C 不要求物理载体恰好如此窄；尤其不足 128B 的结果仍需合法分配容量。保留布局时不得将输出 padding 当成有效元素。源容量没有专为归约设置的 2048B 上限。

目标使用与源不同的 Tile。行归约按列号递增、列归约按行号递增进行左折叠：SUM 从同类型零开始，PROD 从同类型一开始，MIN/MAX/ARG 从首个元素开始。每一步使用该操作 dtype 的对应元素函数；整数求和/乘积按位宽取模，浮点每步产生的状态按位或汇总，结果保持规定的折叠顺序。ARG 使用该极值选择规则，保留最早获胜位置；NaN及符号零由同一MIN/MAX profile处理。输入维度为正。

RowMajor 行结果的物理列数为1，物理行数由目标容量和目标dtype推导；列结果保持源物理列数。CUBE 行结果的物理列数保持源物理列数，物理行为M16的16或M32的32；列结果保持源物理行数，物理列数由目标容量和dtype推导。目标容量按这些物理形状计算，ARG的U32结果容量可大于窄类型输入。源可使用等宽非packed解释，RCPE6M2不作为归约backing。

预检完整输入definedness、编码、形状、目标容量和分配；失败发生在发布前。完成时将有效结果、所选padding和累计数值状态一并发布。默认Null padding未定义；其他padding按操作dtype确定。Local Writer只改变输出范围和发布阶段，归约域仍是所选输入Part。

## 结果可检查的示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Input = Tile<Location::Vec, float, 32, 32>;
using RowValue = Tile<Location::Vec, float, 32, 1>;
using ColValue = Tile<Location::Vec, float, 1, 32>;
using RowIndex = Tile<Location::Vec, uint32_t, 32, 1>;
using ColIndex = Tile<Location::Vec, uint32_t, 1, 32>;
void reduce(RowValue &row_max, ColValue &col_sum,
            RowIndex &row_index, ColIndex &col_index, Input &x) {
  TROWMAX(row_max, x);
  TCOLSUM(col_sum, x);
  TROWARGMAX(row_index, x);
  TCOLARGMIN(col_index, x);
}
```

若 `x[r,c]=r+c`，row_max[r,0]=r+31，col_sum[0,c]=496+32c，row_index 全为 31，col_index 全为 0。示例输入由调用者预先加载，未编译执行。

## Reader/Writer

src 只能为已完成的输入，dst 为新结果。Reader 分片改变归约集合：沿被归约轴切分会产生部分归约，库不会自动合并。行 ARG 对一个子片段给出的列索引也不能未经调整就当作 parent 列索引。Writer 的 Part 描述归约结果存储，不得从输入 R×C 推导目标片段也为 R×C。

Writer 输出按归约结果的 Part 几何校验。Reader 输入的归约域就是 Part 的有效区域；ARG 的结果为 Part 内从 0 开始的索引，不自动加 parent 偏移。

依据：[TileOperandsLegal_ExecuteTileReduction](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/reduction-and-expansion.asl)；[TileReductionInitialValue、TileReductionStepWithFlags、ExecuteTileReductionToValue](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/reduction.asl)。
