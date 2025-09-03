import os
import streamlit as st
from anthropic import Anthropic

def initialize_session_state():
    """Initialize all necessary session state variables"""
    # Project workflow state
    if "use_case_step" not in st.session_state:
        st.session_state.use_case_step = "create_new"
    
    # Chat and data collection
    if "onboarding_chat" not in st.session_state:
        st.session_state.onboarding_chat = []
    
    if "use_case_data" not in st.session_state:
        st.session_state.use_case_data = {}
    
    if "collection_step" not in st.session_state:
        st.session_state.collection_step = "name"
    
    # Selected solution/project
    if "selected_solution" not in st.session_state:
        st.session_state.selected_solution = None
    
    # URL parameter handling for project selection
    if "project" in st.query_params:
        project_name = st.query_params.project
        if project_name and project_name != st.session_state.selected_solution:
            st.session_state.selected_solution = project_name
            st.session_state.use_case_step = "selected"

def extract_data_from_input(user_input, context_data):
    """Extract project data from user input using Claude"""
    try:
        client = Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])
        
        # Include current context to avoid overwriting
        current_context = ""
        if context_data:
            current_context = f"\nCurrent context: {context_data}"
        
        system_prompt = f"""You are a data extraction assistant. Extract project information from user input and return it as JSON.

Required fields:
- name: Project name
- description: What the project does
- countries: Deployment countries (for compliance)
- platforms: Target platforms (web, mobile, desktop, etc.)
- application_type: Internal or External
- constraints: Technical and business constraints
- criticality: Business criticality level (1-5 scale)

IMPORTANT: 
- Only extract data that is explicitly mentioned in the user input
- If a field is not mentioned or unclear, set it to null
- Don't guess or infer beyond what's clearly stated
- If current context exists, don't re-extract already captured data unless user is updating it

{current_context}

Return ONLY a JSON object in this exact format:
{{
  "name": "extracted name or null",
  "description": "extracted description or null", 
  "countries": "extracted countries or null",
  "platforms": "extracted platforms or null",
  "application_type": "extracted type or null",
  "constraints": "extracted constraints or null",
  "criticality": "extracted criticality or null"
}}"""

        message = client.messages.create(
            model="claude-opus-4-1-20250805",
            max_tokens=1024,
            temperature=0.1,
            system=system_prompt,
            messages=[{"role": "user", "content": f"Extract project data from: {user_input}"}]
        )
        
        response_text = message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
        
        # Parse JSON response
        import json
        try:
            # Clean the response to extract just JSON
            response_text = response_text.strip()
            if response_text.startswith('```'):
                # Remove code block markers
                lines = response_text.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip().startswith('```') and not in_json:
                        in_json = True
                        continue
                    elif line.strip().startswith('```') and in_json:
                        break
                    elif in_json:
                        json_lines.append(line)
                response_text = '\n'.join(json_lines)
            
            extracted_data = json.loads(response_text)
            
            # Filter out null values and empty strings
            filtered_data = {}
            for key, value in extracted_data.items():
                if value and value != "null" and str(value).strip():
                    filtered_data[key] = str(value).strip()
            
            return filtered_data
            
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract JSON from the response
            import re
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                try:
                    extracted_data = json.loads(json_match.group())
                    # Filter out null values and empty strings
                    filtered_data = {}
                    for key, value in extracted_data.items():
                        if value and value != "null" and str(value).strip():
                            filtered_data[key] = str(value).strip()
                    return filtered_data
                except json.JSONDecodeError:
                    pass
            return {}
            
    except Exception as e:
        st.error(f"Error extracting data: {str(e)}")
        return {}

