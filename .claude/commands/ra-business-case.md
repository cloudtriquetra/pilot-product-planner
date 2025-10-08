As a Senior Business Analyst and Product Strategy expert, your task is to read the product use case description in $ARGUMENT and produce a comprehensive **Business Case** document that justifies the investment and outlines the strategic value proposition.

## Analysis Requirements

Before creating the business case, analyze the following from the use case documentation:

1. **Business Context**: Understand the problem being solved and market opportunity
2. **Technical Scope**: Review any existing FR, NFR, SDD documents for technical complexity
3. **Strategic Alignment**: Assess how this initiative supports broader business objectives
4. **Stakeholder Impact**: Identify key beneficiaries and affected parties

## Deliverables

Create TWO outputs:
1. **Markdown Business Case Document** (ra-business-case.md)
2. **Excel-Ready CSV Data** (ra-business-case.csv) for importing into Excel

### Business Case Sections:

#### 1. Initiative Purpose / Description
**Problem Statement & Solution Overview**
- Current state challenges and pain points
- Proposed approach and key capabilities
- Strategic rationale for the initiative

#### 2. Initiative Outcomes / Impact
**Business Value & Success Metrics**
- Revenue impact, operational improvements, strategic benefits
- Key performance indicators (KPIs) and success metrics
- Timeline for value realization

#### 3. Objectives & Key Results (OKRs)
**Quarterly Planning Structure:**
- **EPICs**: High-level business outcomes
- **Features**: Major functional deliverables under each EPIC
- **User Stories**: Detailed user value propositions under each Feature
- **Quarterly Timeline**: Q1 2026, Q2 2026, Q3 2026, Q4 2026

#### 4. Key Delivery Milestones
**Milestone Planning**
- Major milestone definitions with dates
- Success criteria and deliverables
- Dependencies and timelines

#### 5. Key Dependencies / Risks & Issues
**Risk Management**
- Critical dependencies (internal/external)
- Risk assessment with mitigation strategies
- Current issues and resolution plans

## Data Structure Requirements

### Hierarchy Rules for CSV Generation:

1. **EPIC Structure**: Each EPIC should be a high-level strategic objective spanning one or more quarters
   - Format: `EPIC_[number]_Q[quarter]` (e.g., EPIC_1_Q1, EPIC_2_Q1)
   - Item: "Objective"

2. **Key Results**: Each EPIC should have 2-4 measurable Key Results
   - Format: `EPIC_[number]_Q[quarter]_KR[number]` (e.g., EPIC_1_Q1_KR1, EPIC_1_Q1_KR2)
   - Item: "Key_Result"

3. **Feature Structure**: Each EPIC should have 3-5 Features that deliver the objective
   - Format: `EPIC_[number]_Q[quarter]_Feature_[number].[subnumber]` (e.g., EPIC_1_Q1_Feature_1.1, EPIC_1_Q1_Feature_1.2)
   - Item: "Feature"

4. **User Story Structure**: Each Feature should have 2-4 User Stories
   - Format: `EPIC_[number]_Q[quarter]_Feature_[number].[subnumber]_US[number]` (e.g., EPIC_1_Q1_Feature_1.1_US1)
   - Item: "User_Story"
   - Follow format: "As a [user type] I want [goal] so that [benefit]"

### Quarterly Distribution:
- **Q1**: Focus on foundational EPICs and core infrastructure
- **Q2**: Scale and optimize based on Q1 learnings  
- **Q3**: Advanced features and integrations
- **Q4**: Performance optimization and future planning

### Success Metrics:
- Create 6-8 quantifiable success metrics with quarterly targets
- Include baseline, Q1, Q2, Q3, and Q4 targets
- Metrics should align with EPIC outcomes

## Template Output

First, create the main markdown document:

```markdown
# Business Case: [USE CASE NAME]

## 1. Initiative Purpose / Description

[Detailed description section as before...]

## 2. Initiative Outcomes / Impact

[Business value section as before...]

## 3. Objectives & Key Results (OKRs)

[Quarterly OKR structure as before...]

## 4. Key Delivery Milestones

[Milestone planning as before...]

## 5. Key Dependencies / Risks & Issues

[Dependencies and risks as before...]
```

Then, create a CSV file with structured data for Excel import:

