# 公共类型与单位

公开入口 `<common/pto_tileop.hpp>`，命名空间 `pto`。Tile 是编译器管理的 Tile 值及几何描述。本手册不为 `tile[i]`、取 payload 地址或跨普通函数 ABI 传递硬件句柄定义语义。

## Tile

```cpp
template <Location Loc, typename Element, int Rows, int Cols,
          BLayout Layout = BLayout::RowMajor,
          int ValidRows = Rows, int ValidCols = Cols,
          SLayout SubLayout = SLayout::NoneBox,
          int FractalSize = 512, PadValue Pad = PadValue::Null,
          CompactMode Compact = CompactMode::Null,
          bool ElementProfile = false>
struct Tile;
```

| 参数 | 含义 |
| --- | --- |
| Loc | Vec、Left、Right、Acc、Bias 等操作数角色 |
| Element | backing dtype；packed 低精度类型不能按 C++ sizeof 推导逻辑元素数 |
| Rows/Cols | 编译期物理行列，元素单位 |
| ValidRows/ValidCols | 有效行列；默认覆盖物理矩形，DYNAMIC 表示运行时维度 |
| Layout | RowMajor、ColMajor 或 CubeM16/CubeM32/CubeN8，操作逐项限制 |
| SubLayout/FractalSize | boxed 存储配置；不能凭默认 Tile 能构造就推定算子支持 boxed |
| Pad/Compact/ElementProfile | 存储 profile 参数，由类型定义固定 |

静态 Tile 默认构造只建立载体，不能视为已初始化。动态形状构造的 `(valid_rows, valid_cols)` 按行、列顺序；许多算子的维度实参反而是列、行，必须按声明使用。`GetValidRow()` / `GetValidCol()` 查询库侧保存的有效维度：普通静态 Tile 取模板值，动态轴取对象中保存的运行时值。getter 不读取硬件 Tile 描述符，也不因硬件产生尾片而自动改变返回值；操作若更新库侧元数据，须在该操作页明确规定。payload 的已定义范围由 producer 的执行合同确定。修改有效区不改变物理布局或容量。

## reinterpret_tile

`reinterpret_tile` 创建借用输入视图，消费操作按 NewDType 解释原始元素位。它保留 backing dtype、物理字节、布局、有效维度及 parent 身份，返回值满足 Readable。该接口本身只构造描述，源 payload 保持原值。

```cpp
template <typename NewDType, Readable S>
auto reinterpret_tile(S &&src);
```

| 参数 | 含义 | 默认值 / 推导 |
| --- | --- | --- |
| NewDType | 消费操作使用的元素类型 | 显式指定 |
| S | Local 数值输入计算视图 | 由 src 推导 |
| src | 已定义普通 Local Tile 左值，或 Local Reader 片段描述 | 必填 |

NewDType 须有合法类型编码，与 backing dtype 等位宽，并满足布局及消费操作的 carrier 兼容条件。消费操作分别检查操作类型、backing 类型和源内容的编码合法性；例如 TEXPDIF 使用非 packed 的等宽 carrier，并按其类型配对表选择输出。此视图的用途是输入解释，输出仍由消费操作的 Writable 参数指定。

普通 Tile 通过引用借用；Reader 片段通过保存其 parent 引用、CELL 偏移及本次几何借用。因而 `reinterpret_tile<float>(reader.read<Part>(offset))` 可以直接作为输入；临时片段描述的结束不影响其保存的 parent 引用。两种形式的借用均须在 parent 有效生命周期内使用。普通 Tile 临时值、Shared、Predicate 及 Writer 输出描述均不满足此接口的输入约束。

