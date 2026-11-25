# Tile 与标量运算：公共规则

**算子声明：** [TADDS](TADDS.md)、[TANDS](TANDS.md)、[TDIVS](TDIVS.md)、[TEXPANDS](TEXPANDS.md)、[TMAXS](TMAXS.md)、[TMINS](TMINS.md)、[TMULS](TMULS.md)、[TORS](TORS.md)、[TREMS](TREMS.md)、[TSELS](TSELS.md)、[TSHLS](TSHLS.md)、[TSHRS](TSHRS.md)、[TSUBS](TSUBS.md)、[TXORS](TXORS.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。标量 s 作用于每一个有效元素，不需要先创建同形状 Tile。默认值逐操作声明列出；TEXPANDS 的维度参数可省略。

## 算术与位运算合同



D/S 独立推导目标与源计算视图。dst 为 out，src 为 in，s 为 in，标量类型为 `element_type_t<S>`，无独立的“标量类型提升”模板参数。布局采用一致的 RowMajor 或已支持的 Local CUBE_M16/M32；输入有效区域必须已定义，目标有对应容量。

| 操作 | 每元素结果 | src=6，s=2 |
| --- | --- | --- |
| TADDS | src+s | 8 |
| TSUBS | src−s | 4 |
| TMULS | src×s | 12 |
| TDIVS | src/s | 3 |
| TREMS | src 除以 s 的余数 | 0 |
| TMAXS | max(src,s) | 6 |
| TMINS | min(src,s) | 2 |
| TANDS | src & s | 2 |
| TORS | src \| s | 6 |
| TXORS | src ^ s | 4 |
| TSHLS | src 左移 s 位 | 24 |
| TSHRS | src 右移 s 位 | 1（U32） |

算术操作按下表选择操作 dtype。

| 操作 | 操作 dtype |
| --- | --- |
| TADDS、TDIVS、TEXPANDS | FP64/32、TF32、HF32、FP16、BF16、E4M3、E5M2、S/U8/16/32/64 |
| TSUBS、TMAXS、TMINS | FP64/32/16、BF16、S/U8/16/32/64 |
| TMULS、TREMS | FP64/32/16、BF16、S/U16/32/64 |

AND/OR/XOR 使用整数集合。TSHLS/TSHRS 使用 S/U8、16、32、64 操作 dtype。元素位宽为 W 时，实际移位量取标量的无符号低 log2(W) 位；左移保留低 W 位，有符号右移补符号位，无符号右移补零。例如 U32 的移位量 33 等效于 1。整数加减乘按元素位宽取模；DIVS/REMS 的整数零除数在活动计算效果前拒绝。REMS 的非零有符号结果与除数同号；浮点边界及精确 profile 见 [逐元素执行合同](Numerics.md#逐元素执行合同)。

## TEXPANDS：用标量初始化



dst 为 out，s 为 in。把目标有效区域每个元素设为 s，不读取旧 dst。有效形状来自目标类型或对象；padding 不属于初始化保证。类型集合见上表的 TEXPANDS 行。

## TSELS：false 分支为标量

类型、载体位选择和谓词几何见 [TSELS](TSELS.md)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using F = Tile<Location::Vec, float, 32, 32>;
using U = Tile<Location::Vec, uint32_t, 32, 32>;
void affine(F &scaled, F &result, F &input) {
  TMULS(scaled, input, 2.0f);
  TADDS(result, scaled, 1.0f);
}
void initialize(U &result) { TEXPANDS(result, uint32_t{7}); }
void bits(U &result, U &input) { TANDS(result, input, uint32_t{3}); }
```

input 全为 3 时 affine 输出全为 7；initialize 将有效区域填成 7。片段未编译执行。普通源/目标同名按操作前源值计算，输入快照先于输出发布。

## Reader/Writer

算术/逻辑 src 是 Readable，dst 是 Writable，s 是普通标量。Part 的 dtype 必须与标量对应，不能使用 Parent dtype/容量掩盖不匹配。TEXPANDS 只有目标角色；其 Writer Part 必须提供有效形状。TSELS 的谓词接受 PredicateReadable，具体合同见 [Predicate](Predicate.md)。标量比较及 GPR mask 返回形式见 [比较与转换](CompareConvertRules.md)。

谓词载体使用 [PredicateTile](Predicate.md)，不以普通 U8 Tile 代替。

## 编码、发布与边界

标量通过 B.IOR.RegSrc0 传递一个元素的原始位编码，保留低元素位宽；浮点值按其编码传递。B.IOR 其余字段为零。库签名中的标量必填，值为零时可选择架构零寄存器。操作的有效维度来自 src，TEXPANDS 来自 dst；B.DIM 的 LB0/LB1/LB2 分别绑定有效列/有效行/物理列。

输出 dtype 等于操作 dtype，布局为一致的 Local RowMajor/M16/M32；M16 排除 b64，M32 的 b64 使用双 CELL。标量按计算 dtype 解释；源可使用合法的等宽非 packed reinterpret 输入。TEXPANDS 复制标量的低元素位宽，不转换数值；M16/M32 的有效行数分别至多16/32。

默认 Null padding 未定义，Zero/Max/Min 定义对应物理填充值。完整 Tile 的合法性和分配检查在发布前完成，payload、definedness、描述符和适用数值状态一起发布；预检失败无本次输出效果。Writer 描述使用同一计算语义，范围与最终发布遵守 [Writer](Writer.md)。
