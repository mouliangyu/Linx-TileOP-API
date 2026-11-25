# 逐项 C builtin 原型目录

此文件由 `build_tile_builtin_catalog.py` 生成。它是接口设计 schema，尚不是 Clang 支持的 C 头文件。
所有操作统一 `void` 返回，目标通过显式输出位置传入；输入 tile 仍为向量值。
`T`/`T_a`/`T_b` 等表示独立选取容量的向量类型；它们是签名元变量，不是 C++ 模板或一个固定宽度 typedef。
Shared 操作数的值类型为 target Shared carrier，并要求 `space=SHARED`；不能用普通整数冒充 Local tile。

## 参数约定

每个原型都完整列出所有参数，不使用参数宏、descriptor struct 或 `...` 可变参数。

`capacity_code` 为普通输出容量或 INIT parent 容量；没有重复的 dst_size/parent_size。
`dst_base_units + dst_offset_units` 是片段在 parent 内的偏移（128 B 单位），**不是 tile 队列的相对索引**。
parent 身份由 `dst` 指定；队列相对索引由后端分配。
输入参数的 view 基址也表示片段偏移，binder 的输入编号由参数位置决定。
`NONE/INIT/MIDDLE/LAST/INIT_LAST` 分别是无 modifier、(1,0)、(0,0)、(0,1)、(1,1)；
NONE 与 MIDDLE 不能因 INIT/LAST 都为零而混淆。
`NONE` 时 writer/base/offset 必须为零，容量仍有效；无 view 时其 base/offset/size 必须为零。

所有编码枚举、size、space、phase、offset、enable、PE mask 为编译期常量；
DIM、地址、步长、标量位模式、参数控制字、base 可以运行时传入。
标量采用 dtype 对应的原始位模式，浮点不做数值到整数转换。
可选 tile 禁用时必须传对应类型的零载体，可选输出禁用时传 null；编译器不生成这些 binder，不能传未初始化值。
`range_min/range_max` 保留 PTO-C IndexedByteRange 的字节边界语义，不擅自改成元素编号。
atomic 的 indices 单位须随具体 opcode 核对，不能套用普通 MGATHER 的 byte offsets。

公共字段是设计超集，不意味着所有操作都允许 view/assemble/FPATR 全组合。
不支持的字段必须为零并由 Sema 拒绝非法组合；下方 ASS 映射是已发现的支持证据。
Fixed Shared SLOT 是 S0..S63 名称，和 assemble phase 无关。
FPATR enable 与可选 operands/results 必须按 Options 的合法组合检查，不能仅保留一个 fixp_mode。

## 原型（每个入口单独列出）

### `__builtin_gmov`

peer move

```c
void __builtin_gmov(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t peer_tid,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather`

gather; byte offsets

```c
void __builtin_mgather(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    T_byte_offsets byte_offsets,
    unsigned byte_offsets_space,
    unsigned byte_offsets_dtype,
    unsigned byte_offsets_capacity_code,
    unsigned byte_offsets_view_enabled,
    int64_t byte_offsets_view_base_units,
    unsigned byte_offsets_view_offset_units,
    unsigned byte_offsets_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_add`

atomic with old-value output

```c
void __builtin_mgather_add(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_and`

atomic with old-value output

```c
void __builtin_mgather_and(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_cas`

atomic CAS: old-value output

```c
void __builtin_mgather_cas(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_expected expected,
    unsigned expected_space,
    unsigned expected_dtype,
    unsigned expected_capacity_code,
    unsigned expected_view_enabled,
    int64_t expected_view_base_units,
    unsigned expected_view_offset_units,
    unsigned expected_view_size_code,
    T_replacement replacement,
    unsigned replacement_space,
    unsigned replacement_dtype,
    unsigned replacement_capacity_code,
    unsigned replacement_view_enabled,
    int64_t replacement_view_base_units,
    unsigned replacement_view_offset_units,
    unsigned replacement_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_dec`

atomic with old-value output

```c
void __builtin_mgather_dec(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_exch`

atomic with old-value output