```csv
Section,Category,Item,Description,Q1_2026,Q2_2026,Q3_2026,Q4_2026,Owner,Risk_Level,Mitigation
Initiative_Purpose,Problem_Statement,Current_Challenge,[Description],,,,,Business_Team,,
Initiative_Purpose,Solution_Overview,Proposed_Approach,[Description],,,,,Product_Team,,
Initiative_Outcomes,Success_Metrics,KPI_1,[Metric Name],[Baseline],[Q1 Target],[Q2 Target],[Q3 Target],[Q4 Target],Team_Lead,,
Initiative_Outcomes,Success_Metrics,KPI_2,[Metric Name],[Baseline],[Q1 Target],[Q2 Target],[Q3 Target],[Q4 Target],Team_Lead,,
Initiative_Outcomes,Success_Metrics,KPI_3,[Metric Name],[Baseline],[Q1 Target],[Q2 Target],[Q3 Target],[Q4 Target],Team_Lead,,
OKR,EPIC_1_Q1,Objective,[High-level strategic objective for Q1],TRUE,FALSE,FALSE,FALSE,Product_Manager,,
OKR,EPIC_1_Q1_KR1,Key_Result,[Measurable outcome 1 for EPIC_1],TRUE,FALSE,FALSE,FALSE,Lead_1,,
OKR,EPIC_1_Q1_KR2,Key_Result,[Measurable outcome 2 for EPIC_1],TRUE,FALSE,FALSE,FALSE,Lead_2,,
OKR,EPIC_1_Q1_KR3,Key_Result,[Measurable outcome 3 for EPIC_1],TRUE,FALSE,FALSE,FALSE,Lead_3,,
OKR,EPIC_1_Q1_Feature_1.1,Feature,[Feature 1 supporting EPIC_1],TRUE,FALSE,FALSE,FALSE,Engineering_Lead_1,,
OKR,EPIC_1_Q1_Feature_1.1_US1,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_1,,
OKR,EPIC_1_Q1_Feature_1.1_US2,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_2,,
OKR,EPIC_1_Q1_Feature_1.1_US3,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_3,,
OKR,EPIC_1_Q1_Feature_1.2,Feature,[Feature 2 supporting EPIC_1],TRUE,FALSE,FALSE,FALSE,Engineering_Lead_2,,
OKR,EPIC_1_Q1_Feature_1.2_US1,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_4,,
OKR,EPIC_1_Q1_Feature_1.2_US2,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_5,,
OKR,EPIC_1_Q1_Feature_1.3,Feature,[Feature 3 supporting EPIC_1],TRUE,FALSE,FALSE,FALSE,Engineering_Lead_3,,
OKR,EPIC_1_Q1_Feature_1.3_US1,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_6,,
OKR,EPIC_1_Q1_Feature_1.3_US2,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_7,,
OKR,EPIC_2_Q1,Objective,[High-level strategic objective 2 for Q1],TRUE,FALSE,FALSE,FALSE,Product_Manager_2,,
OKR,EPIC_2_Q1_KR1,Key_Result,[Measurable outcome 1 for EPIC_2],TRUE,FALSE,FALSE,FALSE,Lead_4,,
OKR,EPIC_2_Q1_KR2,Key_Result,[Measurable outcome 2 for EPIC_2],TRUE,FALSE,FALSE,FALSE,Lead_5,,
OKR,EPIC_2_Q1_Feature_2.1,Feature,[Feature 1 supporting EPIC_2],TRUE,FALSE,FALSE,FALSE,Engineering_Lead_4,,
OKR,EPIC_2_Q1_Feature_2.1_US1,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_8,,
OKR,EPIC_2_Q1_Feature_2.1_US2,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_9,,
OKR,EPIC_2_Q1_Feature_2.2,Feature,[Feature 2 supporting EPIC_2],TRUE,FALSE,FALSE,FALSE,Engineering_Lead_5,,
OKR,EPIC_2_Q1_Feature_2.2_US1,User_Story,[As a [user] I want [goal] so that [benefit]],TRUE,FALSE,FALSE,FALSE,Developer_10,,
OKR,EPIC_1_Q2,Objective,[High-level strategic objective for Q2],FALSE,TRUE,FALSE,FALSE,Product_Manager,,
OKR,EPIC_1_Q2_KR1,Key_Result,[Measurable outcome 1 for Q2 EPIC],FALSE,TRUE,FALSE,FALSE,Lead_6,,
OKR,EPIC_1_Q2_KR2,Key_Result,[Measurable outcome 2 for Q2 EPIC],FALSE,TRUE,FALSE,FALSE,Lead_7,,
OKR,EPIC_1_Q2_Feature_1.4,Feature,[Feature 4 for Q2],FALSE,TRUE,FALSE,FALSE,Engineering_Lead_6,,
OKR,EPIC_1_Q2_Feature_1.4_US1,User_Story,[As a [user] I want [goal] so that [benefit]],FALSE,TRUE,FALSE,FALSE,Developer_11,,
OKR,EPIC_1_Q2_Feature_1.4_US2,User_Story,[As a [user] I want [goal] so that [benefit]],FALSE,TRUE,FALSE,FALSE,Developer_12,,
OKR,EPIC_1_Q2_Feature_1.5,Feature,[Feature 5 for Q2],FALSE,TRUE,FALSE,FALSE,Engineering_Lead_7,,
OKR,EPIC_1_Q2_Feature_1.5_US1,User_Story,[As a [user] I want [goal] so that [benefit]],FALSE,TRUE,FALSE,FALSE,Developer_13,,
Milestones,Q1_Milestone_1,Milestone,[Milestone description],30-Mar-26,,,,Project_Manager,,
Milestones,Q2_Milestone_1,Milestone,[Milestone description],,30-Jun-26,,,Project_Manager,,
Milestones,Q3_Milestone_1,Milestone,[Milestone description],,,30-Sep-26,,Project_Manager,,
Milestones,Q4_Milestone_1,Milestone,[Milestone description],,,,31-Dec-26,Project_Manager,,
Dependencies,Internal_Dependency,Platform_Integration,[Dependency description],,,,,Platform_Team,High,Parallel development approach
Dependencies,External_Dependency,Vendor_Delivery,[Dependency description],,,,,Vendor,Medium,Alternative vendor identified
Risks,Technical_Risk,Integration_Complexity,[Risk description],,,,,Tech_Lead,High,Proof of concept development
Risks,Business_Risk,Market_Changes,[Risk description],,,,,Business_Lead,Medium,Market research and monitoring
```

