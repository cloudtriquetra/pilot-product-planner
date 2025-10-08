#!/usr/bin/env python3
"""
Business Case Excel Generator
Converts Business Case markdown and CSV data to formatted Excel file
"""

import pandas as pd
import openpyxl
import csv
import os
import sys
import re
from openpyxl.styles import Font, Fill, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
import os
import sys
import re
from datetime import datetime

def read_csv_data(project_path):
    """Read and organize data from the CSV file"""
    csv_file = os.path.join(project_path, "ra-business-case.csv")
    
    if not os.path.exists(csv_file):
        print(f"Warning: CSV file not found at {csv_file}")
        return None
    
    data = {
        'initiative_purpose': [],
        'initiative_outcomes': [],
        'okr': [],
        'milestones': [],
        'risks': []
    }
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                section = row['Section'].lower()
                if 'initiative_purpose' in section:
                    data['initiative_purpose'].append(row)
                elif 'initiative_outcomes' in section:
                    data['initiative_outcomes'].append(row)
                elif 'okr' in section:
                    data['okr'].append(row)
                elif 'milestones' in section:
                    data['milestones'].append(row)
                elif 'risks' in section or 'dependencies' in section:
                    data['risks'].append(row)
        
        return data
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None

def create_business_case_excel(project_path, project_name):
    """
    Create a formatted Excel Business Case document from markdown data in a single sheet
    """
    
    # File paths
    md_file = os.path.join(project_path, "ra-business-case.md")
    excel_file = os.path.join(project_path, f"{project_name}_business_case.xlsx")
    
    # Check if source files exist
    if not os.path.exists(md_file):
        print(f"Error: {md_file} not found. Please generate Business Case first.")
        return None
    
    # Read markdown content
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Extract sections from markdown
    data_dict = extract_sections_from_md(md_content)
    
    # Create Excel workbook with single sheet
    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Business Case"
    
    # Define styles
    header_font = Font(bold=True, color="FFFFFF", size=14)
    header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    subheader_font = Font(bold=True, size=12, color="FFFFFF")
    subheader_fill = PatternFill(start_color="5B9BD5", end_color="5B9BD5", fill_type="solid")
    table_header_font = Font(bold=True, size=10)
    table_header_fill = PatternFill(start_color="D6EAF8", end_color="D6EAF8", fill_type="solid")
    border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    
    current_row = 1
    
    # Title
    sheet.merge_cells(f'A{current_row}:H{current_row}')
    sheet[f'A{current_row}'] = f"Business Case: {project_name.replace('-', ' ').title()}"
    sheet[f'A{current_row}'].font = Font(bold=True, size=16)
    sheet[f'A{current_row}'].fill = PatternFill(start_color="2E75B6", end_color="2E75B6", fill_type="solid")
    sheet[f'A{current_row}'].font = Font(bold=True, size=16, color="FFFFFF")
    current_row += 2
    
    # Section 1: Initiative Purpose / Description
    current_row = add_section_header(sheet, current_row, "Initiative Purpose / Description:", header_font, header_fill)
    purpose_text = extract_text_from_section(data_dict.get('purpose', ''))
    current_row = add_text_content(sheet, current_row, purpose_text, 6)
    current_row += 1
    
    # Section 2: Initiative Outcomes / Impact
    current_row = add_section_header(sheet, current_row, "Initiative Outcomes / Impact:", header_font, header_fill)
    outcomes_text = extract_text_from_section(data_dict.get('outcomes', ''))
    current_row = add_text_content(sheet, current_row, outcomes_text, 4)
    current_row += 1
    
    # Section 3: Objectives and Key Results
    current_row = add_section_header(sheet, current_row, "Objectives and Key Results", header_font, header_fill)
    
    # OKR Table Headers
    okr_headers = ["Objective", "Key Result", "Baseline", "Q1 '26", "Q2 '26", "Q3 '26", "Q4 '26"]
    for i, header in enumerate(okr_headers):
        cell = sheet.cell(row=current_row, column=i+1, value=header)
        cell.font = table_header_font
        cell.fill = table_header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')
    current_row += 1
    
    # Sample OKR data
    okr_data = [
        ("Maximized and Secure Speed to Production", "% of secrets inventoried and classified", "# of secrets identified by GitLeaks in 2025", "0", "50% of baseline", "100% of baseline", "Baseline + containers, SharePoint, etc"),
    ]
    
    for okr_row in okr_data:
        for i, value in enumerate(okr_row):
            cell = sheet.cell(row=current_row, column=i+1, value=value)
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        current_row += 1
    
    current_row += 1
    
    # Section 4: Key Delivery Milestones
    current_row = add_section_header(sheet, current_row, "Key Delivery Milestones:", header_font, header_fill)
    
    # Milestones Table Headers
    milestone_headers = ["Milestone name", "Milestone description", "OKR this milestone is contributing to", "Milestone date"]
    for i, header in enumerate(milestone_headers):
        cell = sheet.cell(row=current_row, column=i+1, value=header)
        cell.font = table_header_font
        cell.fill = table_header_fill
        cell.border = border
        cell.alignment = Alignment(horizontal='center', vertical='center')
    current_row += 1
    
    # Sample milestone data
    milestones = [
        ("SSU_Q1_Milestone1: Solution design and Architecture reviews completed", 
         "Define, Design and secure various stakeholders sign-off (OTCR, RO, ADO etc) to implement VHT as service and validation of non-pipeline controls capabilities", 
         "% of secrets inventoried and classified", 
         "30-Mar-26"),
        ("SSU_Q2_Milestone2: Proof of value completion and vendor onboarding along with implementation plan is established", 
         "Ensure proof of value is concluded and Supplier onboarding along with implementation plan is established", 
         "% of secrets inventoried and classified", 
         "30-May-26"),
        ("SSU_Q4_Milestone3: Wider rollout of secret scanning solution to increase Pipeline security", 
         "Operationalize solution and onboard pilot users for capability consumption", 
         "% of secrets inventoried and classified", 
         "30-Oct-26"),
    ]
    
    for milestone in milestones:
        for i, value in enumerate(milestone):
            cell = sheet.cell(row=current_row, column=i+1, value=value)
            cell.border = border
            cell.alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)
        current_row += 1
    
    current_row += 1
    
    # Section 5: Key Dependencies/Risks&Issues
    current_row = add_section_header(sheet, current_row, "Key Dependencies/Risks&Issues:", header_font, header_fill)
    
    dependencies_text = """Dependency with ADO Platform and engineering team resources to design, integrate & implement solutions in ADO pipeline
Risk of slipping schedule/milestones due to delay in solution operationalization and handover activities
Risk of proof of value and supplier registration delays due to architecture, supply chain and other technical dependencies
Vendor / External Dependency: HashiCorp/Vault"""
    
    current_row = add_text_content(sheet, current_row, dependencies_text, 4)
    
    # Set column widths
    sheet.column_dimensions['A'].width = 30
    sheet.column_dimensions['B'].width = 50
    sheet.column_dimensions['C'].width = 20
    sheet.column_dimensions['D'].width = 15
    sheet.column_dimensions['E'].width = 15
    sheet.column_dimensions['F'].width = 15
    sheet.column_dimensions['G'].width = 20
    sheet.column_dimensions['H'].width = 15
    
    # Save Excel file
    wb.save(excel_file)
    print(f"✅ Single-sheet Excel Business Case created: {excel_file}")
    return excel_file

