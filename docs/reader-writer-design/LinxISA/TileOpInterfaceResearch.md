# TileOP 接口文档：调研与结构设计

## 交付目标

形成一份 kernel 作者可阅读的 [TileOP 接口指南](TileOpInterfaceGuide.md)，覆盖现有库的对象和算子组织，重点定义 assemble/subview 改造后的接口、语义和迁移方式。设计讨论的细节保留在专题文档，主指南按读者任务组织，不按讨论时间顺序排列。

## 调研来源

库基线为 LinxISA/Linx-TileOP-API `5f764847b707fabf998c93fb4725787bcd2d6417`；ISA 基线为 PTO-ISA/pto-spec `a89a53d48f5708328be609fe2e6296ac8bdb4bc2`。以下路径相对于对应仓库。

| 来源 | 核对内容 | 对文档的影响 |
| --- | --- | --- |
| `docs/tileop-usage/README.md`、`support-status.md` | 现有 API/spec 版本、算子目录、元素接口与后端支持边界 | 复用逐操作参考；不把 wrapper 存在等同完整编译支持 |
| `include/common/pto_tile.hpp` | Tile 类型、FixpAttr、raw_acc/acc_hint | 区分类型、容量、后处理与缓存控制 |
| `include/common/pto_tile_region.hpp` | BorrowedTileArray、TileArray、TPARTVIEW、TASSEMBLY | 明确旧接口迁移和元素 profile 例外 |
| `include/common/pto_local_cube_assembly.hpp` | 已有 assembly owner/writer/result 类型 | 可参考所有权，不复制静态 writer 列表限制 |
| `docs/tileop-usage/b-subview-b-assemble.md` | 分片层次、旧空间 slot、TLOAD assembly | 新接口解耦阶段与位置；记录旧规范几何差异 |
| TADD、TSTORE、TMATMUL、TMATMUL_ACC 操作页及 `options.md` | 参数次序、range 支持、groupM 与 options | 保留现有算子命名和专用约束 |
| ISA `asl/block/model/operands/local-generation*.asl` | assembly 边界、覆盖、物理形状和完成 | 以当前基线规则替代旧版几何叙述，详见 ReaderWriter 专题已有源码核对 |
| ISA `asl/tile/model/execution/internal-accumulator.asl` | 透明缓存、显式 C/D、每步发布 | 纠正“raw acc 不可读”的错误前提 |
| ISA `asl/tile/model/execution/cube.asl` | CommitMatrixRawPartial 实际发布结果 | raw D 仍是 tile，不另造不可读 accumulator 类型 |
| ISA `asl/block/model/dispatch/cube-accumulator-routing.asl`、`cube-tmatmul.asl` | CCTRL 合法性、hint 调用、C/D 索引区分 | 保留 acc_hint，不承诺原地累加 |

调研使用已有本地参考 checkout，并读取固定提交的在线 ISA 源码。没有升级参考 checkout，没有修改库实现或 ISA。

## 主要发现

1. 现有库已经有按算子分类的参考页，新文档应提供统一编程模型和入口，避免手工复制全部重载后与实现分叉。
2. 分片接口目前包含高层 TileArray/TPARTVIEW、专用 LocalCubeAssembly 和专家 range 接口。新 Reader/Writer 统一一般分片表达，但不自动替换逻辑元素 profile、Shared 发布和固定 ABI 专家接口。
3. 当前库 assembly 文档部分内容绑定旧规范；parent 物理几何与当前 ISA 不同。文档必须显式锁定两个来源版本。
4. 已记录两套 Writer：当前 ISA 的阶段方案，以及需修改 ISA 的 BEGIN/END 方案。主文选择前者作为当前基线，单列后者，避免同名 finish 的行为冲突。此组织选择不是宣布用户已选定最终 ISA 方案。
5. InternalAcc 的缓存行为对架构透明，raw D 是正常发布的 tile。此前讨论的不可读 acc handle、独立 spill 指针和 CREATE 不作为当前接口事实。

## 章节结构与必需信息

| 章节 | 回答读者的问题 | 必需信息 |
| --- | --- | --- |
| 范围与版本 | 哪些已存在，哪些还在设计？ | 固定提交、实现状态、层次边界 |
| 对象与单位 | 手里是什么对象，参数怎么填？ | Tile/Shared/GM、物理与有效形状、CELL/count/groupM 单位 |
| 操作数角色 | 哪些能读，哪些能写？ | Readable/Writable 矩阵、禁止的组合 |
| Reader | 如何获取一个可读片段？ | 构造、read、fragments、借用、编码与边界 |
| Writer | 如何把结果直接写进 parent？ | 完整方法集、状态转换、首次结果保存和 finish |
| 用例 | 实际代码如何组合？ | 混合片段、非递增位置、single、重复读 |
| 迭代器 | 动态循环与提前结束如何处理？ | 解引用/自增、count、分派、break/continue、PHI |
| 算子适配 | 其他算子和 matmul 怎么用？ | 类别导航、逐角色适配要求、options 与 CCTRL |
| 迁移 | 旧 API 替换成什么？ | TPARTVIEW/TileArray/LocalCubeAssembly/range 映射及例外 |
| ISA 备选 | 如何进一步简化？ | BEGIN/write/END 与绑定阶段的差异 |
| 实现边界 | 哪些还需要工程验证？ | 类型、动态检查、编译器顺序、相对索引、模型验收 |

## 维护规则

- 每个新接口明确标记拟议或已实现；示意返回类型不伪装成已发布头文件。
- 新增算子适配时记录完整签名、操作数角色、dtype/layout、subview/assembly 支持、alias、动态参数、错误行为和验证状态。
- 主指南说明用户可观察语义；builtin、IR 与机器实现细节链接到专题，不混入日常调用示例。
- 阶段方案与独立 END 方案若最终择一，应同步修改主指南和两个专题，不能只改快速示例。
- 验证等级区分源码核对、目标编译、汇编检查、模型数值验证。本次文档交付不宣称后三项已完成。