def get_claude_response(prompt, context="", is_data_collection=False):
    """Get response from Claude"""
    try:
        client = Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])
        
        if is_data_collection:
            system_prompt = """You are a product planning assistant collecting project information. You can extract multiple pieces of information from a single user input.

Current collection requirements:
- Name: Project name
- Description: What the project does
- Countries: Deployment countries (for compliance)
- Platforms: Target platforms (web, mobile, desktop, etc.)
- Application type: Internal or External
- Constraints: Technical and business constraints (Response time, Data Privacy & Protection, Data compliance)
- Criticality: Business criticality level (1-5 scale)

Be conversational but concise. When users provide comprehensive information, acknowledge what you've extracted and ask for any missing pieces. Extract data intelligently and ask the next relevant question based on what's missing."""
        else:
            system_prompt = """You are a helpful product planning assistant. You help users decide between creating a new project or working with an existing one. 

When users express interest in:
- Creating something new, building from scratch, starting fresh -> respond with "NEW_USE_CASE"
- Working with existing, continuing previous work, selecting from existing -> respond with "EXISTING_USE_CASE"

Always be friendly and guide them through their decision. Try to suggest criticality based on above input. If they're unclear, ask clarifying questions to help them decide."""

        with st.spinner("Thinking..."):
            message = client.messages.create(
                model="claude-opus-4-1-20250805",  # Fixed model name
                max_tokens=1024,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text if hasattr(message.content[0], 'text') else str(message.content[0])
            
            if not is_data_collection:
                # Check for decision keywords
                if "NEW_USE_CASE" in response_text:
                    st.session_state.use_case_step = "create_new"
                    # Clear chat and start fresh for new project
                    st.session_state.onboarding_chat = []
                    st.session_state.use_case_data = {}
                    st.session_state.collection_step = "name"
                    return "Perfect! Let's create your new project. What's the name of your project?"
                elif "EXISTING_USE_CASE" in response_text:
                    st.session_state.use_case_step = "select_existing"
                    return "Great! You want to work with an existing project. Let me show you what's available."
            
            return response_text
            
    except Exception as e:
        return f"I'm having trouble connecting right now. Error: {str(e)}"

def run_analysis_command(command_name, command_info, solution_path):
    """Run the selected analysis command using Claude"""
    try:
        with st.spinner(f"🔄 Running {command_name}..."):
            # Read the usecase content for analysis
            usecase_file = os.path.join(solution_path, "usecase.md")
            context_file = os.path.join(solution_path, "context.md")
            
            usecase_content = ""
            if os.path.exists(usecase_file):
                with open(usecase_file, 'r', encoding='utf-8') as f:
                    usecase_content = f.read()
            elif os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    usecase_content = f.read()
            
            if not usecase_content:
                st.error("❌ No project content found to analyze")
                return
            
            # Create analysis prompt
            analysis_prompt = f"Based on the following project information, please provide a {command_name.lower()}:\n\n{usecase_content}"
            
            # Get Claude's response
            response = get_claude_response(analysis_prompt, usecase_content)
            
            if response and len(response) > 100:
                output_file = command_info.get('output_file')
                if output_file:
                    output_path = os.path.join(solution_path, output_file)
                    os.makedirs(solution_path, exist_ok=True)
                    
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response)
                    
                    st.success(f"✅ {command_name} completed successfully!")
                    st.info(f"📄 Output saved to: `{output_file}`")
                else:
                    st.success(f"✅ {command_name} completed successfully!")
                    st.markdown("### Analysis Result:")
                    st.markdown(response)
            else:
                st.error("❌ Analysis failed - insufficient response from AI")
            
    except Exception as e:
        st.error(f"❌ Error running {command_name}: {e}")

def regenerate_analysis(command_name, command_info, solution_path):
    """Regenerate analysis with versioning"""
    try:
        output_file = command_info.get('output_file')
        if output_file:
            output_path = os.path.join(solution_path, output_file)
            
            if os.path.exists(output_path):
                import datetime
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                version_name = f"{output_file.replace('.md', '')}_v{timestamp}.md"
                version_path = os.path.join(solution_path, version_name)
                import shutil
                shutil.move(output_path, version_path)
                st.info(f"📋 Previous version saved as: `{version_name}`")
        
        run_analysis_command(command_name, command_info, solution_path)
        
    except Exception as e:
        st.error(f"❌ Error regenerating {command_name}: {e}")

def get_existing_solutions():
    """Get list of existing solutions from workspace"""
    workspace_dir = "../workspace"
    if not os.path.exists(workspace_dir):
        return []
    
    solutions = []
    for item in os.listdir(workspace_dir):
        item_path = os.path.join(workspace_dir, item)
        if os.path.isdir(item_path):
            solutions.append(item)
    return solutions