```c
void __builtin_mgather_exch(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_inc`

atomic with old-value output

```c
void __builtin_mgather_inc(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_mask`

masked gather

```c
void __builtin_mgather_mask(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    T_byte_offsets byte_offsets,
    unsigned byte_offsets_space,
    unsigned byte_offsets_dtype,
    unsigned byte_offsets_capacity_code,
    unsigned byte_offsets_view_enabled,
    int64_t byte_offsets_view_base_units,
    unsigned byte_offsets_view_offset_units,
    unsigned byte_offsets_view_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_max`

atomic with old-value output

```c
void __builtin_mgather_max(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_min`

atomic with old-value output

```c
void __builtin_mgather_min(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_or`

atomic with old-value output

```c
void __builtin_mgather_or(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mgather_xor`

atomic with old-value output

```c
void __builtin_mgather_xor(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter`

scatter; byte offsets

```c
void __builtin_mscatter(
    void *base,
    T_byte_offsets byte_offsets,
    unsigned byte_offsets_space,
    unsigned byte_offsets_dtype,
    unsigned byte_offsets_capacity_code,
    unsigned byte_offsets_view_enabled,
    int64_t byte_offsets_view_base_units,
    unsigned byte_offsets_view_offset_units,
    unsigned byte_offsets_view_size_code,
    T_values values,
    unsigned values_space,
    unsigned values_dtype,
    unsigned values_capacity_code,
    unsigned values_view_enabled,
    int64_t values_view_base_units,
    unsigned values_view_offset_units,
    unsigned values_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_add`

atomic reduction without output

```c
void __builtin_mscatter_add(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_and`

atomic reduction without output

```c
void __builtin_mscatter_and(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_dec`

atomic reduction without output

```c
void __builtin_mscatter_dec(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_inc`

atomic reduction without output

```c
void __builtin_mscatter_inc(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_mask`

masked scatter

```c
void __builtin_mscatter_mask(
    void *base,
    T_byte_offsets byte_offsets,
    unsigned byte_offsets_space,
    unsigned byte_offsets_dtype,
    unsigned byte_offsets_capacity_code,
    unsigned byte_offsets_view_enabled,
    int64_t byte_offsets_view_base_units,
    unsigned byte_offsets_view_offset_units,
    unsigned byte_offsets_view_size_code,
    T_values values,
    unsigned values_space,
    unsigned values_dtype,
    unsigned values_capacity_code,
    unsigned values_view_enabled,
    int64_t values_view_base_units,
    unsigned values_view_offset_units,
    unsigned values_view_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_max`

atomic reduction without output

```c
void __builtin_mscatter_max(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_min`

atomic reduction without output

```c
void __builtin_mscatter_min(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_or`

atomic reduction without output

```c
void __builtin_mscatter_or(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_popc`

atomic popcount: no values operand

```c
void __builtin_mscatter_popc(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_mscatter_xor`

atomic reduction without output

```c
void __builtin_mscatter_xor(
    void *base,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    T_value_or_limit value_or_limit,
    unsigned value_or_limit_space,
    unsigned value_or_limit_dtype,
    unsigned value_or_limit_capacity_code,
    unsigned value_or_limit_view_enabled,
    int64_t value_or_limit_view_base_units,
    unsigned value_or_limit_view_offset_units,
    unsigned value_or_limit_view_size_code,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_predicate_atomic_add`

predicate atomic add

```c
void __builtin_predicate_atomic_add(
    void *base,
    T_offsets offsets,
    unsigned offsets_space,
    unsigned offsets_dtype,
    unsigned offsets_capacity_code,
    unsigned offsets_view_enabled,
    int64_t offsets_view_base_units,
    unsigned offsets_view_offset_units,
    unsigned offsets_view_size_code,
    T_values values,
    unsigned values_space,
    unsigned values_dtype,
    unsigned values_capacity_code,
    unsigned values_view_enabled,
    int64_t values_view_base_units,
    unsigned values_view_offset_units,
    unsigned values_view_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    unsigned range_enabled,
    uint64_t range_min,
    uint64_t range_max,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_predicate_concatenate`

