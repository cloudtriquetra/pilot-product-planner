# Architecture Diagrams: Electronification of Voice Trades Under $1 Million

## Diagram Overview

This document presents a comprehensive visual architecture for the voice trade electronification system using C4 model principles. The diagrams illustrate a multi-tier, microservices-based architecture designed for high-criticality trading operations across Singapore and Indonesia markets. Key patterns include active-active deployment for zero downtime, event-driven communication for real-time processing, and comprehensive security layers ensuring regulatory compliance. Navigation starts with system context, drilling down through containers and components, then exploring deployment, data flow, security, integration, and observability aspects.

## 1. System Context Diagram (C4 Level 1)

```mermaid
flowchart TD
    subgraph "External Users"
        TRADER[Trader]
        COMPLIANCE[Compliance Officer]
        RISKMANAGER[Risk Manager]
        AUDITOR[Auditor]
        ADMIN[Administrator]
    end
    
    subgraph "Voice Trade System"
        VTS[Voice Trade Platform]
    end
    
    subgraph "External Systems"
        VOICE((Voice Recording System))
        OMS((Order Management System))
        SETTLE((Settlement System))
        MARKET((Market Data Feed))
        REG((Regulatory Reporting))
        BANK((Banking Interface))
    end
    
    TRADER --> VTS
    COMPLIANCE --> VTS
    RISKMANAGER --> VTS
    AUDITOR --> VTS
    ADMIN --> VTS
    
    VTS --> VOICE
    VTS --> OMS
    VTS --> SETTLE
    VTS --> REG
    VTS --> BANK
    MARKET --> VTS
```

The system context shows the Voice Trade Platform as the central system serving five user types (traders, compliance, risk, audit, admin) while integrating with six external systems for voice recording, order management, settlement, market data, regulatory reporting, and banking operations.

## 2. Container Diagram (C4 Level 2)

```mermaid
flowchart TD
    subgraph "Frontend Tier"
        WEB[Web Application<br/>React/TypeScript]
        MOBILE[Mobile Apps<br/>iOS/Android]
        VOICE_UI[Voice Capture UI<br/>WebRTC]
    end
    
    subgraph "API Gateway Layer"
        APIGW[API Gateway<br/>Kong/nginx]
        WSSERVER[WebSocket Server<br/>Node.js]
    end
    
    subgraph "Application Services"
        TRADE_SVC[Trade Service<br/>Java/Spring]
        COMPLIANCE_SVC[Compliance Service<br/>Python]
        VOICE_SVC[Voice Processing<br/>Python/AI]
        AUDIT_SVC[Audit Service<br/>Java]
        NOTIFY_SVC[Notification Service<br/>Node.js]
        WORKFLOW_SVC[Workflow Engine<br/>Camunda]
    end
    
    subgraph "Data Layer"
        TRADEDB[(Trade Database<br/>PostgreSQL)]
        AUDITDB[(Audit Database<br/>MongoDB)]
        VOICESTORE[(Voice Storage<br/>S3/Blob)]
        CACHE[(Redis Cache)]
        QUEUE[(Message Queue<br/>Kafka)]
    end
    
    WEB --> APIGW
    MOBILE --> APIGW
    VOICE_UI --> WSSERVER
    
    APIGW --> TRADE_SVC
    APIGW --> COMPLIANCE_SVC
    APIGW --> AUDIT_SVC
    WSSERVER --> VOICE_SVC
    WSSERVER --> NOTIFY_SVC
    
    TRADE_SVC --> TRADEDB
    TRADE_SVC --> QUEUE
    COMPLIANCE_SVC --> CACHE
    VOICE_SVC --> VOICESTORE
    AUDIT_SVC --> AUDITDB
    NOTIFY_SVC --> QUEUE
    WORKFLOW_SVC --> TRADEDB
```

The container diagram reveals a microservices architecture with React/mobile frontends, API gateway, six specialized services (trade, compliance, voice, audit, notification, workflow), and a polyglot persistence layer using PostgreSQL, MongoDB, object storage, Redis, and Kafka.

## 3. Component Diagram (C4 Level 3)

