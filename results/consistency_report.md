# Consistency of the re-run with the previously submitted numbers

Classes: OK (same order of magnitude, or both >= 2,000), DIFF, BUG (legacy cell scored against the wrong profile), pending (not yet computed).

## Canary ranks
Summary: legacy re-score {'pending': 228, 'BUG': 24}; re-run {'pending': 186, 'BUG': 24, 'OK': 42}


| cell | paper | legacy re-score | class | new seed 42 | new median (seeds) | class |
|---|---|---|---|---|---|---|
| i2b2|100|A|eps4|A | 3338 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|E | 2762 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|N | 81 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|N,A | 486 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|N,A,E | 54 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|N,A,P,E | 945 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps4|P | 5228 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|A | 2863 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|E | 2908 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|N | 116 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|N,A | 387 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|N,A,E | 33 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|N,A,P,E | 822 | -- | pending | -- | -- | pending |
| i2b2|100|A|eps8|P | 4938 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|A | 5 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|E | 1560 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|N | 1047 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|N,A | 1 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|N,A,E | 1 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|N,A,P,E | 1 | -- | pending | -- | -- | pending |
| i2b2|100|A|nodp|P | 1419 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|A | 251 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|E | 1650 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|N | 6304 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|N,A | 282 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|N,A,E | 481 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|N,A,P,E | 2118 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps4|P | 7102 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|A | 125 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|E | 1582 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|N | 5270 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|N,A | 204 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|N,A,E | 442 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|N,A,P,E | 1459 | -- | pending | -- | -- | pending |
| i2b2|100|B|eps8|P | 6724 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|A | 1 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|E | 106 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|N | 16 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|N,A | 1 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|N,A,E | 1 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|N,A,P,E | 1 | -- | pending | -- | -- | pending |
| i2b2|100|B|nodp|P | 2772 | -- | pending | -- | -- | pending |
| i2b2|10|A|eps4|A | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps4|E | 7 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps4|N | 4965 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps4|N,A | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps4|N,A,E | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps4|N,A,P,E | 3481 | -- | pending | -- | -- | pending |
| i2b2|10|A|eps4|P | 61 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|A | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|E | 10 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|N | 4997 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|N,A | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|N,A,E | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|eps8|N,A,P,E | 3693 | -- | pending | -- | -- | pending |
| i2b2|10|A|eps8|P | 74 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|A | 4 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|E | 274 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|N | 5320 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|N,A | 4 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|N,A,E | 1 | -- | BUG | -- | -- | BUG |
| i2b2|10|A|nodp|N,A,P,E | 87 | -- | pending | -- | -- | pending |
| i2b2|10|A|nodp|P | 1156 | -- | BUG | -- | -- | BUG |
| i2b2|10|B|eps4|A | 1595 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|E | 3049 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|N | 7005 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|N,A | 1208 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|N,A,E | 3023 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|N,A,P,E | 6653 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps4|P | 7350 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|A | 1403 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|E | 3408 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|N | 6703 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|N,A | 1098 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|N,A,E | 3202 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|N,A,P,E | 6854 | -- | pending | -- | -- | pending |
| i2b2|10|B|eps8|P | 7046 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|A | 7 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|E | 206 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|N | 10 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|N,A | 2 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|N,A,E | 2 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|N,A,P,E | 129 | -- | pending | -- | -- | pending |
| i2b2|10|B|nodp|P | 3437 | -- | pending | -- | -- | pending |
| i2b2|1|A|eps4|A | 6845 | -- | pending | 6593 | 6593 | OK |
| i2b2|1|A|eps4|E | 3186 | -- | pending | 3263 | 3263 | OK |
| i2b2|1|A|eps4|N | 70 | -- | pending | 74 | 74 | OK |
| i2b2|1|A|eps4|N,A | 1709 | -- | pending | 1649 | 1649 | OK |
| i2b2|1|A|eps4|N,A,E | 418 | -- | pending | 355 | 355 | OK |
| i2b2|1|A|eps4|N,A,P,E | 4000 | -- | pending | 3698 | 3698 | OK |
| i2b2|1|A|eps4|P | 6066 | -- | pending | 5741 | 5741 | OK |
| i2b2|1|A|eps8|A | 6834 | -- | pending | 6767 | 6767 | OK |
| i2b2|1|A|eps8|E | 3390 | -- | pending | 3491 | 3491 | OK |
| i2b2|1|A|eps8|N | 92 | -- | pending | 83 | 83 | OK |
| i2b2|1|A|eps8|N,A | 1742 | -- | pending | 1734 | 1734 | OK |
| i2b2|1|A|eps8|N,A,E | 577 | -- | pending | 461 | 461 | OK |
| i2b2|1|A|eps8|N,A,P,E | 4093 | -- | pending | 4308 | 4308 | OK |
| i2b2|1|A|eps8|P | 5792 | -- | pending | 5799 | 5799 | OK |
| i2b2|1|A|nodp|A | 6157 | -- | pending | 7067 | 7067 | OK |
| i2b2|1|A|nodp|E | 3086 | -- | pending | 1759 | 1759 | OK |
| i2b2|1|A|nodp|N | 458 | -- | pending | 86 | 86 | OK |
| i2b2|1|A|nodp|N,A | 1437 | -- | pending | 3371 | 3371 | OK |
| i2b2|1|A|nodp|N,A,E | 2878 | -- | pending | 1038 | 1038 | OK |
| i2b2|1|A|nodp|N,A,P,E | 3195 | -- | pending | 2970 | 2970 | OK |
| i2b2|1|A|nodp|P | 4162 | -- | pending | 8591 | 8591 | OK |
| i2b2|1|B|eps4|A | 1798 | -- | pending | 1890 | 1890 | OK |
| i2b2|1|B|eps4|E | 3282 | -- | pending | 3697 | 3697 | OK |
| i2b2|1|B|eps4|N | 7128 | -- | pending | 6252 | 6252 | OK |
| i2b2|1|B|eps4|N,A | 1412 | -- | pending | 1189 | 1189 | OK |
| i2b2|1|B|eps4|N,A,E | 3407 | -- | pending | 3335 | 3335 | OK |
| i2b2|1|B|eps4|N,A,P,E | 7009 | -- | pending | 7050 | 7050 | OK |
| i2b2|1|B|eps4|P | 7365 | -- | pending | 7326 | 7326 | OK |
| i2b2|1|B|eps8|A | 1646 | -- | pending | 1725 | 1725 | OK |
| i2b2|1|B|eps8|E | 3699 | -- | pending | 3797 | 3797 | OK |
| i2b2|1|B|eps8|N | 6857 | -- | pending | 5259 | 5259 | OK |
| i2b2|1|B|eps8|N,A | 1307 | -- | pending | 1135 | 1135 | OK |
| i2b2|1|B|eps8|N,A,E | 3549 | -- | pending | 3229 | 3229 | OK |
| i2b2|1|B|eps8|N,A,P,E | 7233 | -- | pending | 7176 | 7176 | OK |
| i2b2|1|B|eps8|P | 7080 | -- | pending | 7067 | 7067 | OK |
| i2b2|1|B|nodp|A | 485 | -- | pending | 231 | 231 | OK |
| i2b2|1|B|nodp|E | 840 | -- | pending | 2178 | 2178 | OK |
| i2b2|1|B|nodp|N | 130 | -- | pending | 743 | 743 | OK |
| i2b2|1|B|nodp|N,A | 248 | -- | pending | 171 | 171 | OK |
| i2b2|1|B|nodp|N,A,E | 353 | -- | pending | 384 | 384 | OK |
| i2b2|1|B|nodp|N,A,P,E | 4792 | -- | pending | 3507 | 3507 | OK |
| i2b2|1|B|nodp|P | 3693 | -- | pending | 9070 | 9070 | OK |
| meddocan|100|A|eps4|A | 108 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|E | 7822 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|N | 9045 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|N,A | 401 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|N,A,E | 1989 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|N,A,P,E | 5106 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps4|P | 6038 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps8|A | 73 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps8|E | 2355 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|eps8|N | 9035 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps8|N,A | 368 | -- | pending | -- | -- | pending |
| meddocan|100|A|eps8|N,A,E | 610 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|eps8|N,A,P,E | 2150 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|eps8|P | 6071 | -- | pending | -- | -- | pending |
| meddocan|100|A|nodp|A | 11 | -- | pending | -- | -- | pending |
| meddocan|100|A|nodp|E | 109 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|nodp|N | 9653 | -- | pending | -- | -- | pending |
| meddocan|100|A|nodp|N,A | 566 | -- | pending | -- | -- | pending |
| meddocan|100|A|nodp|N,A,E | 3449 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|nodp|N,A,P,E | 350 | -- | BUG | -- | -- | BUG |
| meddocan|100|A|nodp|P | 1635 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|A | 163 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|E | 64 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|N | 6447 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|N,A | 489 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|N,A,E | 15 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|N,A,P,E | 189 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps4|P | 6233 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|A | 87 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|E | 51 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|N | 5768 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|N,A | 216 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|N,A,E | 2 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|N,A,P,E | 115 | -- | pending | -- | -- | pending |
| meddocan|100|B|eps8|P | 6171 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|A | 1 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|E | 1 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|N | 3201 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|N,A | 1 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|N,A,E | 1 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|N,A,P,E | 1 | -- | pending | -- | -- | pending |
| meddocan|100|B|nodp|P | 3942 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|A | 290 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|E | 9146 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|N | 9327 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|N,A | 807 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|N,A,E | 3516 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|N,A,P,E | 6804 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps4|P | 6231 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|A | 289 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|E | 9039 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|N | 9313 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|N,A | 754 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|N,A,E | 3461 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|N,A,P,E | 6892 | -- | pending | -- | -- | pending |
| meddocan|10|A|eps8|P | 6266 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|A | 38 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|E | 3275 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|N | 9725 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|N,A | 576 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|N,A,E | 837 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|N,A,P,E | 1220 | -- | pending | -- | -- | pending |
| meddocan|10|A|nodp|P | 2155 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|A | 856 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|E | 226 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|N | 7436 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|N,A | 1810 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|N,A,E | 158 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|N,A,P,E | 1251 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps4|P | 6560 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|A | 812 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|E | 223 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|N | 7192 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|N,A | 1503 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|N,A,E | 142 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|N,A,P,E | 1039 | -- | pending | -- | -- | pending |
| meddocan|10|B|eps8|P | 6421 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|A | 7 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|E | 3 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|N | 3842 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|N,A | 7 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|N,A,E | 1 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|N,A,P,E | 21 | -- | pending | -- | -- | pending |
| meddocan|10|B|nodp|P | 3374 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|A | 321 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|E | 9261 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|N | 9346 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|N,A | 824 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|N,A,E | 3595 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|N,A,P,E | 6971 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps4|P | 6269 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|A | 320 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|E | 9216 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|N | 9335 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|N,A | 754 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|N,A,E | 3567 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|N,A,P,E | 7147 | -- | pending | -- | -- | pending |
| meddocan|1|A|eps8|P | 6307 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|A | 191 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|E | 7388 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|N | 9569 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|N,A | 1480 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|N,A,E | 2268 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|N,A,P,E | 4006 | -- | pending | -- | -- | pending |
| meddocan|1|A|nodp|P | 4037 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|A | 963 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|E | 268 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|N | 7586 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|N,A | 2069 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|N,A,E | 208 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|N,A,P,E | 1402 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps4|P | 6689 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|A | 923 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|E | 273 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|N | 7415 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|N,A | 1763 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|N,A,E | 208 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|N,A,P,E | 1342 | -- | pending | -- | -- | pending |
| meddocan|1|B|eps8|P | 6509 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|A | 51 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|E | 221 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|N | 5800 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|N,A | 126 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|N,A,E | 34 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|N,A,P,E | 681 | -- | pending | -- | -- | pending |
| meddocan|1|B|nodp|P | 4562 | -- | pending | -- | -- | pending |

