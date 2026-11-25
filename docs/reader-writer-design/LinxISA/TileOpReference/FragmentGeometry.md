# 分片几何与局部坐标

本页补充 Readable/Writable 协议。支持分片的算子将 Part 作为本次操作的计算视图，不把 CELL 偏移当作逻辑行列。调用者负责选择正确的片段；偏移必须满足 Reader/Writer 的容量、布局和对齐合同。输入与输出分别推导物理容量，均不得越出 Parent。

| 算子族 | 输入与输出 Part 的合同 |
| --- | --- |
| 逐元素、标量 | 相同计算几何，dtype 配对符合该算子；各输入可选不同 CELL 偏移 |
| 行归约 | 输入 R×C，输出 R×1；仅归约选中片段的 C 列 |
| 列归约 | 输入 R×C，输出 1×C；仅归约选中片段的 R 行 |
| ARG 归约 | 返回片段内从 0 开始的元素索引；库不推导全 parent 坐标 |
| ROW 广播 | 矩形 R×C 配广播源 R×Cb（Cb≥1），按 BroadcastByteOffset 选列，输出 R×C |
| COL 广播 | 矩形 R×C 配广播源 Rb×C（Rb≥1），读取第0行，输出 R×C |
| TCVT | 输入/输出相同逻辑有效 R×C；各自按 dtype 推导物理容量和 SizeCode，满足该布局的转换规则 |
| TPERMUTE | 每个源表在 Part 内建立；U8 索引按输出元素字节数扩展；不得索引选中表外的 parent 数据 |
| TSHUF | lane/segment 从 Part 的第 0 行计，边界处理相对于 Part 有效区域；完整 segment 和控制 word 映射须保留 |
| TPACK / TUNPACK | 按 Part 内 raw-word 配对和选中字节有效范围校验；尾 word 与 U64 配对条件见操作页；输出列数按目标 dtype 换算 |
| TGPR2T | Writer Part 固定为 U8 M32 32×4 或 M16 16×8；无 Reader 输入 |

沿归约轴分片得到部分归约，finish 只组装结果，不自动求和或合并极值。广播源和矩形源须由调用者选择匹配的逻辑区域，相同 CELL 偏移不保证逻辑对应。所有更严格的布局、dtype、固定形状和物理行对齐要求仍适用。

## 序列、三角形和 Local 索引

TCI/TCI_2D/TCI_ROW/TCI_COL 的 r/c 从输出 Part 的 0 开始；每个片段的 s 独立提供，库不根据 CELL 偏移调整起点。TTRI 同样按 Part 的局部坐标、固定 lower 和对角线偏移 0 生成三角形；拼接多个局部三角形不自动等同于生成 Parent 的整体三角形。

TGATHER 的 off 是源 Part 内的行号，必须小于源 Part 的有效行数；列坐标保持 Part 内的列号。TSCATTER 的 off 是目标 Part 内的行号；零初始化仅作用于本次目标 Part，不清除其他 Writer 片段。重复目标检查作用于本次调用，Writer 的各物理片段仍须互不重叠。索引不会因 CELL 偏移自动加减 Parent 行号。

## 单片容量

Reader 的 Part（B.SUBVIEW）和 Writer 的 Part（B.ASSEMBLE）均使用以下单片容量范围：Local 为 SizeCode 1..10，即 128 B～64 KiB；Shared 为 SizeCode 1..12，即 128 B～256 KiB。容量按二次幂编码，且须满足该操作的布局和对齐要求。Local完整parent也受B.IOT的SizeCode 1..10限制；Shared parent上限为256KiB。偏移加 Part 容量仍须落在 Parent 内。
