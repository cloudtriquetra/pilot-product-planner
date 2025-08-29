import streamlit as st
import os
import git
import subprocess
import re
from streamlit_mermaid import st_mermaid
import shutil
import signal
import queue
import threading
import time
import random
import streamlit_shadcn_ui as ui
import logging



st.set_page_config(
    page_title="PILOT",  # This is the browser tab title
    page_icon="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICA8Y2lyY2xlIGN4PSI0MCIgY3k9IjQwIiByPSIzNSIgZmlsbD0iIzNiODJmNiIgb3BhY2l0eT0iMC44Ii8+CiAgPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iMjUiIGZpbGw9IiMxMGI5ODEiIG9wYWNpdHk9IjAuNyIvPgogIDxjaXJjbGUgY3g9IjQwIiBjeT0iNDAiIHI9IjgiIGZpbGw9IiNmZmZmZmYiLz4KICA8Y2lyY2xlIGN4PSI0MCIgY3k9IjIwIiByPSIzIiBmaWxsPSIjZjU5ZTBiIi8+CiAgPGNpcmNsZSBjeD0iNjAiIGN5PSI0MCIgcj0iMyIgZmlsbD0iI2Y1OWUwYiIvPgogIDxjaXJjbGUgY3g9IjQwIiBjeT0iNjAiIHI9IjMiIGZpbGw9IiNmNTllMGIiLz4KICA8Y2lyY2xlIGN4PSIyMCIgY3k9IjQwIiByPSIzIiBmaWxsPSIjZjU5ZTBiIi8+Cjwvc3ZnPgo=",
    layout="centered"                  # Optional: 'centered' or 'wide'
)


# --- Logging Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Session State Initialization ---
if 'usecase_ports' not in st.session_state:
    st.session_state.usecase_ports = {}
if 'running_servers' not in st.session_state:
    st.session_state.running_servers = {} # port -> process
if 'next_port' not in st.session_state:
    st.session_state.next_port = 8005
if 'selected_usecase_index' not in st.session_state:
    st.session_state.selected_usecase_index = 0
if 'selected_usecase' not in st.session_state:
    st.session_state.selected_usecase = None
if 'current_process' not in st.session_state:
    st.session_state.current_process = None
if 'last_generation_status' not in st.session_state:
    st.session_state.last_generation_status = None



def run_command_in_thread(process, q):
    try:
        for line in iter(process.stdout.readline, ''):
            # Log the output to the console
            line_without_newline = line.strip()
            if line_without_newline:
                logging.info(line_without_newline)
            q.put(line)
        process.stdout.close()
        return_code = process.wait()
        q.put(f"---RC:{return_code}---")
    except Exception as e:
        logging.error(f"Error in command thread: {e}")
        q.put(str(e))
        q.put("---RC:1---")


def start_docs_server(usecase_path, port):
    # Kill any existing server on this specific port
    if port in st.session_state.running_servers:
        proc = st.session_state.running_servers[port]
        if proc.poll() is None:
            st.warning(f"Stopping previous documentation server (PID: {proc.pid}) on port {port}...")
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                proc.wait()
            except ProcessLookupError:
                pass  # Process already dead
            finally:
                if port in st.session_state.running_servers:
                    del st.session_state.running_servers[port]
    
    # Give the OS a moment to release the port
    time.sleep(2)

    ra_path = os.path.join(usecase_path, '_ra')
    if not os.path.isdir(ra_path):
        st.error(f"Directory not found: {ra_path}. Cannot start documentation server.")
        return

    try:
        # Step 1: Install documentation dependencies
        with st.spinner("Installing documentation dependencies..."):
            install_process = subprocess.run(
                [
                    "pip", "install",
                    "mkdocs>=1.5.0",
                    "mkdocs-material>=9.0.0",
                    "mkdocs-mermaid2-plugin>=1.0.0",
                    "pymdown-extensions>=10.0.0",
                    "mkdocs-awesome-pages-plugin>=2.8.0",
                    "mkdocs-minify-plugin>=0.7.0",
                    "mkdocs-git-revision-date-localized-plugin>=1.2.0"
                ],
                cwd=ra_path,
                capture_output=True,
                text=True,
                check=False
            )
            if install_process.returncode != 0:
                st.error("Failed to install dependencies:")
                st.code(install_process.stderr)
                return

        # Step 2: Build docs
        with st.spinner("Building documentation..."):
            build_process = subprocess.run(
                ["mkdocs", "build", "--clean"],
                cwd=ra_path,
                capture_output=True,
                text=True,
                check=False
            )
            if build_process.returncode != 0:
                st.error("Failed to build documentation:")
                st.code(build_process.stderr)
                return
        
        # Step 3: Serve docs
        with st.spinner(f"Starting documentation server on port {port}..."):
            proc = subprocess.Popen(
                ["mkdocs", "serve", f"--dev-addr=127.0.0.1:{port}"],
                cwd=ra_path,
                preexec_fn=os.setsid
            )
            st.session_state.running_servers[port] = proc
            st.success("Documentation server started.")
            
            # Centered button to view docs
            _, col, _ = st.columns([1, 2, 1])
            with col:
                st.link_button("View Documentation", url=f"http://localhost:{port}", use_container_width=True)

    except Exception as e:
        st.error(f"An error occurred while setting up the documentation server: {e}")

