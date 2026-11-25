# GM 原子更新与归约：公共规则

**算子声明：** [MGATHER_ADD](MGATHER_ADD.md)、[MGATHER_AND](MGATHER_AND.md)、[MGATHER_DEC](MGATHER_DEC.md)、[MGATHER_EXCH](MGATHER_EXCH.md)、[MGATHER_INC](MGATHER_INC.md)、[MGATHER_MAX](MGATHER_MAX.md)、[MGATHER_MIN](MGATHER_MIN.md)、[MGATHER_OR](MGATHER_OR.md)、[MGATHER_XOR](MGATHER_XOR.md)、[MSCATTER_ADD](MSCATTER_ADD.md)、[MSCATTER_AND](MSCATTER_AND.md)、[MSCATTER_DEC](MSCATTER_DEC.md)、[MSCATTER_INC](MSCATTER_INC.md)、[MSCATTER_MAX](MSCATTER_MAX.md)、[MSCATTER_MIN](MSCATTER_MIN.md)、[MSCATTER_OR](MSCATTER_OR.md)、[MSCATTER_POPC](MSCATTER_POPC.md)、[MSCATTER_XOR](MSCATTER_XOR.md)。

头文件 `<common/pto_tileop.hpp>`，命名空间 `pto`。每个有效 lane 对 `base + index[r,c]` 执行一次原子更新。MGATHER 族把观察到的旧值写入 Local 输出；MSCATTER 族仅更新 GM。二者均返回 void，不能将 MSCATTER 当作有旧值输出的接口。比较交换单独见 [MGATHER_CAS](MGATHER_CAS.md)。

## 公共参数合同

| 参数 | 方向/单位 | 要求 |
| --- | --- | --- |
| old | out | MGATHER 独立 Local 结果，dtype 与 value 相同 |
| base | in，字节地址 | uint64_t，当前 PE 的 GM 基址 |
| index | in，字节位移 | Local S/U32 或 S/U64，不自动乘元素宽度 |
| value | in | 每 lane 的更新值；INC/DEC 中为上限 |
| validCol | in，元素数 | 无默认值；静态维度来自类型，动态维度才使用实参 |
| validRow | in，元素数 | 默认 1；静态维度仍来自类型 |
| range | in，闭区间起点包络 | 可选，位于 validCol 后、validRow 前；见 [范围合同](IndexedMemoryRules.md#indexedbyterange) |

所有 Tile 为 Local，布局类一致，有效形状一致。每个访问满足 payload 自然对齐和读写权限；输入必须已定义。使用独立 old 输出，不依赖输入/输出 alias。各操作的完整声明见页首链接。

## MGATHER_EXCH

payload dtype：U32/U64。原子更新规则：`new = value`。



## MGATHER_MAX / MSCATTER_MAX

payload dtype：S32/S64/U32/U64。原子更新规则：`new = max(old,value)`。



## MGATHER_MIN / MSCATTER_MIN

payload dtype：S32/S64/U32/U64。原子更新规则：`new = min(old,value)`。



## MGATHER_ADD / MSCATTER_ADD

payload dtype：FP16/BF16/FP32/FP64/S32/U32/U64。原子更新规则：`new = old + value`。



## MGATHER_INC / MSCATTER_INC

payload dtype：U32。原子更新规则：`new = old >= limit ? 0 : old+1`。



## MGATHER_DEC / MSCATTER_DEC

payload dtype：U32。原子更新规则：`new = (old == 0 || old > limit) ? limit : old-1`。



## MGATHER_AND / MSCATTER_AND

payload dtype：U32/U64。原子更新规则：`new = old & value`。



## MGATHER_OR / MSCATTER_OR

payload dtype：U32/U64。原子更新规则：`new = old | value`。



## MGATHER_XOR / MSCATTER_XOR

payload dtype：U32/U64。原子更新规则：`new = old ^ value`。



## MSCATTER_POPC



目标固定为 U32，每个 lane 对其地址贡献 +1；没有 value 参数，也没有旧值输出。重复地址会贡献多次。

## 原子性、顺序与故障

重复地址的 lane 全部执行，以未指定顺序逐个原子更新。old 各项不构成同一时刻的 GM 快照。原子性属于单 lane，各 lane 分别提交更新。没有 memory_order 参数，不能从 C++ memory clobber 推断系统级 C++ 原子同步。

ISA 在提交前探测所有 active lane 的地址/读写权限并保存输入；本请求的探测错误发生在首个原子事件前，不发布旧值。已经提交的其他 PE 请求不回滚。非法类型/部分形状有编译期检查；错误地址可能触发架构 fault。

## 示例：累加并取旧值

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using U = Tile<Location::Vec, uint32_t, 1, 32, BLayout::RowMajor>;
void add_counters(uint32_t *counters, U &offset, U &increment, U &previous) {
  MGATHER_ADD(previous, reinterpret_cast<uint64_t>(counters),
              offset, increment, 32, IndexedByteRange{0,124});
}
```

offset 已初始化为 `4*i`，increment 全为 1，GM 原值全为 7 时，previous 全为 7，GM 更新为 8。若 offset 全为 0，则同一计数器增加 32，各 lane 获得不同旧值，不能假设按下标递增分配。示例未编译执行。

## Reader / Writer

所有 Local 输入为 Readable；MGATHER 的旧值结果为 Writable，支持 Writer 组装。MSCATTER 没有 Local 输出。遵守 [索引操作分片合同](IndexedMemoryRules.md#reader--writer-分片合同)，包括独立 Part 几何、字节索引、GM 更新与 finish 的关系。

固定依据：[GMAtomicOperationDataTypeLegal、GMReductionOperationDataTypeLegal、GMIncValue、GMDecValue](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red.asl)、[旧值/输入类型和独立几何](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red-values.asl)。整数更新按 payload 位宽取模；浮点 ADD 按 `GMFloatingAddPTX` 使用相应格式的原子加法数值规则。

旧值输出以默认 Null 填充物理非有效区，写入已定义零位模式；源、索引和目标各自按 dtype 分配物理列及容量。B.DIM 的有效列/行描述本次元素域，B.IOR.RegSrc0 传入 base；带 range 时 RegSrc1/2 选择 Min/Max GPR，省略时两个 selector 为零。
