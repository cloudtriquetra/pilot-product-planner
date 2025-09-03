import streamlit as st
import os
import re
import subprocess
import threading
import queue
import time
from streamlit_mermaid import st_mermaid
from ui import apply_compact_styles


st.set_page_config(
    page_title="Project Dashboard",
    page_icon="",
    layout="wide"
)

apply_compact_styles()

@st.cache_data(ttl=60)
def get_claude_cli_status():
    """Return (is_runnable, version_text_or_none) for the backend CLI (Claude)."""
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


def _read_usecase_title_and_desc(usecase_path: str):
    md_path = os.path.join(usecase_path, "usecase.md")
    try:
        with open(md_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.split("\n")
        title = lines[0].replace("# ", "").strip() if lines else os.path.basename(usecase_path)
        description = "\n".join(lines[2:]).strip() if len(lines) > 2 else ""
        return title, description
    except Exception:
        return os.path.basename(usecase_path), ""


# --- Background command execution utilities ---
def _reader_thread(proc: subprocess.Popen, q: "queue.Queue[str]") -> None:
    try:
        for line in iter(proc.stdout.readline, ''):
            if not line:
                break
            q.put(line)
        if proc.stdout:
            proc.stdout.close()
        rc = proc.wait()
        q.put(f"---RC:{rc}---")
    except Exception:
        q.put("---RC:1---")


def start_background(run_key: str, shell_cmd: str) -> None:
    if 'cmd_runs' not in st.session_state:
        st.session_state.cmd_runs = {}
    # Prevent duplicate run keys
    if run_key in st.session_state.cmd_runs and st.session_state.cmd_runs[run_key].get('process') and st.session_state.cmd_runs[run_key]['process'].poll() is None:
        return
    q: "queue.Queue[str]" = queue.Queue()
    proc = subprocess.Popen(
        shell_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, cwd="../", bufsize=1, universal_newlines=True
    )
    th = threading.Thread(target=_reader_thread, args=(proc, q), daemon=True)
    th.start()
    st.session_state.cmd_runs[run_key] = {
        'process': proc,
        'q': q,
        'log': '',
        'return_code': None,
        'started_at': time.time(),
    }


@st.fragment
def show_run_progress(run_key: str, title: str):
    info = st.session_state.cmd_runs.get(run_key)
    if not info:
        return
    label = f"Running: {title}"
    with st.status(label, expanded=True) as status:
        log_placeholder = st.empty()
        while True:
            q = info.get('q')
            if q:
                while not q.empty():
                    line = q.get_nowait()
                    if line.startswith("---RC:"):
                        try:
                            info['return_code'] = int(line.replace("---RC:", "").replace("---", ""))
                        except Exception:
                            info['return_code'] = 1
                    else:
                        info['log'] += line
            # Update the visible log
            if info.get('log'):
                log_placeholder.code(info['log'][-6000:])

            # Exit when finished
            if info.get('return_code') is not None:
                if info['return_code'] == 0:
                    status.update(label=f"Completed: {title}", state="complete", expanded=False)
                else:
                    status.update(label=f"Failed: {title}", state="error")
                break
            else:
                time.sleep(0.5)


selected_usecase = st.session_state.get("selected_usecase")
if not selected_usecase:
    st.warning("No project selected. Please choose one from the Dashboard.")
    st.page_link("pages/00_Dashboard.py", label="Go to Dashboard", icon="🏠")
    st.stop()

usecase_path = os.path.join("../workspace", selected_usecase)
title, desc = _read_usecase_title_and_desc(usecase_path)

st.title(f"Project Dashboard: {title}")
st.caption(f"`{selected_usecase}`")
if desc:
    with st.expander("📋 Project Description", expanded=False):
        st.write(desc)

cli_ok, cli_version = get_claude_cli_status()
if cli_ok:
    st.caption(f"🟢 Backend {cli_version if cli_version else ''}")
else:
    st.caption("🔴 Backend CLI not runnable")

st.subheader("⚙️ Actions")

# Parse commands from frontend/commands.md
command_map = {}
commands_file = os.path.join(".", "commands.md")
try:
    if os.path.exists(commands_file):
        with open(commands_file, "r", encoding="utf-8") as f:
            relative_usecase_path = os.path.join("workspace", selected_usecase) + os.sep
            for line in f:
                if line.strip():
                    parts = [p.strip() for p in line.strip().split(",", 2)]
                    if len(parts) >= 2:
                        name = parts[0]
                        command_template = parts[1]
                        output_file = parts[2] if len(parts) > 2 else None
                        command = command_template.replace("$USECASE", relative_usecase_path)
                        command_map[name] = (command, output_file)
except Exception as e:
    st.error(f"Failed to load commands: {e}")

if not command_map:
    st.info("No commands found in commands.md")
else:
    st.markdown('<div class="actions-grid">', unsafe_allow_html=True)
    names = list(command_map.keys())
    cols = st.columns(2)
    for idx, name in enumerate(names):
        cmd, output_file = command_map[name]
        with cols[idx % len(cols)]:
            with st.container(border=True):
                    # Header row: title + compact action icons
                    can_newver = False
                    report_file_path = None
                    if output_file:
                        report_file_path = os.path.join(usecase_path, output_file)
                        can_newver = os.path.exists(report_file_path)

                    title_col, gen_col, new_col = st.columns([8, 1, 1])
                    with title_col:
                        st.markdown(f"###### {name}")
                    with gen_col:
                        gen_clicked = st.button("▶", key=f"gen_{idx}_{name}", help="Generate", use_container_width=True)
                    with new_col:
                        new_clicked = st.button("🆕", key=f"newver_{idx}_{name}", help="New Version", use_container_width=True, disabled=not can_newver)

                    # Filename caption removed for a more compact card

                    # Generate (icon-only) button - Non-blocking
                    if gen_clicked:
                        should_run = True
                        if output_file and os.path.exists(report_file_path):
                            st.warning(f"Report '{output_file}' exists. Use New Version.")
                            should_run = False
                        if should_run:
                            run_key = f"run_{idx}_{name}"
                            start_background(run_key, cmd)
                            show_run_progress(run_key, name)

                    # New Version (icon-only) button (only if output exists now) - Non-blocking
                    if new_clicked:
                        import datetime
                        import shutil
                        try:
                            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                            base_name = output_file.replace('.md', '')
                            versioned_name = f"{base_name}_v{timestamp}.md"
                            versioned_path = os.path.join(usecase_path, versioned_name)
                            shutil.move(report_file_path, versioned_path)
                            st.success(f"Backed up as '{versioned_name}'. Generating…")
                            run_key = f"newver_{idx}_{name}"
                            start_background(run_key, cmd)
                            show_run_progress(run_key, name)
                        except Exception as e:
                            st.error(f"Failed to create new version: {e}")
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.subheader("📄 Results")
if not os.path.isdir(usecase_path):
    st.info("Project folder not found.")
else:
    allowed_md_files = ["ra-fr.md", "ra-nfr.md", "ra-diagrams.md", "ra-sdd.md", "ra-security-controls.md"]
    report_names = ["Functional Requirements", "Non-Functional Requirements", "Architecture Diagrams", "System Design Document", "Security Controls Assessment"]
    file_to_report_map = dict(zip(allowed_md_files, report_names))
    report_to_file_map = dict(zip(report_names, allowed_md_files))

    all_files = os.listdir(usecase_path)
    current_reports = [f for f in all_files if f in allowed_md_files]

    versioned_reports = {}
    for base_file in allowed_md_files:
        base_name = base_file.replace('.md', '')
        versions = [f for f in all_files if f.startswith(f"{base_name}_v") and f.endswith('.md')]
        if versions:
            versions.sort(reverse=True)
            versioned_reports[base_file] = versions

    if not current_reports and not versioned_reports:
        st.info("No designated markdown reports found for this project.")
    else:
        available_report_names = []
        if current_reports:
            available_report_names.extend([file_to_report_map[f] for f in current_reports])

        selected_report_name = st.selectbox("Select a report type", available_report_names)
        if selected_report_name:
            selected_md_file = report_to_file_map[selected_report_name]

            if selected_md_file in versioned_reports:
                version_options = ["Current Version"] + [
                    f"Version {v.split('_v')[1].replace('.md', '')}" for v in versioned_reports[selected_md_file]
                ]
                selected_version = st.selectbox("Select version", version_options)
                if selected_version != "Current Version":
                    version_timestamp = selected_version.replace("Version ", "")
                    selected_md_file = f"{selected_md_file.replace('.md', '')}_v{version_timestamp}.md"
                    st.info(f"📄 Viewing archived version: {selected_version}")
                else:
                    st.info(f"📄 Viewing current version: {selected_md_file}")

            md_path = os.path.join(usecase_path, selected_md_file)
            try:
                with open(md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()
                parts = re.split(r"(```mermaid\n.*?\n```)", md_content, flags=re.DOTALL)
                for part in parts:
                    if part.strip().startswith("```mermaid"):
                        mermaid_code = part.strip().replace("```mermaid", "").replace("```", "")
                        st_mermaid(mermaid_code)
                    else:
                        st.markdown(part, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error reading markdown file: {e}")