def update_url_with_project(project_name):
    """Update URL with the current project"""
    if project_name:
        st.query_params.project = project_name
    else:
        # Clear project parameter if no project selected
        if 'project' in st.query_params:
            del st.query_params.project

def generate_and_save_use_case():
    """Generate and save the complete use case"""
    try:
        data = st.session_state.use_case_data
        
        # Validate required data
        if not data.get('name'):
            st.error("Project name is required")
            return False
        
        # Generate comprehensive prompt
        prompt = f"""# {data.get('name', 'Unnamed Project')}

## Project Overview
- **Description:** {data.get('description', 'N/A')}
- **Target Platforms:** {data.get('platforms', 'N/A')}

## Technical & Business Constraints
- **Business Criticality:** {data.get('criticality', 'N/A')}
- **Application Type:** {data.get('application_type', 'N/A')} application requirements
- **Constraints:** {data.get('constraints', 'N/A')}

## Compliance Requirements
Based on the target countries **({data.get('countries', 'N/A')})**, relevant compliance are required.
- GDPR (if applicable to EU countries)
- Data protection laws
- Privacy regulations
- Industry-specific compliance requirements

## Please provide a comprehensive analysis covering:
1. Functional and Non-Functional Requirements Analysis
2. Architecture Recommendations based on platforms and constraints
3. Compliance and Security Requirements based on countries and criticality
4. Risk Assessment and Mitigation Strategies
5. Implementation Roadmap and Success Metrics
"""
        
        # Create workspace directory
        project_name = data.get('name', 'unnamed').lower().replace(" ", "-").replace("/", "-")
        workspace_dir = os.path.join("../workspace", project_name)
        os.makedirs(workspace_dir, exist_ok=True)
        
        # Save to usecase.md file
        usecase_file = os.path.join(workspace_dir, "usecase.md")
        with open(usecase_file, 'w', encoding='utf-8') as f:
            f.write(prompt)
        
        # Set as selected solution
        st.session_state.selected_solution = project_name
        st.session_state.use_case_step = "selected"
        
        return True
        
    except Exception as e:
        st.error(f"Error saving project: {str(e)}")
        return False

def get_next_missing_field(use_case_data):
    """Get the next missing required field"""
    required_fields = [
        ("name", "What's the name of your project?"),
        ("description", "What does your project do? Briefly describe its main functionality."),
        ("countries", "Which countries will this project be deployed in? (This helps determine compliance requirements)"),
        ("platforms", "What platforms will you target? (e.g., web, mobile, desktop)"),
        ("application_type", "Is this an Internal application (for company employees) or External application (for public/customers)?"),
        ("constraints", "What are your main technical and business constraints? Consider: Response time requirements, Data privacy, Mobile-friendly interface, GDPR and Data policy compliant."),
        ("criticality", "What's the business criticality level? (1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical)")
    ]
    
    for field, question in required_fields:
        if field not in use_case_data or not use_case_data[field]:
            return field, question
    
    return None, None

def display_extracted_summary(extracted_fields, use_case_data):
    """Display a summary of extracted information"""
    if not extracted_fields:
        return ""
    
    field_icons = {
        "name": "🏷️",
        "description": "📝",
        "countries": "🌍",
        "platforms": "💻",
        "application_type": "🏢",
        "constraints": "⚠️",
        "criticality": "🔥"
    }
    
    field_descriptions = {
        "name": "Project Name",
        "description": "Description",
        "countries": "Target Countries",
        "platforms": "Platforms",
        "application_type": "Application Type",
        "constraints": "Constraints",
        "criticality": "Criticality Level"
    }
    
    summary = ""
    for field in extracted_fields:
        if field in use_case_data and use_case_data[field]:
            icon = field_icons.get(field, "📋")
            desc = field_descriptions.get(field, field.replace('_', ' ').title())
            summary += f"{icon} **{desc}:** {use_case_data[field]}\n"
    
    return summary

