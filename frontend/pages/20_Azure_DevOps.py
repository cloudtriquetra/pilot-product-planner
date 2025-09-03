import streamlit as st
import os
import time
import re
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from ui import apply_compact_styles
from ado import load_stories_from_json

st.set_page_config(
    page_title="Azure DevOps Integration",
    page_icon="",
    layout="wide"
)

# Initialize session state
if 'selected_usecase' not in st.session_state:
    st.session_state.selected_usecase = None

# Apply custom styling
apply_compact_styles()

st.title("Azure DevOps Integration")
st.caption("Create user stories in Azure DevOps from your product requirements")

selected_usecase = st.session_state.get('selected_usecase')

if selected_usecase:
    usecase_path = os.path.join("../workspace", selected_usecase)
    st.info(f"Working with use case: **{selected_usecase}**")

    # ADO Configuration in sidebar
    with st.sidebar:
        st.markdown("### 📤 Azure DevOps Settings")

        # Store ADO settings in session state
        if 'ado_settings' not in st.session_state:
            st.session_state.ado_settings = {
                'organization': 'pandeymohit',
                'project': 'devsecops',
                'pat': '',
            }

        # ADO Configuration
        organization = st.text_input(
            "Organization",
            value=st.session_state.ado_settings['organization'],
            help="Your Azure DevOps organization name"
        )
        project = st.text_input(
            "Project",
            value=st.session_state.ado_settings['project'],
            help="Your project name"
        )
        pat = st.text_input(
            "PAT",
            value=st.session_state.ado_settings['pat'],
            type="password",
            help="Personal Access Token with Work Items permissions"
        )

        # Save settings
        st.session_state.ado_settings.update({
            'organization': organization,
            'project': project,
            'pat': pat,
        })

    # Main content area
    try:
        stories_data = load_stories_from_json(usecase_path)
        if stories_data:
            st.success(f"Found {len(stories_data)} stories to upload")

            # Add story editing section
            st.markdown("### 📝 Edit Stories")
            for story_id, story in stories_data.items():
                with st.expander(f"{story_id}: {story['title']}"):
                    # Create columns for better layout
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        story['as_a'] = st.text_input(
                            "As a",
                            value=story['as_a'],
                            key=f"as_a_{story_id}"
                        )
                        story['i_want'] = st.text_area(
                            "I want to",
                            value=story['i_want'],
                            key=f"i_want_{story_id}"
                        )
                        story['so_that'] = st.text_area(
                            "So that",
                            value=story['so_that'],
                            key=f"so_that_{story_id}"
                        )

                    with col2:
                        story['points'] = st.number_input(
                            "Story Points",
                            min_value=1,
                            max_value=13,
                            value=int(story['points']),
                            key=f"points_{story_id}"
                        )
                        story['priority'] = st.selectbox(
                            "Priority",
                            ["Critical", "High", "Medium", "Low"],
                            index=["Critical", "High", "Medium", "Low"].index(story['priority']),
                            key=f"priority_{story_id}"
                        )
                        story['tags'] = st.text_input(
                            "Tags",
                            value=story['tags'],
                            key=f"tags_{story_id}"
                        )

                    # Acceptance Criteria
                    st.markdown("#### Acceptance Criteria")
                    if 'ac_list' not in story:
                        story['ac_list'] = []

                    ac_count = st.number_input(
                        "Number of Acceptance Criteria",
                        min_value=1,
                        max_value=10,
                        value=len(story.get('ac_list', [])) or 1,
                        key=f"ac_count_{story_id}"
                    )

                    new_ac_list = []
                    for i in range(ac_count):
                        ac_list = story['ac_list'][i] if i < len(story['ac_list']) else ""
                        # Update the acceptance criteria section
                        ac_value = f"{ac_list.get('id', '')}: Given {ac_list.get('given', '')}, when {ac_list.get('when', '')}, then {ac_list.get('then', '')}." if ac_list else ""
                        ac = st.text_input(
                            f"Acceptance Criteria {i+1}",
                            value=ac_value,
                            key=f"ac_{story_id}_{i}"
                        )
                        if ac:
                            new_ac_list.append(ac)
                    story['ac_list'] = new_ac_list

            if st.button("🚀 Upload Stories to Azure DevOps", type="primary", use_container_width=True):
                if not organization or not project or not pat:
                    st.error("Please fill in all Azure DevOps settings in the sidebar to continue.")
                else:
                    with st.spinner("Uploading stories to Azure DevOps..."):
                        # Initialize ADO connection
                        credentials = BasicAuthentication('', pat)
                        organization_url = f"https://dev.azure.com/{organization}"
                        connection = Connection(base_url=organization_url, creds=credentials)
                
                        # Get clients
                        core_client = connection.clients.get_core_client()
                        wit_client = connection.clients.get_work_item_tracking_client()

                        # Set up progress tracking
                        progress_bar = st.progress(0)   
                        status_text = st.empty()

                        # Start work item creation    
                        for idx, (story_id, story) in enumerate(stories_data.items(), 1):
                            status_text.text(f"Creating story {idx}/{len(stories_data)}...")

                            time.sleep(0.5)  # Simulate network delay
                            
                            # Create work item
                            area_path = project
                            iteration_path = f"{area_path}\\Sprint 1"
                            
                            wit_create = [
                                {"op": "add", "path": "/fields/System.Title",
                                    "value": f"{story_id}: {story['title']}"},
                                {"op": "add", "path": "/fields/System.Description",
                                    "value": f"As a {story['as_a']}\nI want to {story['i_want']}\nSo that {story['so_that']}"},
                                {"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                                    "value": "\r\n".join([f"- {ac}" for ac in story['ac_list']])},
                                {"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                                    "value": story['points']},
                                {"op": "add", "path": "/fields/System.AreaPath",
                                    "value": area_path},
                                {"op": "add", "path": "/fields/System.IterationPath",
                                    "value": iteration_path},
                                {"op": "add", "path": "/fields/System.Tags",
                                    "value": story['tags']}
                            ]

                            created_item = wit_client.create_work_item(
                                document=wit_create,
                                project=project,
                                type='User Story'
                            )

                            progress = int((idx / len(stories_data)) * 100)
                            progress_bar.progress(progress)

                        status_text.text("✅ All stories uploaded successfully!")
                        st.success(f"Created {len(stories_data)} user stories in Azure DevOps")

        else:
            st.warning("No stories found in the requirements files.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
else:
    st.warning("Please select a use case first on the Dashboard page.")
    st.info("Go to the Dashboard, select a use case, then return to this page.")
