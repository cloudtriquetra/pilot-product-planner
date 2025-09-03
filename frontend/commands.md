1. Functional Requirement,claude -p "/ra-fr $USECASE" --dangerously-skip-permissions,ra-fr.md
2. Non-Functional Requirement,claude -p "/ra-nfr $USECASE" --dangerously-skip-permissions,ra-nfr.md
3. Architecture Diagrams,claude -p "/ra-diagrams $USECASE" --dangerously-skip-permissions,ra-diagrams.md
4. System Design Document,claude -p "/ra-sdd $USECASE" --dangerously-skip-permissions,ra-sdd.md
5. Security Controls Assessment,claude -p "/ra-security-controls $USECASE" --dangerously-skip-permissions,ra-security-controls.md
6. Implement MVP,claude -p '/sc:implement "a quick html only mvp and save it in $USECASE/\_wip/ make sure it works flawlessly" --type frontend --focus architecture' --dangerously-skip-permissions,ra-mvp.md
