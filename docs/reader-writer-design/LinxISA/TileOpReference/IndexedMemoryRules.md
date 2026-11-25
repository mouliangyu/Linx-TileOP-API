# 索引 GM 读写：公共规则

**算子声明：** [MGATHER](MGATHER.md)、[MGATHER_MASK](MGATHER_MASK.md)、[MSCATTER](MSCATTER.md)、[MSCATTER_MASK](MSCATTER_MASK.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。本章的索引是**字节位移**；Local [TGATHER/TSCATTER](IrregularRules.md) 的行索引不能直接复用。

## MGATHER / MSCATTER



非 packed 类型中，MGATHER 将 `src.base + offset[r,c]` 处的一个元素写入 dst[r,c]。MSCATTER 将 src[r,c] 写到 `dst.base + offset[r,c]`。packed 4-bit 类型每个索引访问一个字节，承载相邻两个 payload 元素，具体形状见下节。G 的行列步长不参与这个地址计算。MGATHER 的 dst 为 out、其余为 in；MSCATTER 的 GM dst 为内存写目标、src/offset 为 in。均返回 void。

## MGATHER_MASK / MSCATTER_MASK



mask 满足 IndexedMaskReadable：RowMajor 使用 Numeric U8；CUBE_M16/M32 支持 Numeric U8 或 PredicateCell。每个有效掩码字节为规范 0 或 1，PredicateCell 的比较 basis 独立于 payload dtype。1 执行访问；0 抑制该位置的地址生成与内存访问，gather 按 Pad 处理输出，scatter 保留内存原值。其他掩码字节值在效果前拒绝。

## 参数、形状和错误

| 参数 | 单位/约束 |
| --- | --- |
| G | [GlobalMemoryView](CommonTypes.md#globalmemoryview)；MGATHER 源可读，MSCATTER 目标可写；GM dtype 与 payload 匹配 |
| dst/src payload | Local 数值 Tile 与 GM 元素类型匹配，不做数值转换 |
| offset | S32/U32/S64/U64；有符号值可为负；每项为相对 GM base 的字节位移 |
| mask | Numeric U8 或 CUBE PredicateCell；和 index 有效形状相同；packed 4-bit 时一项控制一对 payload 元素 |
| range | 可选起始地址位移包络；定义见下节 |
| Pad | 编译期常量，默认 Null；本族 Null/Zero 写入已定义零位模式，Max/Min 按 dtype 填充 |

普通 gather/scatter 按位搬运全部已分配的数值 dtype，包括 packed 4-bit；每种 dtype 仍须满足其布局合法性，M16 排除 b64，N8 不属于本族布局。原子形式按 [各操作封闭集合](AtomicsRules.md) 校验。

payload、offset、mask 的布局类应相同（RowMajor、CUBE_M16 或 CUBE_M32），物理列数和容量分别满足各自 dtype 的布局约束，不要求相同。

| 数据形式 | payload 有效形状 | offset 有效形状 | mask 有效形状 |
| --- | --- | --- | --- |
| 非 packed | R×C | R×C | R×C |
| packed 4-bit | R×(2C) | R×C | R×C |

packed 4-bit 的 `offset[r,c]` 指向一个完整字节，按该 dtype 的低/高 nibble 顺序对应 payload 的 `[r,2c]` 和 `[r,2c+1]`。例如 payload 1×64 对应 index 和 mask 各 1×32。payload 有效列数必须为偶数；不能访问半对元素。mask=0 同时抑制整对元素的地址生成和访问，gather 对两项执行 Pad，scatter 不写这个字节。

每个实际地址须满足非 packed payload 元素自然对齐；packed 对按一个字节访问。地址空间必须可访问且地址运算不溢出。

同一次 scatter 的重复目标没有确定的最后写入顺序；需要原子更新时使用 [原子接口](AtomicsRules.md)。本请求先探测全部活动地址并保存输入，再提交 scatter 或发布 gather 结果；探测错误发生在本请求内存效果和结果发布之前。成功请求的 lane 可按架构允许的顺序与其他请求交错；其他 PE 已提交的效果保留。

## IndexedByteRange

```cpp
struct IndexedByteRange { int64_t min; int64_t max; };
```

LinxISA 0.59.1 已纳入可选范围操作数；本设计同时提供带 range 和不带 range 的重载。

`IndexedByteRange` 给出有符号 64 位的最小/最大**访问起点位移**，上下界均包含。若一次索引访问的宽度为 W 字节（packed 4-bit 对为 1 字节），涉及的完整字节包络为 `[base+min, base+max+W)`。例如访问三个 float，起点位移为 0、4、8，range 为 `{0,8}`。

包络两端须位于 64 位 GM 地址域，且 `base+min` 和 `base+max+W` 的数学计算不回绕；该保证由调用者提供。

range 向内存依赖分析提供访问包络；调用者负责分配内存并保证每项实际访问包含在声明内。min>max 是非法范围；当前 PE 在内存副作用前拒绝，其他 PE 不因此自动回滚。省略 range 使用无显式包络的重载，访问位置仍由各项 offset 决定。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Values = Tile<Location::Vec, float, 1, 32, BLayout::RowMajor>;
using Offsets = Tile<Location::Vec, int32_t, 1, 32, BLayout::RowMajor>;
using GM = global_tensor<float, RowMajor<1, 32>>;
using GMInput = global_tensor<const float, RowMajor<1, 32>>;
void indexed_copy(float *output, const float *input, Offsets &byte_offsets) {
  GMInput in(input);
  GM out(output);
  Values values;
  MGATHER(values, in, byte_offsets);
  MSCATTER(out, values, byte_offsets);
}
```

byte_offsets 由调用者初始化为 `4*i` 时，复制 32 个 float 到相同下标。源和目标 GM 区域不重叠；示例未编译执行。分片调用遵守下列 Reader / Writer 合同。

## Reader / Writer 分片合同

数值 Local 输入为 Readable，显式 mask 为 IndexedMaskReadable，每个 MGATHER Local 结果为 Writable。输入可以独立选择 Reader 片段，结果可以选择 Writer 的 first/middle/last/single 输出描述。MSCATTER 没有 Local 结果；GM 写目标不属于 Writable Tile 协议。

所有形状、布局和 dtype 检查作用于本次计算视图：普通 Tile 使用自身几何，片段使用 Part 几何。payload、索引及 mask（如有）遵守上表的有效形状关系和相同布局类要求；元素宽度、物理容量及各自 CELL 偏移可以不同。显式有效维度参数也作用于 Part，不作用于 Parent 总形状。

Reader 的 CELL 偏移只选择存放索引或数据的 Local 片段，不参与 GM 地址计算。索引元素仍是相对 base 的字节位移，不随片段位置自动重定位。Writer 的 CELL 偏移只决定返回值在 parent 中的存放位置，不影响 GM 地址。range 覆盖本次调用实际访问的 GM 起点位移。

一次调用消费一个输出阶段描述；不能为实现 Writer 阶段而重复执行内存访问。首次调用保存 parent，后续调用向同一 parent 写入各自的结果片段；finish 返回该 parent，不再发起 GM 访问。各阶段遵守 TileOP 的有序副作用合同。

对原子形式，每次调用独立完成其 GM 更新，Writer 仅组装返回的旧值。finish 不提交、合并或回滚 GM 更新；单 lane 原子性、重复地址顺序及故障边界保持各操作原有合同。GM 更新发生于各次原子调用。

固定依据：[布局/类型/packed 形状](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/indexed-layout.asl)、[mask descriptor 与规范字节](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/legality/predicate-carriers.asl)、[scatter 探测与提交](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gather-scatter.asl)、[gather 目标值构造](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gather-scatter-values.asl)。

MGATHER 与 MGATHER_MASK 在成功后将完整物理目标标为已定义。Null 与 Zero 均填入零位模式，包括 MASK 为0的位置；E8M0 的零位模式按该格式解释为 2^-127。依据 [TilePadValueForDataType](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/definedness/elements.asl) 与上述 gather 结果构造。
