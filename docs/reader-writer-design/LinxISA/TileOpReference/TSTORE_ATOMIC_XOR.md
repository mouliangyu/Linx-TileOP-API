# TSTORE_ATOMIC_XOR

按规则矩形 GM 地址逐元素原子更新，无 Local 返回值。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

| 重载 | src | active |
| --- | --- | --- |
| Local | Local RowMajor/M16/M32 | 无此参数 |
| Shared | 已发布 Shared RowMajor | 无此参数 |
| 谓词形式 | Local M16/M32 | 必填，Local PredicateReadable |

本页按下列顺序列出全部重载；实参类型与参数列表共同决定选择。各重载的存储角色和专用要求见后文。

```cpp
template <int PEMask = 15, GlobalMemoryView G, Readable S>
void TSTORE_ATOMIC_XOR(G &dst, S &&src);

template <int PEMask = 15, GlobalMemoryView G, SharedReadable S>
void TSTORE_ATOMIC_XOR(G &dst, S &&src);

template <int PEMask = 15, bool PredInv = false,
          GlobalMemoryView G, Readable S, PredicateReadable P>
void TSTORE_ATOMIC_XOR(G &dst, S &&src, P &&active);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `PEMask` | 编译期参与 PE 位掩码，含义及可用集合按本操作合同 | `15` |
| `G` | GlobalMemoryView 的元素类型、基址和访问属性 | 由实参推导 |
| `S` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |
| `PredInv` | 谓词形式：是否反选 active | `false` |
| `P` | 对应函数参数的计算视图类型，约束见声明 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `src`（Local） | Readable | Local | Local Reader | 不接受 |
| `src`（Shared） | SharedReadable | Shared | Shared Reader | 不接受 |
| `src`（谓词形式） | Readable | Local CUBE | Local CUBE Reader | 不接受 |
| `active`（谓词形式） | PredicateReadable | Local CUBE Predicate | 对应 Predicate Reader | 不接受 |

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `dst` | in（GM 内存读写） | 目标，结果存储与布局按本页合同 | 必填 |
| `src` | in | 已定义的输入计算视图 | 必填 |
| `active` | in | 谓词形式的活动元素输入 | 该重载必填 |

## 操作语义

每个活动位置以旧 GM 值 old 执行 `new = old ^ src`。src dtype 为 U32/U64，GM dtype 相同。地址由 GM base、行距和逻辑列计算，不接受 indexed offset。

## 合法组合与限制

全部重载的PEMask可取0、1、2、4、8、12、14、15。默认15，0为严格no-op。PE0/1/2/3对应bit3/2/1/0。Local源支持RowMajor/M16/M32，b64使用RowMajor/M32；Shared源支持已发布RowMajor。active 形式只允许 Local CUBE，布局及有效形状与源匹配；PredInv 默认 false，为 true 时反选。固定 Zero=0，未活动位置不更新 GM，不做 zero-fill。

每个 GM 元素独立提交原子更新；重复地址执行多次更新，先后次序不作 lane 顺序保证。输出 void，不产生 old Tile，不参与 Writer 组装。Reader 的偏移只选择源，GM 子区域由调用者另行指定。

本操作由BSTART.TSTORE Function1、Canonicalize=1、CMode=5选择；RMode=0、Sat=0、Zero=0。有效行列来自源计算视图，GM地址使用视图基址与元素行距换算后的字节stride；CUBE源转换到逻辑ND坐标后访问GM。GM元素类型与源相同，访问地址须满足该元素的读写权限和对齐。

每个选中PE先快照源并探测本请求全部活动地址，成功后逐元素提交原子更新。未选中PE不读取源或检查其私有地址；谓词关闭的位置不访问GM。一个PE的失败不撤回其他PE已经提交的更新。Shared源未发布时等待；成功提交的延迟请求保存源generation与snapshot，源最后使用在请求及所需参与者完成后释放。GM写入的跨执行者可见性遵守适用的内存顺序与同步规则。

整数ADD按目标位宽取模，MIN/MAX按dtype符号比较，位运算仅使用目标有效位。INC以src为limit，old≥limit时写0；DEC在old=0或old>limit时写limit，否则写old−1。浮点ADD逐次RMW按自身dtype使用RN-even并保留subnormal；NaN或异号无穷相加为canonical NaN，同为负零得负零，其余精确抵消得正零；不产生数值状态写入。以上算术规则分别适用于对应操作。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using V = Tile<Location::Vec, uint32_t, 1, 32>;
using G = global_tensor<uint32_t, RowMajor<1, 32>>;
void example(uint32_t *memory, V &src) {
  G dst(memory);
  TSTORE_ATOMIC_XOR<8>(dst, src);
}
```

memory 指向对齐的 32 个可读写 U32；src 已定义；仅 PE0 由掩码 8 参与，无其他并发访问。 各 GM 元素初值为 5、src 全为 1 时，每个位置更新为 4。

### Shared 源与谓词重载

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using SharedShape = Tile<Location::Vec, uint32_t, 32, 4>;
using Published = SharedTile<SharedShape>;
using Cube = VecTileM32<uint32_t, 32, 4>;
using Pred = PredicateTile<Cube>;
using GM = global_tensor<uint32_t, RowMajor<32, 4>>;
void shared_source(uint32_t *memory, Published &source) {
  GM dst(memory);
  TSTORE_ATOMIC_XOR<8>(dst, source);
}
void selected_rows(uint32_t *memory, Cube &source, Cube &gate) {
  GM dst(memory);
  Pred active;
  TCMPS<CmpMode::NE>(active, gate, uint32_t{0});
  TSTORE_ATOMIC_XOR<8, false>(dst, source, active);
}
void inverted_rows(uint32_t *memory, Cube &source, Cube &gate) {
  GM dst(memory);
  Pred active;
  TCMPS<CmpMode::NE>(active, gate, uint32_t{0});
  TSTORE_ATOMIC_XOR<8, true>(dst, source, active);
}
```

每个函数独立调用前将可读写且元素对齐的memory[128]初始化为5，source全部有效元素为1；Shared版本的source已完整发布。gate在偶数行全1、奇数行全0。仅PE0参与：shared_source全部更新为4；selected_rows仅偶数行变为4，奇数行保持5；inverted_rows反转所选行。载体容量：Shared和U32 M32均512B，谓词按PredicateCell独立推导。结果按固定规范推导，编译及硬件运行未执行。

边界：mask0无访问；INC的limit0始终写0，DEC的old0写limit；同一请求若最后一个活动地址不可写，在首个原子效果前拒绝该PE请求。跨PE失败边界见[原子存储证据](../TileOpContractEvidence.md#规则地址原子存储)。

## 公共规则与相关接口

依据：[固定执行入口](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/block/model/dispatch/tlsu-atomic-tstore.asl)、[原子更新与生命周期](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/atomic-tstore.asl)、[类型与数值](https://github.com/PTO-ISA/pto-spec/blob/a89a53d48f5708328be609fe2e6296ac8bdb4bc2/asl/tile/model/memory/gm-atom-red.asl)；核对记录见[核对证据](../TileOpContractEvidence.md#规则地址原子存储)。

[返回算子索引](README.md)