def smart_data_processing(user_input):
    """Process user input intelligently, extracting multiple fields if present"""
    # Extract data using Claude
    extracted_data = extract_data_from_input(user_input, st.session_state.use_case_data)
    
    # Track what was extracted
    extracted_fields = []
    
    # Update session state with extracted data
    for field, value in extracted_data.items():
        if value and value.strip():
            st.session_state.use_case_data[field] = value.strip()
            extracted_fields.append(field)
    
    # If no data was extracted and we're in sequential mode, fall back to current step
    if not extracted_fields:
        current_step = st.session_state.collection_step
        if current_step == "name":
            # For name, always accept the input as the project name
            st.session_state.use_case_data[current_step] = user_input.strip()
            extracted_fields.append(current_step)
        else:
            # For other fields, try keyword detection
            lower_input = user_input.lower()
            
            # Simple keyword-based extraction as fallback
            if current_step == "countries" and any(country in lower_input for country in ["usa", "us", "united states", "uk", "germany", "india", "canada", "australia", "france", "spain", "italy", "japan", "china", "brazil", "global", "worldwide", "europe", "asia"]):
                st.session_state.use_case_data[current_step] = user_input.strip()
                extracted_fields.append(current_step)
            elif current_step == "platforms" and any(platform in lower_input for platform in ["web", "mobile", "desktop", "ios", "android", "windows", "mac", "linux", "browser"]):
                st.session_state.use_case_data[current_step] = user_input.strip()
                extracted_fields.append(current_step)
            elif current_step == "application_type" and any(app_type in lower_input for app_type in ["internal", "external", "public", "private", "employee", "customer", "client"]):
                st.session_state.use_case_data[current_step] = user_input.strip()
                extracted_fields.append(current_step)
            elif current_step == "criticality" and any(crit in lower_input for crit in ["1", "2", "3", "4", "5", "low", "medium", "high", "critical"]):
                st.session_state.use_case_data[current_step] = user_input.strip()
                extracted_fields.append(current_step)
            else:
                # Default fallback - accept any input for the current step
                st.session_state.use_case_data[current_step] = user_input.strip()
                extracted_fields.append(current_step)
    
    # Find next missing field
    next_field, next_question = get_next_missing_field(st.session_state.use_case_data)
    
    if next_field:
        st.session_state.collection_step = next_field
        
        # Create response acknowledging what was extracted
        if len(extracted_fields) > 1:
            response = f"Excellent! I captured multiple details from your message:\n\n"
            response += display_extracted_summary(extracted_fields, st.session_state.use_case_data)
            response += f"\nNext: {next_question}"
        elif len(extracted_fields) == 1:
            response = display_extracted_summary(extracted_fields, st.session_state.use_case_data)
            response += f"\n{next_question}"
        else:
            response = next_question
        
        return response
    else:
        # All fields collected - show final summary
        response = "🎉 Perfect! Here's what I collected:\n\n"
        all_fields = ["name", "description", "countries", "platforms", "application_type", "constraints", "criticality"]
        response += display_extracted_summary(all_fields, st.session_state.use_case_data)
        response += "\nCreating your project now..."
        return response

def restart_project_creation():
    """Restart the project creation process"""
    st.session_state.use_case_step = "create_new"
    st.session_state.onboarding_chat = []
    st.session_state.use_case_data = {}
    st.session_state.collection_step = "name"
    st.session_state.selected_solution = None
    update_url_with_project(None)  # Clear URL

def interactive_data_collection():
    """Handle interactive data collection using simplified approach"""
    
    # Initialize with first question if chat is empty
    if not st.session_state.onboarding_chat:
        welcome_msg = {
            "role": "assistant", 
            "content": "What's the name of your project?"
        }
        st.session_state.onboarding_chat.append(welcome_msg)
    
    # Display conversation
    for message in st.session_state.onboarding_chat:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Show progress
    required_fields = ["name", "description", "countries", "platforms", "application_type", "constraints", "criticality"]
    completed_fields = len([k for k in required_fields if k in st.session_state.use_case_data and st.session_state.use_case_data[k]])
    progress = completed_fields / len(required_fields)
    
    if completed_fields > 0:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(progress, text=f"Progress: {completed_fields}/{len(required_fields)} fields completed")
        with col2:
            if st.button("🗑️ Clear All", help="Clear all data and start fresh", key="clear_data"):
                restart_project_creation()
                st.rerun()
        
        # Show extracted data summary
        with st.expander("📋 Extracted Information", expanded=False):
            for field in required_fields:
                if field in st.session_state.use_case_data and st.session_state.use_case_data[field]:
                    st.markdown(f"**{field.replace('_', ' ').title()}:** {st.session_state.use_case_data[field]}")
    
    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message
        st.session_state.onboarding_chat.append({"role": "user", "content": prompt})
        
        # Smart processing
        response = smart_data_processing(prompt)
        
        # Check if we're done
        if "Creating your project now" in response:
            # Generate and save
            if generate_and_save_use_case():
                response += "\n\n✅ Your project has been successfully created and saved! You can now proceed to the other tabs."
                # Update URL with new project
                update_url_with_project(st.session_state.selected_solution)
            else:
                response = "❌ There was an error creating your project. Please try again."
        
        # Add assistant response
        st.session_state.onboarding_chat.append({"role": "assistant", "content": response})
        st.rerun()

