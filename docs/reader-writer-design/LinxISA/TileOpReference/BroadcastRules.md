# 行列广播：公共规则

**算子声明：** [TCOLEXPAND](TCOLEXPAND.md)、[TCOLEXPANDADD](TCOLEXPANDADD.md)、[TCOLEXPANDDIV](TCOLEXPANDDIV.md)、[TCOLEXPANDEXPDIF](TCOLEXPANDEXPDIF.md)、[TCOLEXPANDMAX](TCOLEXPANDMAX.md)、[TCOLEXPANDMIN](TCOLEXPANDMIN.md)、[TCOLEXPANDMUL](TCOLEXPANDMUL.md)、[TCOLEXPANDSUB](TCOLEXPANDSUB.md)、[TROWEXPAND](TROWEXPAND.md)、[TROWEXPANDADD](TROWEXPANDADD.md)、[TROWEXPANDDIV](TROWEXPANDDIV.md)、[TROWEXPANDEXPDIF](TROWEXPANDEXPDIF.md)、[TROWEXPANDMAX](TROWEXPANDMAX.md)、[TROWEXPANDMIN](TROWEXPANDMIN.md)、[TROWEXPANDMUL](TROWEXPANDMUL.md)、[TROWEXPANDSUB](TROWEXPANDSUB.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。ROW 表示“每行一个值向各列展开”，COL 表示“每列一个值向各行展开”。输出几何由 dst 的有效区域决定。

## 参数约定



ROW 族提供编译期 BroadcastByteOffset，默认 0，单位为字节；COL 族不提供该参数。所有普通函数实参必填。偏移选择及布局约束见 [广播偏移](BroadcastRules.md#广播偏移)。

## 参数、形状和运算

D 为输出类型，A 为完整矩形源类型，B/S 为广播源类型。模板独立是为了容纳不同形状，dtype 配对遵守本页规则。

| 参数 | 方向 | ROW 族有效形状 | COL 族有效形状 |
| --- | --- | --- | --- |
| dst | out | R×C | R×C |
| src0 | in | R×C | R×C |
| src1 | in | R×Cb，Cb≥1 | Rb×C，Rb≥1 |
| src（无后缀 EXPAND） | in | R×Cb，Cb≥1 | Rb×C，Rb≥1 |

令 x=src0[r,c]，ROW 族的 v=src1[r,slot]（slot 由 BroadcastByteOffset 决定），COL 族的 v=src1[0,c]。

| 操作 | 每元素结果 | x=6，v=2 |
| --- | --- | --- |
| TROWEXPAND / TCOLEXPAND | v（取 src，无 src0） | 2 |
| TROWEXPANDADD / TCOLEXPANDADD | x+v | 8 |
| TROWEXPANDSUB / TCOLEXPANDSUB | x−v | 4 |
| TROWEXPANDMUL / TCOLEXPANDMUL | x×v | 12 |
| TROWEXPANDDIV / TCOLEXPANDDIV | x/v | 3 |
| TROWEXPANDMAX / TCOLEXPANDMAX | max(x,v) | 6 |
| TROWEXPANDMIN / TCOLEXPANDMIN | min(x,v) | 2 |
| TROWEXPANDEXPDIF / TCOLEXPANDEXPDIF | exp(x−v) | 约 exp(4) |

ROW 广播源可含多列；仅选择 slot 列作为每行广播值，其余列不提供广播值。源仍须满足本次布局合同；无执行掩码时整个有效区域须已定义。COL 源有效形状为 Rb×C（Rb≥1），只从第0行广播；额外有效行须已定义。

## 合法组合与数值

普通算术广播：同 dtype，支持 FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8、16、32、64。EXPDIF 广播的（源操作类型，目标类型）配对为 FP64→FP64、FP32→FP32、FP16→FP16、BF16→BF16、FP16→FP32、BF16→FP32。混合精度先精确扩展到 FP32，再做 FP32 减法和指数。Local 源目标布局必须一致，RowMajor 及受支持的 CUBE_M 布局使用相应广播视图；不接受 Shared handle 代替 Local 数学输入。

结果为新目标；src/src0/src1 均须已经定义。普通同名源/目标按操作前快照计算。EXPAND复制所选源位模式，保持NaN位且不产生数值状态；其他后缀使用 [逐元素执行合同](Numerics.md#逐元素执行合同)，整数DIV的活动广播除数为零时在效果前拒绝。默认Null padding未定义，其他padding按所选dtype填充。合法性、容量、分配和全部源快照先于结果发布；完整结果与状态一起发布，Writer遵守对应阶段。

## 示例：按行缩放，按列加偏置

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Matrix = Tile<Location::Vec, float, 32, 32>;
using Rows = Tile<Location::Vec, float, 32, 1>;
using Cols = Tile<Location::Vec, float, 1, 32>;
void broadcast(Matrix &scaled, Matrix &biased, Matrix &x,
                Rows &scale, Cols &bias) {
  TROWEXPANDMUL(scaled, x, scale);
  TCOLEXPANDADD(biased, scaled, bias);
}
```

若 x 全为 1，scale[r,0]=r，bias[0,c]=c，则 biased[r,c]=r+c。输入由调用者提供有效 Tile；示例未编译执行。

## Reader/Writer

dst 为 Writable，所有源为 Readable，但广播源必须保留其行/列语义。沿行切分 ROW 操作时必须选取对应行的广播值；沿列切分时仍需要相同的每行值。COL 操作相反。不能给所有参数同一个 CELL offset 就假定选中了对应逻辑区域。分片各轴及坐标合同见 [分片几何](FragmentGeometry.md)。

## 广播偏移

ROW 族八个入口（TROWEXPAND、ADD、SUB、MUL、DIV、MAX、MIN、EXPDIF）均使用首个模板参数 `unsigned BroadcastByteOffset = 0`。例如 `TROWEXPANDADD<2>(dst, matrix, row_values)` 在 FP16 CUBE 布局中选取 row_values 每行的第 1 列。COL 族没有这一参数。

RowMajor 只允许偏移 0，slot=0。CUBE_M16/M32 的偏移编码范围为 0..7；令 E 为操作 dtype 的元素字节数，要求偏移是 E 的倍数，slot=offset/E，小于广播源有效列数及该类型每 CELL 的逻辑列数。M16 偏移必须小于 8；M32 非 b64 必须小于 4，b64 M32 使用双 CELL 的 8 字节组，且只允许偏移 0。M16 不支持 b64。

该偏移只选择已绑定广播源的首个逻辑 CELL 组内的位置；读取更后面的组时先使用 Reader 的 CELL 偏移。两个偏移单位不同：Reader 偏移为 128 B，BroadcastByteOffset 为 CELL 组内每行的字节偏移。输入可用 Reader，输出可用 Writer，偏移规则作用于各自 Part。偏移非法的静态调用应诊断。

依据：[TileOperandsLegal_ExecuteTileExpandAs 与 TileExpansionBroadcastSelectorLegal](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/reduction-and-expansion.asl)；[广播执行](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/expansion.asl)。