two TAND assemble blocks, not one opcode

```c
void __builtin_predicate_concatenate(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_left left,
    unsigned left_space,
    unsigned left_dtype,
    unsigned left_capacity_code,
    unsigned left_view_enabled,
    int64_t left_view_base_units,
    unsigned left_view_offset_units,
    unsigned left_view_size_code,
    T_right right,
    unsigned right_space,
    unsigned right_dtype,
    unsigned right_capacity_code,
    unsigned right_view_enabled,
    int64_t right_view_base_units,
    unsigned right_view_offset_units,
    unsigned right_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_predicate_logical_numeric`

U8 logical numeric

```c
void __builtin_predicate_logical_numeric(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    T_numeric numeric,
    unsigned numeric_space,
    unsigned numeric_dtype,
    unsigned numeric_capacity_code,
    unsigned numeric_view_enabled,
    int64_t numeric_view_base_units,
    unsigned numeric_view_offset_units,
    unsigned numeric_view_size_code,
    unsigned logical_opcode,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_predicate_subview`

predicate materialization via TMOV plus SUBVIEW

```c
void __builtin_predicate_subview(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tabs`

TEPL unary

```c
void __builtin_tabs(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tadd`

TEPL binary

```c
void __builtin_tadd(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tadds`

TEPL scalar

```c
void __builtin_tadds(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tand`

TEPL binary

```c
void __builtin_tand(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tands`

TEPL scalar

```c
void __builtin_tands(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tci`

iota 1D

```c
void __builtin_tci(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    uint64_t start_bits,
    unsigned descending,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tci_2d`

iota 2D

```c
void __builtin_tci_2d(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    uint64_t start_bits,
    uint64_t packed_row_col_steps,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcmp`

compare

```c
void __builtin_tcmp(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    unsigned cmp_mode,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcmps`

compare scalar

```c
void __builtin_tcmps(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    unsigned cmp_mode,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolargmax`

reduce: source geometry

```c
void __builtin_tcolargmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolargmin`

reduce: source geometry

```c
void __builtin_tcolargmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpand`

expand: output geometry

```c
void __builtin_tcolexpand(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandadd`

expand binary: output geometry

```c
void __builtin_tcolexpandadd(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpanddiv`

expand binary: output geometry

```c
void __builtin_tcolexpanddiv(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandexpdif`

expand binary: output geometry

```c
void __builtin_tcolexpandexpdif(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandmax`

expand binary: output geometry

```c
void __builtin_tcolexpandmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandmin`

expand binary: output geometry

```c
void __builtin_tcolexpandmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandmul`

expand binary: output geometry

```c
void __builtin_tcolexpandmul(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolexpandsub`

expand binary: output geometry

```c
void __builtin_tcolexpandsub(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolmax`

reduce: source geometry

```c
void __builtin_tcolmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolmin`

reduce: source geometry

```c
void __builtin_tcolmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolprod`

reduce: source geometry

```c
void __builtin_tcolprod(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcolsum`

reduce: source geometry

```c
void __builtin_tcolsum(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tcvt`

convert

```c
void __builtin_tcvt(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned rounding_mode,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tdiv`

TEPL binary

```c
void __builtin_tdiv(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tdivs`

TEPL scalar

```c
void __builtin_tdivs(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_texp`

TEPL unary

```c
void __builtin_texp(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_texpands`

splat

```c
void __builtin_texpands(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_texpdif`

TEPL binary

```c
void __builtin_texpdif(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tfma`

fma

```c
void __builtin_tfma(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_c c,
    unsigned c_space,
    unsigned c_dtype,
    unsigned c_capacity_code,
    unsigned c_view_enabled,
    int64_t c_view_base_units,
    unsigned c_view_offset_units,
    unsigned c_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tgather`

local index: indices geometry

