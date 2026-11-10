# Choose methods by responsibility and structure

This is a decision aid, not a compulsory algorithm catalog. Inspect task data and verify any library capability in the available environment. Choose only responsibilities the task needs; a pipeline may mix problem types.

| Need / condition | Methods to consider | Assumption to challenge |
|---|---|---|
| Known deterministic rule, required calculation or transformation | Direct calculation/rules | Are rules complete, units consistent and edge cases defined? |
| Numeric or class target with usable historical labels | Simple regression/classification baseline; more complex estimators only if warranted | Labels and features exist at the correct time; evaluation matches intended future use. |
| Unusual observations with few/no defect labels | Rule/statistical baseline or anomaly detection | Rarity is not necessarily a defect; anomaly score is not automatically a probability. |
| Small discrete search | Enumeration/backtracking as solver or independent reference | All valid choices are represented; pruning is logically safe. |
| Repeated subproblems | Dynamic programming | State preserves every fact needed for future choices; state space is tractable. |
| Assignment/transport with matching or flow structure | Specialized matching/min-cost flow | Extra ordering/coupling constraints are not lost to force the structure. |
| Continuous amounts with linear objective/constraints | LP | Fractional values are meaningful and linearity is adequate. |
| Discrete or mixed choices with linear relations | Integer/MILP solver | Variable domains, logical conditions and numeric scaling match reality. |
| Schedules, precedence, exclusivity or Boolean logic | Constraint programming/CP-SAT | Time discretization and optional/required choices preserve the task. |
| Large search under a short budget | Greedy, local/LNS or other heuristics | A good feasible result is not a proof of optimality; compare fairly. |
| Continuous nonlinear settings | Appropriate constrained/gradient or derivative-free search | Smoothness/gradients, bounds, starting points and local/global claims are justified. |
| Few tunable settings with an expensive black-box evaluation | Small grid/random reference, Bayesian optimization when justified | Evaluation cost/noise and search dimension fit; learned associations alone do not prove intervention effects. |
| Source-grounded lookup/explanation | Retrieval/rules; RAG only when useful | Source validity, applicability, unsupported answers and abstention are checked. |
| Uncertain timing/demand or stochastic outcomes | Scenario/simulation evaluation, or task-supported robust/stochastic formulation | The uncertainty model is justified; a simulator score is not reality. |

Record a method's role: estimator, mathematical formulation, search algorithm, evaluator, verifier or UI. LP/MILP are formulations; greedy/local search are strategies; a library may implement several. Do not force them into a single mutually exclusive list.

Method selection need not exhaust all alternatives before a baseline. State why the selected minimum meets required behavior, what it does not guarantee and which observed failure would justify a more expensive method. A failed assumption may require changing data or the formulation instead of adding another algorithm.
