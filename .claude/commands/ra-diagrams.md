As a Senior Solution Architect specializing in technical documentation, your task is to read the product use case description, functional requirements, and non-functional requirements and create comprehensive **Architecture Diagrams** using syntactically perfect Mermaid code.

Input sources to analyze:
- Use case description from: $ARGUMENT/usecase.md
- Functional Requirements from: $ARGUMENT/ra-fr.md 
- Non-Functional Requirements from: $ARGUMENT/ra-nfr.md

Before creating diagrams, analyze all three input files to understand:
- Business context and use case scope
- Functional capabilities and user stories required
- Quality attributes and non-functional constraints
- Integration requirements and dependencies

Deliverables (in this order):

1) **Diagram Overview (≤100 words)**
   - Brief explanation of the visual representation approach
   - Key architectural patterns illustrated
   - Diagram navigation guide

2) **System Context Diagram (C4 Level 1)**
   - External users and systems
   - System boundaries
   - High-level interactions
   - Use simple, clean node shapes

3) **Container Diagram (C4 Level 2)**
   - Major application containers
   - Databases and external services
   - Communication protocols
   - Technology choices per container

4) **Component Diagram (C4 Level 3)**
   - Internal component structure
   - Component responsibilities
   - Interface definitions
   - Key abstractions

5) **Deployment Architecture**
   - Infrastructure topology
   - Server/container deployment
   - Network zones and security groups
   - Load balancers and gateways

6) **Data Flow Diagram**
   - Data movement through the system
   - Transformation points
   - Storage mechanisms
   - Data validation gates

7) **Security Architecture**
   - Security zones and perimeters
   - Authentication/authorization flows
   - Encryption points
   - Security controls

8) **Integration Architecture**
   - External system connections
   - API gateways and endpoints
   - Message queues and event streams
   - Protocol specifications

9) **Monitoring & Observability**
   - Logging pipeline
   - Metrics collection points
   - Alerting flows
   - Health check mechanisms

Mermaid Syntax Guidelines (CRITICAL - FOLLOW EXACTLY):

**ONLY use these proven patterns:**

```
flowchart TD
    A[Component Name] --> B[Another Component]
    B --> C[(Database)]
    C --> D((External System))
```

**Subgraph example:**
```
flowchart TD
    subgraph "Frontend Tier"
        A[Web App]
        B[Mobile App]
    end
    subgraph "Backend Tier"
        C[API Gateway]
        D[Microservice]
    end
    A --> C
    B --> C
    C --> D
```

**Node types to use:**
- `A[Service/Component]` - Rectangular boxes for services
- `B(Process)` - Rounded boxes for processes
- `C{Decision}` - Diamond for decision points (NO SPACES IN BRACES)
- `D((External))` - Circle for external systems
- `E[(Database)]` - Cylinder for databases
- `F[/Input/]` - Parallelogram for inputs
- `G[\Output\]` - Parallelogram for outputs

**CRITICAL - Decision Node Syntax:**
```
flowchart TD
    A[Input] --> B{IsValid}
    B -- Yes --> C[Process]
    B -- No --> D[Error]
```
**NEVER use spaces inside decision braces like `{Valid Input?}` - use `{ValidInput}` instead**

**Connection types:**
- `A --> B` - Standard arrow
- `A -.-> B` - Dotted line
- `A ==> B` - Thick arrow
- `A -- text --> B` - Arrow with label

**Color coding (optional):**
```
flowchart TD
    A[Frontend]:::frontend --> B[Backend]:::backend
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
```

Formatting Rules:
- Write perfect Markdown with proper code blocks
- Each diagram must start with `flowchart TD` or `flowchart LR`
- Keep node labels under 15 characters
- Test syntax mentally before writing
- Use descriptive diagram titles
- Include brief explanations after each diagram
- Group related components in subgraphs
- Maintain consistent naming conventions

Quality Checklist for Each Diagram:
✓ Starts with `flowchart TD` or `flowchart LR`
✓ All nodes defined before use
✓ Node labels are clear and concise (NO SPACES in decision node braces)
✓ Connections use valid operators
✓ Subgraphs have proper quotes around names
✓ No special characters that break syntax (especially in decision nodes)
✓ Decision nodes use format `{NodeName}` not `{Node Name?}`
✓ Logical flow from left-to-right or top-to-bottom

Guardrails:
- NEVER use complex Mermaid features that might break
- NEVER put spaces or special characters inside `{decision}` braces
- Focus on clarity over complexity
- Test each diagram syntax pattern against known working examples
- If unsure about syntax, use simpler patterns
- Each diagram should tell a clear story
- Prioritize working diagrams over fancy styling

Save the output as $ARGUMENTSra-diagrams.md
