As a Senior Security Architect, your task is to read the product use case description in $ARGUMENT and produce a comprehensive **Security Control Applicability Assessment** specification.

Input sources to analyze:
- Use case description from: $ARGUMENT

Before starting the security assessment, first read and analyze the use case file to understand:
- Business context and use case scope
- Platform and technology stack
- Business criticality level
- Deployment model (internal/external/internet-facing)
- Target country/region for deployment
- Data types and sensitivity levels

Save the generated assessment to: $ARGUMENTSra-security-controls.md

## Security Controls Framework

**Assessment Basis:**
- **Internal Bank Standards**: Organization-specific security policies and procedures
- **Master Control List**: Comprehensive catalog of approved security controls
- **Regulatory Requirements**: Country/region-specific compliance frameworks
- **Industry Best Practices**: NIST, ISO 27001, and other recognized standards

**Core Security Controls (from Master Control List):**
1. **Data Protection** - Data privacy, encryption, and compliance controls
2. **Pentest** - Penetration testing and vulnerability assessments (using existing bank pentest framework - **mandatory before go-live**)
3. **Secret Scanning** - Code and repository secret detection
4. **SAST** - Static Application Security Testing

## Applicability Rules
- **Data Protection**: Applicable for ALL systems
- **Pentest**: 
  - Applicable only for external/internet-facing applications
  - **Uses existing bank pentest framework**
  - **Mandatory completion before go-live**
- **Secret Scanning**: Applicable for ALL systems
- **SAST**: 
  - Mandatory for Business Criticality 3, 4, 5
  - Optional for Business Criticality 1, 2

## Compliance Requirements by Country/Region

### European Union (GDPR)
- **Data Protection**: Mandatory - GDPR compliance required
- **Additional Requirements**: Data minimization, consent management, breach notification
- **Enhanced Controls**: Data Processing Impact Assessments (DPIA) for high-risk processing

### United States
- **Federal**: SOC 2, NIST Cybersecurity Framework
- **Sector-Specific**: 
  - Healthcare: HIPAA
  - Financial: SOX, PCI DSS
  - Education: FERPA
- **State-Level**: CCPA (California), SHIELD Act (New York)

### Canada
- **PIPEDA**: Personal Information Protection and Electronic Documents Act
- **Provincial**: PIPA (Alberta, BC), FOIP (various provinces)
- **Enhanced Controls**: Privacy breach notification requirements

### United Kingdom
- **UK GDPR**: Similar to EU GDPR with local variations
- **Data Protection Act 2018**: Additional UK-specific requirements
- **Enhanced Controls**: ICO guidance compliance

### Australia
- **Privacy Act 1988**: Australian Privacy Principles (APPs)
- **Notifiable Data Breaches**: Mandatory breach notification
- **Enhanced Controls**: Privacy impact assessments

### Singapore
- **PDPA**: Personal Data Protection Act
- **MAS Guidelines**: Technology Risk Management (TRM), Cyber Hygiene, Outsourcing Guidelines
- **Enhanced Controls**: Data breach notification, DPO appointment for large organizations
- **Financial Services**: MAS Notice 644 (Cyber Security), Business Continuity Management

### India
- **IT Rules 2011**: Reasonable security practices
- **Upcoming**: Personal Data Protection Bill
- **Enhanced Controls**: Data localization requirements

### Japan
- **APPI**: Act on Protection of Personal Information
- **Enhanced Controls**: Cross-border data transfer restrictions

### South Korea
- **PIPA**: Personal Information Protection Act
- **Enhanced Controls**: Strict consent requirements, data localization

### Brazil
- **LGPD**: Lei Geral de Proteção de Dados
- **Enhanced Controls**: Similar to GDPR with local variations

### China
- **Cybersecurity Law**: Data localization and security requirements
- **PIPL**: Personal Information Protection Law
- **Enhanced Controls**: Strict data sovereignty requirements

### Hong Kong
- **PDPO**: Personal Data (Privacy) Ordinance
- **HKMA Guidelines**: Technology Risk Management, Cyber Security, Operational Risk Management
- **Enhanced Controls**: Data breach notification, cross-border data transfer restrictions
- **Financial Services**: HKMA SPM modules (IC-2, IC-3, OR-2), Banking Conduct Guidelines