## Additional Excel Template Creation

Also create a Python script to generate a proper Excel file with formatted sheets:

```python
# Save this as generate_business_case_excel.py in the project workspace
import pandas as pd
import openpyxl
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import os

def create_business_case_excel(project_name, data_dict):
    """
    Create a formatted Excel Business Case document
    """
    wb = openpyxl.Workbook()
    
    # Remove default sheet
    wb.remove(wb.active)
    
    # Create sheets
    purpose_sheet = wb.create_sheet("Initiative Purpose")
    outcomes_sheet = wb.create_sheet("Initiative Outcomes")
    okr_sheet = wb.create_sheet("OKRs")
    milestones_sheet = wb.create_sheet("Milestones")
    risks_sheet = wb.create_sheet("Dependencies & Risks")
    
    # Styling
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    
    # Purpose Sheet
    purpose_sheet.append(["Initiative Purpose / Description:", data_dict.get('purpose', '')])
    purpose_sheet.append(["Initiative Outcomes / Impact:", data_dict.get('outcomes', '')])
    
    # OKR Sheet with quarterly structure
    okr_headers = ["Objective", "Key Result", "Baseline", "Q1 '26", "Q2 '26", "Q3 '26", "Q4 '26"]
    okr_sheet.append(okr_headers)
    
    # Apply header styling
    for cell in okr_sheet[1]:
        cell.font = header_font
        cell.fill = header_fill
    
    # Milestones Sheet
    milestone_headers = ["Milestone name", "Milestone description", "OKR this milestone is contributing to", "Milestone date"]
    milestones_sheet.append(milestone_headers)
    
    # Apply header styling
    for cell in milestones_sheet[1]:
        cell.font = header_font
        cell.fill = header_fill
    
    # Dependencies & Risks Sheet
    risks_headers = ["Key Dependencies/Risks&Issues:", "Description"]
    risks_sheet.append(risks_headers)
    
    # Apply header styling
    for cell in risks_sheet[1]:
        cell.font = header_font
        cell.fill = header_fill
    
    # Save the file
    filename = f"{project_name}_business_case.xlsx"
    wb.save(filename)
    return filename

# Usage example (this would be called by the Claude command)
if __name__ == "__main__":
    project_name = "sample_project"
    data = {
        'purpose': 'Enhancing our secret scanning capabilities...',
        'outcomes': 'Secret Scanning uplift...'
    }
    create_business_case_excel(project_name, data)
```

Save both the markdown business case analysis to $ARGUMENTSra-business-case.md and the CSV data to $ARGUMENTSra-business-case.csv

Also save the Python Excel generator script to $ARGUMENTSgenerate_business_case_excel.py

This provides multiple formats:
1. **Markdown document** for documentation
2. **CSV file** for easy Excel import with structured data
3. **Python script** for generating formatted Excel files with proper styling matching your screenshot

### 1. Initiative Purpose / Description
**Problem Statement & Solution Overview**
- Current state challenges and pain points
- Proposed approach and key capabilities
- Strategic rationale for the initiative

### 2. Initiative Outcomes / Impact
**Business Value & Success Metrics**
- Revenue impact, operational improvements, strategic benefits
- Key performance indicators (KPIs) and success metrics
- Timeline for value realization

### 3. Objectives & Key Results (OKRs)
**Quarterly Planning Structure:**
- **EPICs**: High-level business outcomes
- **Features**: Major functional deliverables under each EPIC
- **User Stories**: Detailed user value propositions under each Feature
- **Quarterly Timeline**: Q1 2026, Q2 2026, Q3 2026, Q4 2026

### 4. Key Delivery Milestones
**Milestone Planning**
- Major milestone definitions with dates
- Success criteria and deliverables
- Dependencies and timelines

