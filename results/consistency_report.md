# Consistency of the re-run with the previously submitted numbers

Classes: OK (same order of magnitude, or both >= 2,000), DIFF, BUG (legacy cell scored against the wrong profile), pending (not yet computed).

## Canary ranks
Summary: legacy re-score {'OK': 228, 'BUG': 24}; re-run {'OK': 220, 'DIFF': 8, 'BUG': 24}


| cell | paper | legacy re-score | class | new seed 42 | new median (seeds) | class |
|---|---|---|---|---|---|---|
| i2b2:100:A:eps4:A | 3338 | 3322 | OK | 4148 | 4148 | OK |
| i2b2:100:A:eps4:E | 2762 | 2774 | OK | 2910 | 2910 | OK |
| i2b2:100:A:eps4:N | 81 | 66 | OK | 72 | 72 | OK |
| i2b2:100:A:eps4:N,A | 486 | 478 | OK | 643 | 643 | OK |
| i2b2:100:A:eps4:N,A,E | 54 | 33 | OK | 67 | 67 | OK |
| i2b2:100:A:eps4:N,A,P,E | 945 | 961 | OK | 1072 | 1072 | OK |
| i2b2:100:A:eps4:P | 5228 | 5248 | OK | 5426 | 5426 | OK |
| i2b2:100:A:eps8:A | 2863 | 2877 | OK | 3747 | 3747 | OK |
| i2b2:100:A:eps8:E | 2908 | 2769 | OK | 2875 | 2875 | OK |
| i2b2:100:A:eps8:N | 116 | 99 | OK | 87 | 87 | OK |
| i2b2:100:A:eps8:N,A | 387 | 382 | OK | 582 | 582 | OK |
| i2b2:100:A:eps8:N,A,E | 33 | 33 | OK | 53 | 53 | OK |
| i2b2:100:A:eps8:N,A,P,E | 822 | 810 | OK | 959 | 959 | OK |
| i2b2:100:A:eps8:P | 4938 | 4962 | OK | 5134 | 5134 | OK |
| i2b2:100:A:nodp:A | 5 | 6 | OK | 297 | 297 | DIFF |
| i2b2:100:A:nodp:E | 1560 | 1390 | OK | 766 | 766 | OK |
| i2b2:100:A:nodp:N | 1047 | 952 | OK | 1115 | 1115 | OK |
| i2b2:100:A:nodp:N,A | 1 | 1 | OK | 103 | 103 | DIFF |
| i2b2:100:A:nodp:N,A,E | 1 | 1 | OK | 2 | 2 | OK |
| i2b2:100:A:nodp:N,A,P,E | 1 | 1 | OK | 19 | 19 | DIFF |
| i2b2:100:A:nodp:P | 1419 | 1465 | OK | 5081 | 5081 | OK |
| i2b2:100:B:eps4:A | 251 | 246 | OK | 569 | 569 | OK |
| i2b2:100:B:eps4:E | 1650 | 1584 | OK | 2822 | 2822 | OK |
| i2b2:100:B:eps4:N | 6304 | 6259 | OK | 6201 | 6201 | OK |
| i2b2:100:B:eps4:N,A | 282 | 289 | OK | 378 | 378 | OK |
| i2b2:100:B:eps4:N,A,E | 481 | 484 | OK | 1256 | 1256 | OK |
| i2b2:100:B:eps4:N,A,P,E | 2118 | 2003 | OK | 3731 | 3731 | OK |
| i2b2:100:B:eps4:P | 7102 | 7165 | OK | 7197 | 7197 | OK |
| i2b2:100:B:eps8:A | 125 | 134 | OK | 354 | 354 | OK |
| i2b2:100:B:eps8:E | 1582 | 1528 | OK | 2839 | 2839 | OK |
| i2b2:100:B:eps8:N | 5270 | 5333 | OK | 5419 | 5419 | OK |
| i2b2:100:B:eps8:N,A | 204 | 234 | OK | 286 | 286 | OK |
| i2b2:100:B:eps8:N,A,E | 442 | 408 | OK | 1012 | 1012 | OK |
| i2b2:100:B:eps8:N,A,P,E | 1459 | 1487 | OK | 3051 | 3051 | OK |
| i2b2:100:B:eps8:P | 6724 | 6630 | OK | 6881 | 6881 | OK |
| i2b2:100:B:nodp:A | 1 | 1 | OK | 3 | 3 | OK |
| i2b2:100:B:nodp:E | 106 | 122 | OK | 629 | 629 | OK |
| i2b2:100:B:nodp:N | 16 | 18 | OK | 48 | 48 | OK |
| i2b2:100:B:nodp:N,A | 1 | 1 | OK | 4 | 4 | OK |
| i2b2:100:B:nodp:N,A,E | 1 | 1 | OK | 2 | 2 | OK |
| i2b2:100:B:nodp:N,A,P,E | 1 | 1 | OK | 3 | 3 | OK |
| i2b2:100:B:nodp:P | 2772 | 2918 | OK | 5534 | 5534 | OK |
| i2b2:10:A:eps4:A | 1 | 6372 | BUG | 6499 | 6499 | BUG |
| i2b2:10:A:eps4:E | 7 | 3083 | BUG | 3402 | 3402 | BUG |
| i2b2:10:A:eps4:N | 4965 | 67 | BUG | 60 | 60 | BUG |
| i2b2:10:A:eps4:N,A | 1 | 1447 | BUG | 1479 | 1479 | BUG |
| i2b2:10:A:eps4:N,A,E | 1 | 320 | BUG | 267 | 267 | BUG |
| i2b2:10:A:eps4:N,A,P,E | 3481 | 3262 | OK | 3103 | 3103 | OK |
| i2b2:10:A:eps4:P | 61 | 6033 | BUG | 5712 | 5712 | BUG |
| i2b2:10:A:eps8:A | 1 | 6340 | BUG | 6559 | 6559 | BUG |
| i2b2:10:A:eps8:E | 10 | 3209 | BUG | 3497 | 3497 | BUG |
| i2b2:10:A:eps8:N | 4997 | 89 | BUG | 86 | 86 | BUG |
| i2b2:10:A:eps8:N,A | 1 | 1622 | BUG | 1659 | 1659 | BUG |
| i2b2:10:A:eps8:N,A,E | 1 | 444 | BUG | 384 | 384 | BUG |
| i2b2:10:A:eps8:N,A,P,E | 3693 | 3621 | OK | 3849 | 3849 | OK |
| i2b2:10:A:eps8:P | 74 | 5597 | BUG | 5360 | 5360 | BUG |
| i2b2:10:A:nodp:A | 4 | 686 | BUG | 221 | 221 | BUG |
| i2b2:10:A:nodp:E | 274 | 2428 | BUG | 1594 | 1594 | BUG |
| i2b2:10:A:nodp:N | 5320 | 144 | BUG | 100 | 100 | BUG |
| i2b2:10:A:nodp:N,A | 4 | 88 | BUG | 93 | 93 | BUG |
| i2b2:10:A:nodp:N,A,E | 1 | 35 | BUG | 1 | 1 | BUG |
| i2b2:10:A:nodp:N,A,P,E | 87 | 100 | OK | 52 | 52 | OK |
| i2b2:10:A:nodp:P | 1156 | 3403 | BUG | 5859 | 5859 | BUG |
| i2b2:10:B:eps4:A | 1595 | 1564 | OK | 1700 | 1700 | OK |
| i2b2:10:B:eps4:E | 3049 | 2895 | OK | 3411 | 3411 | OK |
| i2b2:10:B:eps4:N | 7005 | 7490 | OK | 5898 | 5898 | OK |
| i2b2:10:B:eps4:N,A | 1208 | 1214 | OK | 1004 | 1004 | OK |
| i2b2:10:B:eps4:N,A,E | 3023 | 3022 | OK | 3213 | 3213 | OK |
| i2b2:10:B:eps4:N,A,P,E | 6653 | 6599 | OK | 6727 | 6727 | OK |
| i2b2:10:B:eps4:P | 7350 | 7286 | OK | 7171 | 7171 | OK |
| i2b2:10:B:eps8:A | 1403 | 1376 | OK | 1400 | 1400 | OK |
| i2b2:10:B:eps8:E | 3408 | 3516 | OK | 3763 | 3763 | OK |
| i2b2:10:B:eps8:N | 6703 | 6908 | OK | 4973 | 4973 | OK |
| i2b2:10:B:eps8:N,A | 1098 | 1110 | OK | 845 | 845 | OK |
| i2b2:10:B:eps8:N,A,E | 3202 | 3130 | OK | 3172 | 3172 | OK |
| i2b2:10:B:eps8:N,A,P,E | 6854 | 6807 | OK | 6647 | 6647 | OK |
| i2b2:10:B:eps8:P | 7046 | 7062 | OK | 7071 | 7071 | OK |
| i2b2:10:B:nodp:A | 7 | 6 | OK | 6 | 6 | OK |
| i2b2:10:B:nodp:E | 206 | 191 | OK | 914 | 914 | OK |
| i2b2:10:B:nodp:N | 10 | 14 | OK | 57 | 57 | OK |
| i2b2:10:B:nodp:N,A | 2 | 2 | OK | 3 | 3 | OK |
| i2b2:10:B:nodp:N,A,E | 2 | 1 | OK | 3 | 3 | OK |
| i2b2:10:B:nodp:N,A,P,E | 129 | 133 | OK | 241 | 241 | OK |
| i2b2:10:B:nodp:P | 3437 | 3423 | OK | 7200 | 7200 | OK |
| i2b2:1:A:eps4:A | 6845 | 6904 | OK | 6593 | 6593 | OK |
| i2b2:1:A:eps4:E | 3186 | 3256 | OK | 3263 | 3263 | OK |
| i2b2:1:A:eps4:N | 70 | 69 | OK | 74 | 74 | OK |
| i2b2:1:A:eps4:N,A | 1709 | 1739 | OK | 1649 | 1649 | OK |
| i2b2:1:A:eps4:N,A,E | 418 | 418 | OK | 355 | 355 | OK |
| i2b2:1:A:eps4:N,A,P,E | 4000 | 3818 | OK | 3698 | 3698 | OK |
| i2b2:1:A:eps4:P | 6066 | 6135 | OK | 5741 | 5741 | OK |
| i2b2:1:A:eps8:A | 6834 | 6890 | OK | 6767 | 6767 | OK |
| i2b2:1:A:eps8:E | 3390 | 3411 | OK | 3491 | 3491 | OK |
| i2b2:1:A:eps8:N | 92 | 90 | OK | 83 | 83 | OK |
| i2b2:1:A:eps8:N,A | 1742 | 1860 | OK | 1734 | 1734 | OK |
| i2b2:1:A:eps8:N,A,E | 577 | 537 | OK | 461 | 461 | OK |
| i2b2:1:A:eps8:N,A,P,E | 4093 | 4109 | OK | 4308 | 4308 | OK |
| i2b2:1:A:eps8:P | 5792 | 5580 | OK | 5799 | 5799 | OK |
| i2b2:1:A:nodp:A | 6157 | 6008 | OK | 7067 | 7067 | OK |
| i2b2:1:A:nodp:E | 3086 | 2902 | OK | 1759 | 1759 | OK |
| i2b2:1:A:nodp:N | 458 | 409 | OK | 86 | 86 | OK |
| i2b2:1:A:nodp:N,A | 1437 | 1613 | OK | 3371 | 3371 | OK |
| i2b2:1:A:nodp:N,A,E | 2878 | 3052 | OK | 1038 | 1038 | OK |
| i2b2:1:A:nodp:N,A,P,E | 3195 | 3248 | OK | 2970 | 2970 | OK |
| i2b2:1:A:nodp:P | 4162 | 4128 | OK | 8591 | 8591 | OK |
| i2b2:1:B:eps4:A | 1798 | 1840 | OK | 1890 | 1890 | OK |
| i2b2:1:B:eps4:E | 3282 | 3074 | OK | 3697 | 3697 | OK |
| i2b2:1:B:eps4:N | 7128 | 7197 | OK | 6252 | 6252 | OK |
| i2b2:1:B:eps4:N,A | 1412 | 1380 | OK | 1189 | 1189 | OK |
| i2b2:1:B:eps4:N,A,E | 3407 | 3175 | OK | 3335 | 3335 | OK |
| i2b2:1:B:eps4:N,A,P,E | 7009 | 7253 | OK | 7050 | 7050 | OK |
| i2b2:1:B:eps4:P | 7365 | 7264 | OK | 7326 | 7326 | OK |
| i2b2:1:B:eps8:A | 1646 | 1578 | OK | 1725 | 1725 | OK |
| i2b2:1:B:eps8:E | 3699 | 3527 | OK | 3797 | 3797 | OK |
| i2b2:1:B:eps8:N | 6857 | 7427 | OK | 5259 | 5259 | OK |
| i2b2:1:B:eps8:N,A | 1307 | 1262 | OK | 1135 | 1135 | OK |
| i2b2:1:B:eps8:N,A,E | 3549 | 3624 | OK | 3229 | 3229 | OK |
| i2b2:1:B:eps8:N,A,P,E | 7233 | 7363 | OK | 7176 | 7176 | OK |
| i2b2:1:B:eps8:P | 7080 | 7104 | OK | 7067 | 7067 | OK |
| i2b2:1:B:nodp:A | 485 | 487 | OK | 231 | 231 | OK |
| i2b2:1:B:nodp:E | 840 | 749 | OK | 2178 | 2178 | OK |
| i2b2:1:B:nodp:N | 130 | 137 | OK | 743 | 743 | OK |
| i2b2:1:B:nodp:N,A | 248 | 238 | OK | 171 | 171 | OK |
| i2b2:1:B:nodp:N,A,E | 353 | 300 | OK | 384 | 384 | OK |
| i2b2:1:B:nodp:N,A,P,E | 4792 | 4950 | OK | 3507 | 3507 | OK |
| i2b2:1:B:nodp:P | 3693 | 3741 | OK | 9070 | 9070 | OK |
| meddocan:100:A:eps4:A | 108 | 114 | OK | 146 | 146 | OK |
| meddocan:100:A:eps4:E | 7822 | 7786 | OK | 7886 | 7886 | OK |
| meddocan:100:A:eps4:N | 9045 | 9053 | OK | 8994 | 8994 | OK |
| meddocan:100:A:eps4:N,A | 401 | 388 | OK | 461 | 461 | OK |
| meddocan:100:A:eps4:N,A,E | 1989 | 1968 | OK | 2735 | 2735 | OK |
| meddocan:100:A:eps4:N,A,P,E | 5106 | 5106 | OK | 5475 | 5475 | OK |
| meddocan:100:A:eps4:P | 6038 | 6064 | OK | 5900 | 5900 | OK |
| meddocan:100:A:eps8:A | 73 | 75 | OK | 128 | 128 | OK |
| meddocan:100:A:eps8:E | 2355 | 6968 | BUG | 7486 | 7486 | BUG |
| meddocan:100:A:eps8:N | 9035 | 9042 | OK | 9005 | 9005 | OK |
| meddocan:100:A:eps8:N,A | 368 | 345 | OK | 433 | 433 | OK |
| meddocan:100:A:eps8:N,A,E | 610 | 1544 | BUG | 2438 | 2438 | BUG |
| meddocan:100:A:eps8:N,A,P,E | 2150 | 4374 | BUG | 4819 | 4819 | BUG |
| meddocan:100:A:eps8:P | 6071 | 6086 | OK | 5899 | 5899 | OK |
| meddocan:100:A:nodp:A | 11 | 3 | OK | 4 | 4 | OK |
| meddocan:100:A:nodp:E | 109 | 3475 | BUG | 3906 | 3906 | BUG |
| meddocan:100:A:nodp:N | 9653 | 9588 | OK | 9020 | 9020 | OK |
| meddocan:100:A:nodp:N,A | 566 | 104 | OK | 30 | 30 | DIFF |
| meddocan:100:A:nodp:N,A,E | 3449 | 600 | BUG | 4 | 4 | BUG |
| meddocan:100:A:nodp:N,A,P,E | 350 | 20 | BUG | 27 | 27 | BUG |
| meddocan:100:A:nodp:P | 1635 | 1528 | OK | 1560 | 1560 | OK |
| meddocan:100:B:eps4:A | 163 | 154 | OK | 300 | 300 | OK |
| meddocan:100:B:eps4:E | 64 | 64 | OK | 89 | 89 | OK |
| meddocan:100:B:eps4:N | 6447 | 6481 | OK | 6187 | 6187 | OK |
| meddocan:100:B:eps4:N,A | 489 | 533 | OK | 652 | 652 | OK |
| meddocan:100:B:eps4:N,A,E | 15 | 13 | OK | 22 | 22 | OK |
| meddocan:100:B:eps4:N,A,P,E | 189 | 220 | OK | 206 | 206 | OK |
| meddocan:100:B:eps4:P | 6233 | 6214 | OK | 6281 | 6281 | OK |
| meddocan:100:B:eps8:A | 87 | 80 | OK | 275 | 275 | OK |
| meddocan:100:B:eps8:E | 51 | 52 | OK | 60 | 60 | OK |
| meddocan:100:B:eps8:N | 5768 | 5739 | OK | 5825 | 5825 | OK |
| meddocan:100:B:eps8:N,A | 216 | 210 | OK | 476 | 476 | OK |
| meddocan:100:B:eps8:N,A,E | 2 | 4 | OK | 11 | 11 | OK |
| meddocan:100:B:eps8:N,A,P,E | 115 | 114 | OK | 137 | 137 | OK |
| meddocan:100:B:eps8:P | 6171 | 6163 | OK | 6282 | 6282 | OK |
| meddocan:100:B:nodp:A | 1 | 1 | OK | 6 | 6 | OK |
| meddocan:100:B:nodp:E | 1 | 1 | OK | 2 | 2 | OK |
| meddocan:100:B:nodp:N | 3201 | 3416 | OK | 6299 | 6299 | OK |
| meddocan:100:B:nodp:N,A | 1 | 1 | OK | 4 | 4 | OK |
| meddocan:100:B:nodp:N,A,E | 1 | 1 | OK | 1 | 1 | OK |
| meddocan:100:B:nodp:N,A,P,E | 1 | 1 | OK | 1 | 1 | OK |
| meddocan:100:B:nodp:P | 3942 | 4101 | OK | 4139 | 4139 | OK |
| meddocan:10:A:eps4:A | 290 | 312 | OK | 306 | 306 | OK |
| meddocan:10:A:eps4:E | 9146 | 9162 | OK | 9023 | 9023 | OK |
| meddocan:10:A:eps4:N | 9327 | 9313 | OK | 9277 | 9277 | OK |
| meddocan:10:A:eps4:N,A | 807 | 740 | OK | 780 | 780 | OK |
| meddocan:10:A:eps4:N,A,E | 3516 | 3368 | OK | 4064 | 4064 | OK |
| meddocan:10:A:eps4:N,A,P,E | 6804 | 6863 | OK | 6848 | 6848 | OK |
| meddocan:10:A:eps4:P | 6231 | 6248 | OK | 6025 | 6025 | OK |
| meddocan:10:A:eps8:A | 289 | 294 | OK | 352 | 352 | OK |
| meddocan:10:A:eps8:E | 9039 | 9037 | OK | 9037 | 9037 | OK |
| meddocan:10:A:eps8:N | 9313 | 9267 | OK | 9260 | 9260 | OK |
| meddocan:10:A:eps8:N,A | 754 | 771 | OK | 711 | 711 | OK |
| meddocan:10:A:eps8:N,A,E | 3461 | 3374 | OK | 3970 | 3970 | OK |
| meddocan:10:A:eps8:N,A,P,E | 6892 | 6991 | OK | 6717 | 6717 | OK |
| meddocan:10:A:eps8:P | 6266 | 6255 | OK | 6044 | 6044 | OK |
| meddocan:10:A:nodp:A | 38 | 43 | OK | 12 | 12 | OK |
| meddocan:10:A:nodp:E | 3275 | 3290 | OK | 2418 | 2418 | OK |
| meddocan:10:A:nodp:N | 9725 | 9717 | OK | 9450 | 9450 | OK |
| meddocan:10:A:nodp:N,A | 576 | 525 | OK | 52 | 52 | DIFF |
| meddocan:10:A:nodp:N,A,E | 837 | 893 | OK | 23 | 23 | DIFF |
| meddocan:10:A:nodp:N,A,P,E | 1220 | 1258 | OK | 1529 | 1529 | OK |
| meddocan:10:A:nodp:P | 2155 | 2123 | OK | 2670 | 2670 | OK |
| meddocan:10:B:eps4:A | 856 | 835 | OK | 746 | 746 | OK |
| meddocan:10:B:eps4:E | 226 | 230 | OK | 234 | 234 | OK |
| meddocan:10:B:eps4:N | 7436 | 7669 | OK | 7509 | 7509 | OK |
| meddocan:10:B:eps4:N,A | 1810 | 1779 | OK | 1620 | 1620 | OK |
| meddocan:10:B:eps4:N,A,E | 158 | 144 | OK | 143 | 143 | OK |
| meddocan:10:B:eps4:N,A,P,E | 1251 | 1188 | OK | 786 | 786 | OK |
| meddocan:10:B:eps4:P | 6560 | 6526 | OK | 6420 | 6420 | OK |
| meddocan:10:B:eps8:A | 812 | 757 | OK | 749 | 749 | OK |
| meddocan:10:B:eps8:E | 223 | 236 | OK | 238 | 238 | OK |
| meddocan:10:B:eps8:N | 7192 | 7090 | OK | 7093 | 7093 | OK |
| meddocan:10:B:eps8:N,A | 1503 | 1508 | OK | 1367 | 1367 | OK |
| meddocan:10:B:eps8:N,A,E | 142 | 135 | OK | 124 | 124 | OK |
| meddocan:10:B:eps8:N,A,P,E | 1039 | 1115 | OK | 722 | 722 | OK |
| meddocan:10:B:eps8:P | 6421 | 6412 | OK | 6365 | 6365 | OK |
| meddocan:10:B:nodp:A | 7 | 5 | OK | 9 | 9 | OK |
| meddocan:10:B:nodp:E | 3 | 20 | OK | 8 | 8 | OK |
| meddocan:10:B:nodp:N | 3842 | 3658 | OK | 4588 | 4588 | OK |
| meddocan:10:B:nodp:N,A | 7 | 1 | OK | 6 | 6 | OK |
| meddocan:10:B:nodp:N,A,E | 1 | 1 | OK | 1 | 1 | OK |
| meddocan:10:B:nodp:N,A,P,E | 21 | 7 | OK | 2 | 2 | DIFF |
| meddocan:10:B:nodp:P | 3374 | 3515 | OK | 4724 | 4724 | OK |
| meddocan:1:A:eps4:A | 321 | 301 | OK | 358 | 358 | OK |
| meddocan:1:A:eps4:E | 9261 | 9213 | OK | 9171 | 9171 | OK |
| meddocan:1:A:eps4:N | 9346 | 9345 | OK | 9271 | 9271 | OK |
| meddocan:1:A:eps4:N,A | 824 | 771 | OK | 811 | 811 | OK |
| meddocan:1:A:eps4:N,A,E | 3595 | 3543 | OK | 4152 | 4152 | OK |
| meddocan:1:A:eps4:N,A,P,E | 6971 | 7081 | OK | 7084 | 7084 | OK |
| meddocan:1:A:eps4:P | 6269 | 6223 | OK | 6099 | 6099 | OK |
| meddocan:1:A:eps8:A | 320 | 355 | OK | 376 | 376 | OK |
| meddocan:1:A:eps8:E | 9216 | 9172 | OK | 9108 | 9108 | OK |
| meddocan:1:A:eps8:N | 9335 | 9240 | OK | 9313 | 9313 | OK |
| meddocan:1:A:eps8:N,A | 754 | 775 | OK | 813 | 813 | OK |
| meddocan:1:A:eps8:N,A,E | 3567 | 3584 | OK | 4167 | 4167 | OK |
| meddocan:1:A:eps8:N,A,P,E | 7147 | 7094 | OK | 7000 | 7000 | OK |
| meddocan:1:A:eps8:P | 6307 | 6286 | OK | 6026 | 6026 | OK |
| meddocan:1:A:nodp:A | 191 | 180 | OK | 202 | 202 | OK |
| meddocan:1:A:nodp:E | 7388 | 7338 | OK | 8769 | 8769 | OK |
| meddocan:1:A:nodp:N | 9569 | 9534 | OK | 9333 | 9333 | OK |
| meddocan:1:A:nodp:N,A | 1480 | 1546 | OK | 630 | 630 | OK |
| meddocan:1:A:nodp:N,A,E | 2268 | 2320 | OK | 1320 | 1320 | OK |
| meddocan:1:A:nodp:N,A,P,E | 4006 | 3974 | OK | 5580 | 5580 | OK |
| meddocan:1:A:nodp:P | 4037 | 4027 | OK | 4615 | 4615 | OK |
| meddocan:1:B:eps4:A | 963 | 908 | OK | 789 | 789 | OK |
| meddocan:1:B:eps4:E | 268 | 257 | OK | 299 | 299 | OK |
| meddocan:1:B:eps4:N | 7586 | 7483 | OK | 7445 | 7445 | OK |
| meddocan:1:B:eps4:N,A | 2069 | 2059 | OK | 1745 | 1745 | OK |
| meddocan:1:B:eps4:N,A,E | 208 | 195 | OK | 145 | 145 | OK |
| meddocan:1:B:eps4:N,A,P,E | 1402 | 1373 | OK | 1055 | 1055 | OK |
| meddocan:1:B:eps4:P | 6689 | 6733 | OK | 6763 | 6763 | OK |
| meddocan:1:B:eps8:A | 923 | 871 | OK | 785 | 785 | OK |
| meddocan:1:B:eps8:E | 273 | 268 | OK | 236 | 236 | OK |
| meddocan:1:B:eps8:N | 7415 | 7473 | OK | 7130 | 7130 | OK |
| meddocan:1:B:eps8:N,A | 1763 | 1756 | OK | 1674 | 1674 | OK |
| meddocan:1:B:eps8:N,A,E | 208 | 194 | OK | 163 | 163 | OK |
| meddocan:1:B:eps8:N,A,P,E | 1342 | 1270 | OK | 888 | 888 | OK |
| meddocan:1:B:eps8:P | 6509 | 6540 | OK | 6590 | 6590 | OK |
| meddocan:1:B:nodp:A | 51 | 50 | OK | 208 | 208 | OK |
| meddocan:1:B:nodp:E | 221 | 280 | OK | 128 | 128 | OK |
| meddocan:1:B:nodp:N | 5800 | 5750 | OK | 5527 | 5527 | OK |
| meddocan:1:B:nodp:N,A | 126 | 91 | OK | 187 | 187 | OK |
| meddocan:1:B:nodp:N,A,E | 34 | 24 | OK | 19 | 19 | OK |
| meddocan:1:B:nodp:N,A,P,E | 681 | 686 | OK | 58 | 58 | DIFF |
| meddocan:1:B:nodp:P | 4562 | 4502 | OK | 5141 | 5141 | OK |

