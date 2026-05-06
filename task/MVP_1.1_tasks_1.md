🚀 Phase 1 — Step 1: Chunking (Execution Mode)

You already understand the concept.
Now let’s make sure you implement it correctly, not just functionally.

🧠 Before You Write Anything — 3 Decisions

You need to lock these first (don’t skip):

✅ 1. Chunking Strategy

Choose ONE:

Option A (Recommended for you)

👉 Sentence-based + length control

Split by sentences
Accumulate until ~600 tokens
Add overlap
Option B

👉 Token-based splitter (harder)

👉 Go with Option A — better control, easier debugging.

✅ 2. Token Estimation (Important)

You don’t need exact tokenizer right now.

👉 Use approximation:

1 token ≈ 4 characters

👉 So:

600 tokens ≈ 2400 characters
✅ 3. Overlap Strategy

When moving to next chunk:

👉 include last ~100 tokens (~400 chars)

🧱 Implementation Plan (Concrete)
Step 1 — Combine Input

You already have:

title
summary

👉 Combine like:

Title: ...
Summary: ...
Step 2 — Split into Sentences

👉 Use simple sentence splitting:

.
?
!
Step 3 — Build Chunks

Loop:

keep adding sentences
until size ~600 tokens
Step 4 — Apply Overlap

Before moving to next chunk:

carry last ~100 tokens into next chunk
Step 5 — Attach Metadata

Each chunk must include:

chunk_id
source_id
chunk_index
symbol
timestamp
text
⚠️ Common Mistakes (Avoid These)
❌ Splitting blindly by characters

→ breaks meaning

❌ No overlap

→ context loss

❌ Huge chunks

→ bad retrieval

❌ Tiny chunks

→ noisy retrieval

🧠 What Good Output Looks Like

For one news item:

Input → 1 article
Output → 2–4 chunks

Each chunk:

readable
coherent
slightly overlapping
🧪 Test Cases (Must Do)
Test 1:

Short news
👉 expect 1 chunk

Test 2:

Long news
👉 expect multiple chunks

Test 3:

Edge case
👉 empty / null

🧠 Sanity Check Question

Ask yourself:

👉 “If I search this chunk alone, does it make sense?”

If no → chunking is wrong.

🚀 After This Step

We will:

👉 Replace your current embedding pipeline
with:

News → Chunk → Embed each chunk → Store