# Shared 与矩阵的存储合同

Local、Shared 分片都使用 Reader/Writer 选择片段；Shared 的 PE 协作及 generation 发布另受本页约束。支持分片不免除每个操作的布局、物理行距和容量检查。

| 操作 | Reader | Writer |
| --- | --- | --- |
| Local TLOAD / TSTORE | TSTORE 的 Local 源 | TLOAD 的 Local 目标 |
| Shared TLOAD / TSTORE | TSTORE 的已发布 Shared ND 子区间 | TLOAD 的 Shared 组装目标 |
| TMOV Local→Shared | 按源布局检查 | Shared 分段插入，全部完成后发布 |
| TMOV Shared ND→Local ND | 已发布 Shared ND 完整对象或合法 Reader 子视图 | 支持 Local Writer；先读取为完整 Local Part 临时值，再用 Local TMOV 写入 Writer 片段 |
| TMOV Shared ND→Local CUBE | 已发布 Shared ND 完整对象或覆盖完整物理行的合法 Reader 子视图 | 目标为完整 Local CUBE Tile |
| 矩阵全族 | 按矩阵角色选择；不能把任意字节片段当作矩阵 | K 累加仍使用真实 C→D，不等同于组装 |

## Shared Reader

`TileReader<SharedTile<Shape>>` 借用已发布的 Shared generation，`read<Part>(cell_offset)` 使用 128 B 单位，Part 描述 ND 子区域的物理容量和有效形状。范围不得越界，保持 parent 行距；不能通过改变 Part 列数伪装紧密排列的子列。TSTORE 按视图与 parent 有效区域的交集写 GM，GM 地址由调用者另行选择；PEMask 不自动分段或移动 GM 地址。

Shared ND→Local CUBE 读取必须覆盖连续 16/32 个完整物理行，起点为物理行边界，源行距不变；起始行不要求为 16/32 倍数。有效行数为 min(M,max(0,parent.ValidRow-origin_row))，有效列数沿用 parent，均须为正。目标精确容量推导的物理列数与源相等。目标有效形状按上述转换规则确定；不额外施加 C++ 静态模板逐轴相等的限制。

## Shared Writer

`TileWriter<SharedTile<Shape>>` 的各 PE 对象保存同一 Core-wide Sx 的目标身份与几何，阶段描述透传给底层。INIT 建立 generation，其他 PE 可直接通过同一 Sx 执行 MIDDLE/LAST；不要求每个对象先 first 再 last。合法阶段、覆盖和发布按整个 generation 判断。single 表示 INIT_LAST，不能泛化为每个 PE 的唯一写入。

finish 仅交出该 Sx 的 SharedTile 句柄，不读取其他 PE 的 INIT 返回值，不增加硬件结束指令，也不完成同步或发布。持有句柄不等于 payload 已就绪；消费者必须遵守 Shared generation 的发布和读取规则。Writer 和输出描述本身不能构造 Reader；finish 不允许绕过未完成 generation 的输入限制。目标身份仍是架构 Shared 句柄；本页不定义其序列化或跨调用 ABI。详见 [Writer](Writer.md#shared-writer目标身份与阶段透传)。

整块 TMOV 发布显式选择单 PE mask 1/2/4/8；组装 TMOV 同样必须显式填写 PEMask，无默认值。所有参与者须一致地描述 parent、dtype、布局及 generation，写入不重叠并形成合法最终覆盖。各 PE 的 CELL 偏移可以不同。

RowMajor TMOV 组装的参与者使用一致的 parent 有效形状，Local 源物理容量及列数与 Shared parent 一致；实际片段从 Local 源第一行开始，按完整行写入。Writer Part 表达目标插入范围，不能强制它与 Local 源总容量相等。CUBE→ND 的源容量等于 Writer Part 容量；完整输出时才等于 parent。源物理列数由其 CUBE 容量精确推导，Shared parent 保持该列距；插入的字节范围为 [128*cell_offset, 128*cell_offset+PartBytes)。

## 矩阵角色

矩阵公开重载按声明使用完整 Left/Right/Acc/Bias/Scale 对象，逐角色满足 M/N/K、N8/M16/M32、scale 配对和 Shared 发布要求。

K tiling 使用已完成 C 输入和独立 D 输出，raw_acc、acc_hint 仍由 Options 指定。源 A/B 的分块可通过分别加载或受支持的 Shared 转换产生，不能用未完成 Writer 作为 C。

依据：[TMOV](https://linxisa.github.io/PTO-C/#TMOV)、[TSTORE](https://linxisa.github.io/PTO-C/#TSTORE)、[TLOAD](https://linxisa.github.io/PTO-C/#TLOAD)。

## Shared TMOV 的 PEMask

PEMask 是四 PE 的语义位掩码，可编码值为 0、1、2、4、8、12、14、15。PE0 对应 bit3，PE1 对应 bit2，PE2 对应 bit1，PE3 对应 bit0；12（1100）选择 PE0/PE1，14（1110）选择 PE0/PE1/PE2。硬件三位 PEMode 是其编码，不直接作为 C++ PEMask 实参。

Local→Shared 的 B.IOT 与 B.IOS 必须采用相同 mask。不带 assemble 的非零写入只能选择一个 PE（1、2、4、8），由它发布完整 parent；多个 PE 写入必须通过 Writer 描述生成 B.ASSEMBLE，并满足最终覆盖及 LAST 发布要求。统一 TMOV 及 CUBE→Shared ND 专用入口都要求显式 PEMask。

Shared→Local 每个参与 PE 获得独立 Local 结果；默认 PEMask=15 是库的便利约定。ND2M16/ND2M32 方向禁止 B.ASSEMBLE，因此输出只能是完整 Local CUBE Tile，不能使用 Writer 描述；源仍允许合法 Shared Reader 子视图。

mask=0 在 ISA 中为严格 no-op，不读取源、不分配、不发布，也不消费绑定。库不能将零 mask 调用当作成功写入或据此推进 Writer 阶段；需要完成组装的 Writer 调用必须使用非零 mask。

核对依据：LinxISA 0.59.1 手册引用的固定语义版本 `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`：

- [BSTART.TMOV](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/execution/BSTART.TMOV.asl)：发布、方向及零 mask 规则。
- [B.IOS](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/operands/B.IOS.asl)：PEMode 编码。
- [PE 编号映射](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/arch/programming-model/core-pe-topology.asl)：PE0 对应最高位。
