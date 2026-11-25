# 比较与类型转换：公共规则

**算子声明：** [TCMP](TCMP.md)、[TCMPS](TCMPS.md)、[TCVT](TCVT.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。比较产生谓词 Tile 或 GPR 掩码，转换产生数值 Tile。

## TCMP

TCMP 将两个数值计算视图逐元素比较，产生谓词 Tile。参数、支持类型、形状关系与比较行为由 [TCMP 操作页](TCMP.md) 定义；谓词类型、basis 和物理存储规则见 [Predicate](Predicate.md)。

## TCMPS

TCMPS 将数值输入与标量逐元素比较，提供谓词 Tile 输出和 GPR 返回值两种形式。重载、类型与形状范围由 [TCMPS 操作页](TCMPS.md) 定义；返回位号和 High 列范围见 [GPR 返回值编码](TCMPS.md#gpr-返回值编码)。

## 比较示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using F = Tile<Location::Vec, float, 32, 32>;
using P = PredicateTile<F>;
void compare(P &positive, P &less, F &x, F &y) {
  TCMPS<CmpMode::GT>(positive, x, 0.0f);
  TCMP<CmpMode::LT>(less, x, y);
}
```

x 全为 1、y 全为 2 时两个输出的有效谓词均为 true，可供 [TSEL](TSEL.md) 使用。示例未编译执行。不要用 TSTORE 数值数组的方式假定 Predicate 的位存储布局。

## TCVT

参数字段、运算和专用几何由 [TCVT 操作页](TCVT.md) 定义。

## 分片及错误

比较的 dst 需 Predicate 输出合同；Reader 的数值片段与 Writer 的谓词片段不能仅凭元素宽度匹配。TCVT 的 source/destination Part 需要按各自 dtype 和物理形状独立推导容量及 SizeCode；推导结果可以相同，例如相同几何的 FP32→S32。Writer 不作为输入，Reader 不作为输出。静态 Mode/类型/形状检查可拒绝部分错误，运行时数据异常不保证统一 C++ exception；输出不得与尚需读取的源任意 alias。

谓词载体使用 [PredicateTile](Predicate.md)，不以普通 U8 Tile 代替。