```mermaid
flowchart TD
    subgraph "Trade Service Components"
        TC[Trade Controller]
        TV[Trade Validator]
        TE[Trade Engine]
        TR[Trade Repository]
        TM[Trade Mapper]
    end
    
    subgraph "Voice Service Components"  
        VC[Voice Controller]
        VR[Voice Recognition]
        VT[Voice Transcription]
        VS[Voice Storage]
        VA[Voice Analytics]
    end
    
    subgraph "Compliance Service Components"
        CC[Compliance Controller]
        RE[Rules Engine]
        RV[Regulation Validator]
        RL[Rule Library]
        CR[Compliance Reporter]
    end
    
    TC --> TV
    TV --> TE
    TE --> TR
    TE --> TM
    
    VC --> VR
    VR --> VT
    VT --> VA
    VR --> VS
    
    CC --> RE
    RE --> RV
    RV --> RL
    RE --> CR
```

Component breakdown shows internal structure of key services: Trade Service with validation/engine/repository pattern, Voice Service with recognition/transcription/analytics pipeline, and Compliance Service featuring rules engine with Singapore/Indonesia regulation validators.

## 4. Deployment Architecture

```mermaid
flowchart TD
    subgraph "Singapore Region"
        subgraph "AZ1 Singapore"
            WEB1[Web Server]
            APP1[App Server]
            DB1[(Primary DB)]
        end
        
        subgraph "AZ2 Singapore"
            WEB2[Web Server]
            APP2[App Server]
            DB2[(Standby DB)]
        end
        
        LB1[Load Balancer]
    end
    
    subgraph "Indonesia Region"
        subgraph "AZ1 Jakarta"
            WEB3[Web Server]
            APP3[App Server]
            DB3[(Secondary DB)]
        end
        
        subgraph "AZ2 Jakarta"
            WEB4[Web Server]
            APP4[App Server]
            DB4[(Standby DB)]
        end
        
        LB2[Load Balancer]
    end
    
    subgraph "Backup Region Hong Kong"
        BACKUP[(Backup Storage)]
        DRSITE[DR Site]
    end
    
    LB1 --> WEB1
    LB1 --> WEB2
    LB2 --> WEB3
    LB2 --> WEB4
    
    DB1 -.-> DB3
    DB3 -.-> BACKUP
    
    WEB1 --> APP1
    WEB2 --> APP2
    WEB3 --> APP3
    WEB4 --> APP4
    
    APP1 --> DB1
    APP2 --> DB2
    APP3 --> DB3
    APP4 --> DB4
```

Multi-region deployment spans Singapore (primary), Jakarta (secondary), and Hong Kong (backup) with active-active configuration, multiple availability zones, load balancing, and synchronous replication between regions ensuring <15 minute RTO.

## 5. Data Flow Diagram

```mermaid
flowchart TD
    START[Voice Trade Call] --> CAPTURE[Capture Audio]
    CAPTURE --> RECOGNIZE{ValidAudio}
    
    RECOGNIZE -- Yes --> CONVERT[Convert to Text]
    RECOGNIZE -- No --> MANUAL[Manual Entry]
    
    CONVERT --> EXTRACT[Extract Trade Data]
    MANUAL --> EXTRACT
    
    EXTRACT --> VALIDATE{CompliantTrade}
    
    VALIDATE -- Yes --> ENRICH[Enrich Data]
    VALIDATE -- No --> REJECT[Reject Trade]
    
    ENRICH --> STORE[(Store Trade)]
    STORE --> EXECUTE[Execute Trade]
    EXECUTE --> CONFIRM[Send Confirmation]
    
    STORE --> AUDIT[(Audit Log)]
    CONFIRM --> NOTIFY[Notify Users]
    
    REJECT --> AUDIT
    REJECT --> NOTIFY
```

Data flow illustrates the journey from voice capture through recognition, validation, compliance checking, execution, and notification, with comprehensive audit logging at each decision point ensuring complete traceability.

## 6. Security Architecture