```c
void __builtin_tgather(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tgemv`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgemv_acc`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv_acc(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_accum accum,
    unsigned accum_space,
    unsigned accum_dtype,
    unsigned accum_capacity_code,
    unsigned accum_view_enabled,
    int64_t accum_view_base_units,
    unsigned accum_view_offset_units,
    unsigned accum_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgemv_bias`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv_bias(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_bias bias,
    unsigned bias_space,
    unsigned bias_dtype,
    unsigned bias_capacity_code,
    unsigned bias_view_enabled,
    int64_t bias_view_base_units,
    unsigned bias_view_offset_units,
    unsigned bias_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgemv_mx`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv_mx(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgemv_mx_acc`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv_mx_acc(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_accum accum,
    unsigned accum_space,
    unsigned accum_dtype,
    unsigned accum_capacity_code,
    unsigned accum_view_enabled,
    int64_t accum_view_base_units,
    unsigned accum_view_offset_units,
    unsigned accum_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgemv_mx_bias`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tgemv_mx_bias(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_bias bias,
    unsigned bias_space,
    unsigned bias_dtype,
    unsigned bias_capacity_code,
    unsigned bias_view_enabled,
    int64_t bias_view_base_units,
    unsigned bias_view_offset_units,
    unsigned bias_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tgpr2t`

gpr to tile

```c
void __builtin_tgpr2t(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    uint64_t gpr0,
    uint64_t gpr1,
    uint64_t gpr2,
    uint64_t gpr3,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_timg2col`

image to column

```c
void __builtin_timg2col(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    uint64_t param0,
    uint64_t param1,
    uint64_t param2,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_timg2col_spart`

image to column

```c
void __builtin_timg2col_spart(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    uint64_t param0,
    uint64_t param1,
    uint64_t param2,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_timg2col_spart_slot`

fixed shared slot image

```c
void __builtin_timg2col_spart_slot(
    unsigned slot,
    unsigned size_code,
    const void *base,
    uint64_t param0,
    uint64_t param1,
    uint64_t param2,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tload`

load

```c
void __builtin_tload(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload2_dn2zn`

multi-output load (one block)

```c
void __builtin_tload2_dn2zn(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload2_nd2nz`

multi-output load (one block)

```c
void __builtin_tload2_nd2nz(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload2_nd2zn`

multi-output load (one block)

```c
void __builtin_tload2_nd2zn(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload4_dn2zn`

multi-output load (one block)

```c
void __builtin_tload4_dn2zn(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    T_d2 *d2,
    unsigned d2_space,
    unsigned d2_capacity_code,
    T_d3 *d3,
    unsigned d3_space,
    unsigned d3_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload4_nd2nz`

multi-output load (one block)

```c
void __builtin_tload4_nd2nz(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    T_d2 *d2,
    unsigned d2_space,
    unsigned d2_capacity_code,
    T_d3 *d3,
    unsigned d3_space,
    unsigned d3_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload4_nd2zn`

multi-output load (one block)

```c
void __builtin_tload4_nd2zn(
    T_d0 *d0,
    unsigned d0_space,
    unsigned d0_capacity_code,
    T_d1 *d1,
    unsigned d1_space,
    unsigned d1_capacity_code,
    T_d2 *d2,
    unsigned d2_space,
    unsigned d2_capacity_code,
    T_d3 *d3,
    unsigned d3_space,
    unsigned d3_capacity_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload_cube`

load

```c
void __builtin_tload_cube(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload_slot`

fixed shared slot weight load

```c
void __builtin_tload_slot(
    unsigned slot,
    unsigned size_code,
    const void *base,
    uint64_t shape_word,
    uint64_t start_word,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tload_weight`

weight load

```c
void __builtin_tload_weight(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    const void *base,
    uint64_t shape_word,
    uint64_t start_word,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tlog`

TEPL unary

```c
void __builtin_tlog(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmatmul`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_acc`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul_acc(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_accum accum,
    unsigned accum_space,
    unsigned accum_dtype,
    unsigned accum_capacity_code,
    unsigned accum_view_enabled,
    int64_t accum_view_base_units,
    unsigned accum_view_offset_units,
    unsigned accum_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_bias`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul_bias(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_bias bias,
    unsigned bias_space,
    unsigned bias_dtype,
    unsigned bias_capacity_code,
    unsigned bias_view_enabled,
    int64_t bias_view_base_units,
    unsigned bias_view_offset_units,
    unsigned bias_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_mx`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul_mx(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_mx_acc`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul_mx_acc(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_accum accum,
    unsigned accum_space,
    unsigned accum_dtype,
    unsigned accum_capacity_code,
    unsigned accum_view_enabled,
    int64_t accum_view_base_units,
    unsigned accum_view_offset_units,
    unsigned accum_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_mx_bias`

CUBE with explicit FPATR extra operands/results

```c
void __builtin_tmatmul_mx_bias(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_bias bias,
    unsigned bias_space,
    unsigned bias_dtype,
    unsigned bias_capacity_code,
    unsigned bias_view_enabled,
    int64_t bias_view_base_units,
    unsigned bias_view_offset_units,
    unsigned bias_view_size_code,
    unsigned scale_mask,
    T_scale_a scale_a,
    unsigned scale_a_space,
    unsigned scale_a_dtype,
    unsigned scale_a_capacity_code,
    unsigned scale_a_view_enabled,
    int64_t scale_a_view_base_units,
    unsigned scale_a_view_offset_units,
    unsigned scale_a_view_size_code,
    T_scale_b scale_b,
    unsigned scale_b_space,
    unsigned scale_b_dtype,
    unsigned scale_b_capacity_code,
    unsigned scale_b_view_enabled,
    int64_t scale_b_view_base_units,
    unsigned scale_b_view_offset_units,
    unsigned scale_b_view_size_code,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmatmul_slot`

fixed shared input slots; not assemble

```c
void __builtin_tmatmul_slot(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    unsigned slot_a,
    unsigned slot_b,
    unsigned a_dtype,
    unsigned b_dtype,
    int64_t m,
    int64_t n,
    int64_t k,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned pre_quant,
    unsigned relu,
    unsigned group_n_code,
    unsigned row_max_enable,
    unsigned group_max_enable,
    unsigned row_max_init,
    unsigned max_abs_enable,
    unsigned transpose_a,
    unsigned transpose_b,
    unsigned cscale_enable,
    unsigned cube_control,
    uint64_t quant_descriptor,
    uint64_t lrelu_descriptor,
    T_quant quant,
    unsigned quant_space,
    unsigned quant_dtype,
    unsigned quant_capacity_code,
    unsigned quant_view_enabled,
    int64_t quant_view_base_units,
    unsigned quant_view_offset_units,
    unsigned quant_view_size_code,
    T_relu_parameter relu_parameter,
    unsigned relu_parameter_space,
    unsigned relu_parameter_dtype,
    unsigned relu_parameter_capacity_code,
    unsigned relu_parameter_view_enabled,
    int64_t relu_parameter_view_base_units,
    unsigned relu_parameter_view_offset_units,
    unsigned relu_parameter_view_size_code,
    T_row_max_in row_max_in,
    unsigned row_max_in_space,
    unsigned row_max_in_dtype,
    unsigned row_max_in_capacity_code,
    unsigned row_max_in_view_enabled,
    int64_t row_max_in_view_base_units,
    unsigned row_max_in_view_offset_units,
    unsigned row_max_in_view_size_code,
    T_cscale cscale,
    unsigned cscale_space,
    unsigned cscale_dtype,
    unsigned cscale_capacity_code,
    unsigned cscale_view_enabled,
    int64_t cscale_view_base_units,
    unsigned cscale_view_offset_units,
    unsigned cscale_view_size_code,
    T_row_max_out *row_max_out,
    unsigned row_max_out_space,
    unsigned row_max_out_capacity_code,
    T_group_max_out *group_max_out,
    unsigned group_max_out_space,
    unsigned group_max_out_capacity_code);
```

### `__builtin_tmax`

TEPL binary

```c
void __builtin_tmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmaxs`

TEPL scalar

```c
void __builtin_tmaxs(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmin`

TEPL binary

```c
void __builtin_tmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmins`

TEPL scalar

```c
void __builtin_tmins(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov`

move; per-op Local/Shared constraints

```c
void __builtin_tmov(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_cube_to_shared_nd`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_cube_to_shared_nd(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_l2s_insert`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_l2s_insert(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_l2s_publish`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_l2s_publish(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_s2l_broadcast`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_s2l_broadcast(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_s2l_extract`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_s2l_extract(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmov_shared_nd_to_cube`

move; per-op Local/Shared constraints

```c
void __builtin_tmov_shared_nd_to_cube(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmul`

TEPL binary

```c
void __builtin_tmul(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tmuls`

TEPL scalar

```c
void __builtin_tmuls(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tneg`

TEPL unary

```c
void __builtin_tneg(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tnot`

TEPL unary

```c
void __builtin_tnot(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tor`

TEPL binary

```c
void __builtin_tor(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tors`

TEPL scalar

```c
void __builtin_tors(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tpack`

pack

```c
void __builtin_tpack(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    uint64_t control,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tpermute`

permute

```c
void __builtin_tpermute(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tprefetch`

prefetch

```c
void __builtin_tprefetch(
    const void *base,
    int64_t stride_bytes,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trecip`

TEPL unary

```c
void __builtin_trecip(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trelu`

TEPL unary

```c
void __builtin_trelu(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trem`

TEPL binary

```c
void __builtin_trem(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trems`

TEPL scalar

```c
void __builtin_trems(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowargmax`

reduce: source geometry

```c
void __builtin_trowargmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowargmin`

reduce: source geometry

```c
void __builtin_trowargmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpand`

expand: output geometry

```c
void __builtin_trowexpand(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandadd`

expand binary: output geometry

```c
void __builtin_trowexpandadd(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpanddiv`

expand binary: output geometry

```c
void __builtin_trowexpanddiv(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandexpdif`

expand binary: output geometry

```c
void __builtin_trowexpandexpdif(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandmax`

expand binary: output geometry

```c
void __builtin_trowexpandmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandmin`

expand binary: output geometry

```c
void __builtin_trowexpandmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandmul`

expand binary: output geometry

```c
void __builtin_trowexpandmul(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowexpandsub`

expand binary: output geometry

```c
void __builtin_trowexpandsub(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowmax`

reduce: source geometry

```c
void __builtin_trowmax(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowmin`

reduce: source geometry

```c
void __builtin_trowmin(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowprod`

reduce: source geometry

```c
void __builtin_trowprod(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trowsum`

reduce: source geometry

```c
void __builtin_trowsum(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_trsqrt`

TEPL unary

```c
void __builtin_trsqrt(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tscatter`

local index: indices geometry

```c
void __builtin_tscatter(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    T_indices indices,
    unsigned indices_space,
    unsigned indices_dtype,
    unsigned indices_capacity_code,
    unsigned indices_view_enabled,
    int64_t indices_view_base_units,
    unsigned indices_view_offset_units,
    unsigned indices_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tsel`

select: false_value is old dst in PTO wrapper

```c
void __builtin_tsel(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    T_true_value true_value,
    unsigned true_value_space,
    unsigned true_value_dtype,
    unsigned true_value_capacity_code,
    unsigned true_value_view_enabled,
    int64_t true_value_view_base_units,
    unsigned true_value_view_offset_units,
    unsigned true_value_view_size_code,
    T_false_value false_value,
    unsigned false_value_space,
    unsigned false_value_dtype,
    unsigned false_value_capacity_code,
    unsigned false_value_view_enabled,
    int64_t false_value_view_base_units,
    unsigned false_value_view_offset_units,
    unsigned false_value_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tsels`

select scalar

```c
void __builtin_tsels(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    T_true_value true_value,
    unsigned true_value_space,
    unsigned true_value_dtype,
    unsigned true_value_capacity_code,
    unsigned true_value_view_enabled,
    int64_t true_value_view_base_units,
    unsigned true_value_view_offset_units,
    unsigned true_value_view_size_code,
    uint64_t false_scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tshl`

TEPL binary

```c
void __builtin_tshl(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tshls`

TEPL scalar

```c
void __builtin_tshls(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tshr`

TEPL binary

```c
void __builtin_tshr(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tshrs`

TEPL scalar

```c
void __builtin_tshrs(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tshuf`

shuffle

```c
void __builtin_tshuf(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    T_controls controls,
    unsigned controls_space,
    unsigned controls_dtype,
    unsigned controls_capacity_code,
    unsigned controls_view_enabled,
    int64_t controls_view_base_units,
    unsigned controls_view_offset_units,
    unsigned controls_view_size_code,
    uint64_t control,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tsqrt`

TEPL unary

```c
void __builtin_tsqrt(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore`

store

```c
void __builtin_tstore(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tstore2_dn2dn`

two-source store

```c
void __builtin_tstore2_dn2dn(
    void *base,
    int64_t stride_bytes,
    T_src0 src0,
    unsigned src0_space,
    unsigned src0_dtype,
    unsigned src0_capacity_code,
    unsigned src0_view_enabled,
    int64_t src0_view_base_units,
    unsigned src0_view_offset_units,
    unsigned src0_view_size_code,
    T_src1 src1,
    unsigned src1_space,
    unsigned src1_dtype,
    unsigned src1_capacity_code,
    unsigned src1_view_enabled,
    int64_t src1_view_base_units,
    unsigned src1_view_offset_units,
    unsigned src1_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tstore_atomic_add`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_add(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_and`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_and(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_dec`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_dec(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_inc`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_inc(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_max`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_max(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_min`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_min(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_or`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_or(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_atomic_xor`

atomic store Local/Shared; predicated Local only

```c
void __builtin_tstore_atomic_xor(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    unsigned predicate_enabled,
    T_predicate predicate,
    unsigned predicate_space,
    unsigned predicate_dtype,
    unsigned predicate_capacity_code,
    unsigned predicate_view_enabled,
    int64_t predicate_view_base_units,
    unsigned predicate_view_offset_units,
    unsigned predicate_view_size_code,
    unsigned predicate_invert,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tstore_cube`

store

```c
void __builtin_tstore_cube(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tstore_part`

store

```c
void __builtin_tstore_part(
    void *base,
    int64_t stride_bytes,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask,
    unsigned memory_dtype);
```

### `__builtin_tsub`

TEPL binary

```c
void __builtin_tsub(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tsubs`

TEPL scalar

```c
void __builtin_tsubs(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_ttri`

triangle

```c
void __builtin_ttri(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_tunpack`

unpack

```c
void __builtin_tunpack(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t control,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_txor`

TEPL binary

```c
void __builtin_txor(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_a a,
    unsigned a_space,
    unsigned a_dtype,
    unsigned a_capacity_code,
    unsigned a_view_enabled,
    int64_t a_view_base_units,
    unsigned a_view_offset_units,
    unsigned a_view_size_code,
    T_b b,
    unsigned b_space,
    unsigned b_dtype,
    unsigned b_capacity_code,
    unsigned b_view_enabled,
    int64_t b_view_base_units,
    unsigned b_view_offset_units,
    unsigned b_view_size_code,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

### `__builtin_txors`

TEPL scalar

```c
void __builtin_txors(
    T_dst *dst,
    unsigned dst_space,
    unsigned capacity_code,
    unsigned assemble_phase,
    int64_t dst_base_units,
    unsigned dst_offset_units,
    unsigned writer_size_code,
    T_src src,
    unsigned src_space,
    unsigned src_dtype,
    unsigned src_capacity_code,
    unsigned src_view_enabled,
    int64_t src_view_base_units,
    unsigned src_view_offset_units,
    unsigned src_view_size_code,
    uint64_t scalar_bits,
    int64_t lb0,
    int64_t lb1,
    int64_t lb2,
    unsigned operation_dtype,
    unsigned layout,
    unsigned pad,
    unsigned pe_mask);
```

