# Development allocation audit

E counts selected baseline errors. C counts selected errors whose correct action is available (an offered true ID or abstention). G counts correct baseline decisions exposed to possible regression. Every measurement in these tables is offline.

## All development queries

| Ordering | Calls | E | C | G | C per call |
|---|---:|---:|---:|---:|---:|
| Frozen distance | 9 | 4 | 4 | 5 | 0.444 |
| Frozen distance | 19 | 4 | 4 | 15 | 0.211 |
| Narrowest margin | 9 | 4 | 3 | 5 | 0.333 |
| Narrowest margin | 19 | 6 | 5 | 13 | 0.263 |
| Weakest leader | 9 | 2 | 1 | 7 | 0.111 |
| Weakest leader | 19 | 6 | 5 | 13 | 0.263 |
| Abstentions first | 9 | 3 | 2 | 6 | 0.222 |
| Abstentions first | 19 | 6 | 5 | 13 | 0.263 |

| Random calls | Exact expected E / C | Simulated E, mean [central 95%] | Simulated C, mean [central 95%] |
|---:|---:|---:|---:|
| 9 | 1.421 / 1.184 | 1.432 [0, 3] | 1.196 [0, 3] |
| 19 | 3.000 / 2.500 | 2.995 [1, 5] | 2.501 [1, 4] |

## Four acquired cases omitted

| Ordering | Calls | E | C | G | C per call |
|---|---:|---:|---:|---:|---:|
| Frozen distance | 8 | 4 | 4 | 4 | 0.500 |
| Frozen distance | 17 | 4 | 4 | 13 | 0.235 |
| Narrowest margin | 8 | 4 | 3 | 4 | 0.375 |
| Narrowest margin | 17 | 5 | 4 | 12 | 0.235 |
| Weakest leader | 8 | 2 | 1 | 6 | 0.125 |
| Weakest leader | 17 | 5 | 4 | 12 | 0.235 |
| Abstentions first | 8 | 2 | 1 | 6 | 0.125 |
| Abstentions first | 17 | 5 | 4 | 12 | 0.235 |

| Random calls | Exact expected E / C | Simulated E, mean [central 95%] | Simulated C, mean [central 95%] |
|---:|---:|---:|---:|
| 8 | 1.176 / 0.941 | 1.181 [0, 3] | 0.949 [0, 3] |
| 17 | 2.500 / 2.000 | 2.490 [1, 4] | 1.995 [0, 4] |

## All 38 in frozen escalation order

Target rank is the position in the full-registry retrieval. Ranks 1–5 were offered. A dash denotes a reviewed no-match. Scores are rounded for display. Sorting used the frozen precision.

