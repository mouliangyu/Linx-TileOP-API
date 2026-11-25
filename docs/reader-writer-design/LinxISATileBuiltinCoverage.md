# PTO-C TileOP 的 C builtin 设计

上层库的 Reader/Writer、assemble 生命周期和整数 CELL 偏移接口另见 [TileOP 库接口设计](LinxISA/TileReaderWriterDesign.md)。本文讨论底层 builtin；这里“不引入 Reader/Writer”的约定仅适用于 builtin 层。

这是设计草案，尚未实现 Clang builtin 或 LLVM lowering。旧版只有分类表和少量不一致的示例，不能算完整接口。本版以[逐项原型目录](LinxISA/TileBuiltinPrototypes.md)和[源码映射表](LinxISA/TileBuiltinMapping.md)为准；它们包含 153 个拟议入口，映射 `template_asm.hpp` 中提取的 247 个候选名称（含宏生成、别名和退役诊断），并补充 predicate、region 和 TCI 路径。

## 统一约定

所有操作统一 `void` 返回，tile 目标用显式输出位置，tile 输入用向量值。普通计算与 assemble 使用同一个名字，例如 `__builtin_tadd`。没有 Reader/Writer、session token、finish 或额外的 step/last builtin。指针参数是拟议的 Clang 输出操作数协议，仍需专门的 Sema/CodeGen 支持，不能按普通 C 函数调用就得到寄存器语义。

向量容量按每个输入/输出独立确定；4 KiB 只是下面的实例，不能覆盖所有 tile 类型。目录中的 `T_dst/T_a/T_b` 是类型元变量，最终由 Clang builtin 的类型检查实例化，不是 C++ 模板。Shared 的 operand 类型与 Local 向量必须区分，对应 B.IOS 和 B.IOT。

目录中每个原型都完整展开参数，不使用参数宏。每个入口独立列出数据输入、目标、专有控制参数和可选附加结果，可以直接阅读。

## TADD 的完整展开

```c
typedef int tile4k_t __attribute__((vector_size(4096)));

void __builtin_tadd(
    tile4k_t *dst, unsigned dst_space, unsigned capacity_code,
    unsigned assemble_phase, long long dst_base_units,
    unsigned dst_offset_units, unsigned writer_size_code,
    tile4k_t a, unsigned a_space, unsigned a_dtype, unsigned a_capacity_code,
    unsigned a_view_enabled, long long a_view_base_units,
    unsigned a_view_offset_units, unsigned a_view_size_code,
    tile4k_t b, unsigned b_space, unsigned b_dtype, unsigned b_capacity_code,
    unsigned b_view_enabled, long long b_view_base_units,
    unsigned b_view_offset_units, unsigned b_view_size_code,
    long long lb0, long long lb1, long long lb2,
    unsigned operation_dtype, unsigned layout, unsigned pad, unsigned pe_mask);
```

`capacity_code` 是普通输出或 INIT parent 的容量，不再同时提供重复的 dst_size 与 parent_size。`writer_size_code` 是本次 assemble 写入片段大小。`dst_base_units + dst_offset_units` 表示片段在 parent 内的偏移，单位是 128 B；它不是 parent 的寄存器编号或 tile 队列相对索引。parent 身份由 `dst` 对应的变量确定，队列相对索引由后端生成。两个输入的 view 字段也各自描述片段偏移和长度，B.SUBVIEW 的输入编号由参数位置决定。

phase 使用五个独立枚举：

| phase | B.ASSEMBLE | B.IOT tile 输出 |
| --- | --- | --- |
| NONE | 不发射 | 分配普通 tile |
| INIT | INIT=1,LAST=0 | 分配唯一 parent |
| MIDDLE | INIT=0,LAST=0 | 无；绑定已有 parent |
| LAST | INIT=0,LAST=1 | 无；绑定已有 parent |
| INIT_LAST | INIT=1,LAST=1 | 分配 parent 并完成 |

NONE 和 MIDDLE 不能合并。LAST 完成的是已有 parent，没有新的 tile 结果。也不能把 B.IOT 的 `last`（binder 流结束位）误认为 assemble LAST。

## 完整 assemble 调用示例

下面四次 TADD 每次计算 16×16 FP32，即 1 KiB，写入一个 4 KiB parent。所有输入是已初始化的 4 KiB 载体，本例只使用其有效区域。数字常量中 size code 4=1 KiB、6=4 KiB；FP32=1、NORM=0。phase 数值是草案 C 枚举，不是直接的 ISA 编码。

