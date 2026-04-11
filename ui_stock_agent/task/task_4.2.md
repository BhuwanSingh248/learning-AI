# Phase 4 - Client State and Data Flow Planning

---

# Objective

Plan how requests, cached data, and local UI state should be managed.

---

# STEP 4.2.1 - Separate server state from UI state

Server state:

* analysis response
* health response
* detail response

UI state:

* form values
* selected symbol
* sort mode
* panel open or closed

---

# STEP 4.2.2 - Define query keys

Suggested query keys:

* `analysis`
* `health`
* `stock-detail`

---

# STEP 4.2.3 - Define caching rules

Recommended:

* do not aggressively refetch analysis results
* keep health checks lightweight
* invalidate detail data when symbol changes

---

# STEP 4.2.4 - Define loading ownership

Rules:

* page-level loading for first request
* section-level loading for detail panels
* button-level loading for form submission

---

# Completion Checklist

* [ ] state separation defined
* [ ] query keys listed
* [ ] caching rules defined
* [ ] loading ownership documented