### Multi-Country/Worldwide Deployments
- **Highest Standard Approach**: Apply most restrictive compliance requirements
- **Common Standards**: ISO 27001, SOC 2 Type II
- **Regional Variations**: Implement country-specific controls where required

## Output Structure
The assessment should include:

### 1. System Context Analysis
- Application type and exposure
- Business criticality assessment
- Data sensitivity classification
- Compliance requirements

### 2. Security Controls Matrix
| Control | Applicability | Justification | Priority |
|---------|---------------|---------------|----------|
| Data Protection | Mandatory/Optional/N/A | Reasoning | High/Medium/Low |
| Pentest | Mandatory/Optional/N/A | Reasoning | High/Medium/Low |
| Secret Scanning | Mandatory/Optional/N/A | Reasoning | High/Medium/Low |
| SAST | Mandatory/Optional/N/A | Reasoning | High/Medium/Low |

### 3. Implementation Recommendations
- Required security controls with timelines
- Optional security controls with business value
- Integration points with development lifecycle
- Compliance mapping

### 4. Risk Assessment
- Security risks if controls are not implemented
- Business impact of security incidents
- Mitigation strategies

## Example Output Format

```markdown
Deliverables (in this order):

1) **Executive Summary (≤150 words)**
   - Brief overview of the security posture assessment
   - Key security control decisions and rationale
   - Compliance framework summary

2) **System Context Analysis**
   - Use Case Name and Description
   - Platform/Technology Stack
   - Business Criticality (1-5 Scale)
   - Deployment Model (Internal/External/Internet-facing)
   - Target Country/Region
   - Data Types and Sensitivity

3) **Compliance Requirements Analysis**
   - Primary compliance framework based on country/region
   - Sector-specific requirements (if applicable)
   - Cross-border data transfer considerations
   - Enhanced controls for sensitive data types

4) **Security Controls Matrix**
   - Detailed applicability assessment for each control
   - Compliance drivers and regulatory basis
   - Implementation priority (High/Medium/Low)
   - Resource requirements and timelines

5) **Risk Assessment**
   - Compliance risk evaluation
   - Security risk assessment
   - Business impact analysis
   - Overall risk rating and mitigation strategy

6) **Implementation Roadmap**
   - Immediate actions (0-1 month)
   - Phase 1 implementation (1-3 months)
   - Phase 2 enhancement (3-6 months)
   - Ongoing compliance validation

7) **Compliance Validation Checklist**
   - Regulatory compliance verification steps
   - Documentation requirements
   - Audit preparation activities
   - Continuous monitoring processes

## Template Output Format

---

# Security Control Applicability Assessment

**Assessment Basis**: This assessment and applicability of security controls is conducted as per Internal Bank Standards and Master Control List requirements.

## Executive Summary
[Brief overview of security assessment, key decisions, and compliance framework]

## System Context Analysis
- **Use Case Name**: [Auto-extracted from usecase.md]
- **Platform**: [Auto-extracted from usecase.md]
- **Business Criticality**: [Auto-extracted from usecase.md]
- **Deployment**: [Auto-extracted from usecase.md]
- **Target Country/Region**: [Auto-extracted from usecase.md]
- **Data Types**: [Auto-extracted from usecase.md]

## Compliance Requirements Analysis
**Primary Compliance Framework**: [Auto-populated based on country]
**Internal Bank Standards**: [Organization-specific security policies and procedures]
**Master Control List Reference**: [Applicable controls from approved catalog]
**Additional Requirements**: [Sector-specific or enhanced requirements]
**Cross-Border Considerations**: [If applicable for multi-country deployments]

## Security Controls Matrix
| Control | Applicability | Compliance Driver | Master Control Ref | Implementation Priority | Resource Estimate |
|---------|---------------|-------------------|--------------------|------------------------|-------------------|
| Data Protection | [Mandatory/Optional] | [GDPR/Bank Standards] | [MCL-DP-001] | [High/Medium/Low] | [Weeks/Months] |
| Penetration Testing | [Mandatory/Optional] | [Bank Pentest Framework/Pre-Go-Live] | [MCL-PT-001] | [High/Medium/Low] | [Weeks/Months] |
| Secret Scanning | [Mandatory/Optional] | [Bank Standards/Universal] | [MCL-SS-001] | [High/Medium/Low] | [Weeks/Months] |
| SAST | [Mandatory/Optional] | [Bank Standards/Criticality] | [MCL-SA-001] | [High/Medium/Low] | [Weeks/Months] |

## Risk Assessment
- **Compliance Risk**: [High/Medium/Low] - [Detailed analysis]
- **Security Risk**: [High/Medium/Low] - [Threat assessment]
- **Business Risk**: [High/Medium/Low] - [Impact analysis]
- **Overall Risk Rating**: [High/Medium/Low] - [Combined assessment]

## Implementation Roadmap
### Immediate Actions (0-1 month)
- [High priority compliance controls]

### Phase 1 (1-3 months)
- [Essential security controls]

### Phase 2 (3-6 months)
- [Enhanced security measures]

### Pre-Go-Live (Mandatory)
- **Penetration Testing**: Complete pentest using existing bank pentest framework (for internet-facing applications)
- **Security Control Validation**: Verify all mandatory controls are implemented
- **Bank Security Governance Approval**: Obtain final security sign-off

### Ongoing
- [Continuous monitoring and compliance validation]

## Compliance Validation Checklist
- [ ] Internal Bank Standards compliance verified
- [ ] Master Control List controls implemented
- [ ] **Pentest completed using existing bank pentest framework (before go-live)**
- [ ] Privacy policy updated for target jurisdiction
- [ ] Data processing agreements in place
- [ ] Breach notification procedures established
- [ ] User consent mechanisms implemented (if required)
- [ ] Data retention policies defined
- [ ] Cross-border data transfer safeguards (if applicable)
- [ ] Regular compliance audits scheduled
- [ ] Security control implementation validated
- [ ] Documentation updated and maintained
- [ ] Bank security governance approval obtained

---

## Security Control Applicability Assessment

### System Context Analysis
- **Use Case Name**: [Use Case Name]
- **Platform**: [Platform/Technology]
- **Business Criticality**: [1-5 Scale]
- **Deployment**: [Internal/External/Internet-facing]
- **Target Country/Region**: [Country/Region]
- **Data Types**: [Personal Data/Financial/Healthcare/Other]

### Compliance Requirements Analysis
Based on the target country/region, the following compliance frameworks are applicable:

**Primary Compliance Framework**: [Auto-populated based on country]
**Additional Requirements**: [Sector-specific or enhanced requirements]
**Cross-Border Considerations**: [If applicable for multi-country deployments]

### Security Controls Matrix
| Control | Applicability | Compliance Driver | Implementation Priority |
|---------|---------------|-------------------|------------------------|
| Data Protection | [Mandatory/Optional] | [GDPR/PIPEDA/etc.] | [High/Medium/Low] |
| Penetration Testing | [Mandatory/Optional] | [Based on exposure] | [High/Medium/Low] |
| Secret Scanning | [Mandatory/Optional] | [Universal requirement] | [High/Medium/Low] |
| SAST | [Mandatory/Optional] | [Based on criticality] | [High/Medium/Low] |

### Implementation Recommendations
1. **Immediate Actions**: [High priority controls based on compliance requirements]
2. **Phase 1 (0-3 months)**: [Essential compliance controls]
3. **Phase 2 (3-6 months)**: [Enhanced security controls]
4. **Ongoing**: [Continuous monitoring and compliance validation]

### Risk Assessment
- **Compliance Risk**: [High/Medium/Low] - Based on regulatory requirements
- **Security Risk**: [High/Medium/Low] - Based on threat exposure
- **Business Risk**: [High/Medium/Low] - Based on business criticality
- **Overall Risk Rating**: [High/Medium/Low]

### Compliance Validation Checklist
- [ ] Privacy policy updated for target jurisdiction
- [ ] Data processing agreements in place
- [ ] Breach notification procedures established
- [ ] User consent mechanisms implemented (if required)
- [ ] Data retention policies defined
- [ ] Cross-border data transfer safeguards (if applicable)
- [ ] Regular compliance audits scheduled

---

## Integration Points
- Reads from existing use case documentation: $ARGUMENT
- Considers FR/NFR requirements for context (if available)
- Aligns with architecture and design decisions
- Feeds into implementation planning and security validation
