# Verification scope

| Layer | Released evidence |
|---|---|
| General theorem | Explicit maps for every parity/direction case, inverses, boundary inequalities, strictness witnesses, and a decreasing defect statistic in the manuscript. |
| Exact class counts | Direct enumeration, ordered set partitions, and poset assignment agree for every encoding through n = 6. Full ternary data through n = 10 pass the total and classification checks. |
| Injections | Step checks and source recovery for tied and binary classes; all 18,248 parking functions of lengths at most six pass the composed map and its inverse. |
| Strictness | Missing-image witnesses are constructed for all 1,004 nonalternating binary encoding instances through n = 10. |
| Maximum recurrence | Exact integer values computed through n = 20. |
| Snapshot integrity | SHA-256 and byte counts in MANIFEST.json, checked by verify_snapshot.py. |
| External expert review | Not claimed. |
| Proof assistant | No Lean/Coq/Isabelle formalisation is supplied. |

Run the unified verifier from this snapshot. It imports the released implementations and checks their actual outputs. It does not rewrite the frozen audit files. Optional --json PATH writes a fresh summary to a chosen path.

The first-defect comparison requires the preceding prefix to be alternating. No universal claim about flipping an arbitrary defect position is used.
