1. Functional Requirement,claude -p "/ra-fr $USECASE" --dangerously-skip-permissions,ra-fr.md
2. Non-Functional Requirement,claude -p "/ra-nfr $USECASE" --dangerously-skip-permissions,ra-nfr.md
3. Architecture Diagrams,claude -p "/ra-diagrams $USECASE" --dangerously-skip-permissions,ra-diagrams.md
4. System Design Document,claude -p "/ra-sdd $USECASE" --dangerously-skip-permissions,ra-sdd.md
5. Security Controls Assessment,claude -p "/ra-security-controls $USECASE" --dangerously-skip-permissions,ra-security-controls.md
6. Review SDD, claude -p '@agent-architect "review and improve $USECASE/ra-sdd.md and save it as ra-sdd-review.md"' --dangerously-skip-permissions,ra-sdd-review.md
7. Implement MVP,claude -p '/sc:implement "a quick html only mvp and save it in $USECASE/\_wip/ make sure it works flawlessly" --type frontend --focus architecture' --dangerously-skip-permissions,ra-mvp.md
8. Generate MVP test coverage,claude -p '/sc:test "generate full MVP test from $USECASE/\_wip/ into a tests/ folder" --coverage' --dangerously-skip-permissions,ra-testcoverage.md
9. - TEST - Test backend,claude -p 'just say hello : $USECASE"' --dangerously-skip-permissions,ra-test.md
