# 存储、复制与预取：公共规则

**算子声明：** [GMOV](GMOV.md)、[TMOV](TMOV.md)、[TMOV_CUBE_TO_SHARED_ND](TMOV_CUBE_TO_SHARED_ND.md)、[TMOV_SHARED_ND_TO_CUBE](TMOV_SHARED_ND_TO_CUBE.md)、[TPREFETCH](TPREFETCH.md)、[TSTORE](TSTORE.md)、[TSTORE_PART](TSTORE_PART.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。GM→Tile 的全部 TLOAD 声明见 [TLOAD](TLOAD.md)。本章接口返回 void，传输保留 dtype，不执行算术转换。

## TSTORE / TSTORE_PART



src 是已定义 Local/已发布 Shared 输入；dst 是 GM 内存写目标。写入有效矩形，GM 地址与行距来自 global_tensor，写入元素数由有效矩形确定。CUBE 形式按逻辑元素转换到 GM ND 布局；不能把 CUBE 原始 CELL 排列当作普通连续矩阵。GM dtype、可访问范围与源有效矩形必须匹配；不承诺把 padding 写入 GM。TSTORE_PART 的 PEMask 是编译期参与 PE 选择，默认 15。

## TMOV



dst(out)、src(in) 独立推导，计算视图匹配，复制 payload 和 definedness。location、dtype、物理形状、有效形状、布局和容量一致。支持 unboxed RowMajor、CUBE_M16/M32；本 Local→Local 重载不接受 N8、ColumnMajor、boxed；Shared 方向另见下节。复制不把未定义 padding 变成可读数据。不要通过引用别名假设一定免分配。

## Local CUBE / Shared ND 转换



两种形式都要求 dtype 相同；Local 为 M16/M32，Shared 为 unboxed RowMajor。转换保持逻辑坐标及元素原始编码。N8、RCPE6M2 不支持。

| 方向 | 容量/形状 | 参与规则 |
| --- | --- | --- |
| CUBE→ND | 整块输出：源容量等于 Shared parent；Writer 输出：源容量等于 Part 容量。两者的目标列距均等于源精确物理列数 | 普通单次形式必须显式指定单 bit mask；组装形式也显式指定，无默认值 |
| ND→CUBE | 完整源物理行数为 16/32，源容量等于目标 | 默认 15；每个参与 PE 获得独立完整 Local 结果，不自动按 PE 切片 |

ND→CUBE 不支持 M16 b64；M32 b64 使用双 CELL 映射。Shared 源必须已发布。目标有效形状按源描述符及转换规则确定。输出 padding 写原始零，但仍不属于有效区域。该方向 mask=0 为严格 no-op。

Shared 转换源接受合法 Reader 描述，Shared 目标接受 Writer 描述；ND→CUBE 目标必须是完整 Local Tile，完整行子视图和多 PE 组装须遵守 [存储边界](StorageBoundaries.md)。统一入口见 [TMOV](TMOV.md)。

## GMOV

参数字段、运算和专用几何由 [GMOV 操作页](GMOV.md) 定义。

## TPREFETCH



为四个 PE 请求 GM 矩形预取，没有 Tile 输出，也不更新有效区元数据。新库接受可读 RowMajor GlobalMemoryView，包括 global_tensor 的动态视图及 subview；按视图绑定基址、物理列数和元素行距。物理列数须为非零二次幂且覆盖 valid_col，行距须覆盖所访问列。valid_col、valid_row 均为元素数量，无默认值，正值且不超过源形状。调用不替代 TLOAD 或同步；不能把预取完成当作数据已装入 Tile。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, float, 32, 32, BLayout::RowMajor>;
using G = global_tensor<float, RowMajor<32, 32>>;
using GInput = global_tensor<const float, RowMajor<32, 32>>;
void copy_to_gm(float *output, V &initialized) {
  G out(output);
  V copy;
  TMOV(copy, initialized);
  TSTORE(out, copy);
}
void prefetch(const float *input) {
  GInput in(input);
  TPREFETCH(in, 32, 16); // 前 16 行，每行 32 个 float
}
```

示例未编译执行。GM 存储的已完成写入在后续访问错误时保留。Shared 对象应维持函数内或 inline SSA 生命周期，不作为普通整数句柄跨非内联函数传递。
