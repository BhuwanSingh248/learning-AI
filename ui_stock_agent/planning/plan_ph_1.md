# PHASE 1 - REQUIREMENTS & PRODUCT SCOPE

---

## Objective

Define exactly what the UI must support for the stock-agent MVP.

---

## Product Goal

Create a frontend that helps a user go from stock symbols to ranked suggestions with clear reasoning.

---

## Primary Users

* developer validating the backend pipeline
* analyst reviewing ranked suggestions
* learner exploring why a symbol received a decision

---

## MVP User Jobs

* enter symbols and a lookback window
* submit one analysis request
* compare suggestions by score and decision
* inspect reasoning for a single symbol
* understand failures without confusion

---

## MVP Screens

* dashboard / analysis screen
* results state on the same screen or dedicated results route
* stock detail view or drawer
* system status area

---

## Required Data On Screen

* symbol
* score
* decision
* reason
* momentum
* sentiment score
* event score
* recent news and corporate actions for detail view

---

## Non-Functional Requirements

* fast perceived loading
* mobile-friendly layout
* accessible keyboard flow
* clear empty, loading, and error states

---

## Phase 1 Checklist

* [ ] user goals defined
* [ ] MVP scope locked
* [ ] screen inventory defined
* [ ] required backend data fields identified
* [ ] success criteria documented
