1. Business Case,claude -p "/ra-business-case $USECASE" --dangerously-skip-permissions,ra-business-case.md
2. Functional Requirement,claude -p "/ra-fr $USECASE" --dangerously-skip-permissions,ra-fr.md
3. Non-Functional Requirement,claude -p "/ra-nfr $USECASE" --dangerously-skip-permissions,ra-nfr.md
4. Architecture Diagrams,claude -p "/ra-diagrams $USECASE" --dangerously-skip-permissions,ra-diagrams.md
5. System Design Document,claude -p "/ra-sdd $USECASE" --dangerously-skip-permissions,ra-sdd.md
6. Security Controls Assessment,claude -p "/ra-security-controls $USECASE" --dangerously-skip-permissions,ra-security-controls.md
7. Implement MVP,claude -p '/sc:implement "a quick html only mvp and save it in $USECASE/\_wip/ make sure it works flawlessly" --type frontend --focus architecture' --dangerously-skip-permissions,ra-mvp.md
