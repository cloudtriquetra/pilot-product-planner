import os
import streamlit as st
from anthropic import Anthropic
import json
import re

def get_claude_response(prompt, context="", is_data_collection=False):
    """Get response from Claude"""
    try:
        client = Anthropic(api_key=st.secrets['ANTHROPIC_API_KEY'])
        
        if is_data_collection:
            system_prompt = """You are a product planning assistant collecting project information. Ask crisp, direct questions.

Current collection requirements:
- Name: Project name
- Description: What the project does
- Countries: Deployment countries (for compliance)
- Platforms: Target platforms (web, mobile, desktop, etc.)
- Constraints: Technical and business constraints (Internal/External application, Response time requirements, Data privacy, Mobile-friendly interface, GDPR and Data policy compliant)
- Criticality: Business criticality level (1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical)

IMPORTANT: Extract ALL information from user input when provided. Users may provide information for multiple fields in a single message.
Always return your response in this JSON format (and only this format):
{
  "extracted_data": {
    "name": "extracted project name if present",
    "description": "extracted description if present",
    "countries": "extracted countries if present",
    "platforms": "extracted platforms if present",
    "constraints": "extracted constraints if present",
    "criticality": "extracted criticality if present"
  },
  "next_question": "Your conversational response asking about the next piece of information needed",
  "missing_fields": ["list", "of", "field", "names", "still", "missing"]
}

Only include fields in extracted_data that you could confidently extract from the user's input.
The missing_fields array should contain the names of fields that still need to be collected.
NEVER repeat a question for information that has already been provided. Always ask for the next piece of missing information."""
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

def extract_data_from_claude(prompt, current_step):
    """Use Claude to extract multiple fields from a user input"""
    try:
        # Create context of already collected information
        context = ""
        if hasattr(st.session_state, 'use_case_data'):
            collected_info = []
            for field, value in st.session_state.use_case_data.items():
                if value and value.strip():
                    collected_info.append(f"{field}: {value}")
            
            if collected_info:
                context = "Already collected information:\n" + "\n".join(collected_info) + "\n\n"
        
        # Get the response from Claude with the data extraction prompt and context
        enhanced_prompt = context + prompt if context else prompt
        response = get_claude_response(enhanced_prompt, is_data_collection=True)
        
        # Parse Claude's response to get structured data
        extracted_data = parse_claude_response(response)
        
        if extracted_data and "extracted_data" in extracted_data and "next_question" in extracted_data:
            return extracted_data
        
        # Fallback: If we couldn't extract structured data, just store the current field
        fallback_response = {
            "extracted_data": {
                current_step: prompt.strip()
            },
            "next_question": get_next_question(current_step),
            "missing_fields": get_missing_fields([current_step])
        }
        return fallback_response
        
    except Exception as e:
        st.error(f"Error extracting data: {str(e)}")
        # Fallback to storing just the current field
        return {
            "extracted_data": {
                current_step: prompt.strip()
            },
            "next_question": get_next_question(current_step),
            "missing_fields": get_missing_fields([current_step])
        }

def get_next_question(current_step):
    """Get the appropriate question for the next step"""
    if current_step == "name" or "name" in current_step:
        return "What does your project do? Briefly describe its main functionality."
    elif current_step == "description" or "description" in current_step:
        return "Which countries will this project be deployed in? (This helps determine compliance requirements)"
    elif current_step == "countries" or "countries" in current_step:
        return "What platforms will you target? (e.g., web, mobile, desktop)"
    elif current_step == "platforms" or "platforms" in current_step:
        return "What are your main technical and business constraints? Consider: Internal/External application, Response time requirements, Data privacy, Mobile-friendly interface, GDPR and Data policy compliant."
    elif current_step == "constraints" or "constraints" in current_step:
        return "What's the business criticality level? (1=Low, 2=Medium-Low, 3=Medium, 4=High, 5=Critical)"
    elif current_step == "criticality" or "criticality" in current_step:
        return "🎉 Perfect! I have all the information. Let me create your project..."
    else:
        return "What's the name of your project?"  # Default fallback

def get_missing_fields(completed_fields):
    """Get a list of fields that still need to be collected"""
    all_fields = ["name", "description", "countries", "platforms", "constraints", "criticality"]
    
    # If completed_fields is a list of field names
    if isinstance(completed_fields, list):
        return [field for field in all_fields if field not in completed_fields]
    
    # If completed_fields is a dict of field names to values
    elif isinstance(completed_fields, dict):
        return [field for field in all_fields if field not in completed_fields or not completed_fields[field].strip()]
    
    # Default case
    return all_fields

def get_next_field(missing_fields):
    """Determine the next field to collect based on missing fields"""
    field_order = ["name", "description", "countries", "platforms", "constraints", "criticality"]
    for field in field_order:
        if field in missing_fields:
            return field
    return "complete"  # All fields are collected

