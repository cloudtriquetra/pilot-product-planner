import streamlit as st
import os
import re
import time
from ui import apply_compact_styles
from product_use_case import show_product_use_case_page, initialize_session_state

st.set_page_config(
    page_title="Dashboard",
    page_icon="",
    layout="wide"
)

# Initialize session state
initialize_session_state()

# Add session state for expander
if "create_project_expanded" not in st.session_state:
    st.session_state.create_project_expanded = False

apply_compact_styles()

@st.cache_data(ttl=60)
def get_claude_cli_status():
    """Return (is_runnable, version_text_or_none) for the backend CLI (Claude)."""
    import subprocess

    def _try_cmd(args):
        try:
            completed = subprocess.run(
                args, capture_output=True, text=True, check=False, timeout=3
            )
            if completed.returncode == 0:
                output = (completed.stdout or "") + (completed.stderr or "")
                text = output.strip()
                if text:
                    m = re.search(r"v?(\d+\.\d+\.\d+(?:[-+][\w\.-]+)?)", text)
                    return True, (m.group(0) if m else text)
                return True, None
        except FileNotFoundError:
            return False, None
        except subprocess.TimeoutExpired:
            return False, None
        except Exception:
            return False, None
        return False, None

    for cmd in (["claude", "--version"], ["claude", "version"], ["claude", "-v"]):
        ok, ver = _try_cmd(cmd)
        if ok:
            return True, ver
    return False, None


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-").lower()
    return slug or f"usecase-{int(time.time())}"


st.title("Dashboard")
st.caption("Projects overview and quick actions")

cli_ok, cli_version = get_claude_cli_status()
if cli_ok:
    st.caption(f"🟢 Backend {cli_version if cli_version else ''}")
else:
    st.caption("🔴 Backend CLI not runnable")


# --- Create New Project ---
# Check if use_case_step is active to keep expander open
# if st.session_state.get('use_case_step') in ["initial", "create_new", "select_existing"]:
#     st.session_state.create_project_expanded = True

with st.expander("Create a New Project", expanded=st.session_state.create_project_expanded):
    # Set expander to stay open during interaction
    st.session_state.create_project_expanded = True
    
    # Show product use case form
    show_product_use_case_page()
        # name = st.text_input("Project name (identifier)", placeholder="e.g., checkout-service or product-search")
        # desc = st.text_area("Describe your project", placeholder="Enter a paragraph describing your product or feature...")
        # col_create, col_open = st.columns([3, 1])
        # with col_create:
        #     submit = st.form_submit_button("Create Project", type="primary")
        # with col_open:
        #     auto_open = st.checkbox("Open after create", value=True)

        # if submit:
        #     if not name.strip() or not desc.strip():
        #         st.warning("Please provide both a project name and description.")
        #     else:
        #         slug = _slugify(name)
        #         workspace_dir = os.path.join("../workspace", slug)
        #         os.makedirs(workspace_dir, exist_ok=True)
        #         md_path = os.path.join(workspace_dir, "usecase.md")
        #         with open(md_path, "w", encoding="utf-8") as f:
        #             f.write(f"# {name}\n\n{desc}\n")

        #         st.success(f"Project '{name}' created.")
        #         st.session_state.selected_usecase = slug
        #         if auto_open:
        #             st.switch_page("pages/10_Project_Dashboard.py")


# --- List Existing Projects ---
st.subheader("All Projects")

workspace_root = "../workspace"
projects = []
if os.path.exists(workspace_root) and os.path.isdir(workspace_root):
    for entry in os.listdir(workspace_root):
        p_dir = os.path.join(workspace_root, entry)
        if os.path.isdir(p_dir):
            uc_md = os.path.join(p_dir, "usecase.md")
            if os.path.exists(uc_md):
                try:
                    with open(uc_md, "r", encoding="utf-8") as f:
                        content = f.read()
                    lines = content.split("\n")
                    title = lines[0].replace("# ", "").strip() if lines else entry
                    description = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
                except Exception:
                    title, description = entry, ""
                projects.append({
                    "slug": entry,
                    "title": title or entry,
                    "description": description
                })

if not projects:
    st.info("No projects found yet. Create one using the form above.")
else:
    # Sort alphabetically by title
    projects.sort(key=lambda p: p["title"].lower())
    cols = st.columns(3)
    for idx, proj in enumerate(projects):
        with cols[idx % 3]:
            with st.container(border=True):
                st.markdown(f"### {proj['title']}")
                st.caption(f"`{proj['slug']}`")
                if proj["description"]:
                    st.write(proj["description"][:280] + ("..." if len(proj["description"]) > 280 else ""))
                open_key = f"open_{proj['slug']}"
                if st.button("Open", key=open_key, use_container_width=True):
                    st.session_state.selected_usecase = proj["slug"]
                    st.switch_page("pages/10_Project_Dashboard.py")