| Rank | ID | Deposited name | Leader | Runner-up | Gap | Distance | Baseline | Target rank | Assessment |
|---:|---|---|---:|---:|---:|---:|---|---:|---|
| 1 | cr-2096 | UK EPSRC | 0.7692 | 0.5714 | 0.1978 | 0.0192 | link | 1 | correct |
| 2 | cr-2597 | DDL Diagnostics | 0.7857 | 0.7333 | 0.0524 | 0.0224 | link | 4 | selection error |
| 3 | cr-1463 | Natural Science Foundation of Shaanxi Province, China | 0.7727 | 0.6737 | 0.0990 | 0.0227 | link | — | selection error |
| 4 | cr-2110 | Natural Science Foundation of Jiangxi Province of China | 0.7865 | 0.7292 | 0.0574 | 0.0274 | link | — | selection error |
| 5 | cr-2076 | German Ministry for Education and Research | 0.7895 | 0.7895 | 0.0000 | 0.0300 | abstain | 5 | selection error |
| 6 | cr-2819 | Higher Education Commission, Pakistan | 0.8475 | 0.7869 | 0.0606 | 0.0306 | link | 1 | correct |
| 7 | cr-1366 | City University of Hong Kong | 1.0000 | 0.9333 | 0.0667 | 0.0367 | link | 1 | correct |
| 8 | cr-486 | Association Suisse pour la Recherche sur Alzheimer | 0.7126 | 0.6237 | 0.0890 | 0.0374 | abstain | — | correct |
| 9 | cr-1684 | Wilf Family Foundation | 0.9333 | 0.8636 | 0.0697 | 0.0397 | link | 1 | correct |
| 10 | cr-2865 | U.S. Army Engineer (USAE) Waterways Experiment Station | 0.8113 | 0.5778 | 0.2335 | 0.0613 | link | 1 | correct |
| 11 | cr-2435 | Southern Marine Science and Engineering Guangdong Laboratory (Guangzhou), China | 0.9545 | 0.8571 | 0.0974 | 0.0674 | link | 1 | correct |
| 12 | cr-993 | Fonds de Recherche du Québec - Santé | 1.0000 | 0.9000 | 0.1000 | 0.0700 | link | 1 | correct |
| 13 | cr-3256 | United States National Centers for Advancing Translational Sciences | 0.8302 | 0.7158 | 0.1144 | 0.0802 | link | 1 | correct |
| 14 | cr-707 | Association Odyssea | 0.6667 | 0.6500 | 0.0167 | 0.0833 | abstain | — | correct |
| 15 | cr-1477 | Shanghai Municipal Natural Science Foundation | 0.6585 | 0.6292 | 0.0293 | 0.0915 | abstain | — | correct |
| 16 | cr-1194 | Guangxi Nature Science Foundation | 0.6557 | 0.6452 | 0.0106 | 0.0943 | abstain | — | correct |
| 17 | cr-857 | Margaretahemmet foundation | 0.6316 | 0.6190 | 0.0125 | 0.1184 | abstain | — | correct |
| 18 | cr-372 | National Institute of Allergy and Infectious Diseases | 1.0000 | 0.8444 | 0.1556 | 0.1256 | link | 1 | correct |
| 19 | cr-3202 | National Health and Medical Research Council, Canberra | 0.9053 | 0.7381 | 0.1672 | 0.1372 | link | 1 | correct |
| 20 | cr-2105 | Agencia Nacional de Investigación y Desarrollo ANID, Chile | 0.8889 | 0.6972 | 0.1916 | 0.1389 | link | 1 | correct |
| 21 | cr-75 | Education Department of Shaanxi Province | 1.0000 | 0.8250 | 0.1750 | 0.1450 | link | 1 | correct |
| 22 | cr-1006 | Science and Engineering Research Board | 1.0000 | 0.8205 | 0.1795 | 0.1495 | link | 1 | correct |
| 23 | cr-830 | Research Grants Council of Hong Kong | 0.6000 | 0.6000 | 0.0000 | 0.1500 | abstain | — | correct |
| 24 | cr-2083 | Ain Shams University | 1.0000 | 0.8163 | 0.1837 | 0.1537 | link | 1 | correct |
| 25 | cr-970 | Hoffmann - LaRoche Pharmaceuticals | 0.5882 | 0.5882 | 0.0000 | 0.1618 | abstain | 8 | retrieval miss |
| 26 | cr-744 | Universidad de La Laguna | 1.0000 | 0.8000 | 0.2000 | 0.1700 | link | 1 | correct |
| 27 | cr-242 | Guangzhou Science Technology and Innovation Commission | 1.0000 | 0.7885 | 0.2115 | 0.1815 | link | 1 | correct |
| 28 | cr-261 | University of Antwerp | 1.0000 | 0.7619 | 0.2381 | 0.2081 | link | 1 | correct |
| 29 | cr-882 | Bernard van Leer Foundation | 1.0000 | 0.7451 | 0.2549 | 0.2249 | link | 1 | correct |
| 30 | cr-2775 | CNPq process | 0.5217 | 0.5000 | 0.0217 | 0.2283 | abstain | 2 | selection error |
| 31 | cr-176 | Princess Nourah bint Abdulrahman University | 1.0000 | 0.5750 | 0.4250 | 0.2500 | link | 1 | correct |
| 32 | cr-2221 | Norwegian Directorate for Children, Youth and Family Affairs | 1.0000 | 0.6055 | 0.3945 | 0.2500 | link | 1 | correct |
| 33 | cr-2244 | Independent Research Fund Denmark | 1.0000 | 0.6333 | 0.3667 | 0.2500 | link | 1 | correct |
| 34 | cr-2478 | Great Lakes Research Consortium | 1.0000 | 0.7119 | 0.2881 | 0.2500 | link | 1 | correct |
| 35 | cr-3246 | Mastercard Foundation | 1.0000 | 0.6857 | 0.3143 | 0.2500 | link | 1 | correct |
| 36 | cr-462 | Fundación Cellex | 1.0000 | 0.6667 | 0.3333 | 0.2500 | link | 1 | correct |
| 37 | cr-504 | Worldwide Cancer Research | 1.0000 | 0.7037 | 0.2963 | 0.2500 | link | 1 | correct |
| 38 | cr-524 | Association pour la Recherche sur le Cancer | 1.0000 | 0.7000 | 0.3000 | 0.2500 | link | 1 | correct |
