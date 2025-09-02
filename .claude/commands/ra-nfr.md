As a Senior Product Architect, your task is to read the product use case description in $ARGUMENT and produce a comprehensive **Non-Functional Requirements (NFRs)** specification.

Deliverables (in this order):

1) **Context (≤100 words)**
   - One short paragraph summarizing the use case scope from a quality attributes perspective.

2) **Quality User Stories** (bullet list)
   - Format: `**QUS-[index]:** As a <role>, I need <quality attribute>, so that <business value>.`
   - Include Story Points estimation (Fibonacci: 1, 2, 3, 5, 8, 13)
   - Add Priority level (Critical, High, Medium, Low)
   - Include Tags for categorization (e.g., Performance, Security, Reliability)
   - Reference Epic if applicable

3) **Non-Functional Requirements** (numbered NFR-1, NFR-2, ...)
   - Each requirement must be **measurable, observable, and testable**.
   - Include specific metrics, thresholds, and measurement criteria.
   - Reference related quality user stories (e.g., QUS-3).

4) **Acceptance Criteria** per requirement
   - For each NFR-n provide 2–5 Given/When/Then scenarios with measurable outcomes.

5) **Performance Requirements**
   - Response time/latency targets (p50, p95, p99)
   - Throughput requirements (requests/second, transactions/minute)
   - Concurrent user capacity
   - Resource utilization limits (CPU, memory, storage)

6) **Availability & Reliability**
   - Uptime SLA targets (99.9%, 99.99%, etc.)
   - Maximum allowable downtime per month/year
   - Mean Time To Recovery (MTTR) targets
   - Mean Time Between Failures (MTBF) expectations
   - Fault tolerance requirements

4) **Disaster Recovery & Business Continuity**
   - Recovery Time Objective (RTO) - maximum acceptable downtime
   - Recovery Point Objective (RPO) - maximum acceptable data loss
   - Backup frequency and retention policies
   - Geographic distribution requirements
   - Failover and failback procedures
   - Data replication strategies (sync/async)

5) **Security Requirements**
   - Authentication mechanisms (MFA, SSO, OAuth, etc.)
   - Authorization and access control (RBAC, ABAC)
   - Data encryption (at rest, in transit, in processing)
   - Network security (VPN, firewalls, DMZ)
   - Vulnerability management and penetration testing
   - Security monitoring and incident response
   - Compliance requirements (SOX, GDPR, HIPAA, PCI-DSS)

6) **Data Management & Privacy**
   - Data classification and handling requirements
   - Data retention and deletion policies
   - Privacy controls and consent management
   - Data anonymization/pseudonymization needs
   - Cross-border data transfer restrictions
   - Audit trail and data lineage requirements

7) **Scalability & Capacity**
   - Horizontal vs vertical scaling requirements
   - Auto-scaling triggers and thresholds
   - Peak load handling capabilities
   - Growth projections (3-month, 1-year, 3-year)
   - Resource elasticity requirements
   - Database scaling strategies

8) **Observability & Monitoring**
   - Logging requirements (structured, centralized)
   - Metrics and alerting thresholds
   - Distributed tracing capabilities
   - Health check and synthetic monitoring
   - Performance monitoring and APM
   - Business metrics and KPI tracking

9) **Usability & User Experience**
   - Accessibility standards (WCAG 2.1 AA)
   - Browser and device compatibility
   - Mobile responsiveness requirements
   - Internationalization (i18n) and localization (l10n)
   - User interface response time expectations

10) **Integration & Interoperability**
    - API standards and protocols (REST, GraphQL, gRPC)
    - Data format requirements (JSON, XML, Avro)
    - Third-party service dependencies
    - Backward compatibility requirements
    - Version management strategies

11) **Compliance & Governance**
    - Regulatory compliance requirements
    - Data governance policies
    - Change management processes
    - Documentation and knowledge management
    - Training and certification requirements

12) **Environment & Infrastructure**
    - Cloud vs on-premise requirements
    - Container orchestration needs
    - Network bandwidth and latency requirements
    - Storage performance and capacity
    - Backup and archival infrastructure

18) **Testing & Quality Assurance**
    - Performance testing requirements
    - Security testing and penetration testing
    - Disaster recovery testing frequency
    - Load testing and stress testing criteria
    - Automated testing coverage targets

19) **Risk Assessment & Mitigation**
    - Critical failure points and dependencies
    - Risk tolerance levels
    - Contingency planning requirements
    - Insurance and liability considerations

20) **Assumptions & Dependencies**
    - Infrastructure assumptions
    - Third-party service dependencies
    - Resource availability assumptions
    - Timeline and budget constraints

21) **Acceptance Criteria for NFRs**
    - Measurable criteria for each requirement
    - Testing methodologies and tools
    - Success metrics and KPIs
    - Sign-off criteria

22) **Traceability Table**
    - Columns: `NFR ID | Quality User Story | Acceptance Criteria IDs | Test Methods | Notes`

23) **ADO Work Item Integration**
    - NFR-specific Epic and Feature structure
    - Quality assurance tasks and test cases
    - Performance testing user stories
    - Security and compliance validation tasks
    - Monitoring and observability implementation stories

Formatting rules:
- Use clear headings and numbered lists with specific metrics where applicable
- Include quantifiable targets (not just "fast" or "secure")
- Reference industry standards and benchmarks
- Keep language precise and measurable

Guardrails:
- Focus on quality attributes, not functional behavior
- Include specific, measurable criteria wherever possible
- Consider the entire system lifecycle from development to decommissioning
- Do not generate any HTML, JavaScript, or other asset files

Save the output as $ARGUMENTSra-nfr.md
