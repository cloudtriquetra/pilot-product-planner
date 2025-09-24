# Security Control Applicability Assessment

**Assessment Basis**: This assessment and applicability of security controls is conducted as per Internal Bank Standards and Master Control List requirements.

## Executive Summary
This security assessment evaluates the controls required for the electronification of voice trades under $1 million, an external application with business criticality level 5. The system will operate across Singapore and Indonesia, requiring compliance with MAS Technology Risk Management guidelines, PDPA, and Indonesian data protection regulations. Given the external exposure and maximum business criticality, all security controls from the Master Control List are deemed mandatory, with penetration testing using the existing bank framework required before go-live. The implementation prioritizes data protection and SAST due to financial data sensitivity and regulatory requirements.

## System Context Analysis
- **Use Case Name**: Electronification of voice trades under 1million
- **Platform**: All platforms (multi-platform deployment)
- **Business Criticality**: 5 (Maximum criticality level)
- **Deployment**: External application (internet-facing)
- **Target Country/Region**: Singapore and Indonesia
- **Data Types**: Financial transaction data, trading data, customer information, voice recordings

## Compliance Requirements Analysis
**Primary Compliance Framework**: 
- **Singapore**: MAS Technology Risk Management (TRM) Guidelines, Personal Data Protection Act (PDPA), MAS Notice 644 (Cyber Security)
- **Indonesia**: Law No. 27/2022 on Personal Data Protection, OJK regulations for financial services

**Internal Bank Standards**: 
- Master Control List implementation required for all systems
- Enhanced controls for business criticality level 5
- External application security baseline requirements

**Master Control List Reference**: 
- MCL-DP-001: Data Protection Controls
- MCL-PT-001: Penetration Testing Framework
- MCL-SS-001: Secret Scanning Requirements
- MCL-SA-001: Static Application Security Testing

**Additional Requirements**: 
- Voice recording retention and protection requirements
- Cross-border data transfer between Singapore and Indonesia
- Real-time transaction security monitoring
- Audit trail for all trading activities

**Cross-Border Considerations**: 
- Data residency requirements for both Singapore and Indonesia
- Consent mechanisms for cross-border data transfers
- Encrypted transmission channels between jurisdictions

## Security Controls Matrix
| Control | Applicability | Compliance Driver | Master Control Ref | Implementation Priority | Resource Estimate |
|---------|---------------|-------------------|--------------------|------------------------|-------------------|
| Data Protection | **Mandatory** | PDPA (SG/Indonesia), MAS TRM, Bank Standards | MCL-DP-001 | **High** | 2-3 months |
| Penetration Testing | **Mandatory** | External Application, Bank Pentest Framework | MCL-PT-001 | **High** (Pre-Go-Live) | 1-2 months |
| Secret Scanning | **Mandatory** | Universal requirement, Bank Standards | MCL-SS-001 | **High** | 1 month |
| SAST | **Mandatory** | Business Criticality 5, Bank Standards | MCL-SA-001 | **High** | 1-2 months |

### Additional Security Controls (Based on Criticality 5)
| Control | Applicability | Compliance Driver | Implementation Priority |
|---------|---------------|-------------------|------------------------|
| Dynamic Application Security Testing (DAST) | **Mandatory** | External exposure, Criticality 5 | **High** |
| Runtime Application Self-Protection (RASP) | **Recommended** | Real-time transaction protection | **Medium** |
| Web Application Firewall (WAF) | **Mandatory** | Internet-facing application | **High** |
| API Security Gateway | **Mandatory** | External API exposure | **High** |
| Security Information Event Management (SIEM) | **Mandatory** | MAS TRM requirements | **High** |
| Data Loss Prevention (DLP) | **Mandatory** | Financial data protection | **High** |
| Encryption at Rest & In Transit | **Mandatory** | PDPA, Cross-border transfers | **High** |

## Risk Assessment
- **Compliance Risk**: **High** - Operating in two jurisdictions with strict financial regulations (MAS and OJK), non-compliance could result in severe penalties and license revocation
- **Security Risk**: **High** - External application handling financial transactions creates significant exposure to cyber threats, fraud, and data breaches
- **Business Risk**: **High** - Business criticality 5 indicates maximum impact on bank operations; system compromise could affect trading operations and client trust
- **Overall Risk Rating**: **High** - Requires comprehensive security controls and continuous monitoring

### Specific Risk Factors:
1. **Voice Trade Manipulation Risk**: Unauthorized modifications to voice trade recordings or electronification process
2. **Cross-Border Data Transfer Risk**: Data sovereignty and regulatory compliance across Singapore and Indonesia
3. **Insider Threat Risk**: Internal actors with access to trading systems
4. **API Security Risk**: External APIs vulnerable to injection attacks and unauthorized access
5. **Regulatory Non-Compliance Risk**: Failure to meet MAS TRM or Indonesian OJK requirements

## Implementation Roadmap

### Immediate Actions (0-1 month)
- [ ] Establish secure development environment with secret scanning
- [ ] Implement SAST in CI/CD pipeline
- [ ] Define data classification and handling procedures
- [ ] Setup encryption for development and test environments
- [ ] Initiate security architecture review

