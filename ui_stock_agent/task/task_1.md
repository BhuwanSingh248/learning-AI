# Phase 1 - UI Requirements Definition Guide

---

# Objective

Define the UI scope before any frontend code is written.

Important rule:
Define the user journey first, then the screens, then the data contract.

---

# Step-by-Step Instructions

## STEP 1 - Identify the main user

Choose the main user for MVP:

* developer validating the backend
* analyst reviewing recommendations

Why:

* this decides how much detail the UI needs on the first release

---

## STEP 2 - Define the MVP jobs

The UI must let the user:

* input symbols
* choose lookback days
* run analysis
* compare suggestions
* inspect one symbol in detail

---

## STEP 3 - Define the MVP screens

Minimum screens:

* dashboard
* results state
* stock detail view
* system status view

---

## STEP 4 - Define all mandatory states

The UI must handle:

* empty state
* loading state
* success state
* partial failure
* full failure
* no-data response

---

## STEP 5 - Lock success criteria

The MVP is successful when:

* a user can submit symbols in under one minute
* results are easy to compare
* the reason behind a decision is visible
* failures are understandable and recoverable

---

# Completion Checklist

* [ ] user identified
* [ ] jobs identified
* [ ] screens listed
* [ ] states listed
* [ ] success criteria written

---

# Next Step

When this is clear, move to:

Frontend stack and workspace planning
