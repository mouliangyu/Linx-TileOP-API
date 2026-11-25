# 矩阵、MX 与 GEMV：公共规则

**算子声明：** [TGEMV](TGEMV.md)、[TGEMV_ACC](TGEMV_ACC.md)、[TGEMV_BIAS](TGEMV_BIAS.md)、[TGEMV_MX](TGEMV_MX.md)、[TGEMV_MX_ACC](TGEMV_MX_ACC.md)、[TGEMV_MX_BIAS](TGEMV_MX_BIAS.md)、[TMATMUL](TMATMUL.md)、[TMATMUL_BIAS](TMATMUL_BIAS.md)、[TMATMUL_MX](TMATMUL_MX.md)、[TMATMUL_MX_ACC](TMATMUL_MX_ACC.md)、[TMATMUL_MX_BIAS](TMATMUL_MX_BIAS.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。D 始终为新输出；ACC 的 C 为显式已定义输入。完整的协作布局、输入数值类、C/D 独立性和 K 分片例子见 [TMATMUL_ACC](TMATMUL_ACC.md)。后处理见 [Options](Options.md)。

## 选择操作

| 族 | 初始累加值 | 额外数学输入 |
| --- | --- | --- |
| TMATMUL / TGEMV | 零 | 无 |
| 后缀 _ACC | 显式 C | C 与 D 同有效形状，dtype 为累加类型 |
| 后缀 _BIAS | 零；乘积和完成后再加 Bias | Local CUBE_N8，逻辑 1×N，dtype 为累加类型 |
| 名称含 _MX | 对 A/B 按 K 分组缩放后乘加 | 由各侧 dtype 决定 scale 是否存在 |

TMATMUL 计算 A[M,K]×B[K,N]；TGEMV 参数先写 mtx 后写 vec，但数学运算是 **vec[1,K]×mtx[K,N]**，D 为 1×N。输入顺序按声明中的 mtx、vec 传入。

## 公共参数

| 名称 | 方向与合同 |
| --- | --- |
| d / dst / 基础 TMATMUL 的 c | out；不读取旧结果；dtype 由 options 决定 |
| ACC 的 c | in；AccType、M×N；与 d 不同 Tile 索引 |
| a / vec | in；Left，M×K / 1×K |
| b / mtx | in；Right，逻辑 K×N |
| bias | in；1×N，沿 M 广播，不能传完整 C 代替 |
| scale_a / sa / svec | in；A/vec 的分组 scale |
| scale_b / sb / smtx | in；B/mtx 的分组 scale |
| options | in；可借用参数及辅助输出，必须存活到调用结束 |
| groupM | in；核级行数 1..128，仅 TMATMUL Local-A/Shared-B 形式；有 options 时位于其后 |
| Attr | 编译期 FixpAttr，默认全零；无 options 形式使用，只能选择不需额外 operand 的设置 |
| ScaleMask | 编译期两位，默认 3；bit0 对应 A/vec scale，bit1 对应 B/mtx scale |

所有数学输入先初始化。输出 padding 不属于数学结果。以下模板参数可由实参推导，默认值逐声明列出；同名 options 和无 options 形式是不同重载。只删去实现 inline attribute，不用宏折叠接口。

## 布局与 dtype

普通矩阵的浮点输入产生 FP32 累加；有符号输入产生 S32，无符号输入产生 U32。完整 dtype 配对见 [TMATMUL_ACC](TMATMUL_ACC.md#dtype-配对)。Local Left 为 M16/M32、Right 为 N8、D/C 为同一 M 布局。GEMV 仅 Local，Left 的有效行数为 1；不支持 Shared、transpose 或 CScale。

Shared TMATMUL 只接受 Local-A/Shared-B 或 Shared-A/Shared-B。Shared A 在 TransA=0 时存 groupM×K，置位后存 K×groupM；Shared B 在 TransB=0 时存 N×K，置位后存 K×N。Local B 始终按逻辑 K×N 描述。四 PE 分工及尾行见 TMATMUL_ACC，不能将 groupM 当作每 PE 的 M。

## MX 重载约束

`mx_scale_mask_v<Left, Right>` 是编译期类型查询：两侧 primary 属于 MX 类型域时，按是否需要 scale 返回 bit0=Left、bit1=Right 的 0..3；任一侧类型不在 MX 域时返回 -1。FP16/BF16 不需要 scale；E4M3/E5M2/E2M1X2/E1M2X2/HiF4X2 需要 scale。GEMV 另按其类型域排除 HiF4X2。Shared 类型查询其 payload dtype。

所有 MX 声明将该查询放入 requires：无 scale、仅 Left、仅 Right、双 scale 分别匹配 0/1/2/3。完整 Options 形式与显式 ScaleMask 匹配；缺失的 scale 槽使用 NoOperand。这样 scale 即使带 Left/Right 角色，也按 primary 的类型需求唯一选择重载。GEMV 查询顺序为 `<Vec, Mtx>`。匹配后继续校验 scale dtype、布局、存储配对和形状。

## MX scale

MX 的 FP16/BF16 路径不带 scale；E4M3/E5M2/E2M1X2/E1M2X2 需要 E8M0 scale，每 32 个 K 元素一组。Matrix-MX 的 HiF4X2 需要 U32 scale，每 64 个 K 元素一组；HiF4X2 不因此加入普通 Matrix 或 GEMV 类型集合。两侧独立计算 `G=ceil(K/group_size)`，尾组合法。

| scale | Local 物理布局/有效形状 | Shared 物理布局/有效形状 |
| --- | --- | --- |
| A | CUBE_M32，M×G_A | RowMajor，groupM×G_A |
| B | CUBE_M32，N×G_B | RowMajor，N×G_B |

Matrix-MX与GEMV-MX需要Local scale时，该scale的M/N主维度须不超过32；Shared scale按其普通Shared容量和形状校验。

scale 的 Local/Shared 存储必须与对应 primary 相同。Shared scale **不随 TransA/TransB 转置**，转置只影响 primary。B scale 的语义索引是 [g,n]，物理索引是 [n,g]。E8M0 一个 CELL 为 32×4，U32 为 32×1；先重复 K-group，再重复行/N 块。HiF4 字解释见 [数值与编码](Numerics.md)。

无 scale、仅 A scale、仅 B scale 的公开重载用于符合 dtype 的组合，不能为了省参数删除必要 scale。完整 options 形式的 ScaleMask 必须与类型一致；GEMV 中 bit0 是 vec，虽然 vec 在参数列表后面。缺省 3 仅适合两侧均需 scale 的情况。

## 示例：矩阵乘与列偏置

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using A = CubeTileM16<float, 16, 16>;
using B = CubeTileN8<float, 16, 8>;
using D = CubeAccumulatorM16<float, 16, 8>;
using Bias = CubeBias<float, 8>;
void product(D &plain, D &biased, A &a, B &b, Bias &bias) {
  TMATMUL(plain, a, b);
  TMATMUL_BIAS(biased, a, b, bias, fixp::keep_acc());
}
```

a/b 全为 1，bias 全为 2 时，plain 每项为 16，biased 每项为 18。输入由调用者初始化。GEMV 将 A 的有效行数设为 1，并改用 `TGEMV(d,mtx,vec)`；其他 N/K 关系不变。示例未编译执行。

## 更多形状与格式示例

### groupM 大于64的 M32 尾行

<!-- audit-example: matrix_group70 -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace matrix_group70 {
using A = CubeTileM32<__half, 32, 64, DYNAMIC, 35>;
using B = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;
using MXA = CubeTileM32<__fp8_e4m3, 32, 64, DYNAMIC, 35>;
using MXB = SharedTile<SharedMatrixRight<__fp8_e4m3, 8, 64, 8, 35>>;
using SA = VecTileM32<__fp8_e8m0, 32, 4, DYNAMIC, 2>;
using SB = SharedTile<Tile<Location::Vec, __fp8_e8m0, 8, 16,
                           BLayout::RowMajor, 8, 2>>;
using D = CubeAccumulatorM32<float, 32, 8, DYNAMIC, 8>;
using Row = VecTileM32<float, 32, 1, DYNAMIC, 1>;
using Bias = CubeBias<float, 8>;
void product(D &dst, Row &row, A &a, B &b) {
  TMATMUL(dst, a, b, fixp::keep_acc().row_max(row), size_t{70});
}
void accumulate(D &dst, Row &row, D &c, A &a, B &b) {
  TMATMUL_ACC(dst, c, a, b, fixp::keep_acc().row_max(row), size_t{70});
}
void biased(D &dst, Row &row, A &a, B &b, Bias &bias) {
  TMATMUL_BIAS(dst, a, b, bias, fixp::keep_acc().row_max(row), size_t{70});
}
void scaled(D &dst, Row &row, MXA &a, SA &sa, MXB &b, SB &sb) {
  TMATMUL_MX(dst, a, sa, b, sb, fixp::keep_acc().row_max(row), size_t{70});
}
void scaled_accumulate(D &dst, Row &row, D &c,
                       MXA &a, SA &sa, MXB &b, SB &sb) {
  TMATMUL_MX_ACC(dst, c, a, sa, b, sb,
                 fixp::keep_acc().row_max(row), size_t{70});
}
void scaled_biased(D &dst, Row &row, MXA &a, SA &sa,
                   MXB &b, SB &sb, Bias &bias) {
  TMATMUL_MX_BIAS(dst, a, sa, b, sb, bias,
                  fixp::keep_acc().row_max(row), size_t{70});
}
}
```

四PE物理行块为32，实际有效行为32/32/6/0；PE2的A/SA/D/Row分别按 `(6,35)` / `(6,2)` / `(6,8)` / `(6,1)` 构造并准备，C与D有效形状相同。B和SB已发布，四PE均参加协作调用。Row的物理容量128B，SA为128B，D为1024B；PE3没有有效输出元素。

primary有效元素均为1，C/bias均为2。两侧scale第0组为 `0x7f`、第1组为 `0x80`，最后3个K元素使用第二组。普通三个函数的D及Row分别为35/37/37；三个MX函数的数学预期分别为44/46/46。相应操作页还给出groupM=20的16行块、4行尾块及零行PE例子。

### Packed MX 与 HiF4 的不同组长

<!-- audit-example: matrix_scale_formats -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace matrix_scale_formats {
using D = CubeAccumulatorM16<float, 16, 8>;
using PackedA = CubeTileM16<__fp4_e2m1x2, 16, 64, 16, 34>;
using HalfB = CubeTileN8<__half, 64, 8, 34, 8>;
using E8Scale = VecTileM32<__fp8_e8m0, 32, 4, 16, 2>;
using HiFA = CubeTileM16<__fp4_hif4x2, 16, 128, 16, 68>;
using HiFB = CubeTileN8<__fp4_hif4x2, 128, 8, 68, 8>;
using HiFScaleA = VecTileM32<uint32_t, 32, 2, 16, 2>;
using HiFScaleB = VecTileM32<uint32_t, 32, 2, 8, 2>;
void packed(D &dst, PackedA &a, E8Scale &sa, HalfB &b) {
  TMATMUL_MX(dst, a, sa, b, fixp::keep_acc());
}
void hif4(D &dst, HiFA &a, HiFScaleA &sa, HiFB &b, HiFScaleB &sb) {
  TMATMUL_MX(dst, a, sa, b, sb, fixp::keep_acc());
}
}
```

`packed` 的K=34，A的E2M1每个逻辑元素为1（4位编码 `0x2`），B全为1，SA两组都为E8M0的 `0x7f`。两组分别覆盖32和2个K元素，输出数学预期为34。A物理容量512B，B为1024B，SA为128B。

`hif4` 的K=68，primary每个逻辑元素均取数值1（4位编码 `0x4`）；每个U32 scale字为 `0x000000c0`：低8位E6M2表示1，两个指数增量位域均为0。两组覆盖64和4个K元素，输出数学预期为68。A/B物理容量分别1024B/512B，SA/SB各256B、有效形状分别16×2/8×2。HiF4示例适用Matrix-MX；GEMV-MX的类型范围按前文选择。

本节所有输入均已定义，输出独立。带 scale 示例按下文数值规则计算，容量覆盖物理存储，有效形状保留 K 尾组。

## 诊断与分片

K 不匹配、非法角色/存储组合、dtype 类冲突、缺失 scale、scale 形状错误、后处理与输出 dtype 不匹配必须拒绝。共享输入须已完成发布；完整 bundle 的 schema 检查在消费输入或发布输出前完成。浮点结果按每次调用的 K 累加顺序和舍入规则确定。

K 分片通过完整 C→D 累加链表达：前一调用的 D 作为下一调用的 C。每次调用独立遵守 Shared 发布和 scale 配对规则。见 [操作边界](StorageBoundaries.md)。

## Shared packed primary

Shared Matrix有任一4位primary时，K及该packed parent的物理列距均为偶数；TransA/TransB保持此条件。M、groupM和N按各自形状合同校验。此条件作用于Shared packed primary，Local packed A搭配非packed Shared B按原Local几何校验。依据[TMATMUL_ACC legality](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/matrix-and-matrix-vector/matrix-matrix/TMATMUL_ACC.asl)。

## 数值规则

逻辑 K 按索引递增累加，每项执行一次融合乘加，并舍入到声明的物理累加类型。普通浮点输入使用 FP32 累加，有符号和无符号整数分别使用 S32、U32。基础操作从零开始，ACC 从显式 C 开始；BIAS 在完整点积结束后按结果类型相加。

MX 先解码每侧的 scale 并缩放对应逻辑输入，再执行 FP32 融合乘加。E8M0 的 0xff 使对应乘积项及累加结果成为 canonical NaN。HiF4 使用前述 U32 scale 和 64 元素分组条款。点积完成后按 Options 执行逐元素后处理、最终 D 类型的辅助规约，再一起发布输出与状态。

浮点异常值、渐进下溢和编码规则见[数值参考](Numerics.md)。依据：[LinxISA 锁定文件](https://github.com/LinxISA/linx-isa/blob/7c658a8ce0ff89c1a7e0dd6ca47c9858aa062b27/isa/v0.59/pto-spec.lock.json)、[硬件数值规范的 matrix 与 arithmetic 条款](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/spec/hardware-conformance-profile.json)。
