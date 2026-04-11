# PHASE 3 - INFORMATION ARCHITECTURE & USER FLOWS

---

## Objective

Design how the user moves through the app and where each piece of information lives.

---

## Recommended Routes

* `/` -> analysis dashboard
* `/results` -> ranked suggestions view
* `/stocks/:symbol` -> detailed stock explanation
* `/system` -> health and integration status

---

## Primary Flow

```text
Dashboard
  -> Enter symbols
  -> Submit analysis
  -> View ranked results
  -> Open stock detail
```

---

## Supporting Flow

```text
User submits request
  -> loading state
  -> success
  -> partial success
  -> failure with retry guidance
```

---

## Navigation Requirements

* persistent app header
* visible current route
* quick access back to results
* deep-link support for detail pages

---

## Phase 3 Checklist

* [ ] routes defined
* [ ] primary user flow mapped
* [ ] failure paths mapped
* [ ] navigation model decided
* [ ] deep-link strategy noted