### 5. Key Dependencies / Risks & Issues
**Risk Management**
- Critical dependencies (internal/external)
- Risk assessment with mitigation strategies
- Current issues and resolution plans

## Template Output

```markdown
# Business Case: [USE CASE NAME]

## 1. Initiative Purpose / Description

### Problem Statement
[Detailed description of current state challenges and business opportunity]

### Solution Overview
[Proposed approach, key capabilities, and strategic alignment]

### Strategic Rationale
[Why this initiative is critical now and how it supports business strategy]

---

## 2. Initiative Outcomes / Impact

### Business Value
- **Revenue Impact**: [Quantified revenue growth, new streams, or cost savings]
- **Operational Improvements**: [Efficiency gains, quality improvements, compliance benefits]
- **Strategic Benefits**: [Market positioning, customer experience, competitive advantages]

### Success Metrics
| Metric | Baseline | Q1 '26 Target | Q2 '26 Target | Q3 '26 Target | Q4 '26 Target |
|--------|----------|---------------|---------------|---------------|---------------|
| [KPI 1] | [Current] | [Target] | [Target] | [Target] | [Target] |
| [KPI 2] | [Current] | [Target] | [Target] | [Target] | [Target] |
| [KPI 3] | [Current] | [Target] | [Target] | [Target] | [Target] |

---

## 3. Objectives & Key Results (OKRs)

### Q1 2026

#### EPIC 1: [Strategic Theme]
**Objective**: [High-level business outcome for Q1]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 1.1: [Major capability]
- Feature 1.2: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

#### EPIC 2: [Strategic Theme]
**Objective**: [High-level business outcome for Q1]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 2.1: [Major capability]
- Feature 2.2: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

### Q2 2026

#### EPIC 1: [Strategic Theme - Continued]
**Objective**: [High-level business outcome for Q2]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 1.3: [Major capability]
- Feature 1.4: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

#### EPIC 3: [New Strategic Theme]
**Objective**: [High-level business outcome for Q2]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 3.1: [Major capability]
- Feature 3.2: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

### Q3 2026

#### EPIC 2: [Strategic Theme - Continued]
**Objective**: [High-level business outcome for Q3]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 2.3: [Major capability]
- Feature 2.4: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

### Q4 2026

#### EPIC 3: [Strategic Theme - Continued]
**Objective**: [High-level business outcome for Q4]
**Key Results**:
- KR1: [Measurable result]
- KR2: [Measurable result]

**Features**:
- Feature 3.3: [Major capability]
- Feature 3.4: [Major capability]

**User Stories**:
- As a [user type], I want [capability] so that [business value]
- As a [user type], I want [capability] so that [business value]

---

## 4. Key Delivery Milestones

| Milestone Name | Milestone Description | OKR this milestone is contributing to | Milestone Date |
|----------------|----------------------|--------------------------------------|----------------|
| [Q1 Milestone 1] | [Description of deliverable] | [EPIC X - Objective] | [30-Mar-26] |
| [Q1 Milestone 2] | [Description of deliverable] | [EPIC Y - Objective] | [30-Mar-26] |
| [Q2 Milestone 1] | [Description of deliverable] | [EPIC X - Objective] | [30-Jun-26] |
| [Q2 Milestone 2] | [Description of deliverable] | [EPIC Z - Objective] | [30-Jun-26] |
| [Q3 Milestone 1] | [Description of deliverable] | [EPIC Y - Objective] | [30-Sep-26] |
| [Q4 Milestone 1] | [Description of deliverable] | [EPIC Z - Objective] | [31-Dec-26] |

---

## 5. Key Dependencies / Risks & Issues

### Key Dependencies
| Dependency | Risk of slipping schedule/milestones due to delay in solution operationalization and handover activities |
|------------|-----------------------------------------------------------------------------------------------------------|
| [Dependency with ADO Platform and engineering team] | Risk of proof of value and supplier registration delays due to architecture, supply chain and other technical dependencies |
| [Vendor / External Dependency] | [Description of risk and impact] |

### Risks & Issues
| Risk/Issue | Impact | Mitigation Strategy | Owner |
|------------|--------|-------------------|--------|
| [Technical risk] | [High/Med/Low impact description] | [Mitigation approach] | [Person/Team] |
| [Business risk] | [High/Med/Low impact description] | [Mitigation approach] | [Person/Team] |
| [Resource risk] | [High/Med/Low impact description] | [Mitigation approach] | [Person/Team] |

---

*Business Case prepared by: [Team]*  
*Date: [Current Date]*  
*Version: 1.0*
```

Save this focused business case analysis to $ARGUMENTSra-business-case.md

This business case provides a streamlined format focused on the 5 key sections with quarterly OKR planning structured as EPICs → Features → User Stories across Q1-Q4 2026.