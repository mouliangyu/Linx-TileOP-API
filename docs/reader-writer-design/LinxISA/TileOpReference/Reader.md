# TileReader

本页定义新接口的调用合同。完整生命周期和编译绑定说明见 [设计记录](../TileReaderWriterDesign.md)。

## 声明

```cpp
template <class Parent> class TileReader {
public:
  explicit TileReader(const Parent &parent);
  TileReader(Parent &&) = delete;
  template <class Part> auto read(size_t cell_offset) const;
  template <class Part> auto read(size_t cell_offset, size_t valid_rows,
                                  size_t valid_cols) const;
  template <class Part> auto fragments(size_t count) const;
};
```

## 输入输出角色

| 对象 | Readable 输入 | Writable 输出 |
| --- | --- | --- |
| 已定义普通 Tile | 是 | 是 |
| Reader.read 返回描述 | 是 | 否 |
| Writer.first/middle/last/single 返回描述 | 否 | 是 |
| Reader/Writer 本身 | 否 | 否 |

Reader 只借用已完成 parent；read 不复制数据，消费描述的计算绑定 B.SUBVIEW。可重读、重叠读取，借用不可超出 parent 生命周期。未完成 Writer 无法构造 Reader，也不能转换为输入 Tile。

Writer 的阶段及 Local/Shared 区别见 [Writer](Writer.md)，不作为 Reader 的状态机。

## 顺序迭代器

`fragments<Part>(count)` 从 CELL 0 开始。begin/end、解引用、前置 ++ 和同范围比较构成便利遍历接口；不承诺随机访问或全部标准 iterator concept。每次 ++ 推进 Part 的物理 CELL 数。该重载没有运行时片段维度参数，Part 的两轴有效维度须均非 DYNAMIC。

Reader count 可为 0，允许提前 break、continue、重复解引用和复制迭代位置。Reader 没有 first/last/finish 阶段，也不要求消费全部片段。

## 示例：重读片段

```cpp
using Parent = VecTileM32<float, 32, 8>;
using Part = VecTileM32<float, 32, 4>;
void read_twice(Part &dst, Parent &src) {
  TileReader<Parent> reader(src);
  TADD(dst, reader.read<Part>(0), reader.read<Part>(0));
}
```

src 已定义，dst 为独立输出。两次读取同一个起始片段合法；该片段全为 3 时，输出全为 6。Reader 不消耗或修改源。

## 动态有效形状

带 valid_rows/valid_cols 的重载以元素为单位提供本次 Part 有效形状，两轴均以显式值为准，即使 Part 模板对应轴已有静态有效维度。省略这两个参数的重载使用 Part 模板的有效维度，要求两轴均非 DYNAMIC；若任一轴为 DYNAMIC，须使用显式维度重载并传入两轴。这是省略参数的重载没有运行时 Part 对象可提供维度所需的接口规则，不限制动态片段本身。不从 Parent 有效形状或 CELL 偏移猜测 Part 形状。显式维度的合法性由 subview 和消费操作检查，不额外要求与模板中的有效维度逐轴相等。物理容量、布局和迭代步长仍由 Part 类型决定。

## 单片容量

Part 的容量编码、范围和 Parent 边界统一见 [分片几何：单片容量](FragmentGeometry.md#单片容量)。

## 输入类型解释

对选出的 Local 数值片段调用 [reinterpret_tile](CommonTypes.md#reinterpret_tile)，可保留 backing 几何与借用关系并选择消费操作的元素解释类型。完整声明、约束和示例见该接口。
