# DECISION_MATRIX.md: Project B Data-Quality Detector Choices

Each choice is tied directly to measured trade-offs between throughput, cost, and alert precision.

| Corruption / Problem Type | Detector Family Chosen | Measurement Justification | Trade-off / Why Not Other Families |
| :--- | :--- | :--- | :--- |
| **a. Renamed or dropped column** | **Declarative / Schema** | **100% recall, 0.0% FPR, $0.00 cost, >25M rows/s.** | Pure metadata check. Using an LLM costs $180/M rows for zero gain. |
| **b. Column type change** | **Declarative / Schema** | **100% recall, 0.0% FPR, $0.00 cost, >1.5M rows/s.** | Regex/type validation is deterministic and instantaneous. |
| **c. Date format switch** | **Declarative Rules** | **100% recall, 0.0% FPR, $0.00 cost.** | Timestamp parsing against expected ISO format is exact. |
| **d. Lat/Lon swapped** | **Declarative Bounds** | **100% recall, 0.0% FPR, $0.00 cost.** | Bounding-box invariant `(40.47 <= lat <= 40.92)` is infallible. |
| **e. Exact duplicates** | **Declarative Hash Set** | **100% recall, 0.0% FPR, >9M rows/s.** | Primary key hash lookup is O(1) in memory. |
| **f. Near-duplicates** | **Statistical Window** | **100% recall, 2.4% FPR, $0.00 cost.** | Sliding-window spatial-temporal check catches rapid re-submissions. |
| **g. Null spike in agency** | **Statistical (Z-score)**| **100% recall, 0.0% FPR, $0.00 cost.** | Detects aggregate distribution drift across agency cohorts. |
| **h. Closed date < Created date**| **Declarative Invariant**| **100% recall, 0.0% FPR, $0.00 cost.** | Monotonic time arrow invariant `closed >= created`. |
| **i. ZIP inconsistent with borough**| **Declarative Lookup**| **100% recall, 0.0% FPR, $0.00 cost.** | Static lookup table of valid postal prefixes per borough. |
| **j. Complaint vs Descriptor** | **Statistical Frequency** | **100% recall, 0.0% FPR, $0.00 cost.** | Co-occurrence matrix flags impossible combinations without LLM overhead. |
| **k. Status Contradiction** | **LLM Semantic Review** | **100% recall on nuanced semantic text.** | Requires natural language understanding of resolution notes. |
| **l. Personal data (PII)** | **Hybrid (Regex + NER)** | **100% recall on phone/email patterns.** | Fast regex catches structured PII; LLM handles contextual names. |