def add_section_header(sheet, row, text, font, fill):
    """Add a section header spanning multiple columns"""
    sheet.merge_cells(f'A{row}:H{row}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].font = font
    sheet[f'A{row}'].fill = fill
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='center')
    return row + 1

def add_text_content(sheet, row, text, num_rows):
    """Add text content in merged cells"""
    sheet.merge_cells(f'A{row}:H{row + num_rows - 1}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    return row + num_rows

def extract_text_from_section(section_content):
    """Extract clean text from markdown section"""
    # Remove markdown headers and clean up
    lines = section_content.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def extract_sections_from_md(content):
    """Extract structured data from markdown content"""
    sections = {}
    
    # Extract Initiative Purpose
    purpose_match = re.search(r'## 1\. Initiative Purpose / Description.*?\n(.*?)(?=## 2\.|##|\Z)', content, re.DOTALL)
    sections['purpose'] = purpose_match.group(1).strip() if purpose_match else ""
    
    # Extract Initiative Outcomes
    outcomes_match = re.search(r'## 2\. Initiative Outcomes / Impact.*?\n(.*?)(?=## 3\.|##|\Z)', content, re.DOTALL)
    sections['outcomes'] = outcomes_match.group(1).strip() if outcomes_match else ""
    
    # Extract OKRs
    okr_match = re.search(r'## 3\. Objectives & Key Results.*?\n(.*?)(?=## 4\.|##|\Z)', content, re.DOTALL)
    sections['okrs'] = okr_match.group(1).strip() if okr_match else ""
    
    # Extract Milestones
    milestones_match = re.search(r'## 4\. Key Delivery Milestones.*?\n(.*?)(?=## 5\.|##|\Z)', content, re.DOTALL)
    sections['milestones'] = milestones_match.group(1).strip() if milestones_match else ""
    
    # Extract Dependencies & Risks
    risks_match = re.search(r'## 5\. Key Dependencies / Risks & Issues.*?\n(.*?)(?=##|\Z)', content, re.DOTALL)
    sections['risks'] = risks_match.group(1).strip() if risks_match else ""
    
    return sections

def add_section_header(sheet, row, text, font, fill):
    """Add a section header spanning multiple columns"""
    sheet.merge_cells(f'A{row}:H{row}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].font = font
    sheet[f'A{row}'].fill = fill
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='center')
    return row + 1

def add_text_content(sheet, row, text, num_rows):
    """Add text content in merged cells"""
    sheet.merge_cells(f'A{row}:H{row + num_rows - 1}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    return row + num_rows

def extract_text_from_section(section_content):
    """Extract clean text from markdown section"""
    # Remove markdown headers and clean up
    lines = section_content.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def main():
    """Main function to generate Excel from command line"""
    if len(sys.argv) != 3:
        print("Usage: python generate_business_case_excel.py <project_path> <project_name>")
        print("Example: python generate_business_case_excel.py ../workspace/my-project my-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2]
    
    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)
    
    excel_file = create_business_case_excel(project_path, project_name)
    if excel_file:
        print(f"✅ Success! Single-sheet Excel file created: {excel_file}")
    else:
        print("❌ Failed to create Excel file")
        sys.exit(1)

if __name__ == "__main__":
    main()

def extract_text_from_section(section_content):
    """Extract clean text from markdown section"""
    # Remove markdown headers and clean up
    lines = section_content.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def main():
    """Main function to generate Excel from command line"""
    if len(sys.argv) != 3:
        print("Usage: python generate_business_case_excel.py <project_path> <project_name>")
        print("Example: python generate_business_case_excel.py ../workspace/my-project my-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2]
    
    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)
    
    excel_file = create_business_case_excel(project_path, project_name)
    if excel_file:
        print(f"✅ Success! Excel file created: {excel_file}")
    else:
        print("❌ Failed to create Excel file")
        sys.exit(1)

if __name__ == "__main__":
    main()

def add_section_header(sheet, row, text, font, fill):
    """Add a section header spanning multiple columns"""
    sheet.merge_cells(f'A{row}:H{row}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].font = font
    sheet[f'A{row}'].fill = fill
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='center')
    return row + 1

def add_text_content(sheet, row, text, num_rows):
    """Add text content in merged cells"""
    sheet.merge_cells(f'A{row}:H{row + num_rows - 1}')
    sheet[f'A{row}'] = text
    sheet[f'A{row}'].alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
    return row + num_rows

def extract_text_from_section(section_content):
    """Extract clean text from markdown section"""
    # Remove markdown headers and clean up
    lines = section_content.split('\n')
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('*'):
            clean_lines.append(line)
    return '\n'.join(clean_lines)

def main():
    """Main function to generate Excel from command line"""
    if len(sys.argv) != 3:
        print("Usage: python generate_business_case_excel.py <project_path> <project_name>")
        print("Example: python generate_business_case_excel.py ../workspace/my-project my-project")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2]
    
    if not os.path.exists(project_path):
        print(f"Error: Project path '{project_path}' does not exist.")
        sys.exit(1)
    
    excel_file = create_business_case_excel(project_path, project_name)
    if excel_file:
        print(f"✅ Success! Single-sheet Excel file created: {excel_file}")
    else:
        print("❌ Failed to create Excel file")
        sys.exit(1)

if __name__ == "__main__":
    main()