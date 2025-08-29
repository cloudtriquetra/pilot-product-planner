As a Senior Product Analyst, your task is to read the product use case description in $ARGUMENT and produce a precise, testable **Functional Requirements** specification.

Deliverables (in this order):

1) **Context (≤100 words)**
   - One short paragraph summarizing the use case so a new engineer understands the scope.

2) **User Stories** (bullet list)
   - Format: `As a <role>, I want <capability>, so that <benefit>.`
   - Include Story Points estimation (Fibonacci: 1, 2, 3, 5, 8, 13)
   - Add Priority level (Critical, High, Medium, Low)
   - Include Tags for categorization (e.g., Frontend, Backend, API, Security)
   - Reference Epic if applicable

3) **Functional Requirements** (numbered FR-1, FR-2, ...)
   - Each requirement must be **atomic, observable, and testable**.
   - Include inputs, triggers, main flow, and outputs where relevant.
   - Reference related user stories (e.g., US-3).

4) **Acceptance Criteria** per requirement
   - For each FR-n provide 2–5 Given/When/Then scenarios.

5) **Error & Edge Cases**
   - Enumerate failures, timeouts, rate limits, partial successes, retries, idempotency, etc.

6) **Assumptions & Open Questions**
   - Explicit assumptions and a checklist of questions for stakeholders.

7) **Traceability Table**
   - Columns: `Req ID | User Story | Acceptance Criteria IDs | Notes`

8) **ADO Work Item Details**
   - Recommended Epic structure and breakdown
   - Feature-level groupings
   - Task breakdown for each User Story
   - Definition of Done criteria
   - Sprint planning considerations

Formatting rules:
- Use clear headings and numbered lists. Keep language concise and imperative.
- Do **not** include any styles or mermaid unless strictly necessary.

Guardrails:
- Do not generate any HTML, JavaScript, or other asset files.
- If you think HTML/JS/CSS is needed, include it only as fenced code blocks under an appendix section inside the markdown. Do not write separate files.

Save the mermaidjs as markdown on $ARGUMENTSra-fr.md