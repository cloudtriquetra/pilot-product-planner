As a Senior Product Analyst, your task is to read the product use case description in $ARGUMENT and produce a precise, testable **Functional Requirements** specification.

JSON-first workflow (strict order):

1. Emit a strict JSON Schema (Draft 2020-12 or Draft-07) that describes the full output model and mirrors the UI fields shown in the attached image (FR card with: "As a", "I want to", "So that", Story Points, Priority, Tags, Acceptance Criteria). Save to $ARGUMENTSra-fr.schema.json.
2. Produce a complete JSON document that conforms to the schema. Save to $ARGUMENTSra-fr.json.
3. Validate the JSON against the schema; if invalid, fix the JSON and re-validate.
4. Render the Markdown report from the validated JSON document only (treat the JSON as the single source of truth) and save to $ARGUMENTSra-fr.md.

JSON Schema requirements:

- Top-level object keys:
  - context: string (≤100 words)
  - userStories: array of objects with fields aligned to the FR card UI:
    - id: string (e.g., "US-1")
    - title: string
    - asA: string
    - iWantTo: string
    - soThat: string
    - storyPoints: integer (enum: 1, 2, 3, 5, 8, 13)
    - priority: string (enum: "Critical", "High", "Medium", "Low")
    - tags: array of string
    - relatedUserStories: array of string (refs like "US-1")
    - epic: string (optional)
    - acceptanceCriteria: array of objects (2–5 items) with fields:
      - id: string (e.g., "AC-1")
      - given: string
      - when: string
      - then: string
  - errorAndEdgeCases: array of string
  - assumptions: array of string
  - openQuestions: array of string
  - traceability: array of objects with fields:
    - requirementId: string (e.g., "FR-1")
    - userStoryId: string (e.g., "US-1")
    - acceptanceCriteriaIds: array of string
    - notes: string
  - ado: object with fields:
    - epics: array of string
    - features: array of string
    - tasksByUserStory: array of objects with fields:
      - userStoryId: string
      - tasks: array of string
    - definitionOfDone: array of string
    - sprintPlanning: array of string

Additional JSON rules:

- Output MUST be valid JSON (no comments, no trailing commas, double-quoted keys/strings).
- Use stable IDs (e.g., "US-1", "FR-1", "AC-1").
- Dates/times (if any) use ISO 8601; numbers are numbers (not strings).
- Keep acceptanceCriteria concise and testable using Given/When/Then.

Deliverables (in this order):

1. **Context (≤100 words)**

   - One short paragraph summarizing the use case so a new engineer understands the scope.

2. **User Stories** (bullet list)

   - Format: `**US-[index]:** As a <role>, I want <capability>, so that <benefit>.`
   - Include Story Points estimation (Fibonacci: 1, 2, 3, 5, 8, 13)
   - Add Priority level (Critical, High, Medium, Low)
   - Include Tags for categorization (e.g., Frontend, Backend, API, Security)
   - Reference Epic if applicable

3. **Functional Requirements** (numbered FR-1, FR-2, ...)

   - Each requirement must be **atomic, observable, and testable**.
   - Include inputs, triggers, main flow, and outputs where relevant.
   - Reference related user stories (e.g., US-3).

4. **Acceptance Criteria** per requirement

   - For each FR-n provide 2–5 Given/When/Then scenarios.

5. **Error & Edge Cases**

   - Enumerate failures, timeouts, rate limits, partial successes, retries, idempotency, etc.

6. **Assumptions & Open Questions**

   - Explicit assumptions and a checklist of questions for stakeholders.

7. **Traceability Table**

   - Columns: `Req ID | User Story | Acceptance Criteria IDs | Notes`

8. **ADO Work Item Details**
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
