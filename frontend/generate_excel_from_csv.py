#!/usr/bin/env python3
"""
Simple Excel generator that reads directly from CSV data
"""

import pandas as pd
import os
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

def get_quarter_from_row(row):
    """Extract quarter information from row data"""
    if row.get('Q1_2026') == 'TRUE':
        return "Q1 2026"
    elif row.get('Q2_2026') == 'TRUE':
        return "Q2 2026"
    elif row.get('Q3_2026') == 'TRUE':
        return "Q3 2026"
    elif row.get('Q4_2026') == 'TRUE':
        return "Q4 2026"
    else:
        return "TBD"

def create_excel_from_csv(project_path, project_name):
    """Create Excel file directly from CSV data"""
    
    # Handle None project_name
    if not project_name:
        project_name = "Business Case"
    
    # Read CSV file
    csv_file = os.path.join(project_path, "ra-business-case.csv")
    
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return None
    
    try:
        # Read CSV data with robust parsing
        df = pd.read_csv(csv_file, skipinitialspace=True, on_bad_lines='skip')
        
        # Create workbook
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Business Case"
        
        # Define styles
        header_font = Font(bold=True, size=14, color="FFFFFF")
        header_fill = PatternFill(start_color="2F75B5", end_color="2F75B5", fill_type="solid")
        table_header_font = Font(bold=True, size=11)
        table_header_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
        
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        current_row = 1
        
        # Title
        sheet.merge_cells(f'A{current_row}:H{current_row}')
        title_cell = sheet[f'A{current_row}']
        title_cell.value = f"Business Case: {project_name.replace('-', ' ').title()}"
        title_cell.font = Font(bold=True, size=16)
        title_cell.alignment = Alignment(horizontal='center')
        current_row += 2
        
        # Process sections
        sections = df['Section'].unique()
        
        for section in sections:
            section_data = df[df['Section'] == section]
            
            # Special handling for OKR section
            if section == 'OKR':
                # Add section header
                sheet.merge_cells(f'A{current_row}:H{current_row}')
                header_cell = sheet[f'A{current_row}']
                header_cell.value = "Objectives & Key Results (OKRs)"
                header_cell.font = header_font
                header_cell.fill = header_fill
                header_cell.alignment = Alignment(horizontal='left', vertical='center')
                current_row += 1
                
                # Get Objectives and Key Results by Item field
                objectives_data = section_data[section_data['Item'] == 'Objective']
                key_results_data = section_data[section_data['Item'] == 'Key_Result']
                
                if not objectives_data.empty:
                    # Table headers for OKR
                    okr_headers = ['Quarter', 'Objective', 'Key Results', 'Owner']
                    for i, header in enumerate(okr_headers):
                        cell = sheet.cell(row=current_row, column=i+1, value=header)
                        cell.font = table_header_font
                        cell.fill = table_header_fill
                        cell.border = border
                        cell.alignment = Alignment(horizontal='center', vertical='center')
                    current_row += 1
                    
                    # Process each Objective with its Key Results
                    for _, obj_row in objectives_data.iterrows():
                        quarter = get_quarter_from_row(obj_row)
                        obj_category = obj_row.get('Category', '')
                        
                        # Find matching Key Results for this Objective (same EPIC category prefix)
                        epic_prefix = obj_category  # e.g., "EPIC_1_Q1"
                        matching_krs = key_results_data[key_results_data['Category'].str.startswith(epic_prefix)]
                        
                        # Combine Key Results into one cell
                        kr_descriptions = []
                        kr_owners = []
                        for _, kr_row in matching_krs.iterrows():
                            kr_descriptions.append(f"• {kr_row.get('Description', '')}")
                            if kr_row.get('Owner'):
                                kr_owners.append(kr_row.get('Owner'))
                        
                        key_results_text = '\n'.join(kr_descriptions) if kr_descriptions else 'TBD'
                        combined_owners = ', '.join(set(kr_owners)) if kr_owners else obj_row.get('Owner', '')
                        
                        data_row = [
                            quarter,
                            obj_row.get('Description', ''),
                            key_results_text,
                            combined_owners
                        ]
                        
                        for i, value in enumerate(data_row):
                            cell = sheet.cell(row=current_row, column=i+1, value=str(value))
                            cell.border = border
                            cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                            if i == 1:  # Objective column
                                cell.font = Font(bold=True)
                        current_row += 1
                    
                    current_row += 1
                
                # Create Implementation Plan section with better structure
                sheet.merge_cells(f'A{current_row}:H{current_row}')
                impl_header_cell = sheet[f'A{current_row}']
                impl_header_cell.value = "Implementation Plan"
                impl_header_cell.font = header_font
                impl_header_cell.fill = header_fill
                impl_header_cell.alignment = Alignment(horizontal='left', vertical='center')
                current_row += 1
                
                # Headers for implementation plan
                impl_headers = ['Quarter', 'EPIC', 'Feature/User Story', 'Type', 'Owner', 'Dependencies']
                for i, header in enumerate(impl_headers):
                    cell = sheet.cell(row=current_row, column=i+1, value=header)
                    cell.font = table_header_font
                    cell.fill = table_header_fill
                    cell.border = border
                    cell.alignment = Alignment(horizontal='center', vertical='center')
                current_row += 1
                
                # Get implementation data organized by EPIC
                objectives_data = section_data[section_data['Item'] == 'Objective']
                features_data = section_data[section_data['Item'] == 'Feature']
                user_stories_data = section_data[section_data['Item'] == 'User_Story']
                
                # Process by EPIC (Objective) to maintain hierarchy
                for _, objective_row in objectives_data.iterrows():
                    quarter = get_quarter_from_row(objective_row)
                    epic_category = objective_row.get('Category', '')
                    epic_name = objective_row.get('Description', '')
                    
                    # Find features belonging to this EPIC
                    epic_features = features_data[features_data['Category'].str.startswith(epic_category)]
                    epic_user_stories = user_stories_data[user_stories_data['Category'].str.startswith(epic_category)]
                    
                    # Add EPIC row (if there are features/stories under it) with enhanced merging
                    if not epic_features.empty or not epic_user_stories.empty:
                        # Quarter column
                        sheet.cell(row=current_row, column=1, value=quarter)
                        quarter_cell = sheet.cell(row=current_row, column=1)
                        quarter_cell.font = Font(bold=True, size=11)
                        quarter_cell.border = border
                        quarter_cell.alignment = Alignment(horizontal='center', vertical='center')
                        quarter_cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
                        
                        # EPIC name - merge across 3 columns for prominence
                        sheet.cell(row=current_row, column=2, value=f"EPIC: {epic_name}")
                        sheet.merge_cells(f'B{current_row}:D{current_row}')
                        epic_cell = sheet[f'B{current_row}']
                        epic_cell.font = Font(bold=True, size=11, color='FFFFFF')
                        epic_cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                        epic_cell.border = border
                        epic_cell.alignment = Alignment(horizontal='center', vertical='center')
                        
                        # Owner - merge across remaining columns
                        sheet.cell(row=current_row, column=5, value=objective_row.get('Owner', ''))
                        sheet.merge_cells(f'E{current_row}:F{current_row}')
                        owner_cell = sheet[f'E{current_row}']
                        owner_cell.font = Font(bold=True, size=10)
                        owner_cell.border = border
                        owner_cell.alignment = Alignment(horizontal='center', vertical='center')
                        owner_cell.fill = PatternFill(start_color="E8F3FF", end_color="E8F3FF", fill_type="solid")
                        
                        current_row += 1
                        
                        # Add Features under this EPIC
                        for _, feature_row in epic_features.iterrows():
                            feature_quarter = get_quarter_from_row(feature_row)
                            feature_category = feature_row.get('Category', '')
                            
                            # Add Feature row with enhanced merging
                            # Quarter column
                            sheet.cell(row=current_row, column=1, value=feature_quarter)
                            q_cell = sheet.cell(row=current_row, column=1)
                            q_cell.font = Font(size=10)
                            q_cell.border = border
                            q_cell.alignment = Alignment(horizontal='center', vertical='center')
                            
                            # Feature name - merge across 2 columns for more space
                            sheet.cell(row=current_row, column=2, value=f"Feature: {feature_row.get('Description', '')}")
                            sheet.merge_cells(f'B{current_row}:C{current_row}')
                            feature_cell = sheet[f'B{current_row}']
                            feature_cell.font = Font(bold=True, size=10, color='FFFFFF')
                            feature_cell.fill = PatternFill(start_color="70AD47", end_color="70AD47", fill_type="solid")
                            feature_cell.border = border
                            feature_cell.alignment = Alignment(horizontal='left', vertical='center')
                            
                            # Type column
                            sheet.cell(row=current_row, column=4, value='Feature')
                            type_cell = sheet.cell(row=current_row, column=4)
                            type_cell.font = Font(size=10, italic=True)
                            type_cell.border = border
                            type_cell.alignment = Alignment(horizontal='center', vertical='center')
                            
                            # Owner and Risk - individual columns
                            sheet.cell(row=current_row, column=5, value=feature_row.get('Owner', ''))
                            owner_cell = sheet.cell(row=current_row, column=5)
                            owner_cell.font = Font(size=10)
                            owner_cell.border = border
                            owner_cell.alignment = Alignment(horizontal='center', vertical='center')
                            
                            sheet.cell(row=current_row, column=6, value=feature_row.get('Risk_Level', ''))
                            risk_cell = sheet.cell(row=current_row, column=6)
                            risk_cell.font = Font(size=10)
                            risk_cell.border = border
                            risk_cell.alignment = Alignment(horizontal='center', vertical='center')
                            
                            current_row += 1
                            
                            # Find and add ALL User Stories for this specific Feature
                            feature_user_stories = user_stories_data[user_stories_data['Category'].str.startswith(feature_category + '_US')]
                            
                            for _, story_row in feature_user_stories.iterrows():
                                story_quarter = get_quarter_from_row(story_row)
                                story_data = [
                                    story_quarter,
                                    '',  # Empty EPIC column for stories
                                    '    → ' + story_row.get('Description', ''),  # Indent with arrow
                                    'User Story',
                                    story_row.get('Owner', ''),
                                    story_row.get('Risk_Level', '')
                                ]
                                
                                for i, value in enumerate(story_data):
                                    cell = sheet.cell(row=current_row, column=i+1, value=str(value))
                                    cell.border = border
                                    cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                                    if i == 2:  # Feature/Story column
                                        cell.font = Font(italic=True, size=9)
                                    else:
                                        cell.font = Font(size=9)
                                current_row += 1
                        
                        current_row += 1  # Space between EPICs
                
            else:
                # Special handling for Initiative Purpose section - main header with sub-content
                if section == 'Initiative_Purpose':
                    # Create main section header
                    sheet.cell(row=current_row, column=1, value="Initiative Purpose / Description:")
                    header_cell = sheet.cell(row=current_row, column=1)
                    header_cell.font = Font(bold=True, size=11)
                    header_cell.fill = PatternFill(start_color='E8F3FF', end_color='E8F3FF', fill_type='solid')
                    header_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                    header_cell.border = border
                    
                    # Combine all content or show separately
                    content_parts = []
                    # Process each purpose item separately to show Problem Statement and Solution
                    for _, row in section_data.iterrows():
                        category = row.get('Category', '') or ''
                        description = row.get('Description', '') or ''
                        
                        # Handle None values properly
                        category = str(category).replace('_', ' ').title() if category else ''
                        description = str(description) if description else ''
                        content_parts.append(f"{category}: {description}")
                    
                    combined_content = "\n\n".join(content_parts)
                    
                    # Content merged across all remaining columns (B:H)
                    sheet.cell(row=current_row, column=2, value=combined_content)
                    sheet.merge_cells(f'B{current_row}:H{current_row}')
                    desc_cell = sheet[f'B{current_row}']
                    desc_cell.font = Font(size=11)
                    desc_cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                    desc_cell.border = border
                    
                    current_row += 1
                    
                    # Set column widths - header narrow, description wide
                    sheet.column_dimensions['A'].width = 25  # Header column
                    sheet.column_dimensions['B'].width = 15  # Description start
                    sheet.column_dimensions['C'].width = 15  # Description
                    sheet.column_dimensions['D'].width = 15  # Description
                    sheet.column_dimensions['E'].width = 15  # Description
                    sheet.column_dimensions['F'].width = 15  # Description
                    sheet.column_dimensions['G'].width = 15  # Description
                    sheet.column_dimensions['H'].width = 15  # Description end
                
                else:
                    # Special handling for Milestones, Dependencies, and Risks sections - simple table format
                    if section in ['Milestones', 'Dependencies', 'Risks']:
                        # Add section header
                        sheet.merge_cells(f'A{current_row}:H{current_row}')
                        header_cell = sheet[f'A{current_row}']
                        header_cell.value = section.replace('_', ' ').title()
                        header_cell.font = header_font
                        header_cell.fill = header_fill
                        header_cell.alignment = Alignment(horizontal='left', vertical='center')
                        current_row += 1
                        
                        # Custom headers based on section type
                        if section == 'Milestones':
                            custom_headers = ['Milestone', 'Description', 'Target Date', 'Owner']
                        elif section == 'Dependencies':
                            custom_headers = ['Dependency Type', 'Description', 'Risk Level', 'Mitigation']
                        else:  # Risks
                            custom_headers = ['Risk Type', 'Description', 'Risk Level', 'Mitigation']
                        
                        # Add headers
                        for i, header in enumerate(custom_headers):
                            cell = sheet.cell(row=current_row, column=i+1, value=header)
                            cell.font = table_header_font
                            cell.fill = table_header_fill
                            cell.border = border
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        current_row += 1
                        
                        # Add data rows
                        for _, row in section_data.iterrows():
                            if section == 'Milestones':
                                data_values = [
                                    row.get('Item', ''),
                                    row.get('Description', ''),
                                    row.get('Q1_2026', '') or row.get('Q2_2026', '') or row.get('Q3_2026', '') or row.get('Q4_2026', ''),
                                    row.get('Owner', '')
                                ]
                            else:  # Dependencies or Risks
                                data_values = [
                                    str(row.get('Category', '') or '').replace('_', ' '),
                                    str(row.get('Description', '') or ''),
                                    str(row.get('Risk_Level', '') or ''),
                                    str(row.get('Mitigation', '') or '')
                                ]
                            
                            for i, value in enumerate(data_values):
                                cell = sheet.cell(row=current_row, column=i+1, value=str(value))
                                cell.border = border
                                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                                if i == 0:  # First column bold
                                    cell.font = Font(bold=True, size=10)
                                else:
                                    cell.font = Font(size=10)
                            current_row += 1
                        
                        # Set custom column widths
                        sheet.column_dimensions['A'].width = 25  # Type column
                        sheet.column_dimensions['B'].width = 60  # Description column
                        sheet.column_dimensions['C'].width = 15  # Risk Level/Date column
                        sheet.column_dimensions['D'].width = 40  # Mitigation/Owner column
                    
                    else:
                        # Regular section processing for other sections
                        # Add section header
                        sheet.merge_cells(f'A{current_row}:H{current_row}')
                        header_cell = sheet[f'A{current_row}']
                        header_cell.value = section.replace('_', ' ').title()
                        header_cell.font = header_font
                        header_cell.fill = header_fill
                        header_cell.alignment = Alignment(horizontal='left', vertical='center')
                        current_row += 1
                        
                        # Add table headers
                        headers = ['Category', 'Item', 'Description', 'Q1_2026', 'Q2_2026', 'Q3_2026', 'Q4_2026', 'Owner']
                        for i, header in enumerate(headers):
                            cell = sheet.cell(row=current_row, column=i+1, value=header.replace('_', ' '))
                            cell.font = table_header_font
                            cell.fill = table_header_fill
                            cell.border = border
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                        current_row += 1
                        
                        # Add data rows
                        for _, row in section_data.iterrows():
                            data_row = [
                                row.get('Category', ''),
                                row.get('Item', ''),
                                row.get('Description', ''),
                                row.get('Q1_2026', ''),
                                row.get('Q2_2026', ''),
                                row.get('Q3_2026', ''),
                                row.get('Q4_2026', ''),
                                row.get('Owner', '')
                            ]
                            
                            for i, value in enumerate(data_row):
                                cell = sheet.cell(row=current_row, column=i+1, value=str(value))
                                cell.border = border
                                cell.alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)
                            current_row += 1
            
            current_row += 1  # Add space between sections
        
        # Auto-adjust column widths
        column_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i, column_letter in enumerate(column_letters):
            max_length = 0
            for row in sheet.iter_rows(min_col=i+1, max_col=i+1):
                for cell in row:
                    if not hasattr(cell, 'column_letter'):  # Skip merged cells
                        continue
                    try:
                        if cell.value and len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
            adjusted_width = min(max_length + 2, 50)
            sheet.column_dimensions[column_letter].width = adjusted_width
        
        # Save file
        excel_file = os.path.join(project_path, f"{project_name}_business_case_from_csv.xlsx")
        wb.save(excel_file)
        
        print(f"✅ Excel file created from CSV: {excel_file}")
        return excel_file
        
    except Exception as e:
        print(f"❌ Error creating Excel from CSV: {e}")
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python generate_excel_from_csv.py <project_path> <project_name>")
        sys.exit(1)
    
    project_path = sys.argv[1]
    project_name = sys.argv[2]
    
    excel_file = create_excel_from_csv(project_path, project_name)
    if not excel_file:
        sys.exit(1)

if __name__ == "__main__":
    main()