def initialize_session_state():
    """Initialize all required session state variables"""
    if "use_case_step" not in st.session_state:
        st.session_state.use_case_step = "create_new"
    
    if "onboarding_chat" not in st.session_state:
        st.session_state.onboarding_chat = []
    
    if "use_case_data" not in st.session_state:
        st.session_state.use_case_data = {}
    
    if "collection_step" not in st.session_state:
        st.session_state.collection_step = "name"
    
    if "selected_solution" not in st.session_state:
        st.session_state.selected_solution = None
    
    # Check URL parameters for project selection
    if "project" in st.query_params and st.query_params.project:
        project_name = st.query_params.project
        if os.path.exists(os.path.join("../workspace", project_name)):
            st.session_state.selected_solution = project_name
            st.session_state.use_case_step = "selected"

def parse_claude_response(response):
    """Parse Claude's response to ensure we get valid JSON format"""
    try:
        # Try to find JSON content in Claude's response
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            try:
                # Try to parse the JSON content
                json_content = json.loads(json_match.group(0))
                return json_content
            except json.JSONDecodeError:
                pass
    except Exception as e:
        st.error(f"Error parsing Claude response: {str(e)}")
    
    return None  # Return None if we couldn't parse JSON

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
**Description:** {data.get('description', 'N/A')}
**Target Countries:** {data.get('countries', 'N/A')}
**Target Platforms:** {data.get('platforms', 'N/A')}
**Business Criticality:** {data.get('criticality', 'N/A')}

## Technical & Business Constraints
{data.get('constraints', 'N/A')}

### Constraint Categories:
- **Application Type:** Internal/External application requirements
- **Performance:** Response time and performance requirements
- **Data Privacy:** Data privacy and protection measures
- **Compliance:** GDPR and Data policy compliance requirements

## Compliance Requirements
Based on the target countries ({data.get('countries', 'N/A')}), relevant compliance requirements will need to be considered including:
- GDPR (if applicable to EU countries)
- Data protection laws
- Privacy regulations
- Industry-specific compliance requirements

Please provide a comprehensive analysis covering:
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
        
        # Close project creation expander if it exists
        if hasattr(st.session_state, 'create_project_expanded'):
            st.session_state.create_project_expanded = False
        
        return True
        
    except Exception as e:
        st.error(f"Error saving project: {str(e)}")
        return False

def interactive_data_collection():
    """Handle interactive data collection using intelligent extraction"""
    # st.markdown("### 🤖 Interactive Project Builder")
    
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
    required_fields = ["name", "description", "countries", "platforms", "constraints", "criticality"]
    completed_fields = [field for field in required_fields if field in st.session_state.use_case_data and st.session_state.use_case_data[field].strip()]
    progress = len(completed_fields) / len(required_fields)
    
    if completed_fields:
        st.progress(progress, text=f"Progress: {len(completed_fields)}/{len(required_fields)} fields completed")
        
        # Show collected data in an expander
        with st.expander("📝 Information Collected So Far"):
            for field in required_fields:
                if field in st.session_state.use_case_data and st.session_state.use_case_data[field].strip():
                    field_name = field.capitalize()
                    st.markdown(f"**{field_name}**: {st.session_state.use_case_data[field]}")
    
    # Chat input
    if prompt := st.chat_input("Your response..."):
        # Add user message to chat
        st.session_state.onboarding_chat.append({"role": "user", "content": prompt})
        
        # Get current step
        current_step = st.session_state.collection_step
        
        # Extract data from user input using Claude
        extracted_data = extract_data_from_claude(prompt, current_step)
        
        # Update session state with extracted data
        if "extracted_data" in extracted_data:
            for field, value in extracted_data["extracted_data"].items():
                if field in required_fields and value and value.strip():
                    st.session_state.use_case_data[field] = value.strip()
        
        # Recalculate which fields are still missing after updating data
        completed_fields = [field for field in required_fields if field in st.session_state.use_case_data and st.session_state.use_case_data[field].strip()]
        missing_fields = [field for field in required_fields if field not in completed_fields]
        
        # Check if we've completed all fields
        if not missing_fields:
            # All fields collected, generate project
            completion_message = "🎉 Perfect! I have all the information. Let me create your project..."
            
            # Generate and save
            if generate_and_save_use_case():
                completion_message += "\n\n✅ Your project has been successfully created and saved! You can now proceed to the other tabs."
                # Update URL with new project
                update_url_with_project(st.session_state.selected_solution)
            else:
                completion_message = "❌ There was an error creating your project. Please try again."
            
            # Add assistant response
            st.session_state.onboarding_chat.append({"role": "assistant", "content": completion_message})
        else:
            # Still need more fields, set next step
            next_field = get_next_field(missing_fields)
            st.session_state.collection_step = next_field
            
            # Get next question from Claude or use default
            next_question = extracted_data.get("next_question", get_next_question(next_field))
            
            # Add assistant response
            st.session_state.onboarding_chat.append({"role": "assistant", "content": next_question})
        
        st.rerun()

def handle_new_use_case():
    """Handle creating new use case with interactive collection"""
    st.markdown("## 🆕 Create New Project")
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
    
    # Initialize all session state variables
    initialize_session_state()
    
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