@st.fragment
def show_generation_progress():
    with st.status(f"Running artifact generation: `{st.session_state.selected_command_name_running}` on `{st.session_state.selected_usecase}`...", expanded=True) as status:
        log_placeholder = st.empty()

        # Loop to update the log
        while st.session_state.get('command_is_running'):
            while not st.session_state.command_q.empty():
                line = st.session_state.command_q.get_nowait()
                if line.startswith("---RC:"):
                    st.session_state.command_return_code = int(line.replace("---RC:", "").replace("---", ""))
                    st.session_state.command_is_running = False
                    st.session_state.current_process = None
                    break
                st.session_state.command_log += line
            
            log_placeholder.code(st.session_state.command_log)
            
            if not st.session_state.get('command_is_running'):
                # Command has just finished
                if st.session_state.command_return_code == 0:
                    # Post-run actions: if it was a doc generation, start the server.
                    if "documentation" in st.session_state.selected_command_name_running.lower():
                        status.update(label="Documentation generated!", state="complete", expanded=False)
                        logging.info("Documentation generation successful.")
                        st.success("Documentation generation complete. Starting server...")
                        running_usecase_path = st.session_state.usecase_path_running
                        if running_usecase_path not in st.session_state.usecase_ports:
                            st.session_state.usecase_ports[running_usecase_path] = st.session_state.next_port
                            st.session_state.next_port += 1
                        port_to_start = st.session_state.usecase_ports[running_usecase_path]
                        start_docs_server(running_usecase_path, port_to_start)
                    else:
                        status.update(label="Artifact generation complete!", state="complete", expanded=False)
                        logging.info(f"Artifact generation successful: {st.session_state.selected_command_name_running}")
                        st.session_state.last_generation_status = {"status": "success", "message": "Artifact generation complete!"}

                else:
                    status.update(label="Artifact Generation failed!", state="error")
                    logging.error(f"Artifact Generation failed!: {st.session_state.selected_command_name_running} with exit code {st.session_state.command_return_code}")
                    st.session_state.last_generation_status = {"status": "error", "message": f"Artifact Generation failed with exit code: {st.session_state.command_return_code}"}

                # Rerun one last time to clear the spinner
                st.session_state.current_process = None
                
            else:
                time.sleep(1) # The fragment will re-run itself, not the whole app

st.title("PILOT")
st.caption("Product Innovation & Lifecycle Orchestration Tool")

if st.session_state.get('selected_usecase'):
    st.caption(f"Selected Use Case: `{st.session_state.get('selected_usecase')}`")

# --- Tabs ---
tab_options = ["Product Use Case"]
if st.session_state.get('selected_usecase'):
    tab_options.extend(["Product Planning", "Results"])

# Determine default tab
if st.session_state.get('command_is_running'):
    # Command is running, default to Product Planning tab
    default_tab = "Product Planning"
else:
    default_tab = "Product Use Case"

selected_tab = ui.tabs(options=tab_options, default_value=default_tab)

def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-").lower()
    return slug or f"usecase-{int(time.time())}"

