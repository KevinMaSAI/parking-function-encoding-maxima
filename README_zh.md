# 停车函数相邻比较编码的最大类

**Qiyuan Ma · 上海交通大学**  
[ORCID: 0009-0000-9532-0821](https://orcid.org/0009-0000-9532-0821) · [English](README.md)

本仓库保存研究预印本、完整中文证明、显式单射与逆映射、精确计数和复现程序。版本 1.0.0，2026-10-28；不声称已通过独立专家审稿或证明助理形式化。

- [英文论文 PDF](paper.pdf)
- [完整中文证明](docs/proof_zh.md)
- [LaTeX 源码](preprints/Parking-Function-Comparison-Encodings-October-28-2026/main.tex)
- [完整复现包](reproducibility.zip)
- [核验范围](VERIFICATION.md)

## 结论

对长度 n−1 的相邻比较编码，以 A、D、T 分别表示严格上升、严格下降、相等：

| n | 全部最大编码 |
|---|---|
| 1 | 空编码 |
| 2 | A、D、T，各有 1 个停车函数 |
| 奇数 n≥3 | 仅 ADAD…AD |
| 偶数 n≥4 | ADAD…A 与 DADA…D 并列 |

证明严格排除含 T 编码，再通过四种单射修复首个 AA 或 DD，最后区分两个交替方向。最大值由交替偏序上的精确子集递推计算。

## 复现

在仓库根目录执行：

~~~sh
python -I -B verify_snapshot.py
python -I -B proof_artifacts/verify.py
python -B proof_artifacts/solve_maximum.py 20
~~~

只需 Python 3.10 及以上，证明核验不依赖第三方包。有限检查用于审查程序；任意 n 的结论由论文中的一般证明给出。

正文、文档和 JSON 数据采用 CC BY 4.0；Python、C++ 和核验自动化采用 MIT。作者与引用信息见 [CITATION.cff](CITATION.cff)，AI 协助范围见 [AI_ASSISTANCE.md](AI_ASSISTANCE.md)。