先由 Reader 选择 backing 类型的 Part，再对该片段调用 reinterpret_tile。视图保留原 CELL 偏移、容量和显式有效维度；消费时将这些信息绑定到同一个源操作数。

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Bits = VecTileM32<uint32_t, 32, 8>;
using BitPart = VecTileM32<uint32_t, 32, 4>;
using FloatPart = VecTileM32<float, 32, 4>;
void exp_difference(FloatPart &dst, Bits &a, Bits &b) {
  TileReader<Bits> ar(a), br(b);
  TEXPDIF(dst,
          reinterpret_tile<float>(ar.read<BitPart>(0)),
          reinterpret_tile<float>(br.read<BitPart>(0)));
}
```

输入所选片段的每个 U32 元素均已初始化为 FP32 的合法编码。若 a、b 对应元素均为 `0x40000000`（FP32 的 2），结果元素为 FP32 的 1。dst 为独立输出。

相关：[Reader](Reader.md)、[操作数角色](OperandRoles.md)、[TEXPDIF 类型配对](ElementwiseRules.md#texpdif差值的指数)。

## 常用 CUBE 别名

下列别名模板参数均为 `<Element, Rows, Cols, ValidRows=Rows, ValidCols=Cols>`。

| 别名 | 角色 | 布局 |
| --- | --- | --- |
| VecTileM16 / VecTileM32 | Vec | CubeM16 / CubeM32 |
| CubeTileM16 / CubeTileM32 | Left | CubeM16 / CubeM32 |
| CubeTileN8 | Right | CubeN8 |
| CubeAccumulatorM16 / CubeAccumulatorM32 | Acc | CubeM16 / CubeM32 |

`CubeBias<Element, Cols, ValidCols=Cols>` 固定有效行数为 1、角色 Bias、布局 N8；物理行数由位宽决定，为 b64:2、b32:4、b16:8、b8:16、b4:32。

```cpp
using Input = VecTileM32<float, 32, 8>;
using Left = CubeTileM16<float, 16, 16>;
using Right = CubeTileN8<float, 16, 8>;
using Result = CubeAccumulatorM16<float, 16, 8>;
```

这些类型分别表达向量运算、矩阵左输入、矩阵右输入、累加结果，不能只因 float 相同就互换角色。

## Shared 与 GM

`SharedTile<LocalTile>` 使用对应 Tile 的 dtype/几何描述 Shared 存储；Shared 数据由相应 producer 写入。必须由合法 producer 发布后才能读。SharedMatrixLeft/SharedMatrixRight 表达矩阵角色，Shared primary 物理形状与 Local CUBE 不同，见矩阵章节。

`global_tensor<Element, RowMajor<Rows,Cols>>` 用 GM 指针建立外部矩阵视图，不分配内存。TLOAD/TSTORE 使用它的形状和步长；索引 GM 操作只用基址加字节位移。const 输入指针不能被用作可写 GM 输出。

```cpp
using GM = global_tensor<float, RowMajor<16, 8>>;
using GMInput = global_tensor<const float, RowMajor<16, 8>>;
// GMInput input(input_pointer); // 128 个 float 的外部可读区域
// GM output(output_pointer); // 128 个 float 的外部可写区域
```

### SharedTile 构造与维度查询

```cpp
template <class Shape>
class SharedTile {
public:
  SharedTile();
  explicit SharedTile(const Shape &shape);
  int GetValidRow() const;
  int GetValidCol() const;
};
```

默认构造使用Shape的静态有效维度；DYNAMIC轴初始为0，生产前须提供有效形状。动态形状可通过 `SharedTile<Shape>(shape)` 从已经设置维度的Shape对象取得；该构造只复制几何描述，payload由producer写入。GetValidRow/GetValidCol查询库侧保存的有效维度，生产操作的元数据更新按各页约定执行。Shared存储容量及RowMajor布局与包装Shape一同校验，嵌套SharedTile不合法。

### Shared 矩阵形状别名

```cpp
template <typename Element, int Rows, int Cols,
          int ValidRows = Rows, int ValidCols = Cols>
using SharedMatrixLeft =
    Tile<Location::Left, Element, Rows, Cols, BLayout::RowMajor,
         ValidRows, ValidCols>;
