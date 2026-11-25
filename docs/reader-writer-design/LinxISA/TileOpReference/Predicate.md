# Predicate 类型与分片

比较的 Tile 结果使用独立 Predicate 类型，不用普通 U8 Tile 的类型伪装谓词。GPR 结果仍为 uint64_t，不属于此类型。

```cpp
template <class NumericShape> struct PredicateTile;
```

NumericShape 指定被比较的数值 dtype（basis）、物理/有效逻辑形状和布局。PredicateTile 保留这组逻辑属性；谓词物理存储由谓词布局计算，不按 NumericShape 的数值字节宽度复制容量。CUBE_M16/M32 使用 U8 PredicateCell 及其 CELL 容量，64 位数值 basis 仅允许 M32。RowMajor 使用对应的架构谓词布局，调用者不能据 sizeof 或普通数值 Tile 的容量计算谓词寻址。

Predicate 的每个有效逻辑位置是一个布尔条件。TCMP/TCMPS 产生内容和 basis 元数据；默认构造不初始化内容。不能通过 TLOAD 普通 0/1 数组建立 Predicate 类型的内容。普通算术、数值 TSTORE 和 element_type_t 标量接口不接受 Predicate；MGATHER_MASK/MSCATTER_MASK 通过 IndexedMaskReadable 接受 CUBE PredicateCell；RowMajor 分支使用 Numeric U8。

`PredicateReadable` 接受已定义 PredicateTile 或其 Reader 片段；`PredicateWritable` 接受 PredicateTile 目标或其 Writer 输出描述。二者使用独立的谓词操作数协议。Predicate Reader/Writer 的 Parent/Part 都必须为 PredicateTile，basis 和布局一致。CELL 偏移单位仍为 128 B，但按谓词自身的物理容量取片段；禁止复用数值源的 CELL 偏移而不检查逻辑对应。

比较要求源与谓词输出 Part 的逻辑形状、布局及 basis 匹配；选择仅要求谓词与 payload 的有效形状和布局匹配，比较 basis 不限制 payload 类型或元素位宽。Writer 的所有阶段保留同一 basis，finish 才交出可读 PredicateTile。谓词片段的完整 CELL 几何由 PredicateTile<NumericPart> 推导，不允许截断或仅修改 ValidCol 冒充另一种 packing。

```cpp
using F = VecTileM32<float, 32, 8>;
using P = PredicateTile<F>;
// x、y 已定义；p 是新谓词结果。
P p;
TCMP<CmpMode::LT>(p, x, y);
TSEL(x, p, y, x); // 显式 false 源为旧 x，true 选择 y
```

本页定义接口类型及语义，类型的物理编码由编译器按 ISA 谓词规则生成；访问通过本页规定的谓词操作进行。

RowMajor 比较结果是 packed predicate，CUBE 比较结果是 PredicateCell；二者不能互换。GPR 掩码的完整列覆盖及双 word 形式见 [TSEL](TSEL.md#gpr-掩码)。本库保留 PredicateTile<NumericShape> 类型协议封装这些存储差异。

## 谓词位运算

[TAND](TAND.md#predicatecell-重载)、[TOR](TOR.md#predicatecell-重载)、[TXOR](TXOR.md#predicatecell-重载) 支持 CUBE PredicateCell。双谓词产生 U8-basis PredicateTile；与 Numeric U8 混合产生 Numeric U8。这些专用重载不把 Predicate 纳入通用数值 Readable/Writable，也不向 TNOT 或其他算术操作自动推广。

## 编码依据

RowMajor的低位优先packed bit与CUBE的规范U8字节由固定 [comparison.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/execution/comparison.asl) 和 [predicate-carriers.asl](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl) 定义。比较输出Zero/Min padding为0、Max为1、Null未定义。比较Mode为EQ=0、NE=1、LT=2、GT=3、LE=4、GE=5。
