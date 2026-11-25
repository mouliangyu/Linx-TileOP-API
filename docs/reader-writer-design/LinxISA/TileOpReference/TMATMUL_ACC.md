# TMATMUL_ACC

计算显式累加输入 C 与 A×B 之和，经所选后处理产生独立输出 D。

**头文件：** `<common/pto_tileop.hpp>` · **命名空间：** `pto` · [版本约定](README.md#版本与阅读约定)。

## 声明与重载

无 options 重载使用 Attr；需额外后处理操作数时选择 options 重载。带 groupM 重载用于 Local-A/Shared-B 的核级行分配。

```cpp
template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d,
          is_tile_data_v tile_shape_c, is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b>
void TMATMUL_ACC(tile_shape_d &d, tile_shape_c &c,
                 tile_shape_a &a, tile_shape_b &b);

template <FixpAttr Attr = FixpAttr{}, is_tile_data_v tile_shape_d,
          is_tile_data_v tile_shape_c, is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b>
void TMATMUL_ACC(tile_shape_d &d, tile_shape_c &c,
                 tile_shape_a &a, tile_shape_b &b, size_t groupM);

template <is_tile_data_v tile_shape_d, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b, fixp::is_options_v Options>
void TMATMUL_ACC(tile_shape_d &d, tile_shape_c &c,
                 tile_shape_a &a, tile_shape_b &b, const Options &options);

template <is_tile_data_v tile_shape_d, is_tile_data_v tile_shape_c,
          is_local_or_shared_left tile_shape_a,
          is_local_or_shared_right tile_shape_b, fixp::is_options_v Options>
void TMATMUL_ACC(tile_shape_d &d, tile_shape_c &c,
                 tile_shape_a &a, tile_shape_b &b, const Options &options,
                 size_t groupM);
```

## 参数与操作数角色

| 模板参数 | 含义或约束 | 默认值 / 推导 |
| --- | --- | --- |
| `Attr` | 不需额外 operand 的 FixpAttr 后处理配置 | `FixpAttr{}` |
| `tile_shape_d` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_c` | 由对应实参推导的类型，满足 `is_tile_data_v` 约束 | 由实参推导 |
| `tile_shape_a` | 由对应实参推导的类型，满足 `is_local_or_shared_left` 约束 | 由实参推导 |
| `tile_shape_b` | 由对应实参推导的类型，满足 `is_local_or_shared_right` 约束 | 由实参推导 |
| `Options` | 后处理与累加选项类型 | 由实参推导 |

| 参数 | 协议或存储角色 | 普通 Tile | Reader 片段 | Writer 输出描述 |
| --- | --- | --- | --- | --- |
| `d` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `c` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `a` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |
| `b` | 完整矩阵角色 Tile | 支持，按重载角色 | 不接受 | 不接受 |

### Options

| 写法 | 效果与条件 |
| --- | --- |
| `fixp::keep_acc()` | 无转换，D 为派生 AccType；不自动设置 raw/cache 控制位 |
| `fixp::keep_acc().raw_acc()` | 请求 raw accumulator D；禁止最终转换、激活和辅助 reduction |
| `fixp::keep_acc().raw_acc().acc_hint()` | 在上项基础上，对显式 C 添加透明缓存提示 |
| `fixp::f16()` / `fixp::bf16()` | 浮点 accumulator 转换到 FP16/BF16，D 必须匹配 |
| `fixp::f16().relu().acc_hint()` | 转换/激活并对 C 给缓存提示；不设置 raw_acc |
| `fixp::keep_acc().cscale(scale)` | 在累加前对 C 做 ISA 定义的逐行指数缩放；需要 FP32 C |

CScale 是 Local U8、CUBE_M32、有效形状 M×1。raw_acc 允许合法 CScale，因为它作用于累加输入；仍禁止最终后处理。编码 q 对应乘数 `2^-q`，0 表示保持 C，1 表示减半，完整参数参考见 [Options](Options.md)。

`raw_acc` 对应 CCTRL[0]；`acc_hint` 对应 CCTRL[1]，后者仅用于 ACC 形式。InternalAcc 是透明缓存：命中与否不能改变结果、D 的分配/发布或生命周期。**raw D 仍是可读的真实 Tile**，可以作为下一次 C，也可以用于合法的其他计算；不存在由调用者另传的“溢出指针”参数。

Options 还支持标量/向量量化、PReLU/LReLU、RowMax/GroupMax。量化模式必须匹配浮点或 S32 accumulator 类；RowMax/GroupMax 归约最终后处理后的 D，结果载体只支持 FP32/FP16/BF16，并按每 PE 行数分配。完整模式枚举、描述符位域和额外 operand 表见 [Options](Options.md)。

| 参数 | 方向 | 含义及单位 | 默认值 |
| --- | --- | --- | --- |
| `d` | out | 当前 PE 的 M×N 结果；后处理决定 dtype | 必填 |
| `c` | in | 同一 PE 的 M×N 累加值，dtype 必须为 AccType | 必填 |
| `a` | in | Left 矩阵；Local 为每 PE M×K，Shared 为组级矩阵 | 必填 |
| `b` | in | Right 矩阵；Local 逻辑 K×N，Shared 形状见下表 | 必填 |
| `groupM` | in | 核级总有效行数，单位为行，范围 1..128；无 | 必填 |
| `options` | in | 本次计算的转换、激活、CScale、cache hint 和 reduction 配置；参数没有默认值 | 必填 |

表中“必填”适用于包含该参数的重载；按选中重载的参数列表提供实参。

## 操作语义

未启用 CScale 时：

```text
acc[r,n] = C[r,n] + sum(A[r,k] * B[k,n], k = 0..K-1)
D = selected_postprocess(acc)
```

默认后处理保持 accumulator 类型。不读取旧 D；C 是显式输入 Tile。函数返回 void，D 是新结果；options 还可能指定 RowMax/GroupMax 辅助输出。

## 合法组合与限制

本页各重载按声明接受完整 Left/Right/Acc/Bias/Scale 角色对象。K 分片使用已完成 C 输入与独立 D 输出形成累加链；raw_acc 结果为完整可读 Tile。groupM 指定核级行分配，options 提供后处理及累加控制。

| 场景 | 选择 |
| --- | --- |
| Local A + Local B | 四参数形式，或追加 options |
| Shared A + Shared B | 从 Shared A 推导整个核的 M；可追加 options |
| Local A 分片 + Shared B | 显式传 groupM；有 options 时先 options、后 groupM |
| Shared A + Local B | 不支持 |

A/B 可以取同一行内的不同类型，不能跨行混合。

### dtype 配对

| A/B 数值类 | 各自可选 dtype | C 的 AccType | 无转换 D |
| --- | --- | --- | --- |
| 浮点 | FP32、TF32、HF32、FP16、BF16、HiF8、E4M3、E5M2、E3M2、E2M3、E2M1X2、E1M2X2 | FP32 | FP32 |
| 有符号整数 | S16、S8、S4X2 | S32 | S32 |
| 无符号整数 | U16、U8、U4X2 | U32 | U32 |

例如 FP16×BF16 配 FP32 C 属于浮点类；S8×U8 不合法。本接口的矩阵输入类型限于上述集合。带 MX scale 的操作是独立 TMATMUL_MX_ACC 接口，不能给本函数随意追加 scale 参数。

| 操作数 | 物理/有效描述 |
| --- | --- |
| Local A | CUBE_M16 或 CUBE_M32，与 D 同 M 布局，逻辑 M×K |
| Local B | CUBE_N8，逻辑 K×N，不允许 TransB |
| Shared A | 非 boxed RowMajor；TransA=0 为 groupM×K，TransA=1 为 K×groupM |
| Shared B | 非 boxed RowMajor；**TransB=0 为 N×K**，TransB=1 为 K×N |
| C/D | Local CUBE_M16/M32，布局相同，有效行列相同；无转换时容量相同 |

A/B 有效 K 必须相同。Local M16 最多 16 行，M32 最多 32 行；N/K 还须可由所选 dtype 的 CELL 物理存储承载。Shared 输入必须已经完成 generation 发布。

### 四 PE 行分配

协作执行以 groupM 分配四个 PE：groupM≤64 时每 PE 物理行块为 16，否则为 32。第 i 个 PE 的实际有效行数为：

```text
validM(i) = clamp(groupM - i * rowsPerPE, 0, rowsPerPE)
```

Shared-A 形式的 C/D 描述每 PE 行块，groupM 指定核级总行数。Local-A/Shared-B 同样按上述 16 或 32 行物理块分配，通过 groupM 决定各 PE 实际参与行数；物理块大小不要求 C++ 有效维度必须使用静态类型。A/C/D 的容量及输入有效区域须覆盖本 PE 实际参与的计算区域。显式 groupM 超出 1..128 会触发运行时 trap。

C 与 D 必须绑定不同 Tile 索引；不要写 `TMATMUL_ACC(c,c,a,b)`。后续 K 分片可将上一次真实 D 作为下一次 C。

编译期可判定的 dtype 类、K、布局和 options 冲突由模板检查拒绝；运行时有效维度按本次计算合同校验。运行时地址/Shared 发布错误不统一表现为 C++ 异常。浮点乘加按逻辑 K 递增逐项融合并舍入到累加类型；异常值、下溢与编码按[数值参考](Numerics.md)处理。

## 示例

```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
using Left = CubeTileM16<float, 16, 16>;
using Right = CubeTileN8<float, 16, 8>;
using Acc = CubeAccumulatorM16<float, 16, 8>;
using AGM = global_tensor<const float, RowMajor<16, 16>>;
using BGM = global_tensor<const float, RowMajor<16, 8>>;
using CGM = global_tensor<const float, RowMajor<16, 8>>;
using OutputGM = global_tensor<float, RowMajor<16, 8>>;

void two_k_parts(float *out, const float *initial_c,
                 const float *a0, const float *b0,
                 const float *a1, const float *b1) {
  AGM ga0(a0), ga1(a1);
  BGM gb0(b0), gb1(b1);
  CGM gc(initial_c);
  OutputGM gd(out);
  Left x0, x1;
  Right y0, y1;
  Acc c, partial, result;
  TLOAD(c, gc);
  TLOAD(x0, ga0); TLOAD(y0, gb0);
  TMATMUL_ACC(partial, c, x0, y0, fixp::keep_acc().raw_acc());
  TLOAD(x1, ga1); TLOAD(y1, gb1);
  TMATMUL_ACC(result, partial, x1, y1, fixp::keep_acc().acc_hint());
  TSTORE(gd, result);
}
```

初始 C 全为 0、两组 A/B 全为 1 时，16×8 个输出均为 32。C 的 GM 描述为 16×8，不能错误复用 A 的 16×16 描述。

### Local 输入与逐重载调用

<!-- audit-example: tmatmul_acc_local -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_acc_local {
using D = CubeAccumulatorM16<float, 16, 8, 16, 8>;
using Row = VecTileM16<float, 16, 2, 16, 1>;
using A16 = CubeTileM16<__half, 16, 64, 16, 35>;
using B16 = CubeTileN8<__half, 64, 8, 35, 8>;

void product(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_ACC(by_attr, c, a, b);
  TMATMUL_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row));
}

}
```
输入的有效 K=35，物理 K=64；有效 M=16、N=8。所有 primary 的有效元素取数值1。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35 + 2 = 37。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 1 | `product` 中的 `by_attr` 调用 |
| 3 | `product` 中的 `by_options` 调用 |

### Local A 与 Shared B：显式 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；A 使用 `(validM, 35)` 构造并准备对应核级行块；C 使用 `(validM, 8)` 构造，参与行的初值为2；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_acc_mixed -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_acc_mixed {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = CubeTileM16<__half, 16, 64, DYNAMIC, 35>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;

void product(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_ACC(by_attr, c, a, b, size_t{20});
  TMATMUL_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row), size_t{20});
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；所有 primary 的有效元素取数值1。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35 + 2 = 37。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 2 | `product` 中的 `by_attr` 调用 |
| 4 | `product` 中的 `by_options` 调用 |