### Phase 1 (1-3 months)
- [ ] Complete data protection implementation (encryption, access controls)
- [ ] Deploy WAF and API Gateway
- [ ] Implement comprehensive logging and SIEM integration
- [ ] Conduct initial SAST and remediate critical findings
- [ ] Establish secure cross-border data transfer mechanisms

### Phase 2 (3-6 months)
- [ ] Deploy DAST in staging environment
- [ ] Implement DLP controls for financial data
- [ ] Complete security control validation
- [ ] Conduct security awareness training for operations team
- [ ] Establish incident response procedures

### Pre-Go-Live (Mandatory)
- [ ] **Complete Penetration Testing using existing bank pentest framework**
- [ ] Remediate all critical and high severity findings
- [ ] Obtain security sign-off from CISO office
- [ ] Complete MAS Technology Risk Assessment
- [ ] Validate compliance with Indonesian data protection requirements
- [ ] **Bank Security Governance Approval obtained**

### Ongoing
- [ ] Quarterly penetration testing
- [ ] Monthly vulnerability assessments
- [ ] Continuous SAST/DAST scanning
- [ ] Real-time security monitoring via SIEM
- [ ] Annual compliance audits for MAS and OJK requirements

## Compliance Validation Checklist

### Singapore (MAS) Requirements
- [ ] MAS TRM Guidelines compliance verified
- [ ] MAS Notice 644 (Cyber Security) requirements implemented
- [ ] PDPA compliance measures in place
- [ ] Consent mechanisms for data collection implemented
- [ ] Data breach notification procedures established (72 hours)
- [ ] DPO appointed for Singapore operations

### Indonesia Requirements
- [ ] Law No. 27/2022 compliance verified
- [ ] OJK financial services regulations compliance
- [ ] Data localization requirements assessed
- [ ] Indonesian language privacy notices prepared
- [ ] Local data protection officer designated

### Bank Internal Requirements
- [ ] Internal Bank Standards compliance verified
- [ ] Master Control List controls implemented
- [ ] **Pentest completed using existing bank pentest framework (before go-live)**
- [ ] Security architecture review completed
- [ ] Third-party security assessment (if applicable)
- [ ] Risk acceptance for residual risks obtained

### Cross-Border Requirements
- [ ] Cross-border data transfer agreements in place
- [ ] Encryption for data in transit between countries
- [ ] Consent for international data transfers obtained
- [ ] Data residency requirements mapped and implemented

### Technical Security Requirements
- [ ] All APIs secured with authentication and authorization
- [ ] Rate limiting and DDoS protection implemented
- [ ] Security headers configured correctly
- [ ] Input validation for all user inputs
- [ ] Secure session management implemented
- [ ] Audit logging for all transactions enabled

### Operational Security Requirements
- [ ] Incident response plan documented and tested
- [ ] Security monitoring dashboards configured
- [ ] Backup and recovery procedures validated
- [ ] Change management process includes security review
- [ ] Regular security training scheduled for operations team

## Appendix A: Security Control Implementation Details

### Data Protection Implementation
- **Encryption Standards**: AES-256 for data at rest, TLS 1.3 for data in transit
- **Key Management**: Hardware Security Module (HSM) for key storage
- **Access Controls**: Role-based access control with principle of least privilege
- **Data Masking**: PII and financial data masked in non-production environments

### Penetration Testing Scope
- **Application Security**: OWASP Top 10 coverage
- **API Security**: REST/SOAP API testing
- **Infrastructure Security**: Network and host security assessment
- **Social Engineering**: Phishing simulation for operations team
- **Physical Security**: Data center access controls (if applicable)

### SAST Configuration
- **Languages Covered**: All programming languages used in the application
- **Rule Sets**: OWASP, CWE, SANS Top 25
- **Integration Points**: IDE, Git hooks, CI/CD pipeline
- **Remediation SLA**: Critical - 24 hours, High - 7 days, Medium - 30 days

### Secret Scanning Implementation
- **Coverage**: Source code, configuration files, documentation
- **Tools**: Integration with bank-approved secret scanning tools
- **Response**: Immediate rotation of exposed secrets
- **Prevention**: Pre-commit hooks to prevent secret commits

## Appendix B: Regulatory Reference Links
- [MAS Technology Risk Management Guidelines](https://www.mas.gov.sg/regulation/guidelines/technology-risk-management-guidelines)
- [Singapore PDPA Overview](https://www.pdpc.gov.sg/Overview-of-PDPA/The-Legislation/Personal-Data-Protection-Act)
- [Indonesia Personal Data Protection Law](https://www.dpr.go.id/dokjdih/document/uu/2022/UU_NO_27_TAHUN_2022.pdf)
- [OJK Digital Banking Regulations](https://www.ojk.go.id/en/kanal/perbankan/regulasi/Pages/default.aspx)

---

**Document Version**: 1.0  
**Assessment Date**: 2025-09-03  
**Next Review Date**: Quarterly or upon significant system changes  
**Document Classification**: Internal - Confidential