## Leakage (unique counts; new = median over training seeds)

| row | metric | paper | new | ratio |
|---|---|---|---|---|
| i2b2|eps4|substring | singles | 1046 | 1482 | 1.42 |
| i2b2|eps4|substring | pairs | 1274 | 2606 | 2.05 |
| i2b2|eps4|substring | pairs_one_doc | 551 | 878 | 1.59 |
| i2b2|eps4|substring | triples | 95 | 323 | 3.40 |
| i2b2|eps4|substring | quadruples | 5 | 26 | 5.20 |
| i2b2|eps4|whole_word | singles | 645 | 1100 | 1.71 |
| i2b2|eps4|whole_word | pairs | 459 | 1282 | 2.79 |
| i2b2|eps4|whole_word | pairs_one_doc | 227 | 491 | 2.16 |
| i2b2|eps4|whole_word | triples | 3 | 47 | 15.67 |
| i2b2|eps4|whole_word | quadruples | 0 | 2 | -- |
| i2b2|eps8|substring | singles | 1069 | 1572 | 1.47 |
| i2b2|eps8|substring | pairs | 1387 | 2751 | 1.98 |
| i2b2|eps8|substring | pairs_one_doc | 555 | 923 | 1.66 |
| i2b2|eps8|substring | triples | 112 | 282 | 2.52 |
| i2b2|eps8|substring | quadruples | 2 | 8 | 4.00 |
| i2b2|eps8|whole_word | singles | 724 | 1167 | 1.61 |
| i2b2|eps8|whole_word | pairs | 526 | 1308 | 2.49 |
| i2b2|eps8|whole_word | pairs_one_doc | 250 | 519 | 2.08 |
| i2b2|eps8|whole_word | triples | 14 | 27 | 1.93 |
| i2b2|eps8|whole_word | quadruples | 0 | 0 | -- |
| i2b2|nodp|substring | singles | 1540 | 1665 | 1.08 |
| i2b2|nodp|substring | pairs | 3015 | 3302 | 1.10 |
| i2b2|nodp|substring | pairs_one_doc | 974 | 1085 | 1.11 |
| i2b2|nodp|substring | triples | 330 | 433 | 1.31 |
| i2b2|nodp|substring | quadruples | 16 | 15 | 0.94 |
| i2b2|nodp|whole_word | singles | 1145 | 1255 | 1.10 |
| i2b2|nodp|whole_word | pairs | 1427 | 1681 | 1.18 |
| i2b2|nodp|whole_word | pairs_one_doc | 583 | 636 | 1.09 |
| i2b2|nodp|whole_word | triples | 36 | 51 | 1.42 |
| i2b2|nodp|whole_word | quadruples | 1 | 0 | 0.00 |
| meddocan|eps4|substring | singles | 924 | -- | -- |
| meddocan|eps4|substring | pairs | 1601 | -- | -- |
| meddocan|eps4|substring | pairs_one_doc | 1871 | -- | -- |
| meddocan|eps4|substring | triples | 523 | -- | -- |
| meddocan|eps4|substring | quadruples | 39 | -- | -- |
| meddocan|eps4|whole_word | singles | 856 | -- | -- |
| meddocan|eps4|whole_word | pairs | 1405 | -- | -- |
| meddocan|eps4|whole_word | pairs_one_doc | 1741 | -- | -- |
| meddocan|eps4|whole_word | triples | 393 | -- | -- |
| meddocan|eps4|whole_word | quadruples | 17 | -- | -- |
| meddocan|eps8|substring | singles | 960 | -- | -- |
| meddocan|eps8|substring | pairs | 1594 | -- | -- |
| meddocan|eps8|substring | pairs_one_doc | 1792 | -- | -- |
| meddocan|eps8|substring | triples | 466 | -- | -- |
| meddocan|eps8|substring | quadruples | 39 | -- | -- |
| meddocan|eps8|whole_word | singles | 897 | -- | -- |
| meddocan|eps8|whole_word | pairs | 1375 | -- | -- |
| meddocan|eps8|whole_word | pairs_one_doc | 1663 | -- | -- |
| meddocan|eps8|whole_word | triples | 350 | -- | -- |
| meddocan|eps8|whole_word | quadruples | 20 | -- | -- |
| meddocan|nodp|substring | singles | 1181 | -- | -- |
| meddocan|nodp|substring | pairs | 2299 | -- | -- |
| meddocan|nodp|substring | pairs_one_doc | 2284 | -- | -- |
| meddocan|nodp|substring | triples | 1038 | -- | -- |
| meddocan|nodp|substring | quadruples | 105 | -- | -- |
| meddocan|nodp|whole_word | singles | 1116 | -- | -- |
| meddocan|nodp|whole_word | pairs | 2016 | -- | -- |
| meddocan|nodp|whole_word | pairs_one_doc | 2144 | -- | -- |
| meddocan|nodp|whole_word | triples | 812 | -- | -- |
| meddocan|nodp|whole_word | quadruples | 73 | -- | -- |
