# Security Control Applicability Assessment

**Assessment Basis**: This assessment and applicability of security controls is conducted as per Internal Bank Standards and Master Control List requirements.

## Executive Summary

The EsDashboard is an internet-facing web application designed for monitoring Checkov failure analytics in ADO pipelines. With a business criticality level of 2 and deployment in Singapore, the application requires implementation of data protection controls under Singapore's PDPA and MAS guidelines, along with mandatory penetration testing before go-live due to its internet-facing nature. Secret scanning controls are universally required, while SAST implementation is optional given the low-to-medium business criticality rating. The overall security risk is assessed as Medium, requiring structured implementation of mandatory controls within a 3-month timeline.

## System Context Analysis

- **Use Case Name**: EsDashboard
- **Description**: Elastic Search Dashboard for Checkov failure in ADO pipeline
- **Platform**: Web
- **Business Criticality**: 2 (Low-Medium)
- **Deployment**: Internet-facing
- **Target Country/Region**: Singapore
- **Data Types**: Pipeline analytics data, potentially including code scanning results and infrastructure configurations

## Compliance Requirements Analysis

**Primary Compliance Framework**: Singapore PDPA (Personal Data Protection Act) and MAS Guidelines

**Internal Bank Standards**: Organization-specific security policies and procedures
**Master Control List Reference**: Applicable controls from approved catalog
**Additional Requirements**: 
- **MAS Guidelines**: Technology Risk Management (TRM), Cyber Hygiene, Outsourcing Guidelines
- **MAS Notice 644**: Cyber Security requirements for financial institutions
- **Enhanced Controls**: Data breach notification, cross-border data transfer restrictions

**Cross-Border Considerations**: Not applicable - single country deployment in Singapore

## Security Controls Matrix

| Control | Applicability | Compliance Driver | Master Control Ref | Implementation Priority | Resource Estimate |
|---------|---------------|-------------------|--------------------|------------------------|-------------------|
| Data Protection | **Mandatory** | PDPA/MAS Guidelines/Bank Standards | MCL-DP-001 | **High** | 4-6 weeks |
| Penetration Testing | **Mandatory** | Bank Pentest Framework/Internet-facing/Pre-Go-Live | MCL-PT-001 | **High** | 2-3 weeks |
| Secret Scanning | **Mandatory** | Bank Standards/Universal Requirement | MCL-SS-001 | **High** | 1-2 weeks |
| SAST | **Optional** | Bank Standards (Not required for Criticality 2) | MCL-SA-001 | **Medium** | 2-4 weeks |

## Risk Assessment

- **Compliance Risk**: **Medium** - Singapore PDPA and MAS guidelines compliance required for internet-facing financial services applications. Non-compliance could result in regulatory penalties and operational restrictions.

- **Security Risk**: **Medium** - Internet-facing application with pipeline analytics data requires protection against web-based attacks, data exposure, and potential code/infrastructure information disclosure.

- **Business Risk**: **Low-Medium** - Business criticality level 2 indicates limited direct business impact, but reputational risks exist due to internet exposure and regulatory environment.

- **Overall Risk Rating**: **Medium** - Balanced assessment considering compliance requirements, internet exposure, and moderate business criticality.

## Implementation Roadmap

### Immediate Actions (0-1 month)
- **Secret Scanning Implementation**: Deploy automated secret detection across codebase and CI/CD pipeline
- **Data Protection Policy Review**: Align application data handling with Singapore PDPA requirements
- **MAS Guidelines Assessment**: Evaluate application against MAS cyber security and technology risk management requirements

### Phase 1 (1-3 months)
- **Data Protection Controls**: Implement data minimization, retention policies, and breach notification procedures
- **Security Architecture Review**: Validate internet-facing security controls and access management
- **User Consent Mechanisms**: Implement if personal data processing is involved

### Phase 2 (3-6 months)
- **SAST Implementation** (Optional): Deploy static application security testing for enhanced code quality
- **Enhanced Monitoring**: Implement security monitoring and incident response capabilities
- **Regular Security Assessments**: Establish ongoing vulnerability management processes

### Pre-Go-Live (Mandatory)
- **Penetration Testing**: Complete comprehensive pentest using existing bank pentest framework
- **Security Control Validation**: Verify all mandatory controls are operational and effective
- **Bank Security Governance Approval**: Obtain final security sign-off and regulatory compliance verification
- **MAS Compliance Verification**: Ensure adherence to MAS cyber security guidelines

### Ongoing
- **Quarterly Security Reviews**: Regular assessment of security controls effectiveness
- **Annual Compliance Audits**: PDPA and MAS guidelines compliance validation
- **Continuous Secret Scanning**: Automated monitoring for code and configuration secrets
- **Security Awareness Training**: Regular updates for development and operations teams

## Compliance Validation Checklist

- [ ] Internal Bank Standards compliance verified
- [ ] Master Control List controls implemented
- [ ] **Pentest completed using existing bank pentest framework (mandatory before go-live)**
- [ ] Singapore PDPA privacy requirements assessed and implemented
- [ ] MAS Technology Risk Management guidelines compliance verified
- [ ] MAS Cyber Security requirements (Notice 644) implemented
- [ ] Data processing documentation and policies updated
- [ ] Breach notification procedures established for Singapore regulatory requirements
- [ ] User consent mechanisms implemented (if personal data processing required)
- [ ] Data retention policies defined per PDPA requirements
- [ ] Cross-border data transfer safeguards (not applicable for single-country deployment)
- [ ] Regular compliance audits scheduled (quarterly security, annual regulatory)
- [ ] Security control implementation validated and documented
- [ ] Bank security governance approval obtained
- [ ] MAS regulatory compliance sign-off completed
- [ ] Incident response procedures aligned with MAS guidelines
- [ ] Business continuity management procedures established
- [ ] Vendor and third-party risk management processes implemented (if applicable)

---

**Assessment Date**: 2025-09-02
**Next Review Date**: 2025-12-02 (Quarterly)
**Compliance Framework Version**: Singapore PDPA 2012 (as amended), MAS Guidelines 2023

*This assessment should be reviewed and updated whenever there are significant changes to the application architecture, data processing activities, regulatory requirements, or business criticality level.*