def handle_new_use_case():
    """Handle creating new use case with interactive collection"""
    # st.markdown("## 🆕 Create New Project")
    interactive_data_collection()

def handle_existing_use_case():
    """Handle selecting existing use case"""
    st.markdown("## 📁 Select Existing Project")
    
    existing_solutions = get_existing_solutions()
    
    if not existing_solutions:
        st.warning("⚠️ No existing projects found in workspace.")
        st.info("💡 Would you like to create a new project instead?")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🆕 Create New Project", type="primary", use_container_width=True):
                st.session_state.use_case_step = "create_new"
                st.session_state.onboarding_chat = []
                st.session_state.use_case_data = {}
                st.session_state.collection_step = "name"
                update_url_with_project(None)  # Clear URL
                st.rerun()
        with col2:
            if st.button("← Start Over", use_container_width=True):
                st.session_state.use_case_step = "initial"
                st.session_state.onboarding_chat = []
                update_url_with_project(None)  # Clear URL
                st.rerun()
        return
    
    st.markdown("Here are your existing projects:")
    
    # Interactive selection
    selected = st.selectbox(
        "Choose your project:",
        options=[""] + existing_solutions,
        format_func=lambda x: "Select a project..." if x == "" else x.replace("-", " ").title(),
        help="Select from your existing projects"
    )
    
    if selected:
        st.session_state.selected_solution = selected
        st.session_state.use_case_step = "selected"
        update_url_with_project(selected)  # Update URL
        st.success(f"🎯 Selected: {selected.replace('-', ' ').title()}")
        st.rerun()

def ask_use_case_type():
    """Interactive chat for use case type selection"""
    if st.session_state.use_case_step == "initial":
        st.markdown("### 💬 Let's get started with your project planning")
        
        # Initialize chat with welcome message
        if not st.session_state.onboarding_chat:
            welcome_msg = {
                "role": "assistant", 
                "content": "Hi! Would you like to create a new project or work with an existing one?"
            }
            st.session_state.onboarding_chat.append(welcome_msg)
        
        # Display chat messages
        for message in st.session_state.onboarding_chat:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Tell me what you'd like to do..."):
            # Add user message
            st.session_state.onboarding_chat.append({"role": "user", "content": prompt})
            
            # Get Claude's response
            response = get_claude_response(prompt)
            st.session_state.onboarding_chat.append({"role": "assistant", "content": response})
            
            st.rerun()
    
    elif st.session_state.use_case_step == "create_new":
        handle_new_use_case()
    
    elif st.session_state.use_case_step == "select_existing":
        handle_existing_use_case()

def show_product_use_case_page():
    """Show the Product Use Case page with editable markdown and analysis button"""
    if not st.session_state.get('selected_solution'):
        ask_use_case_type()
    else:
        # Show selected use case with content
        st.markdown(f"## 📋 {st.session_state.selected_solution.replace('-', ' ').title()}")
        
        solution_path = os.path.join("../workspace", st.session_state.selected_solution)
        usecase_file = os.path.join(solution_path, "usecase.md")
        
        # Determine which file to use
        if os.path.exists(usecase_file):
            current_file = usecase_file
        else:
            st.error("⚠️ Project files not found. Please recreate the project.")
            return
        
        try:
            with open(current_file, 'r', encoding='utf-8') as f:
                context_content = f.read()
        except Exception as e:
            st.error(f"❌ Error reading project file: {str(e)}")
            return

        # Show context in expandable section
        with st.expander("📄 Project Context", expanded=False):
            st.markdown(context_content)