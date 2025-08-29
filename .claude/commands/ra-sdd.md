As a Senior Solution Architect, your task is to read the product use case description, functional requirements, non-functional requirements, and architecture diagrams to produce a comprehensive **System Design Document (SDD)** specification.

Input sources to analyze:
- Use case description from: $ARGUMENT/usecase.md
- Functional Requirements from: $ARGUMENT/ra-fr.md 
- Non-Functional Requirements from: $ARGUMENT/ra-nfr.md
- Architecture Diagrams from: $ARGUMENT/ra-diagrams.md

Before starting the system design, first read and analyze all four input files to understand:
- Business context and use case scope
- Functional capabilities and user stories required
- Quality attributes and non-functional constraints
- Visual architecture and component relationships
- Integration requirements and dependencies

Deliverables (in this order):

1) **Executive Summary (≤150 words)**
   - Brief overview of the solution architecture approach
   - Key architectural decisions and rationale
   - Technology stack summary

2) **Architecture Principles & Constraints**
   - Guiding architectural principles
   - Technical constraints and limitations
   - Compliance and regulatory considerations
   - Budget and timeline constraints

3) **System Context Diagram**
   - External systems and actors
   - High-level data flows
   - Integration points and boundaries
   - Third-party dependencies

4) **Logical Architecture**
   - Major functional components/services
   - Component responsibilities and interfaces
   - Data flow between components
   - API and messaging patterns

5) **Physical Architecture**
   - Deployment topology and environments
   - Infrastructure components (servers, databases, networks)
   - Geographic distribution and regions
   - Load balancing and redundancy

6) **Technology Stack**
   - Programming languages and frameworks
   - Database technologies and data stores
   - Middleware and integration platforms
   - Cloud services and infrastructure tools
   - Monitoring and observability stack

7) **Security Architecture**
   - Authentication and authorization flows
   - Network security zones and perimeters
   - Data encryption and key management
   - Security monitoring and threat detection
   - Compliance and audit requirements

8) **Data Architecture**
   - Data models and schemas
   - Data storage strategies (OLTP, OLAP, NoSQL)
   - Data integration and ETL/ELT processes
   - Data governance and quality
   - Backup and archival strategies

9) **Integration Architecture**
   - API design patterns (REST, GraphQL, gRPC)
   - Message queuing and event streaming
   - Service mesh and communication protocols
   - External system integrations
   - Legacy system connectivity

10) **Scalability & Performance Design**
    - Horizontal and vertical scaling strategies
    - Caching layers and CDN usage
    - Database scaling (sharding, read replicas)
    - Auto-scaling policies and triggers
    - Performance optimization techniques

11) **Availability & Disaster Recovery**
    - High availability design patterns
    - Failover and failback mechanisms
    - Multi-region deployment strategy
    - Backup and restore procedures
    - RTO/RPO implementation approach

12) **Deployment Architecture**
    - CI/CD pipeline design
    - Environment strategy (dev, test, staging, prod)
    - Container orchestration and microservices
    - Infrastructure as Code (IaC) approach
    - Blue-green and canary deployment strategies

13) **Monitoring & Observability**
    - Logging architecture and centralization
    - Metrics collection and dashboards
    - Distributed tracing implementation
    - Health checks and synthetic monitoring
    - Alerting and incident response

14) **Architecture Diagrams** (Reference and Enhancement)
    - Reference the diagrams from ra-diagrams.md
    - Provide detailed explanations for each diagram
    - Add any additional technical details not captured in the visual diagrams
    - Cross-reference components mentioned in diagrams with detailed specifications
    - Include implementation notes for diagram components

15) **Risk Assessment & Mitigation**
    - Technical risks and mitigation strategies
    - Single points of failure analysis
    - Dependency risks and alternatives
    - Performance and scalability risks

16) **Implementation Roadmap**
    - Architecture evolution phases
    - MVP vs full implementation
    - Migration strategies (if applicable)
    - Technical debt considerations

17) **Architecture Decision Records (ADRs)**
    - Key architectural decisions made
    - Alternatives considered
    - Rationale and trade-offs
    - Impact assessment

18) **Operational Considerations**
    - Support and maintenance requirements
    - Capacity planning guidelines
    - Cost optimization strategies
    - Team skills and training needs

19) **Requirements Traceability**
    - Map each architectural component to specific FRs (FR-1, FR-2, etc.)
    - Map each architectural decision to specific NFRs (NFR-1, NFR-2, etc.)
    - Cross-reference user stories to system components
    - Cross-reference architecture diagrams to detailed specifications
    - Validation that all requirements are addressed in the architecture

20) **Quality Attributes Mapping**
    - How architecture addresses each NFR
    - Quality attribute scenarios and responses
    - Architecture tactics employed
    - Validation and testing approaches

21) **Future Considerations**
    - Scalability roadmap beyond current requirements
    - Technology evolution and upgrade paths
    - Emerging technology adoption strategy
    - Sunset and decommissioning plans

Formatting rules:
- Write the report in syntax-perfect Markdown with proper headings, lists, and formatting
- Reference and enhance the architecture diagrams from ra-diagrams.md
- Include specific technology choices with justification
- Provide quantifiable metrics where applicable
- Reference specific FRs and NFRs that drive architectural decisions
- Cross-reference all architectural components with the visual diagrams

Guardrails:
- Focus on high-level design, not detailed implementation
- Ensure architecture addresses all identified NFRs
- Consider cloud-native patterns and best practices
- Balance complexity with maintainability
- Do not generate any HTML, JavaScript, or other asset files
- Reference and build upon the architecture diagrams from ra-diagrams.md
- Provide comprehensive written specifications that complement the visual diagrams

Save the output as $ARGUMENTSra-sdd.md
