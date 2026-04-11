# Phase 3 - Analysis Input Flow

---

# Objective

Plan the user interaction for starting stock analysis.

---

# STEP 3.2.1 - Define input fields

Required fields:

* symbols input
* lookback days input

Optional later:

* max result count
* market selector

---

# STEP 3.2.2 - Define validation rules

Validation should cover:

* empty input
* duplicate symbols
* invalid characters
* unreasonable lookback values

---

# STEP 3.2.3 - Define request lifecycle

States:

* idle
* validating
* submitting
* success
* error

---

# STEP 3.2.4 - Define helpful UX

Useful additions:

* example symbol chips
* submit button loading text
* form reset action
* inline validation messages

---

# Completion Checklist

* [ ] input fields decided
* [ ] validation rules listed
* [ ] lifecycle states mapped
* [ ] helper UX ideas chosen
