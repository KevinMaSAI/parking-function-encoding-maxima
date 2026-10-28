# Parking function encoding maxima

**Qiyuan Ma · Shanghai Jiao Tong University**  
[mqyqwerty@sjtu.edu.cn](mailto:mqyqwerty@sjtu.edu.cn) · [ORCID: 0009-0000-9532-0821](https://orcid.org/0009-0000-9532-0821) · [中文说明](README_zh.md)

This repository contains the research preprint **Maximizing the adjacent comparison classes of parking functions**, explicit injections and inverse maps, exact counts, and executable verification. Version **1.0.0**, October 28, 2026. Independent expert peer review and proof-assistant formalisation are not claimed.

- **[Read the paper (PDF)](paper.pdf)** or its **[LaTeX source](preprints/Parking-Function-Comparison-Encodings-October-28-2026/main.tex)**.
- **[Read the full Chinese proof](docs/proof_zh.md)**.
- **[Download the complete reproducibility archive](reproducibility.zip)**.
- See **[verification scope](VERIFICATION.md)**, **[related work](RELATED_WORK.md)** and **[AI assistance](AI_ASSISTANCE.md)**.

## Main theorem

Let F_n(w) count the parking functions of length n whose adjacent comparisons form w, using A for strict ascent, D for strict descent, and T for equality.

| Length | All maximizing encodings |
|---|---|
| n = 1 | The empty word |
| n = 2 | A, D, T; each class has size 1 |
| Odd n ≥ 3 | Only ADAD…AD |
| Even n ≥ 4 | Both ADAD…A and DADA…D |

Every word has length n−1. The proof strictly eliminates tied words, then strictly repairs the **first** pair AA or DD of a nonalternating binary word. The number of defects decreases by one at every repair. The two alternating directions are equal for even n; for odd n, the word starting with A is strictly larger.

The maximum values for n = 1,…,12 are

    1, 1, 4, 17, 120, 915, 9470, 104436, 1432713, 20709209, 354493902, 6343919118.

The maximum is the up-down parking function count [OEIS A260694](https://oeis.org/A260694). These counts were already known; the manuscript supplies the comparison arguments and an exact subset recurrence.

## Reproduce

Python 3.10 or later; no third-party packages, solver, account, or network is required:

~~~sh
python -I -B verify_snapshot.py
python -I -B proof_artifacts/verify.py
python -B proof_artifacts/solve_maximum.py 20
~~~

The unified verifier executes three independent counting methods through n = 6, checks the injections and their inverses, constructs strictness witnesses, compares the classification with all ternary encoding counts through n = 10, and checks all 18,248 parking functions of lengths at most six through the full composed injection. Finite tests audit the implementation; the universal statements are proved in the manuscript.

The optional C++ enumerator regenerates every ternary class count through n = 10; see [BUILD.md](preprints/Parking-Function-Comparison-Encodings-October-28-2026/BUILD.md).

## Citation and licences

Use [CITATION.cff](CITATION.cff) or [CITATION.bib](CITATION.bib). No DOI is assigned to this GitHub deposit.

Manuscript, documentation and JSON data: **CC BY 4.0**. Python, C++ and verification automation: **MIT**. See [licence scopes](LICENSES.md). Linked third-party papers are not redistributed.