```mermaid
flowchart TD
    subgraph "Internet Zone"
        USER[User Browser/App]
        ATTACKER[Potential Threat]
    end
    
    subgraph "DMZ Zone"
        WAF[Web Application Firewall]
        DDOS[DDoS Protection]
        LB[Load Balancer]
    end
    
    subgraph "Application Zone"
        subgraph "Authentication Layer"
            MFA[Multi-Factor Auth]
            SSO[Single Sign-On]
            CERT[Certificate Auth]
        end
        
        subgraph "Application Services"
            APP[Application Servers]
            API[API Services]
        end
    end
    
    subgraph "Data Zone"
        subgraph "Encryption Layer"
            TLS[TLS 1.3 Transport]
            AES[AES-256 Storage]
        end
        
        DB[(Encrypted Database)]
        HSM[Hardware Security Module]
    end
    
    USER --> WAF
    ATTACKER -.-> DDOS
    WAF --> LB
    LB --> MFA
    MFA --> SSO
    SSO --> APP
    APP --> API
    API --> TLS
    TLS --> DB
    AES --> DB
    HSM --> AES
    CERT --> API
```

Security architecture implements defense-in-depth with WAF/DDoS protection at perimeter, multi-factor authentication, SSO integration, TLS 1.3 for transport, AES-256 encryption at rest, and HSM-based key management meeting regulatory requirements.

## 7. Integration Architecture

```mermaid
flowchart TD
    subgraph "Voice Trade Platform"
        APIGW[API Gateway]
        ESB[Enterprise Service Bus]
        ADAPTER[Protocol Adapters]
    end
    
    subgraph "Market Connectivity"
        FIX[FIX Gateway]
        MARKET1((Primary Market Feed))
        MARKET2((Backup Market Feed))
    end
    
    subgraph "Order Management"
        OMSAPI[OMS REST API]
        OMS((Order System))
    end
    
    subgraph "Settlement"
        SETTLEAPI[Settlement API]
        SETTLE((Settlement System))
    end
    
    subgraph "Regulatory"
        MASAPI[MAS Reporting API]
        OJKAPI[OJK Reporting API]
    end
    
    subgraph "Voice Recording"
        VOICEAPI[Voice API]
        VOICEREC((Recording System))
    end
    
    APIGW --> ESB
    ESB --> ADAPTER
    
    ADAPTER --> FIX
    FIX --> MARKET1
    FIX -.-> MARKET2
    
    ADAPTER --> OMSAPI
    OMSAPI --> OMS
    
    ADAPTER --> SETTLEAPI
    SETTLEAPI --> SETTLE
    
    ADAPTER --> MASAPI
    ADAPTER --> OJKAPI
    
    ADAPTER --> VOICEAPI
    VOICEAPI --> VOICEREC
```

Integration architecture shows API Gateway fronting ESB with protocol adapters connecting to external systems via REST APIs, FIX protocol for markets, regulatory reporting interfaces for MAS/OJK, and voice recording integration.

## 8. Monitoring & Observability

```mermaid
flowchart TD
    subgraph "Application Layer"
        APP[Applications]
        SVC[Services]
        DB[(Databases)]
    end
    
    subgraph "Collection Layer"
        AGENT[Monitoring Agents]
        COLLECTOR[Log Collectors]
        TRACER[Distributed Tracing]
    end
    
    subgraph "Processing Layer"
        LOGPIPE[Log Pipeline]
        METRICPROC[Metrics Processor]
        TRACEAGG[Trace Aggregator]
    end
    
    subgraph "Storage Layer"
        LOGS[(Log Storage)]
        METRICS[(Metrics DB)]
        TRACES[(Trace Store)]
    end
    
    subgraph "Visualization Layer"
        DASHBOARD[Dashboards]
        ALERTS[Alert Manager]
        REPORTS[Report Engine]
    end
    
    subgraph "Notification Channels"
        EMAIL[Email]
        SMS[SMS]
        SLACK[Slack/Teams]
    end
    
    APP --> AGENT
    SVC --> COLLECTOR
    DB --> TRACER
    
    AGENT --> METRICPROC
    COLLECTOR --> LOGPIPE
    TRACER --> TRACEAGG
    
    LOGPIPE --> LOGS
    METRICPROC --> METRICS
    TRACEAGG --> TRACES
    
    LOGS --> DASHBOARD
    METRICS --> DASHBOARD
    TRACES --> DASHBOARD
    
    DASHBOARD --> ALERTS
    ALERTS --> EMAIL
    ALERTS --> SMS
    ALERTS --> SLACK
    
    DASHBOARD --> REPORTS
```

Comprehensive observability stack captures logs, metrics, and traces from all layers, processes through dedicated pipelines, stores in specialized databases, visualizes via dashboards, and triggers multi-channel alerts ensuring <30 second incident detection.