```c
enum { ASM_NONE, ASM_INIT, ASM_MIDDLE, ASM_LAST, ASM_INIT_LAST };
enum { LOCAL = 0, FP32 = 1, SIZE_1K = 4, SIZE_4K = 6 };

void assemble_add(tile4k_t *parent,
                  tile4k_t a0, tile4k_t b0, tile4k_t a1, tile4k_t b1,
                  tile4k_t a2, tile4k_t b2, tile4k_t a3, tile4k_t b3) {
  /* 写入 parent 的第 1 个 1 KiB 片段；输入均不启用 subview。 */
  __builtin_tadd(
      parent, LOCAL, SIZE_4K, ASM_INIT, 0, 0, SIZE_1K,
      a0, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      b0, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      16, 16, 16, FP32, 0, 0, 15);
  /* 写入 parent 的第 2 个 1 KiB 片段；输入均不启用 subview。 */
  __builtin_tadd(
      parent, LOCAL, SIZE_4K, ASM_MIDDLE, 0, 8, SIZE_1K,
      a1, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      b1, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      16, 16, 16, FP32, 0, 0, 15);
  /* 写入 parent 的第 3 个 1 KiB 片段；输入均不启用 subview。 */
  __builtin_tadd(
      parent, LOCAL, SIZE_4K, ASM_MIDDLE, 0, 16, SIZE_1K,
      a2, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      b2, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      16, 16, 16, FP32, 0, 0, 15);
  /* 写入 parent 的第 4 个 1 KiB 片段；输入均不启用 subview。 */
  __builtin_tadd(
      parent, LOCAL, SIZE_4K, ASM_LAST, 0, 24, SIZE_1K,
      a3, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      b3, LOCAL, FP32, SIZE_4K, 0, 0, 0, 0,
      16, 16, 16, FP32, 0, 0, 15);
  /* 此后 parent 的组装内容才可被消费。 */
}
```

普通 TADD 使用 ASM_NONE，base/offset/writer_size 都为零，capacity_code 仍为输出容量。输入没有 subview 时四个 view 字段必须为零。

此 C 签名不能自动禁止提前读取 parent。底层调用者或上层 IR 必须遵守 assemble 完成前不可读的协议；是否由 Clang 验证、使用何种 IR 顺序依赖、何时剥离上层假依赖，仍需确定。接口字段足够描述一次调用不等于调度和生命周期问题已解决。原生 intrinsic 的 INIT 可以有真实 tile 结果，MIDDLE/LAST 没有真实 tile 结果；任何顺序依赖都不能被计作相对索引队列的新项。

## 覆盖与核对边界

[逐项目录](LinxISA/TileBuiltinPrototypes.md)包含 TEPL、归约/扩展、转换/选择/重排、TLSU、Shared/peer、indexed/atomic、CUBE/FPATR、predicate 的专名原型。每项都使用统一输出约定。FPATR 明确列出 Quant、PReLU、RowMax、GroupMax、CScale 输入/输出与控制字段；TLOAD 权重路径保留 shape/start 参数；多输出 TLOAD 保留所有结果；atomic store 保留 predicate/invert；TSEL 显式传入 false 值。

[源码映射表](LinxISA/TileBuiltinMapping.md)为每个提取的名称记录目标 builtin 和源码行，固定到 PTO-C commit。`_ASS` 映射回同名计算 builtin 的 phase；固定 Shared SLOT 独立处理。TCI_ROW/COL 映射到 TCI_2D 的步长 (1,0)/(0,1)。predicate concatenate 是两条 TAND assemble 序列，不假称一条指令；predicate subview 是 TMOV 物化路径，和普通 B.SUBVIEW 元数据有区别。

名称覆盖已逐项检查，**逐个重载的所有编码组合尚未完成验证**。尤其需核对 CUBE cooperative/Shared/fixp 的组合、各操作允许的 view/assemble 形式、atomic indices 单位，以及固定 Shared slot 的依赖。目录中的公共字段是可表达的超集；不存在的组合必须拒绝，不能因为某个原型有 phase 就认为 ISA 支持。

`TTRANS_ASS/TCONCAT_ASS` 的宏仍存在，而普通 selector 已退役，映射表将其列为冲突待确认。其他退役名称明确排除，不把其历史原型计为现行 builtin。当前仓库真正实现的入口仍见 `clang/include/clang/Basic/BuiltinsLinxISA.td`；本设计不声称这些 153 个专名已实现。

## 可复核性

运行 `python3 clang/docs/LinxISA/build_tile_builtin_catalog.py .work/Linx-TileOP-API` 可更新目录和名称映射；脚本遇到未分类的候选名会失败。它不是 C++ 预处理器或完整调用图分析，因此不能用脚本成功代替完整 lowering/汇编测试。最终实现验收还应逐一比较生成 block 的 B.IOT/B.IOS、DIM、DATR、IOR、FPATR、SUBVIEW、ASSEMBLE，并验证 MIDDLE/LAST 不增加队列项。