if selected_tab == "Product Use Case":
    # Show any saved use case message
    if st.session_state.get('use_case_saved_message'):
        st.success(st.session_state.use_case_saved_message)
        st.session_state.use_case_saved_message = None  # Clear after showing
    
    with st.expander("Create a new Use Case"):
        with st.form("use_case_form"):
            use_case_name = st.text_input(
                "Use case name (identifier)",
                placeholder="e.g., checkout-service or product-search"
            )
            use_case_desc = st.text_area(
                "Describe your product use case:",
                placeholder="Enter a paragraph describing your product or feature..."
            )
            
            submitted = st.form_submit_button("Save Use Case")
            
            if submitted:
                if not use_case_name.strip() or not use_case_desc.strip():
                    st.warning("Please provide both a use case name and description.")
                else:
                    slug = _slugify(use_case_name)
                    uc_dir = os.path.join("../workspace", slug)
                    os.makedirs(uc_dir, exist_ok=True)
                    md_path = os.path.join(uc_dir, "usecase.md")
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(f"# {use_case_name}\n\n{use_case_desc}\n")

                    # Mirror clone flow for use cases: set as selected and index
                    st.session_state.selected_usecase = slug
                    try:
                        entries = [d for d in os.listdir("../workspace") if os.path.isfile(os.path.join("../workspace", d, "usecase.md"))]
                        if slug in entries:
                            st.session_state.selected_usecase_index = entries.index(slug)
                    except Exception:
                        pass

                    # Store success message in session state
                    st.session_state.use_case_saved_message = f"Use case '{use_case_name}' saved successfully"
                    st.rerun()

    # --- 2. List Use Cases and Run Commands ---
    st.header("Select the Use Case")

    workspace_path = "../workspace"
    if os.path.exists(workspace_path) and os.path.isdir(workspace_path):
        saved_use_cases = [d for d in os.listdir(workspace_path) if os.path.isdir(os.path.join(workspace_path, d))]

        if not saved_use_cases:
            st.info("No saved use cases found in the workspace directory.")
        else:
            def on_usecase_change():
                st.session_state.selected_usecase = st.session_state.usecase_selector
                saved_use_cases = [d for d in os.listdir("../workspace") if os.path.isdir(os.path.join("../workspace", d))]
                if st.session_state.usecase_selector in saved_use_cases:
                    st.session_state.selected_usecase_index = saved_use_cases.index(st.session_state.usecase_selector)

            # Use the index from session_state, then reset it
            usecase_index = st.session_state.get('selected_usecase_index', 0)
            st.selectbox(
                "Select a Use Case",
                saved_use_cases,
                index=usecase_index,
                key="usecase_selector",
                on_change=on_usecase_change
            )
            # The script will rerun on change, and the caption will be updated.
            if 'usecase_selector' in st.session_state:
                 st.session_state.selected_usecase = st.session_state.usecase_selector

            # Display use case description after selection
            if st.session_state.get('selected_usecase'):
                st.markdown("---")  # Add a separator
                usecase_md_path = os.path.join("../workspace", st.session_state.get('selected_usecase'), "usecase.md")
                try:
                    with open(usecase_md_path, 'r', encoding='utf-8') as f:
                        usecase_content = f.read()
                    with st.expander("📋 Use Case Description", expanded=True):
                        st.markdown(usecase_content)
                except FileNotFoundError:
                    st.info("Use case description not found.")
                except Exception as e:
                    st.error(f"Error reading use case description: {e}")

    else:
        st.warning("The 'workspace' directory does not exist.")