template <typename Element, int Rows, int Cols,
          int ValidRows = Rows, int ValidCols = Cols>
using SharedMatrixRight =
    Tile<Location::Right, Element, Rows, Cols, BLayout::RowMajor,
         ValidRows, ValidCols>;
```

这些别名定义带Left/Right角色的RowMajor形状；Shared存储对象写为 `SharedTile<SharedMatrixLeft<...>>` 或 `SharedTile<SharedMatrixRight<...>>`。Rows/Cols描述存储轴。A的未转置有效形状为groupM×K；B的未转置有效形状为N×K。转置时分别按K×groupM和K×N准备存储。动态有效维度沿用Tile的DYNAMIC和构造规则。

```cpp
using AShape = SharedMatrixLeft<__half, 32, 16, 20, 16>;
using BShape = SharedMatrixRight<__half, 8, 16>;
using AShared = SharedTile<AShape>;
using BShared = SharedTile<BShape>;
```

A物理1024B、有效20×16，B物理256B、有效8×16；发布后参与groupM=20、K=16、N=8的协作矩阵计算。默认构造建立目标描述；payload由合法producer发布后消费。scale使用独立SharedTile并按[MX scale](MatrixRules.md#mx-scale)准备M/N×groups几何。此别名定义对应固定PTO-C `include/common/pto_tile.hpp`，新库保留其形状与角色含义。

## 单位、padding 与掩码

| 项目 | 单位/意义 |
| --- | --- |
| 有效行列、groupM、GroupN | 元素行数/列数 |
| Reader/Writer cell_offset | 128 B CELL，字节偏移为128×cell_offset |
| fragments(count) | 片段数量，每步推进 Part 的物理 CELL 数 |
| GM index / IndexedByteRange | 字节位移；range 两端包含访问起点 |
| TGATHER/TSCATTER index | 行号，保留当前列 |
| PEMask | PE 参与集合；具体合法集合按算子定义 |
| MGATHER_MASK 的 mask | Numeric U8 或 CUBE PredicateCell 的逐元素 0/1 |
| TCMP/TCMPS Tile 结果 | RowMajor：packed predicate；CUBE：PredicateCell。表示与分片见 [Predicate](Predicate.md) |

Local单PE完整Tile、Reader/Writer的Part及Local Writer parent容量均为128 B..64 KiB（SizeCode 1..10）。Shared完整对象及Part为128 B..256 KiB（SizeCode 1..12）；均按二次幂编码，详见 [分片几何](FragmentGeometry.md#单片容量)。有效形状不决定分配容量；CUBE 的物理映射可能使容量大于有效元素字节数。

对于[TCVT允许的RowMajor非二次幂列数](TCVT.md#合法组合与限制)，完整Tile的库容量选择为：每行按 `ceil(Cols × 元素位宽 / 8)` 字节存储，乘以Rows后向上取到至少128B的最小合法二次幂容量。Rows/Cols保留模板物理形状，容量空余字节不增加物理行数。这是库的容量选择规则，依据为该ISA profile允许存储量小于TSize；其他操作及Reader/Writer仍按各自合同检查。

TmaPadValue 的枚举为 Zero=0、Max=1、Min=2、Null=3。具体操作对 Null 和非有效区的 definedness 可以不同；索引 gather 及原子输出的 Null 写已定义零位模式，不应推广到所有普通 load。输入 padding 除非该操作明确允许，否则不可消费。

## Reader/Writer

操作数角色与接口签名见 [Tile / Readable / Writable](OperandRoles.md)。普通 Tile、只读片段和只写片段不能由一个同类型 `is_tile_data_v` 声明混同表达。

完整签名、状态与迭代器见 [Reader/Writer 参考](Reader.md)。Reader/Writer 与普通 Tile 的可用角色由各算子定义；不提供旧 assemble range 或 `_ASS` 兼容接口。

## GlobalMemoryView

`GlobalMemoryView` 是 GM 内存视图的模板约束，`global_tensor<Element, Layout>` 属于该协议。视图提供 GM 基址、元素类型和布局信息，并保留底层元素的 const 属性及访问属性。它描述已有内存，不分配 Tile 或 GM 存储。

| 项目 | 合同 |
| --- | --- |
| 基址 | 指向操作访问的 GM 存储；调用期间保持有效 |
| 元素类型 | 决定访问宽度和数值类型；与 Local payload 的 dtype 匹配 |
| 布局 | 供使用形状/步长寻址的操作解释；MGATHER/MSCATTER 仅使用基址和逐元素字节位移 |
| 读权限 | MGATHER 的 GM 源必须可读 |
| 写权限 | MSCATTER 的 GM 目标必须可写；底层 const 元素视图不能用作目标 |

`GlobalMemoryView` 与 Local Tile 的 `Readable` / `Writable` 是不同协议。GM 视图不接受 Reader 片段或 Writer 输出描述，也不参与 Writer 的组装生命周期。

`const G &` 限制的是视图描述对象的修改，不代表所指 GM 内存只读；`G &` 也不自动保证底层内存可写。接口须检查元素类型和访问属性能静态判定的权限；实际映射的访问权限、地址有效性及对齐由调用者保证，违反架构访问规则可能触发 fault。

使用裸 `uint64_t base` 的原子接口没有 G 模板参数，调用者必须保证对应 GM 地址可读写；不能从整数地址的 C++ 类型推导权限。

## 计算视图类型查询

`element_type_t<O>` 提取操作数 O 的计算元素类型，查询前移除 C++ 引用及顶层 cv 限定。普通 Tile 取其 DType；Reader 片段和 Writer 输出描述取 Part 的 DType，不取 Parent 的类型。该查询只决定标量参数类型，不意味着可以读取 Writer 的数据。

Readable/Writable 约束解决角色合法性；算子仍须独立检查存储位置、布局、有效形状、容量和 dtype 配对。各页保留的 `is_tile_data_v` / `is_local_tile_v` 表示完整 Local Tile 类型约束，`is_shared_tile_v` 表示 SharedTile 类型约束，二者本身均不包含分片描述。`is_local_or_shared_left/right` 进一步限定矩阵左/右输入角色；几何条件见 [矩阵规则](MatrixRules.md)。

## 有效维度与输出元数据

具有 `UserValidCol = 0, UserValidRow = 0` 的逐元素接口按每一轴独立选择有效维度：非零参数为本次覆写，零参数取第一数值输入计算视图的有效维度。TAND/TOR/TXOR 的双谓词重载取 src0 的 U8 存储视图，具体重载选择表见对应操作页。普通 Tile 的默认维度按上述库侧元数据取得；Reader 片段取本次 Part 描述中的有效维度，显式传入 read 的维度优先于 Part 模板默认值。例如 Part 模板有效行数为 16 而 read 显式传入 4 行时，消费者默认使用 4 行。Writer 描述保存的 Part 有效维度供按目标选择区域的操作使用；按输入选择区域的操作使用上述来源，绑定方式见 [Writer 的维度与范围绑定](Writer.md#维度与范围绑定)。不能把 DYNAMIC 的 -1 转为无符号维度。本次计算的两轴均须为正，不超过各计算视图的物理行列；所有输入须具有本次计算所需的有效元素，输出物理容量须容纳结果。

输出的实际有效形状由各操作的语义及本次维度绑定决定。静态类型和动态类型均可承载尾片，输出物理容量须容纳本次结果。硬件结果描述符按操作语义更新；除操作页明确规定库侧元数据更新外，输出对象的库侧维度保持原值，getter 不自动读回硬件形状。后续操作须绑定实际合法的有效区域，可使用操作的显式维度参数或 Reader 的显式 Part 维度；不得仅凭 getter 返回值推定硬件结果的有效区域。Writer 的 Parent 覆盖与 Part 绑定遵守组装合同；归约、转换和协作分配的结果形状分别按对应操作解释。

这些规则不重定义原子接口中没有默认值的 validCol，或矩阵 groupM 等专用参数。

## GM 视图构造与子区域

新接口将元素 const 属性保留在类型中：可读输入使用 `global_tensor<const float, ...>`，可写目标使用 `global_tensor<float, ...>`，禁止构造时去掉指针 const。下面给出 RowMajor 视图的构造和子区域接口；所有行列、起点与 stride 均为逻辑元素单位。

```cpp
template <typename Element, typename Layout>
class global_tensor {
public:
  using DType = Element;
  explicit global_tensor(Element *base); // 静态形状及静态布局步长
  global_tensor(Element *base, size_t rows, size_t cols,
                size_t row_stride_elements); // 显式运行时形状和行距
  auto subview(size_t row, size_t col, size_t rows, size_t cols) const
      -> global_tensor<Element, RowMajor<DYNAMIC, DYNAMIC>>;
};
```

运行时构造的 rows/cols 必须与 Layout 的非 DYNAMIC 维度相等；行距不得小于 cols，视图跨度须有底层存储覆盖。subview 的矩形必须在父视图内，保留行距和元素 const 属性，只移动基址并改变逻辑形状，不分配或复制数据。父视图描述可销毁，底层存储仍须保持有效。GM subview 是内存视图操作，与 TileReader 的 CELL 分片不同。

普通非 packed 类型的子视图基址为 `base + row * stride + col`。packed 类型的起点必须落在可表示的完整存储单元边界；不允许通过截断字节地址静默舍弃半元素偏移。

```cpp
using In = global_tensor<const float, RowMajor<DYNAMIC, DYNAMIC>>;
using Out = global_tensor<float, RowMajor<DYNAMIC, DYNAMIC>>;
In input(in_ptr, 64, 128, 160);   // in_ptr: const float*
Out output(out_ptr, 32, 32, 32);  // out_ptr: float*
auto window = input.subview(16, 32, 32, 32); // 保留 160 元素行距
// TLOAD(tile, window); TSTORE(output, tile);
```

谓词的公开类型、basis 和分片协议见 [PredicateTile](Predicate.md)。Shared 与矩阵是否接收分片见 [操作边界](StorageBoundaries.md)。

TEXPANDS 没有输入，零有效维度参数取已提供的目标/Part 有效形状；动态目标必须先给出有效形状。带 UserPhysicalCol 的操作对物理列覆写单独校验，不能用改变物理列隐式修改输入数据排列。

## Shared 操作数协议

SharedReadable 接受已发布 SharedTile 或其 Reader 描述；SharedWritable 接受完整 SharedTile 目标或其 Writer 输出描述。二者与 Local 数值 Readable/Writable 分开，禁止未完成 generation 出现在输入上。计算类型查询按 Part 进行，PE 参与、行距和发布条件见 [Shared 存储合同](StorageBoundaries.md)。

`SharedAssemblyOutput` 仅接受 Shared Writer 的阶段输出描述，是 SharedWritable 的子集，不接受完整 SharedTile 或 Writer 对象。[TIMG2COL](TIMG2COL.md) 用它约束固定四 PE 协作发布；具体阶段与偏移限制由该操作定义。

GM 与 Tile 匹配元素类型时忽略 GM 元素类型的顶层 const/volatile；权限单独检查。const GM 可作为加载源，不能作为存储或原子更新目标。

## 物理列覆写

具有 UserPhysicalCol 参数的接口：0 保留当前计算视图的物理列描述；非零值以元素为单位，须覆盖本次有效列且不超过类型 Cols，并满足布局及容量规则。它改变本次操作的寻址几何，不执行裁剪或布局转换。Writer 输出以 Part 校验，不以 Parent 总列数校验。
