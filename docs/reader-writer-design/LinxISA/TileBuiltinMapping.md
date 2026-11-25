# PTO-C 名称逐项映射

来源 commit：`5f764847b707fabf998c93fb4725787bcd2d6417`。共 247 个 template_asm.hpp 公开/宏生成候选名称，
包含退役诊断和别名，**不是 247 条独立 ISA 指令**。
下表为名称覆盖检查，不代表所有重载参数和合法组合已通过编译验证。

| PTO-C 名称 | builtin | 处理 | 源码 |
| --- | --- | --- | --- |
| `ACCCVT` | — | 退役诊断，不定义 builtin | [L6274](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L6274) |
| `ACCCVT_RMAX_SCALE_NZ2DN` | — | 退役诊断，不定义 builtin | [L231](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L231) |
| `ACCSCALE_NZ2DN` | — | 退役诊断，不定义 builtin | [L222](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L222) |
| `ACCSCALE_T` | — | 退役诊断，不定义 builtin | [L214](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L214) |
| `GMOV` | `__builtin_gmov` | 参数映射 | [L5865](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5865) |
| `MGATHER` | `__builtin_mgather` | 参数映射 | [L980](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L980) |
| `MGATHER_ADD` | `__builtin_mgather_add` | 参数映射 | [L5303](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5303) |
| `MGATHER_AND` | `__builtin_mgather_and` | 参数映射 | [L5310](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5310) |
| `MGATHER_CAS` | `__builtin_mgather_cas` | 参数映射 | [L4940](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4940) |
| `MGATHER_DEC` | `__builtin_mgather_dec` | 参数映射 | [L5308](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5308) |
| `MGATHER_EXCH` | `__builtin_mgather_exch` | 参数映射 | [L5294](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5294) |
| `MGATHER_INC` | `__builtin_mgather_inc` | 参数映射 | [L5306](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5306) |
| `MGATHER_MASK` | `__builtin_mgather_mask` | 参数映射 | [L1154](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L1154) |
| `MGATHER_MAX` | `__builtin_mgather_max` | 参数映射 | [L5297](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5297) |
| `MGATHER_MIN` | `__builtin_mgather_min` | 参数映射 | [L5300](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5300) |
| `MGATHER_OR` | `__builtin_mgather_or` | 参数映射 | [L5313](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5313) |
| `MGATHER_XOR` | `__builtin_mgather_xor` | 参数映射 | [L5315](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5315) |
| `MSCATTER` | `__builtin_mscatter` | 参数映射 | [L1070](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L1070) |
| `MSCATTER_ADD` | `__builtin_mscatter_add` | 参数映射 | [L5418](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5418) |
| `MSCATTER_AND` | `__builtin_mscatter_and` | 参数映射 | [L5426](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5426) |
| `MSCATTER_DEC` | `__builtin_mscatter_dec` | 参数映射 | [L5424](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5424) |
| `MSCATTER_INC` | `__builtin_mscatter_inc` | 参数映射 | [L5422](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5422) |
| `MSCATTER_MASK` | `__builtin_mscatter_mask` | 参数映射 | [L1256](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L1256) |
| `MSCATTER_MAX` | `__builtin_mscatter_max` | 参数映射 | [L5410](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5410) |
| `MSCATTER_MIN` | `__builtin_mscatter_min` | 参数映射 | [L5414](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5414) |
| `MSCATTER_OR` | `__builtin_mscatter_or` | 参数映射 | [L5429](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5429) |
| `MSCATTER_POPC` | `__builtin_mscatter_popc` | 参数映射 | [L5705](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5705) |
| `MSCATTER_XOR` | `__builtin_mscatter_xor` | 参数映射 | [L5432](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5432) |
| `TABS` | `__builtin_tabs` | 参数映射 | [L14284](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14284) |
| `TABS_ASS` | `__builtin_tabs` | ASS 阶段参数 | [L21974](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21974) |
| `TADD` | `__builtin_tadd` | 参数映射 | [L12584](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12584) |
| `TADDC` | — | 退役诊断，不定义 builtin | [L14999](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14999) |
| `TADDS` | `__builtin_tadds` | 参数映射 | [L15025](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15025) |
| `TADDSC` | — | 退役诊断，不定义 builtin | [L16930](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16930) |
| `TADDS_ASS` | `__builtin_tadds` | ASS 阶段参数 | [L21982](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21982) |
| `TADD_ASS` | `__builtin_tadd` | ASS 阶段参数 | [L21956](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21956) |
| `TAND` | `__builtin_tand` | 参数映射 | [L13074](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13074) |
| `TANDS` | `__builtin_tands` | 参数映射 | [L15501](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15501) |
| `TANDS_ASS` | `__builtin_tands` | ASS 阶段参数 | [L21987](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21987) |
| `TAND_ASS` | `__builtin_tand` | ASS 阶段参数 | [L21961](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21961) |
| `TAXPY` | — | 退役诊断，不定义 builtin | [L16922](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16922) |
| `TCI` | `__builtin_tci` | 参数映射 | [L17689](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17689) |
| `TCI_2D` | `__builtin_tci_2d` | 参数映射 | [L17751](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17751) |
| `TCI_COL` | `__builtin_tci_2d` | 别名；ROW=(1,0)，COL=(0,1) | [L17807](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17807) |
| `TCI_ROW` | `__builtin_tci_2d` | 别名；ROW=(1,0)，COL=(0,1) | [L17802](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17802) |
| `TCMP` | `__builtin_tcmp` | 参数映射 | [L13668](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13668) |
| `TCMPS` | `__builtin_tcmps` | 参数映射 | [L16334](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16334) |
| `TCMPS_ASS` | `__builtin_tcmps` | ASS 阶段参数 | [L22396](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22396) |
| `TCMP_ASS` | `__builtin_tcmp` | ASS 阶段参数 | [L22388](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22388) |
| `TCOLARGMAX` | `__builtin_tcolargmax` | 参数映射 | [L19239](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19239) |
| `TCOLARGMIN` | `__builtin_tcolargmin` | 参数映射 | [L19327](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19327) |
| `TCOLEXPAND` | `__builtin_tcolexpand` | 参数映射 | [L19157](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19157) |
| `TCOLEXPANDADD` | `__builtin_tcolexpandadd` | 参数映射 | [L20398](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20398) |
| `TCOLEXPANDADD_ASS` | `__builtin_tcolexpandadd` | ASS 阶段参数 | [L22378](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22378) |
| `TCOLEXPANDDIV` | `__builtin_tcolexpanddiv` | 参数映射 | [L20767](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20767) |
| `TCOLEXPANDDIV_ASS` | `__builtin_tcolexpanddiv` | ASS 阶段参数 | [L22381](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22381) |
| `TCOLEXPANDEXPDIF` | `__builtin_tcolexpandexpdif` | 参数映射 | [L21136](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21136) |
| `TCOLEXPANDEXPDIF_ASS` | `__builtin_tcolexpandexpdif` | ASS 阶段参数 | [L22384](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22384) |
| `TCOLEXPANDMAX` | `__builtin_tcolexpandmax` | 参数映射 | [L20890](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20890) |
| `TCOLEXPANDMAX_ASS` | `__builtin_tcolexpandmax` | ASS 阶段参数 | [L22382](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22382) |
| `TCOLEXPANDMIN` | `__builtin_tcolexpandmin` | 参数映射 | [L21013](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21013) |
| `TCOLEXPANDMIN_ASS` | `__builtin_tcolexpandmin` | ASS 阶段参数 | [L22383](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22383) |
| `TCOLEXPANDMUL` | `__builtin_tcolexpandmul` | 参数映射 | [L20644](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20644) |
| `TCOLEXPANDMUL_ASS` | `__builtin_tcolexpandmul` | ASS 阶段参数 | [L22380](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22380) |
| `TCOLEXPANDSUB` | `__builtin_tcolexpandsub` | 参数映射 | [L20521](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20521) |
| `TCOLEXPANDSUB_ASS` | `__builtin_tcolexpandsub` | ASS 阶段参数 | [L22379](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22379) |
| `TCOLEXPAND_ASS` | `__builtin_tcolexpand` | ASS 阶段参数 | [L22369](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22369) |
| `TCOLMAX` | `__builtin_tcolmax` | 参数映射 | [L18893](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18893) |
| `TCOLMAX_ASS` | `__builtin_tcolmax` | ASS 阶段参数 | [L22364](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22364) |
| `TCOLMIN` | `__builtin_tcolmin` | 参数映射 | [L18981](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18981) |
| `TCOLMIN_ASS` | `__builtin_tcolmin` | ASS 阶段参数 | [L22365](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22365) |
| `TCOLPROD` | `__builtin_tcolprod` | 参数映射 | [L19069](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19069) |
| `TCOLPROD_ASS` | `__builtin_tcolprod` | ASS 阶段参数 | [L22366](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22366) |
| `TCOLSUM` | `__builtin_tcolsum` | 参数映射 | [L18801](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18801) |
| `TCOLSUM_ASS` | `__builtin_tcolsum` | ASS 阶段参数 | [L22363](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22363) |
| `TCONCAT` | — | 退役诊断，不定义 builtin | [L21263](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21263) |
| `TCONCAT_ASS` | — | 冲突：普通 selector 退役，但 ASS 宏仍存在；待 ISA 核对 | [L22385](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22385) |
| `TCVT` | `__builtin_tcvt` | 参数映射 | [L15017](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15017) |
| `TCVT_ASS` | `__builtin_tcvt` | ASS 阶段参数 | [L22337](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22337) |
| `TCVT_T` | `__builtin_tcvt` | 参数映射 | [L247](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L247) |
| `TDEQUANT` | — | 退役诊断，不定义 builtin | [L17901](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17901) |
| `TDIV` | `__builtin_tdiv` | 参数映射 | [L12904](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12904) |
| `TDIVS` | `__builtin_tdivs` | 参数映射 | [L15297](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15297) |
| `TDIVS_ASS` | `__builtin_tdivs` | ASS 阶段参数 | [L21985](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21985) |
| `TDIV_ASS` | `__builtin_tdiv` | ASS 阶段参数 | [L21959](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21959) |
| `TEXP` | `__builtin_texp` | 参数映射 | [L14514](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14514) |
| `TEXPANDS` | `__builtin_texpands` | 参数映射 | [L17027](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17027) |
| `TEXPDIF` | `__builtin_texpdif` | 参数映射 | [L14589](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14589) |
| `TEXP_ASS` | `__builtin_texp` | ASS 阶段参数 | [L21977](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21977) |
| `TEXTRACT` | — | 退役诊断，不定义 builtin | [L17314](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17314) |
| `TFILLPAD` | — | 退役诊断，不定义 builtin | [L17681](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17681) |
| `TFMA` | `__builtin_tfma` | 参数映射 | [L17124](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17124) |
| `TFMA_ASS` | `__builtin_tfma` | ASS 阶段参数 | [L22336](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22336) |
| `TFMOD` | — | 退役诊断，不定义 builtin | [L13066](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13066) |
| `TFMODS` | — | 退役诊断，不定义 builtin | [L15493](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15493) |
| `TGATHER` | `__builtin_tgather` | 参数映射 | [L17968](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17968) |
| `TGATHERB` | — | 退役诊断，不定义 builtin | [L21705](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21705) |
| `TGEMV` | `__builtin_tgemv` | 参数映射 | [L11765](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11765) |
| `TGEMV_ACC` | `__builtin_tgemv_acc` | 参数映射 | [L11858](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11858) |
| `TGEMV_BIAS` | `__builtin_tgemv_bias` | 参数映射 | [L11851](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11851) |
| `TGEMV_MX` | `__builtin_tgemv_mx` | 参数映射 | [L12032](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12032) |
| `TGEMV_MX_ACC` | `__builtin_tgemv_mx_acc` | 参数映射 | [L12205](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12205) |
| `TGEMV_MX_BIAS` | `__builtin_tgemv_mx_bias` | 参数映射 | [L12117](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12117) |
| `TGPR2T` | `__builtin_tgpr2t` | 参数映射 | [L21680](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21680) |
| `THISTOGRAM` | — | 退役诊断，不定义 builtin | [L615](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L615) |
| `TIMG2COL` | `__builtin_timg2col` | 参数映射 | [L17336](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17336) |
| `TIMG2COL_SPART` | `__builtin_timg2col_spart` | 参数映射 | [L17572](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17572) |
| `TIMG2COL_SPART_SLOT` | `__builtin_timg2col_spart_slot` | 参数映射 | [L17631](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17631) |
| `TINSERT` | — | 退役诊断，不定义 builtin | [L17323](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17323) |
| `TLOAD` | `__builtin_tload` | 参数映射 | [L2928](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L2928) |
| `TLOAD2_DN2ZN` | `__builtin_tload2_dn2zn` | 参数映射 | [L780](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L780) |
| `TLOAD2_ND2NZ` | `__builtin_tload2_nd2nz` | 参数映射 | [L624](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L624) |
| `TLOAD2_ND2ZN` | `__builtin_tload2_nd2zn` | 参数映射 | [L702](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L702) |
| `TLOAD4_DN2ZN` | `__builtin_tload4_dn2zn` | 参数映射 | [L923](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L923) |
| `TLOAD4_ND2NZ` | `__builtin_tload4_nd2nz` | 参数映射 | [L873](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L873) |
| `TLOAD4_ND2ZN` | `__builtin_tload4_nd2zn` | 参数映射 | [L898](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L898) |
| `TLOAD_ASS` | `__builtin_tload` | ASS 阶段参数 | [L3171](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L3171) |
| `TLOAD_CUBE` | `__builtin_tload_cube` | 参数映射 | [L3877](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L3877) |
| `TLOAD_CUBE_ASS` | `__builtin_tload_cube` | ASS 阶段参数 | [L3623](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L3623) |
| `TLOAD_SLOT` | `__builtin_tload_slot` | 参数映射 | [L3501](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L3501) |
| `TLOG` | `__builtin_tlog` | 参数映射 | [L14628](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14628) |
| `TLOG_ASS` | `__builtin_tlog` | ASS 阶段参数 | [L21978](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21978) |
| `TLRELU` | — | 退役诊断，不定义 builtin | [L16914](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16914) |
| `TMATMUL` | `__builtin_tmatmul` | 参数映射 | [L10228](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L10228) |
| `TMATMUL_ACC` | `__builtin_tmatmul_acc` | 参数映射 | [L10287](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L10287) |
| `TMATMUL_BIAS` | `__builtin_tmatmul_bias` | 参数映射 | [L10887](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L10887) |
| `TMATMUL_MX` | `__builtin_tmatmul_mx` | 参数映射 | [L11060](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11060) |
| `TMATMUL_MX_ACC` | `__builtin_tmatmul_mx_acc` | 参数映射 | [L11234](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11234) |
| `TMATMUL_MX_BIAS` | `__builtin_tmatmul_mx_bias` | 参数映射 | [L11431](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L11431) |
| `TMATMUL_SLOT` | `__builtin_tmatmul_slot` | 参数映射 | [L10177](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L10177) |
| `TMAX` | `__builtin_tmax` | 参数映射 | [L13494](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13494) |
| `TMAXS` | `__builtin_tmaxs` | 参数映射 | [L15991](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15991) |
| `TMAXS_ASS` | `__builtin_tmaxs` | ASS 阶段参数 | [L21992](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21992) |
| `TMAX_ASS` | `__builtin_tmax` | ASS 阶段参数 | [L21966](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21966) |
| `TMIN` | `__builtin_tmin` | 参数映射 | [L13578](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13578) |
| `TMINS` | `__builtin_tmins` | 参数映射 | [L16089](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16089) |
| `TMINS_ASS` | `__builtin_tmins` | ASS 阶段参数 | [L21993](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21993) |
| `TMIN_ASS` | `__builtin_tmin` | ASS 阶段参数 | [L21967](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21967) |
| `TMOV` | `__builtin_tmov` | 参数映射 | [L505](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L505) |
| `TMOV_CUBE_TO_SHARED_ND` | `__builtin_tmov_cube_to_shared_nd` | 参数映射 | [L5990](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5990) |
| `TMOV_L2S_INSERT` | `__builtin_tmov_l2s_insert` | 参数映射 | [L5922](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5922) |
| `TMOV_L2S_PUBLISH` | `__builtin_tmov_l2s_publish` | 参数映射 | [L5953](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L5953) |
| `TMOV_S2L_BROADCAST` | `__builtin_tmov_s2l_broadcast` | 参数映射 | [L6231](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L6231) |
| `TMOV_S2L_EXTRACT` | `__builtin_tmov_s2l_extract` | 参数映射 | [L6252](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L6252) |
| `TMOV_SHARED_ND_TO_CUBE` | `__builtin_tmov_shared_nd_to_cube` | 参数映射 | [L6159](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L6159) |
| `TMRGSORT` | — | 退役诊断，不定义 builtin | [L17949](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17949) |
| `TMUL` | `__builtin_tmul` | 参数映射 | [L12805](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12805) |
| `TMULS` | `__builtin_tmuls` | 参数映射 | [L15210](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15210) |
| `TMULS_ASS` | `__builtin_tmuls` | ASS 阶段参数 | [L21984](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21984) |
| `TMUL_ASS` | `__builtin_tmul` | ASS 阶段参数 | [L21958](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21958) |
| `TNEG` | `__builtin_tneg` | 参数映射 | [L14440](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14440) |
| `TNEG_ASS` | `__builtin_tneg` | ASS 阶段参数 | [L21976](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21976) |
| `TNOT` | `__builtin_tnot` | 参数映射 | [L14366](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14366) |
| `TNOT_ASS` | `__builtin_tnot` | ASS 阶段参数 | [L21975](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21975) |
| `TOR` | `__builtin_tor` | 参数映射 | [L13158](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13158) |
| `TORS` | `__builtin_tors` | 参数映射 | [L15599](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15599) |
| `TORS_ASS` | `__builtin_tors` | ASS 阶段参数 | [L21988](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21988) |
| `TOR_ASS` | `__builtin_tor` | ASS 阶段参数 | [L21962](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21962) |
| `TPACK` | `__builtin_tpack` | 参数映射 | [L21634](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21634) |
| `TPACK_ASS` | `__builtin_tpack` | ASS 阶段参数 | [L21640](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21640) |
| `TPARTADD` | — | 退役诊断，不定义 builtin | [L18108](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18108) |
| `TPARTMAX` | — | 退役诊断，不定义 builtin | [L18124](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18124) |
| `TPARTMIN` | — | 退役诊断，不定义 builtin | [L18132](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18132) |
| `TPARTMUL` | — | 退役诊断，不定义 builtin | [L18116](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18116) |
| `TPERMUTE` | `__builtin_tpermute` | 参数映射 | [L21272](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21272) |
| `TPREFETCH` | `__builtin_tprefetch` | 参数映射 | [L4894](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4894) |
| `TPRELU` | — | 退役诊断，不定义 builtin | [L14161](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14161) |
| `TQUANT` | — | 退役诊断，不定义 builtin | [L17889](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17889) |
| `TRANDOM` | — | 退役诊断，不定义 builtin | [L17875](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17875) |
| `TRECIP` | `__builtin_trecip` | 参数映射 | [L14702](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14702) |
| `TRECIP_ASS` | `__builtin_trecip` | ASS 阶段参数 | [L21979](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21979) |
| `TRELU` | `__builtin_trelu` | 参数映射 | [L14925](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14925) |
| `TRELU_ASS` | `__builtin_trelu` | ASS 阶段参数 | [L22340](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22340) |
| `TREM` | `__builtin_trem` | 参数映射 | [L12988](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12988) |
| `TREMS` | `__builtin_trems` | 参数映射 | [L15395](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15395) |
| `TREMS_ASS` | `__builtin_trems` | ASS 阶段参数 | [L21986](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21986) |
| `TREM_ASS` | `__builtin_trem` | ASS 阶段参数 | [L21960](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21960) |
| `TROWARGMAX` | `__builtin_trowargmax` | 参数映射 | [L18635](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18635) |
| `TROWARGMIN` | `__builtin_trowargmin` | 参数映射 | [L18718](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18718) |
| `TROWEXPAND` | `__builtin_trowexpand` | 参数映射 | [L18547](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18547) |
| `TROWEXPANDADD` | `__builtin_trowexpandadd` | 参数映射 | [L19419](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19419) |
| `TROWEXPANDADD_ASS` | `__builtin_trowexpandadd` | ASS 阶段参数 | [L22371](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22371) |
| `TROWEXPANDDIV` | `__builtin_trowexpanddiv` | 参数映射 | [L19813](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19813) |
| `TROWEXPANDDIV_ASS` | `__builtin_trowexpanddiv` | ASS 阶段参数 | [L22374](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22374) |
| `TROWEXPANDEXPDIF` | `__builtin_trowexpandexpdif` | 参数映射 | [L20203](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20203) |
| `TROWEXPANDEXPDIF_ASS` | `__builtin_trowexpandexpdif` | ASS 阶段参数 | [L22377](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22377) |
| `TROWEXPANDMAX` | `__builtin_trowexpandmax` | 参数映射 | [L19943](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19943) |
| `TROWEXPANDMAX_ASS` | `__builtin_trowexpandmax` | ASS 阶段参数 | [L22375](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22375) |
| `TROWEXPANDMIN` | `__builtin_trowexpandmin` | 参数映射 | [L20073](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L20073) |
| `TROWEXPANDMIN_ASS` | `__builtin_trowexpandmin` | ASS 阶段参数 | [L22376](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22376) |
| `TROWEXPANDMUL` | `__builtin_trowexpandmul` | 参数映射 | [L19679](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19679) |
| `TROWEXPANDMUL_ASS` | `__builtin_trowexpandmul` | ASS 阶段参数 | [L22373](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22373) |
| `TROWEXPANDSUB` | `__builtin_trowexpandsub` | 参数映射 | [L19549](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L19549) |
| `TROWEXPANDSUB_ASS` | `__builtin_trowexpandsub` | ASS 阶段参数 | [L22372](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22372) |
| `TROWEXPAND_ASS` | `__builtin_trowexpand` | ASS 阶段参数 | [L22368](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22368) |
| `TROWMAX` | `__builtin_trowmax` | 参数映射 | [L18297](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18297) |
| `TROWMAX_ASS` | `__builtin_trowmax` | ASS 阶段参数 | [L22360](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22360) |
| `TROWMIN` | `__builtin_trowmin` | 参数映射 | [L18380](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18380) |
| `TROWMIN_ASS` | `__builtin_trowmin` | ASS 阶段参数 | [L22361](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22361) |
| `TROWPROD` | `__builtin_trowprod` | 参数映射 | [L18463](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18463) |
| `TROWPROD_ASS` | `__builtin_trowprod` | ASS 阶段参数 | [L22362](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22362) |
| `TROWSUM` | `__builtin_trowsum` | 参数映射 | [L18142](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18142) |
| `TROWSUM_ASS` | `__builtin_trowsum` | ASS 阶段参数 | [L22359](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22359) |
| `TRSQRT` | `__builtin_trsqrt` | 参数映射 | [L14851](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14851) |
| `TRSQRT_ASS` | `__builtin_trsqrt` | ASS 阶段参数 | [L22339](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22339) |
| `TSCATTER` | `__builtin_tscatter` | 参数映射 | [L18038](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L18038) |
| `TSEL` | `__builtin_tsel` | 参数映射 | [L14175](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14175) |
| `TSELS` | `__builtin_tsels` | 参数映射 | [L16946](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16946) |
| `TSHL` | `__builtin_tshl` | 参数映射 | [L13326](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13326) |
| `TSHLS` | `__builtin_tshls` | 参数映射 | [L15795](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15795) |
| `TSHLS_ASS` | `__builtin_tshls` | ASS 阶段参数 | [L21990](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21990) |
| `TSHL_ASS` | `__builtin_tshl` | ASS 阶段参数 | [L21964](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21964) |
| `TSHR` | `__builtin_tshr` | 参数映射 | [L13410](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13410) |
| `TSHRS` | `__builtin_tshrs` | 参数映射 | [L15893](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15893) |
| `TSHRS_ASS` | `__builtin_tshrs` | ASS 阶段参数 | [L21991](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21991) |
| `TSHR_ASS` | `__builtin_tshr` | ASS 阶段参数 | [L21965](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21965) |
| `TSHUF` | `__builtin_tshuf` | 参数映射 | [L21305](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21305) |
| `TSORT` | — | 退役诊断，不定义 builtin | [L17923](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17923) |
| `TSORT32` | — | 退役诊断，不定义 builtin | [L17936](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17936) |
| `TSQRT` | `__builtin_tsqrt` | 参数映射 | [L14777](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L14777) |
| `TSQRT_ASS` | `__builtin_tsqrt` | ASS 阶段参数 | [L22338](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22338) |
| `TSTORE` | `__builtin_tstore` | 参数映射 | [L3662](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L3662) |
| `TSTORE2_DN2DN` | `__builtin_tstore2_dn2dn` | 参数映射 | [L803](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L803) |
| `TSTORE_ATOMIC_ADD` | `__builtin_tstore_atomic_add` | 参数映射 | [L4792](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4792) |
| `TSTORE_ATOMIC_AND` | `__builtin_tstore_atomic_and` | 参数映射 | [L4795](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4795) |
| `TSTORE_ATOMIC_DEC` | `__builtin_tstore_atomic_dec` | 参数映射 | [L4799](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4799) |
| `TSTORE_ATOMIC_INC` | `__builtin_tstore_atomic_inc` | 参数映射 | [L4798](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4798) |
| `TSTORE_ATOMIC_MAX` | `__builtin_tstore_atomic_max` | 参数映射 | [L4794](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4794) |
| `TSTORE_ATOMIC_MIN` | `__builtin_tstore_atomic_min` | 参数映射 | [L4793](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4793) |
| `TSTORE_ATOMIC_OR` | `__builtin_tstore_atomic_or` | 参数映射 | [L4796](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4796) |
| `TSTORE_ATOMIC_XOR` | `__builtin_tstore_atomic_xor` | 参数映射 | [L4797](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4797) |
| `TSTORE_CUBE` | `__builtin_tstore_cube` | 参数映射 | [L4113](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4113) |
| `TSTORE_PART` | `__builtin_tstore_part` | 参数映射 | [L4807](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L4807) |
| `TSUB` | `__builtin_tsub` | 参数映射 | [L12716](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L12716) |
| `TSUBC` | — | 退役诊断，不定义 builtin | [L15007](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15007) |
| `TSUBS` | `__builtin_tsubs` | 参数映射 | [L15112](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15112) |
| `TSUBSC` | — | 退役诊断，不定义 builtin | [L16938](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L16938) |
| `TSUBS_ASS` | `__builtin_tsubs` | ASS 阶段参数 | [L21983](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21983) |
| `TSUB_ASS` | `__builtin_tsub` | ASS 阶段参数 | [L21957](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21957) |
| `TTRANS` | — | 退役诊断，不定义 builtin | [L17959](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17959) |
| `TTRANS_ASS` | — | 冲突：普通 selector 退役，但 ASS 宏仍存在；待 ISA 核对 | [L22341](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L22341) |
| `TTRI` | `__builtin_ttri` | 参数映射 | [L17813](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L17813) |
| `TUNPACK` | `__builtin_tunpack` | 参数映射 | [L21647](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21647) |
| `TXOR` | `__builtin_txor` | 参数映射 | [L13242](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L13242) |
| `TXORS` | `__builtin_txors` | 参数映射 | [L15697](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L15697) |
| `TXORS_ASS` | `__builtin_txors` | ASS 阶段参数 | [L21989](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21989) |
| `TXOR_ASS` | `__builtin_txor` | ASS 阶段参数 | [L21963](https://github.com/LinxISA/Linx-TileOP-API/blob/5f764847b707fabf998c93fb4725787bcd2d6417/include/jcore/template_asm.hpp#L21963) |

## predicate 与 region

- `predicate::compare_scalar` → `__builtin_tcmps`；predicate 使用 U8 向量载体。
- `predicate::logical_and` → `__builtin_tand`；predicate 使用 U8 向量载体。
- `predicate::logical_or` → `__builtin_tor`；predicate 使用 U8 向量载体。
- `predicate::logical_xor` → `__builtin_txor`；predicate 使用 U8 向量载体。
- `predicate::select` → `__builtin_tsel`；predicate 使用 U8 向量载体。
- `predicate::select_scalar` → `__builtin_tsels`；predicate 使用 U8 向量载体。
- `predicate::scatter` → `__builtin_mscatter_mask`；predicate 使用 U8 向量载体。
- `predicate::subview` → `__builtin_predicate_subview`。
- `predicate::concatenate` → `__builtin_predicate_concatenate`。
- `predicate::logical_numeric` → `__builtin_predicate_logical_numeric`。
- `predicate::atomic_add` → `__builtin_predicate_atomic_add`。
- `predicate::logical<6/7/8>` → `__builtin_tand/tor/txor`。
- `jcore/TCI.hpp::TCI_2D_Impl` → `__builtin_tci_2d`；一维 vector kernel 路径不属 inline TileOP。
- `TLOAD` 权重重载 → `__builtin_tload_weight`，携带 shape/start 两个 GPR 字，而非 row stride。

region 宏实例逐项列在下表；同名 builtin 的 view/assemble 字段承载该路径。

| wrapper 类别 | PTO-C 操作 | 源码行 |
| --- | --- | --- |
| `UNARY_SOURCE_WRAPPER` | `TABS` | 613 |
| `UNARY_SOURCE_WRAPPER` | `TNOT` | 614 |
| `UNARY_SOURCE_WRAPPER` | `TNEG` | 615 |
| `UNARY_SOURCE_WRAPPER` | `TLOG` | 616 |
| `UNARY_SOURCE_WRAPPER` | `TRECIP` | 617 |
| `UNARY_SOURCE_WRAPPER` | `TSQRT` | 618 |
| `UNARY_SOURCE_WRAPPER` | `TRSQRT` | 619 |
| `UNARY_SOURCE_WRAPPER` | `TRELU` | 620 |
| `SCALAR_SOURCE_WRAPPER` | `TADDS` | 630 |
| `SCALAR_SOURCE_WRAPPER` | `TSUBS` | 631 |
| `SCALAR_SOURCE_WRAPPER` | `TMULS` | 632 |
| `SCALAR_SOURCE_WRAPPER` | `TDIVS` | 633 |
| `SCALAR_SOURCE_WRAPPER` | `TMAXS` | 634 |
| `SCALAR_SOURCE_WRAPPER` | `TMINS` | 635 |
| `UNARY_DEST_WRAPPER` | `TABS` | 637 |
| `UNARY_DEST_WRAPPER` | `TNOT` | 638 |
| `UNARY_DEST_WRAPPER` | `TNEG` | 639 |
| `UNARY_DEST_WRAPPER` | `TEXP` | 640 |
| `UNARY_DEST_WRAPPER` | `TLOG` | 641 |
| `UNARY_DEST_WRAPPER` | `TRECIP` | 642 |
| `UNARY_DEST_WRAPPER` | `TSQRT` | 643 |
| `UNARY_DEST_WRAPPER` | `TRSQRT` | 644 |
| `UNARY_DEST_WRAPPER` | `TRELU` | 645 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TABS` | 647 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TNOT` | 648 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TNEG` | 649 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TEXP` | 650 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TLOG` | 651 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TRECIP` | 652 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TSQRT` | 653 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TRSQRT` | 654 |
| `UNARY_SUBVIEW_DEST_WRAPPER` | `TRELU` | 655 |
| `SCALAR_DEST_WRAPPER` | `TADDS` | 674 |
| `SCALAR_DEST_WRAPPER` | `TSUBS` | 675 |
| `SCALAR_DEST_WRAPPER` | `TMULS` | 676 |
| `SCALAR_DEST_WRAPPER` | `TDIVS` | 677 |
| `SCALAR_DEST_WRAPPER` | `TMAXS` | 678 |
| `SCALAR_DEST_WRAPPER` | `TMINS` | 679 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TADDS` | 681 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TSUBS` | 682 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TMULS` | 683 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TDIVS` | 684 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TMAXS` | 685 |
| `SCALAR_SUBVIEW_DEST_WRAPPER` | `TMINS` | 686 |
| `BINARY_SOURCE_WRAPPER` | `TADD` | 1254 |
| `BINARY_SOURCE_WRAPPER` | `TSUB` | 1255 |
| `BINARY_SOURCE_WRAPPER` | `TMUL` | 1256 |
| `BINARY_SOURCE_WRAPPER` | `TDIV` | 1257 |
| `BINARY_SOURCE_WRAPPER` | `TREM` | 1258 |
| `BINARY_SOURCE_WRAPPER` | `TAND` | 1259 |
| `BINARY_SOURCE_WRAPPER` | `TOR` | 1260 |
| `BINARY_SOURCE_WRAPPER` | `TXOR` | 1261 |
| `BINARY_SOURCE_WRAPPER` | `TSHL` | 1262 |
| `BINARY_SOURCE_WRAPPER` | `TSHR` | 1263 |
| `BINARY_SOURCE_WRAPPER` | `TMAX` | 1264 |
| `BINARY_SOURCE_WRAPPER` | `TMIN` | 1265 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDADD` | 1594 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDSUB` | 1595 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDMUL` | 1596 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDDIV` | 1597 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDMAX` | 1598 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDMIN` | 1599 |
| `EXPAND_SOURCE_WRAPPER` | `TROWEXPANDEXPDIF` | 1600 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDADD` | 1601 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDSUB` | 1602 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDMUL` | 1603 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDDIV` | 1604 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDMAX` | 1605 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDMIN` | 1606 |
| `ROW_EXPAND_MIXED_WRAPPER` | `TROWEXPANDEXPDIF` | 1607 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDADD` | 1608 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDSUB` | 1609 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDMUL` | 1610 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDDIV` | 1611 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDMAX` | 1612 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDMIN` | 1613 |
| `COL_EXPAND_MIXED_WRAPPER` | `TCOLEXPANDEXPDIF` | 1614 |
| `BINARY_PREFIX_WRAPPER` | `TADD` | 1831 |
| `BINARY_PREFIX_WRAPPER` | `TSUB` | 1832 |
| `BINARY_PREFIX_WRAPPER` | `TMUL` | 1833 |
| `BINARY_PREFIX_WRAPPER` | `TDIV` | 1834 |
| `BINARY_PREFIX_WRAPPER` | `TREM` | 1835 |
| `BINARY_PREFIX_WRAPPER` | `TAND` | 1836 |
| `BINARY_PREFIX_WRAPPER` | `TOR` | 1837 |
| `BINARY_PREFIX_WRAPPER` | `TXOR` | 1838 |
| `BINARY_PREFIX_WRAPPER` | `TMAX` | 1839 |
| `BINARY_PREFIX_WRAPPER` | `TMIN` | 1840 |
| `BINARY_DEST_WRAPPER` | `TADD` | 2333 |
| `BINARY_DEST_WRAPPER` | `TSUB` | 2334 |
| `BINARY_DEST_WRAPPER` | `TMUL` | 2335 |
| `BINARY_DEST_WRAPPER` | `TDIV` | 2336 |
| `BINARY_DEST_WRAPPER` | `TREM` | 2337 |
| `BINARY_DEST_WRAPPER` | `TAND` | 2338 |
| `BINARY_DEST_WRAPPER` | `TOR` | 2339 |
| `BINARY_DEST_WRAPPER` | `TXOR` | 2340 |
| `BINARY_DEST_WRAPPER` | `TSHL` | 2341 |
| `BINARY_DEST_WRAPPER` | `TSHR` | 2342 |
| `BINARY_DEST_WRAPPER` | `TMAX` | 2343 |
| `BINARY_DEST_WRAPPER` | `TMIN` | 2344 |

region 显式定义的 `TROWSUM/TROWMAX/TROWMIN/TROWPROD/TEXP/TCVT/TMOV` 也映射到同名 builtin。