## Leakage (unique counts; new = median over training seeds)

| row | metric | paper | new | ratio |
|---|---|---|---|---|
| i2b2:eps4:substring | singles | 1046 | 1039 | 0.99 |
| i2b2:eps4:substring | pairs | 1274 | 1419 | 1.11 |
| i2b2:eps4:substring | pairs_one_doc | 551 | 583 | 1.06 |
| i2b2:eps4:substring | triples | 95 | 88 | 0.93 |
| i2b2:eps4:substring | quadruples | 5 | 2 | 0.40 |
| i2b2:eps4:whole_word | singles | 645 | 648 | 1.00 |
| i2b2:eps4:whole_word | pairs | 459 | 485 | 1.06 |
| i2b2:eps4:whole_word | pairs_one_doc | 227 | 242 | 1.07 |
| i2b2:eps4:whole_word | triples | 3 | 6 | 2.00 |
| i2b2:eps4:whole_word | quadruples | 0 | 0 | -- |
| i2b2:eps8:substring | singles | 1069 | 1052 | 0.98 |
| i2b2:eps8:substring | pairs | 1387 | 1341 | 0.97 |
| i2b2:eps8:substring | pairs_one_doc | 555 | 564 | 1.02 |
| i2b2:eps8:substring | triples | 112 | 118 | 1.05 |
| i2b2:eps8:substring | quadruples | 2 | 6 | 3.00 |
| i2b2:eps8:whole_word | singles | 724 | 677 | 0.94 |
| i2b2:eps8:whole_word | pairs | 526 | 502 | 0.95 |
| i2b2:eps8:whole_word | pairs_one_doc | 250 | 245 | 0.98 |
| i2b2:eps8:whole_word | triples | 14 | 10 | 0.71 |
| i2b2:eps8:whole_word | quadruples | 0 | 0 | -- |
| i2b2:nodp:substring | singles | 1540 | 1281 | 0.83 |
| i2b2:nodp:substring | pairs | 3015 | 1995 | 0.66 |
| i2b2:nodp:substring | pairs_one_doc | 974 | 772 | 0.79 |
| i2b2:nodp:substring | triples | 330 | 177 | 0.54 |
| i2b2:nodp:substring | quadruples | 16 | 2 | 0.12 |
| i2b2:nodp:whole_word | singles | 1145 | 896 | 0.78 |
| i2b2:nodp:whole_word | pairs | 1427 | 873 | 0.61 |
| i2b2:nodp:whole_word | pairs_one_doc | 583 | 431 | 0.74 |
| i2b2:nodp:whole_word | triples | 36 | 25 | 0.69 |
| i2b2:nodp:whole_word | quadruples | 1 | 0 | 0.00 |
| meddocan:eps4:substring | singles | 924 | 981 | 1.06 |
| meddocan:eps4:substring | pairs | 1601 | 1701 | 1.06 |
| meddocan:eps4:substring | pairs_one_doc | 1871 | 1877 | 1.00 |
| meddocan:eps4:substring | triples | 523 | 532 | 1.02 |
| meddocan:eps4:substring | quadruples | 39 | 43 | 1.10 |
| meddocan:eps4:whole_word | singles | 856 | 902 | 1.05 |
| meddocan:eps4:whole_word | pairs | 1405 | 1456 | 1.04 |
| meddocan:eps4:whole_word | pairs_one_doc | 1741 | 1758 | 1.01 |
| meddocan:eps4:whole_word | triples | 393 | 399 | 1.02 |
| meddocan:eps4:whole_word | quadruples | 17 | 25 | 1.47 |
| meddocan:eps8:substring | singles | 960 | 1016 | 1.06 |
| meddocan:eps8:substring | pairs | 1594 | 1751 | 1.10 |
| meddocan:eps8:substring | pairs_one_doc | 1792 | 1922 | 1.07 |
| meddocan:eps8:substring | triples | 466 | 582 | 1.25 |
| meddocan:eps8:substring | quadruples | 39 | 43 | 1.10 |
| meddocan:eps8:whole_word | singles | 897 | 939 | 1.05 |
| meddocan:eps8:whole_word | pairs | 1375 | 1518 | 1.10 |
| meddocan:eps8:whole_word | pairs_one_doc | 1663 | 1790 | 1.08 |
| meddocan:eps8:whole_word | triples | 350 | 443 | 1.27 |
| meddocan:eps8:whole_word | quadruples | 20 | 30 | 1.50 |
| meddocan:nodp:substring | singles | 1181 | 1176 | 1.00 |
| meddocan:nodp:substring | pairs | 2299 | 2609 | 1.13 |
| meddocan:nodp:substring | pairs_one_doc | 2284 | 2611 | 1.14 |
| meddocan:nodp:substring | triples | 1038 | 1477 | 1.42 |
| meddocan:nodp:substring | quadruples | 105 | 190 | 1.81 |
| meddocan:nodp:whole_word | singles | 1116 | 1112 | 1.00 |
| meddocan:nodp:whole_word | pairs | 2016 | 2304 | 1.14 |
| meddocan:nodp:whole_word | pairs_one_doc | 2144 | 2462 | 1.15 |
| meddocan:nodp:whole_word | triples | 812 | 1234 | 1.52 |
| meddocan:nodp:whole_word | quadruples | 73 | 141 | 1.93 |
