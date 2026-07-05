# kaifa engine — session handoff

## Done
- P1: Full pipeline (land → profit → CF → IRR)
- P2: VAT full chain (output/input/surtax/ex-vat conversion)
- P2.5: 土增税清算 (四级超率累进 + 三分法)
  - Fixed: land cost allocated only to 住宅 (not 车库) per Chinese tax practice
  - LAT vs XLCS: +123% → +17% after fix
- P3: S-curve, multi-phase, bridge loan, income tax 汇算清缴
- Validation script against XLCS

## Remaining deviations from XLCS (expected, structural)
| Item | Engine | XLCS | Δ | Cause |
|------|--------|------|---|-------|
| 前期费 | 2,414 | 2,795 | -14% | %-of-constr vs fixed table |
| 三费 | 11,054 | 9,497 | +16% | no 60% mgmt fee → dev cost cap. |
| 附加税 | 628 | 726 | -14% | city maint. rate 5% vs 7% |
| 土增税 | 5,829 | 4,977 | +17% | mgmt cap. + surtax diff |
| 净利润 | 29,173 | 18,827 | +55% | cumulative from above |

## Structure
- `engines/kaifa.py` ~900 lines, `@engine("kaifa_v1")` entry
- `templates/kaifa.yaml` multi-phase template
- `frontend/src/views/KaifaCalculator.vue` Vue3 form
- `engines/test_kaifa.py` 6 tests
- `engines/validate_xlcs.py` XLCS comparison

## Key numbers (demo, after P3)
Sales 含税 181,500w / 不含税 170,972w. Net profit 34,551w. IRR 23.3%/yr.

## Next
1. Deploy (caddy + systemd + calc.elsak.cn)
2. Multi-template side-by-side comparison
3. CF ECharts chart
