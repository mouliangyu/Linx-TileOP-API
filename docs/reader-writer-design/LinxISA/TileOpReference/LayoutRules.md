# CUBE 字节与 word 重排：公共规则

**算子声明：** [TGPR2T](TGPR2T.md)、[TPACK](TPACK.md)、[TPERMUTE](TPERMUTE.md)、[TSHUF](TSHUF.md)、[TUNPACK](TUNPACK.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。以下操作处理原始位，不执行数值转换。输出为新 Local Tile，不得与输入 alias；这些接口的普通参数均无默认值。

## TPERMUTE

参数字段、运算和专用几何由 [TPERMUTE 操作页](TPERMUTE.md) 定义。

## TSHUF

逐 word 行选择的控制字段、计算语义、类型和几何要求统一见 [TSHUF](TSHUF.md)。本页的 Local 存储及独立输出规则同样适用。

## TPACK

参数字段、运算和专用几何由 [TPACK 操作页](TPACK.md) 定义。

## TUNPACK

参数字段、运算和专用几何由 [TUNPACK 操作页](TUNPACK.md) 定义。

## TGPR2T



四个有序 GPR carrier 重编码到 Local Numeric U8。固定输出几何、逐位映射及非零示例见 [TGPR2T](TGPR2T.md#操作语义)。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Words = VecTileM16<uint32_t, 16, 32>;
using ByteIndices = VecTileM16<uint8_t, 16, 128>;
using PlaneBytes = VecTileM16<uint8_t, 16, 8>;
void byte_ops(Words &packed, Words &field, Words &permuted,
              Words &a, Words &b, ByteIndices &indices) {
  TPACK(packed, a, b, uint64_t{0x0202});
  TUNPACK(field, a, uint64_t{0x0201});
  TPERMUTE(permuted, a, b, indices);
}
void swap_rows(Words &dst, Words &src, Words &controls) {
  TSHUF(dst, src, controls, uint64_t{0x0302});
}
void zero_planes(PlaneBytes &dst) { TGPR2T(dst, 0, 0, 0, 0); }
```

a word=0x44332211、b word=0x88776655 时 packed=0x66552211，field=0x3322。swap_rows 的 controls 全为 1 时，BFLY 在宽度16的段内互换相邻行。zero_planes 输出全零位。示例未编译执行。

## 分片与限制

TPACK 的 source Part 必须保留 raw-word/CELL 对应关系，输出 Part 的 dtype 不决定字段宽度。TPERMUTE/TSHUF 的局部表和行 segment 不因 Reader offset 自动变成全 parent 坐标。TGPR2T 的固定输出几何也不能任意裁片。Local 输入和输出支持 Reader/Writer；上述 shape/control 条件在各自 Part 上检查，详见 [分片几何](FragmentGeometry.md)。