elif selected_tab == "Product Planning":
    selected_usecase = st.session_state.get('selected_usecase')

    if st.session_state.get('last_generation_status'):
        status_info = st.session_state.last_generation_status
        if status_info['status'] == 'success':
            st.success(status_info['message'])
        elif status_info['status'] == 'error':
            st.error(status_info['message'])
        st.session_state.last_generation_status = None # Clear after displaying

    if selected_usecase:
        usecase_path = os.path.join("../workspace", selected_usecase)

        # --- New: Command Execution Section ---
        st.header("Generate Product Artifacts")
        
        # Load commands from commands.md and replace $USECASE
        command_map = {}
        try:
            with open("commands.md", 'r', encoding='utf-8') as f:
                relative_usecase_path = os.path.join("workspace", selected_usecase) + os.sep
                for line in f:
                    if line.strip():
                        parts = [p.strip() for p in line.strip().split(',', 2)]
                        if len(parts) >= 2:
                            name = parts[0]
                            command_template = parts[1]
                            output_file = parts[2] if len(parts) > 2 else None
                            command = command_template.replace("$USECASE", relative_usecase_path)
                            command_map[name] = (command, output_file)

        except FileNotFoundError:
            command_map["Error"] = ("echo 'commands.md not found'", None)
        
        if not command_map:
            st.warning("No valid commands found in commands.md.")
        else:
            # Hide controls when a command is running
            if not st.session_state.get('command_is_running'):
                selected_command_name = st.selectbox("Select an artifact to generate", list(command_map.keys()))
                run_button = st.button("Generate Product Artifacts")

                # Check if docs server is already running for this usecase
                usecase_port = st.session_state.usecase_ports.get(usecase_path)
                if usecase_port and usecase_port in st.session_state.running_servers and st.session_state.running_servers[usecase_port].poll() is None:
                    st.success("Documentation server is running.")
                    _, col, _ = st.columns([1, 2, 1])
                    with col:
                        st.link_button("View Documentation", url=f"http://localhost:{usecase_port}", use_container_width=True)

                if run_button and selected_command_name:
                    command_to_run, output_file = command_map[selected_command_name]

                    should_run_command = True
                    if output_file:
                        report_file_path = os.path.join(usecase_path, output_file)
                        if os.path.exists(report_file_path):
                            st.info(f"Report '{output_file}' already exists for this use case. Generating new artifact is not required.")
                            should_run_command = False
                    
                    if should_run_command:
                        logging.info(f"Starting generating artifact: {selected_command_name} on use case: {selected_usecase}")

                        # --- Start command execution state ---
                        st.session_state.command_is_running = True
                        st.session_state.command_log = f"$ Go get a coffee while the sentient toasters work their magic\n"
                        st.session_state.command_q = queue.Queue()
                        st.session_state.command_return_code = None
                        st.session_state.selected_command_name_running = selected_command_name
                        st.session_state.usecase_path_running = usecase_path

                        # This logic handles "re-running" the docs server.
                        # It also handles the case where the command *generates* the docs for the first time.
                        if "documentation" in selected_command_name.lower():
                            ra_path = os.path.join(usecase_path, '_ra')
                            if os.path.isdir(ra_path):
                                st.info("Starting/Restarting documentation server...")
                                # Assign a port to the repo if it doesn't have one
                                if usecase_path not in st.session_state.usecase_ports:
                                    st.session_state.usecase_ports[usecase_path] = st.session_state.next_port
                                    st.session_state.next_port += 1
                                usecase_port = st.session_state.usecase_ports[usecase_path]
                                start_docs_server(usecase_path, usecase_port)
                                st.session_state.command_is_running = False # It's not a long-running fg task
                            else:
                                # Run the command to generate the docs first
                                st.info("Documentation not generated yet. Running generation command...")
                                process = subprocess.Popen(
                                    command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, cwd='../', bufsize=1, universal_newlines=True, preexec_fn=os.setsid
                                )
                                st.session_state.current_process = process
                                thread = threading.Thread(target=run_command_in_thread, args=(process, st.session_state.command_q))
                                thread.daemon = True
                                thread.start()
                                st.session_state.command_thread = thread
                        else:
                            process = subprocess.Popen(
                                command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, cwd='../', bufsize=1, universal_newlines=True, preexec_fn=os.setsid
                            )
                            st.session_state.current_process = process
                            thread = threading.Thread(target=run_command_in_thread, args=(process, st.session_state.command_q))
                            thread.daemon = True
                            thread.start()
                            st.session_state.command_thread = thread

        # This block will now handle rendering the logs for a running command
        if st.session_state.get('command_is_running'):
            show_generation_progress()

    else:
        st.info("Please select a use case first.")

elif selected_tab == "Results":
    selected_usecase = st.session_state.get('selected_usecase')
    if selected_usecase:
        usecase_path = os.path.join("../workspace", selected_usecase)
        
        # # --- Display Risk SVG if it exists ---
        # risk_svg_path = os.path.join(usecase_path, 'ra-risk.svg')
        # if os.path.exists(risk_svg_path):
        #     with open(risk_svg_path, "r") as f:
        #         svg_content = f.read()
        #     st.markdown(f"## Risk Graph")
        #     st.markdown(f'<div style="text-align: center;">{svg_content}</div>', unsafe_allow_html=True)

        # --- View Markdown Files ---
        st.header("View Generated Reports")
        
        allowed_md_files = ["ra-fr.md", "ra-nfr.md", "ra-diagrams.md", "ra-sdd.md"]

        report_names = ["Functional Requirements", "Non-Functional Requirements", "Architecture Diagrams", "System Design Document"]

        # Create mapping between report names and filenames
        file_to_report_map = dict(zip(allowed_md_files, report_names))
        report_to_file_map = dict(zip(report_names, allowed_md_files))
        
        md_files = [f for f in os.listdir(usecase_path) if f in allowed_md_files]
        
        if not md_files:
            st.info("No designated markdown files found in the root of this use case.")
        else:
            # Get available report names for files that actually exist
            available_report_names = [file_to_report_map[f] for f in md_files]
            
            selected_report_name = st.selectbox("Select a report to view", available_report_names)
            if selected_report_name:
                # Map the selected report name back to the actual filename
                selected_md_file = report_to_file_map[selected_report_name]
                md_path = os.path.join(usecase_path, selected_md_file)
                try:
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    
                    # Split markdown by mermaid blocks and render accordingly
                    parts = re.split(r"(```mermaid\n.*?\n```)", md_content, flags=re.DOTALL)
                    for part in parts:
                        if part.strip().startswith("```mermaid"):
                            mermaid_code = part.strip().replace("```mermaid", "").replace("```", "")
                            st_mermaid(mermaid_code)
                        else:
                            st.markdown(part, unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"Error reading markdown file: {e}")
    else:
        st.info("Please select a use case first.")