### Shared A 与 Shared B：推导 groupM

四个 PE 均参加本次协作调用，groupM=20。PE0/1/2/3 的有效行数依次为16/4/0/0，物理行块均为16。调用者按本 PE 的有效行数构造 D 和 Row，例如 PE1 使用 `D(4, 8)`、`Row(4, 1)`；C 使用 `(validM, 8)` 构造，参与行的初值为2；Shared 输入及其 scale 均须已经发布。零行 PE 参加协作，其输出没有有效元素可读。

<!-- audit-example: tmatmul_acc_shared -->
```cpp
#include <common/pto_tileop.hpp>
using namespace pto;
namespace tmatmul_acc_shared {
using D = CubeAccumulatorM16<float, 16, 8, DYNAMIC, 8>;
using Row = VecTileM16<float, 16, 2, DYNAMIC, 1>;
using A16 = SharedTile<SharedMatrixLeft<__half, 32, 64, 20, 35>>;
using B16 = SharedTile<SharedMatrixRight<__half, 8, 64, 8, 35>>;

void product(D &by_attr, D &by_options, Row &row, D &c, A16 &a, B16 &b) {
  TMATMUL_ACC(by_attr, c, a, b);
  TMATMUL_ACC(by_options, c, a, b, fixp::keep_acc().row_max(row));
}

}
```
Shared B 按 N×K 存储，有效8×35、物理8×64；Shared A 有效20×35、物理32×64；所有 primary 的有效元素取数值1。C 的有效元素均为2。所有输入已经定义；各输出与数学输入、另一个输出分配独立对象。Options调用额外输出每行最大值row，其物理容量128B、有效M×1；本例各列值相同，因此row等于该行任一D元素。

两个输出的每个有效元素均为35 + 2 = 37。以上为库数学合同的预期；示例的声明选择与数值执行验证分别记录。

| 声明序号 | 本节调用函数 |
| --- | --- |
| 1 | `product` 中的 `by_attr` 调用 |
| 3 | `product` 中的 `by_options` 调用 |

### 后处理与辅助输出

完整的转换、RowMax/GroupMax、CScale、raw_acc、acc_hint、量化和转置函数见 [Options 组合示例](Options.md#完整组合示例)。M32 的协作尾行和其他 scale 格式见[矩阵边界示例](MatrixRules.md#更多形状与格式示例)。

## 公共规则与相关接口

**相关：** [TLOAD](TLOAD.md)、[TADD](TADD.md)、[公共版本说明](README.md)。

**Tile 生命周期：** [矩阵与 Shared 操作边界](StorageBoundaries.md)。

[返回算子索引](README.md)
