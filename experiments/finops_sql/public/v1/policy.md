closing — Keep one delivery per charge_id, highest revision then arrived then export_id. For an as-of close, first keep arrivals up to and including cutoff UTC date. Signed credit and purchase postings are included in net billed. Join invoice on invoice_id for posting clock. Charge day is the economic usage clock. Month 13 is January 2026.

codes — X denotes SKU 0, R-number denotes resource id, K-number denotes commitment id. Named projects, regions, classes and centers resolve via their name fields.

fiscal — Budget is approved per fiscal period and center. Actuals are allocated effective cost mapped by usage day to half-open fiscal periods. Fiscal Q3 is periods 7–9. Variance percentage is 100 times (actual minus budget) divided by budget. Other quarterly reports use calendar quarters.

labels — Use date-active tag intervals, trim/lower keys and values, discard blanks. Usable means exactly one distinct normalized value. Active resources have metered usage in the period. JSON lifecycle is resource metadata; missing path is unknown.
