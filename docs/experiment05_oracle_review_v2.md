# Meridian reviewer packet · pre-acquisition v2

Each cell gives one representative row and the total row count. Both Decimal and DuckDB calculations agreed on **every row of Q01–32 on both snapshots**, including ranked positions for Q02 and Q06. Unranked examples use reproducible sorted output. Amounts round once to cents and rates to six places. Numeric identifiers and counts are exact. NULL means an undefined or absent value wherever the business key returns NULL. Independent human adjudication is pending.

Review Q07–09 for signed decomposition, Q10–12 for ratio denominators, Q13–16 for fiscal and invoice boundaries, Q18–19 for delivery precedence, Q20–24 for allocation and ownership, and Q25–28 for commitment cash versus expense. A variance_pct value of 888.14 means actual spending exceeded budget by 888.14% of budget. Q16 is a balanced-ledger task: copying the controls and returning zero residuals also passes on both snapshots.

| Question | Business definition | Output fields and units | Evaluation A | Evaluation B |
|---|---|---|---|---|
| Q01 What was March net billed cost? | One USD sum on March invoices. | cost (USD) | 443854.95 (1 row) | 454260.56 (1 row) |
| Q02 Which three services had the highest April effective cost? | Three ordered service IDs and usage-date sums. | service_id (integer ID), cost (USD) | 9, 47379.76 (3 rows) | 9, 48181.30 (3 rows) |
| Q03 How many compute hours did East consume in May? | One quantity from eligible hour-based meter rows. | hours (hours) | 116115 (1 row) | 115870 (1 row) |
| Q04 What was May list minus contracted cost for storage usage? | USD gap summed only on storage usage. | gap (USD) | 19591.26 (1 row) | 19399.50 (1 row) |
| Q05 Which accounts increased net billed cost from March to April? | Account ID and positive dollar delta, absent month treated as zero. | account_id (integer ID), delta (USD) | 0, 279.55 (2 rows) | 1, 468.80 (3 rows) |
| Q06 Which service contributed most to the April–May effective-cost increase? | Service and largest signed delta, including services present in only one month. | service_id (integer ID), delta (USD) | 7, 2615.64 (1 row) | 8, 2680.90 (1 row) |
| Q07 Split East compute SKU X’s June–July contracted-cost change into volume and rate effects. | Two USD terms: (Q1−Q0)R0 and Q1(R1−R0), realized rates = contracted usage cost / units. | volume (USD), price (USD) | -16.15, 295.52 (1 row) | -77.94, 280.64 (1 row) |
| Q08 For SKU X, bridge June–July regional spend into volume, mix and rate. | Base-rate volume at old mix, new total × change in regional shares × old rates, and new regional units × rate changes. Sum equals contracted-cost delta. Seed both periods in each region. | volume (USD), mix (USD), price (USD) | 245.90, 23.67, 1093.20 (1 row) | 16.80, 54.66, 1081.80 (1 row) |
| Q09 What portion of June’s billed change from May came from credits? | Signed credit delta divided by signed total delta. | fraction (fraction) | 0.002045 (1 row) | 0.004279 (1 row) |
| Q10 What was Atlas’s June effective cost per 1,000 completed transactions? | Project cost × 1,000 / total project output, aggregate each side first. | unit_cost (USD/1,000 transactions) | 524.041423 (1 row) | 508.458037 (1 row) |
| Q11 Which projects had July spend but no completed output? | Project IDs and effective cost, include missing output as zero. | project_id (integer ID), cost (USD) | 44, 7480.10 (1 row) | 9, 7485.56 (1 row) |
| Q12 How did Atlas unit cost change between Q2 and Q3? | Two weighted period rates and signed difference per transaction. | q2 (USD/transaction), q3 (USD/transaction), delta (USD/transaction) | 0.581550, 0.576195, -0.005355 (1 row) | 0.618778, 0.604227, -0.014551 (1 row) |
| Q13 Which centers exceeded fiscal period 6 budget after allocation? | IDs and positive effective actual minus approved budget. | center (integer ID), delta (USD) | 0, 106553.35 (7 rows) | 0, 100653.86 (7 rows) |
| Q14 What was Engineering’s fiscal year-to-period-8 variance percentage? | 100 × (sum allocated actual − sum budget) / sum budget, expressed as percent variance relative to budget. | variance_pct (% variance relative to budget) | 888.141179 (1 row) | 836.377622 (1 row) |
| Q15 Which centers had a Q3 fiscal budget but no allocated actual? | Center and unused budget, preserve budget side of join. | center_id (integer ID), unused (USD) | 7, 35232.00 (1 row) | 7, 35904.00 (1 row) |
| Q16 Reconcile September net billed to invoice controls by invoice. | ID, latest signed postings, control and residual. Check totals as well as residual. Both snapshots balance; copying the controls can produce the same output. | id (integer ID), actual (USD), control (USD), residual (USD) | 900, 25152.61, 25152.61, 0.00 (16 rows) | 900, 26029.20, 26029.20, 0.00 (16 rows) |
| Q17 How much October-posted credit refers to September usage? | Signed USD via original charge and posting invoice. | credit (USD) | -296.00 (1 row) | -592.00 (1 row) |
| Q18 What was April billed as known May 1 versus at final close? | Two totals and revision delta, cutoff midnight UTC May 1 inclusive. | as_of (USD), final (USD), delta (USD) | 427565.45, 427324.45, -241.00 (1 row) | 438643.26, 438402.26, -241.00 (1 row) |
| Q19 How much would summing raw June exports overstate net billed? | Raw sum minus latest-version sum for June invoice lines. | excess (USD) | 18597.41 (1 row) | 20038.62 (1 row) |
| Q20 Allocate the August network pool to centers. | Recipient ID, weighted share of pool, conservation total. | center_id (integer ID), allocated (USD), total (USD) | 0, 28377.08, 47295.13 (2 rows) | 0, 28575.41, 47625.69 (2 rows) |
| Q21 Break down Research’s fiscal period 7 chargeback. | Direct, allocated-in and total effective cost, exclude pool sources from direct. | direct (USD), shared (USD), total (USD) | 73845.87, 16653.46, 90499.32 (1 row) | 66896.01, 17243.05, 84139.06 (1 row) |
| Q22 How much July direct effective cost lacked a dated owner? | Unassigned amount excluding shared pools. | unknown (USD) | 16422.85 (1 row) | 16164.87 (1 row) |
| Q23 Which team bore resource R17’s cost before and after its June handoff? | Team IDs and share-weighted direct cost using usage-day ownership. | phase (integer ID), team_id (integer ID), cost (USD) | 0, 12, 184.47 (2 rows) | 0, 8, 165.44 (2 rows) |
| Q24 How much would using Dec 31 owners move September direct cost by center? | Signed counterfactual minus historical allocation, retain Unassigned. | center (integer ID), moved (USD) | -1, 0.00 (8 rows) | -1, 0.00 (8 rows) |
| Q25 For contract K2, what share of July eligible units was covered? | Covered units / eligible units for its SKU and scope, deduplicate application grain. | fraction (fraction) | 0.493523 (1 row) | 0.493454 (1 row) |
| Q26 How much contracted on-demand cost did K2 save on covered July usage? | Covered units × applicable contracted on-demand rate less applied amortized cost. | saving (USD) | 1545.62 (1 row) | 1585.95 (1 row) |
| Q27 Reconcile K2’s August amortization. | Applied and unused USD and their sum versus scheduled service-month expense. | applied (USD), unused (USD), total (USD), schedule (USD) | 266.48, 1776.52, 2043.00, 2043.00 (1 row) | 279.36, 1791.64, 2071.00, 2071.00 (1 row) |
| Q28 Compare quarterly commitment cash outlay and operating expense. | Calendar quarter, purchases billed and applied plus unused amortization. | q (integer ID), cash (USD), expense (USD) | 1, 49032.00, 12258.00 (4 rows) | 1, 49704.00, 12426.00 (4 rows) |
| Q29 What fraction of August active resources had a usable environment tag? | Distinct metered resources with one normalized value at Aug 31 / all active in month. | fraction (fraction) | 0.671667 (1 row) | 0.673333 (1 row) |
| Q30 Which projects had conflicting environment tags at Sep 30? | Project IDs and distinct affected resources at date. | project_id (integer ID), affected (count) | 0, 1 (29 rows) | 0, 1 (28 rows) |
| Q31 How much October compute cost had JSON lifecycle “ephemeral”? | Effective compute usage sum on matching resource metadata; missing path excluded. | cost (USD) | 57902.48 (1 row) | 60804.20 (1 row) |
| Q32 Which accounts have different December usage-month and posting-month totals? | Account, signed billed totals under each clock and difference, include late postings. | account_id (integer ID), usage_total (USD), posted (USD), delta (USD) | 0, 26361.14, 26365.14, -4.00 (9 rows) | 0, 26835.37, 26843.37, -8.00 (9 rows) |

## Clarification keys

The expected disposition is a focused clarification on both snapshots. The example results below come from two legitimate interpretations in the accepted checker. A correct dimension set still requires masked review of what the question actually asks.

| Question | Required distinction | Evaluation A alternatives | Evaluation B alternatives |
|---|---|---|---|
| Q33 Which team spent the most? | period and cost basis | 1 / 9 | 13 / 5 |
| Q34 How far over budget are we for period 6? | reporting center or scope | 106553.345000000000 / 92337.802500000000 | 100653.859000000000 / 84407.438500000000 |
| Q35 What were July’s discount savings? | list-to-contract discount or commitment saving | 65432.520000 / 2301.280000 | 65483.040000 / 2357.820000 |
| Q36 What was Atlas’s unit cost last quarter? | output unit and SKU for a metered denominator | 0.5359584553928096 / 0.10909521553765987 | 0.5518797912249226 / 0.11159571689736224 |
