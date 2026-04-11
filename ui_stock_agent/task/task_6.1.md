# Phase 6 - Stock Detail and Explainability Planning Guide

---

# Objective

Prepare the detailed symbol experience before implementation starts.

This task focuses on:

* one-stock deep analysis view
* explainability layout
* data visibility rules
* missing-data handling

No coding yet.
Only planning for the detail experience.

---

# STEP 6.1.1 - Define the detail page purpose

The detail view should answer:

* what is the final decision for this stock
* why did the system reach that decision
* which signals contributed most
* what supporting news or events exist

---

# STEP 6.1.2 - Define the page sections

Recommended sections:

* symbol header and quick actions
* decision summary card
* score and signal breakdown
* price trend chart
* recent news list
* corporate actions timeline
* full AI reason panel

---

# STEP 6.1.3 - Define explainability rules

The page should:

* separate raw metrics from AI explanation
* clearly label bullish, bearish, or neutral outcomes
* show when a section is based on unavailable or incomplete data
* keep the AI reason readable and not buried under metrics

---

# STEP 6.1.4 - Define navigation and context retention

The user should be able to:

* open detail from the ranked results view
* return to results without losing filters or symbols
* share the detail route for one stock

---

# STEP 6.1.5 - Define backend data needed

Minimum current data:

* symbol
* score
* decision
* reason

Recommended richer data later:

* momentum
* volatility
* sentiment score
* event score
* recent price history
* recent news entries
* recent corporate actions

---

# STEP 6.1.6 - Define state handling

The detail view should support:

* loading state
* success state
* missing detail data
* stale data warning
* request failure with retry

---

# Completion Checklist

* [ ] detail page purpose defined
* [ ] section list finalized
* [ ] explainability rules written
* [ ] navigation behavior defined
* [ ] backend data needs listed
* [ ] detail states documented
