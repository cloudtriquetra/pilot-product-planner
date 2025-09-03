import streamlit as st
import os
import subprocess
import re
from streamlit_mermaid import st_mermaid
import signal
import queue
import threading
import time
import streamlit_shadcn_ui as ui
import logging
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from ado import load_stories_from_json
import json


st.set_page_config(
    page_title="PILOT",  # This is the browser tab title
    page_icon="",  # Empty icon for simplicity
    layout="wide"                  # Optional: 'centered' or 'wide'
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


@st.cache_data(ttl=60)
def get_claude_cli_status():
    """Return (is_runnable, version_text_or_none) for the Claude CLI.
    Tries common version invocations and parses a semantic version if present.
    """
    def _try_cmd(args):
        try:
            completed = subprocess.run(
                args, capture_output=True, text=True, check=False, timeout=3
            )
            if completed.returncode == 0:
                output = (completed.stdout or "") + (completed.stderr or "")
                text = output.strip()
                if text:
                    # Extract a version-like token if present
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

    # Try common flags/commands
    for cmd in (["claude", "--version"], ["claude", "version"], ["claude", "-v"]):
        ok, ver = _try_cmd(cmd)
        if ok:
            return True, ver
    return False, None


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
 
# Claude CLI status indicator
cli_ok, cli_version = get_claude_cli_status()
if cli_ok:
    st.caption(f"🟢 Backend {cli_version if cli_version else ''}")
else:
    st.caption("🔴 Backend CLI not runnable")

# --- Tabs ---
tab_options = ["Create or Update Product Use Case", "Product Planning", "Results", "Azure DevOps"]

# Determine default tab
if st.session_state.get('command_is_running'):
    # Command is running, default to Product Planning tab
    default_tab = "Product Planning"
else:
    default_tab = "Create or Update Product Use Case"

selected_tab = ui.tabs(options=tab_options, default_value=default_tab)

def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", name.strip()).strip("-").lower()
    return slug or f"usecase-{int(time.time())}"

def validate_with_ai(question_key: str, user_input: str, previous_answers: dict) -> tuple[bool, str]:
    """
    Use AI to validate user input based on context and previous answers.
    Returns (is_valid, error_message)
    """
    import re
    
    if not user_input.strip():
        return False, "Please provide an answer before continuing."
    
    # Create context from previous answers
    context_info = "\n".join([f"{key}: {value}" for key, value in previous_answers.items()])
    
    validation_prompts = {
        "use_case_name": f"""
        Validate this use case name: "{user_input}"
        
        Requirements:
        - Should be a clear, descriptive identifier
        - Should not contain special characters except hyphens and underscores
        - Should be between 3-50 characters
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """,
        
        "use_case_desc": f"""
        Validate this use case description: "{user_input}"
        
        Requirements:
        - Should be at least 20 characters
        - Should describe functionality clearly
        - Should provide business context
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """,
        
        "business_criticality": f"""
        Validate this business criticality input: "{user_input}"
        
        Context from previous answers:
        {context_info}
        
        Requirements:
        - Must be a number from 1 to 5
        - Should make sense given the use case description
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """,
        
        "app_exposure": f"""
        Validate this application exposure input: "{user_input}"
        
        Context from previous answers:
        {context_info}
        
        Requirements:
        - Must be either "internet" or "internal"
        - Should make sense given the use case description
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """,
        
        "countries": f"""
        Validate this countries input: "{user_input}"
        
        Context from previous answers:
        {context_info}
        
        Requirements:
        - Should be real country names or "worldwide"
        - Should make sense for the application type
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """,
        
        "platforms": f"""
        Validate this platforms input: "{user_input}"
        
        Context from previous answers:
        {context_info}
        
        Requirements:
        - Should be valid platform names (web, mobile android, mobile ios, desktop, etc.)
        - Should make sense given the use case description
        - If the description already mentions specific platforms, validate consistency
        
        Is this valid? Respond with only "VALID" or "INVALID: reason"
        """
    }
    
    # For now, use enhanced rule-based validation
    # In production, this would call Claude API
    if question_key == "use_case_name":
        if len(user_input.strip()) < 3:
            return False, "Use case name should be at least 3 characters long."
        if len(user_input.strip()) > 50:
            return False, "Use case name should be no more than 50 characters."
        if not re.match(r'^[a-zA-Z0-9._-]+$', user_input.strip()):
            return False, "Use case name should only contain letters, numbers, dots, hyphens, and underscores."
        return True, ""
    
    elif question_key == "use_case_desc":
        # Enhanced LLM-style validation for use case description
        input_text = user_input.strip()
        
        if len(input_text) < 20:
            return False, "Description should be at least 20 characters to provide meaningful context."
        
        # Check for garbage patterns
        garbage_patterns = [
            'asdf', 'qwerty', 'hjkl', 'zxcv', 'poiu', 'mnbv',
            '123456', 'abcdef', 'test test test', 'blah blah',
            'lorem ipsum', 'dummy text', 'sample text',
            'fdsa', 'ghjk', 'yuio', 'vbnm', 'rtyu'
        ]
        
        # Check for repetitive patterns
        words = input_text.lower().split()
        if len(words) > 3:
            # Check for repeated words (more than 50% repetition)
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > len(words) * 0.5:
                return False, "Please provide a meaningful description. Avoid repeating the same words excessively."
        
        # Check for garbage patterns
        if any(pattern in input_text.lower() for pattern in garbage_patterns):
            return False, "Please provide a real, meaningful description of your use case functionality and business purpose."
        
        # Check for minimum number of meaningful words
        meaningful_words = [word for word in words if len(word) > 2 and word.isalpha()]
        if len(meaningful_words) < 5:
            return False, "Please provide a more detailed description with at least 5 meaningful words describing the functionality."
        
        # Check for business/technical context
        business_indicators = [
            'user', 'customer', 'business', 'service', 'application', 'system', 'platform',
            'feature', 'functionality', 'process', 'workflow', 'management', 'data',
            'interface', 'integration', 'automation', 'dashboard', 'analytics', 'report',
            'payment', 'order', 'product', 'inventory', 'account', 'profile', 'login',
            'search', 'browse', 'purchase', 'checkout', 'notification', 'email',
            'mobile', 'web', 'api', 'database', 'cloud', 'security', 'authentication'
        ]
        
        has_business_context = any(indicator in input_text.lower() for indicator in business_indicators)
        if not has_business_context:
            return False, "Please describe the business functionality or technical purpose of your use case (e.g., user management, payment processing, data analytics, etc.)."
        
        return True, ""
    
    elif question_key == "business_criticality":
        if user_input.strip() not in ['1', '2', '3', '4', '5']:
            return False, "Please enter a valid criticality level (1, 2, 3, 4, or 5)."
        return True, ""
    
    elif question_key == "app_exposure":
        if user_input.strip().lower() not in ['internet', 'internal']:
            return False, "Please enter either 'internet' for public-facing or 'internal' for internal-only applications."
        return True, ""
    
    elif question_key == "countries":
        # Enhanced LLM-style validation for countries
        input_text = user_input.strip()
        
        if len(input_text) < 2:
            return False, "Please provide at least one country name."
        
        # Handle worldwide option
        if input_text.lower() == "worldwide":
            return True, ""
        
        # Comprehensive list of valid countries and variations
        valid_countries = {
            'united states', 'usa', 'us', 'america', 'united kingdom', 'uk', 'britain', 'england',
            'canada', 'australia', 'germany', 'france', 'italy', 'spain', 'japan', 'china',
            'india', 'brazil', 'mexico', 'russia', 'south korea', 'netherlands', 'sweden',
            'norway', 'denmark', 'finland', 'switzerland', 'austria', 'belgium', 'portugal',
            'ireland', 'new zealand', 'singapore', 'hong kong', 'taiwan', 'thailand', 'vietnam',
            'philippines', 'indonesia', 'malaysia', 'south africa', 'egypt', 'nigeria',
            'morocco', 'kenya', 'ghana', 'argentina', 'chile', 'colombia', 'peru', 'venezuela',
            'ecuador', 'uruguay', 'bolivia', 'paraguay', 'poland', 'czech republic', 'hungary',
            'romania', 'bulgaria', 'croatia', 'slovenia', 'slovakia', 'estonia', 'latvia',
            'lithuania', 'greece', 'turkey', 'israel', 'saudi arabia', 'uae', 'qatar', 'kuwait',
            'bahrain', 'oman', 'jordan', 'lebanon', 'cyprus', 'malta', 'iceland', 'luxembourg',
            'liechtenstein', 'monaco', 'andorra', 'san marino', 'vatican', 'bangladesh',
            'pakistan', 'sri lanka', 'nepal', 'bhutan', 'maldives', 'myanmar', 'laos',
            'cambodia', 'brunei', 'mongolia', 'kazakhstan', 'uzbekistan', 'kyrgyzstan',
            'tajikistan', 'turkmenistan', 'afghanistan', 'iran', 'iraq', 'syria', 'yemen',
            'armenia', 'azerbaijan', 'georgia', 'moldova', 'belarus', 'ukraine', 'serbia',
            'montenegro', 'bosnia', 'herzegovina', 'kosovo', 'macedonia', 'albania', 'tunisia',
            'algeria', 'libya', 'sudan', 'ethiopia', 'somalia', 'djibouti', 'eritrea',
            'madagascar', 'mauritius', 'seychelles', 'comoros', 'zimbabwe', 'zambia', 'malawi',
            'mozambique', 'botswana', 'namibia', 'lesotho', 'swaziland', 'angola', 'democratic republic congo',
            'republic congo', 'cameroon', 'chad', 'central african republic', 'gabon', 'equatorial guinea',
            'benin', 'togo', 'burkina faso', 'mali', 'niger', 'mauritania', 'senegal', 'gambia',
            'guinea bissau', 'guinea', 'sierra leone', 'liberia', 'ivory coast', 'costa rica',
            'panama', 'nicaragua', 'honduras', 'guatemala', 'belize', 'el salvador', 'cuba',
            'jamaica', 'haiti', 'dominican republic', 'puerto rico', 'trinidad', 'tobago',
            'barbados', 'grenada', 'saint lucia', 'saint vincent', 'grenadines', 'antigua',
            'barbuda', 'dominica', 'saint kitts', 'nevis', 'bahamas', 'fiji', 'papua new guinea',
            'solomon islands', 'vanuatu', 'samoa', 'tonga', 'palau', 'micronesia', 'marshall islands',
            'kiribati', 'tuvalu', 'nauru'
        }
        
        # Extended garbage patterns for countries
        garbage_patterns = [
            'asdf', 'qwerty', 'hjkl', 'zxcv', 'poiu', 'mnbv', 'fdsa', 'ghjk', 'yuio', 'vbnm',
            '123', '456', '789', 'abc', 'def', 'xyz', 'test', 'sample', 'example',
            'garbage', 'random', 'dummy', 'fake', 'xxx', 'yyy', 'zzz', 'aaa', 'bbb',
            'qwe', 'rty', 'uio', 'sdf', 'ghj', 'kl', 'xcv', 'bnm', 'wer', 'ert',
            'tyu', 'iop', 'dfg', 'fgh', 'hjk', 'jkl', 'cvb', 'vbn', 'bnm'
        ]
        
        # Check for garbage patterns
        if any(pattern in input_text.lower() for pattern in garbage_patterns):
            return False, "Please provide real country names (e.g., United States, Canada, Germany, Japan, etc.)."
        
        # Parse countries (split by comma, semicolon, or 'and')
        import re
        country_list = re.split(r'[,;]|\sand\s', input_text.lower())
        country_list = [country.strip() for country in country_list if country.strip()]
        
        if not country_list:
            return False, "Please provide at least one valid country name."
        
        # Validate each country
        invalid_countries = []
        for country in country_list:
            # Remove common prefixes/suffixes
            cleaned_country = country.replace('the ', '').replace(' republic', '').replace(' federation', '')
            
            # Check if it's a valid country or close match
            is_valid = False
            
            # Direct match
            if cleaned_country in valid_countries:
                is_valid = True
            
            # Partial match for longer country names
            if not is_valid:
                for valid_country in valid_countries:
                    if (len(cleaned_country) > 4 and cleaned_country in valid_country) or \
                       (len(valid_country) > 4 and valid_country in cleaned_country):
                        is_valid = True
                        break
            
            # Check for obvious non-country patterns
            if not is_valid:
                # Too short and not a known abbreviation
                if len(cleaned_country) < 3 and cleaned_country not in ['us', 'uk']:
                    invalid_countries.append(country)
                # Contains numbers
                elif any(char.isdigit() for char in cleaned_country):
                    invalid_countries.append(country)
                # Too many repeated characters
                elif len(set(cleaned_country.replace(' ', ''))) < 3:
                    invalid_countries.append(country)
                # Common non-country words
                elif cleaned_country in ['city', 'state', 'province', 'region', 'continent', 'world', 'earth', 'planet']:
                    invalid_countries.append(country)
                else:
                    # If it looks like it could be a country name (alphabetic, reasonable length)
                    if cleaned_country.replace(' ', '').isalpha() and 3 <= len(cleaned_country) <= 30:
                        is_valid = True
                    else:
                        invalid_countries.append(country)
        
        if invalid_countries:
            return False, f"Please provide valid country names. These don't appear to be countries: {', '.join(invalid_countries)}. Use real country names like 'United States, Canada, Germany'."
        
        if len(country_list) > 10:
            return False, "Please limit to maximum 10 countries for practical implementation scope."
        
        return True, ""
    
    elif question_key == "platforms":
        # Enhanced validation for platforms with context awareness
        input_lower = user_input.strip().lower()
        
        # Check if it contains obvious garbage
        garbage_indicators = ['asdf', 'qwerty', '123', 'test', 'garbage', 'random', 'xxx']
        if any(indicator in input_lower for indicator in garbage_indicators):
            return False, "Please provide real platform names (e.g., 'web', 'mobile android', 'mobile ios', 'desktop windows')."
        
        # Check if it contains valid platform keywords
        valid_platforms = ['web', 'mobile', 'android', 'ios', 'desktop', 'windows', 'mac', 'linux', 'wearable', 'watch', 'tablet', 'api']
        if not any(platform in input_lower for platform in valid_platforms):
            return False, "Please specify valid platforms such as 'web', 'mobile android', 'mobile ios', 'desktop windows', etc."
        
        # Context-aware validation: check if platforms align with description
        if 'use_case_desc' in previous_answers:
            desc_lower = previous_answers['use_case_desc'].lower()
            
            # If description mentions mobile but platforms don't include mobile
            if any(word in desc_lower for word in ['mobile', 'phone', 'smartphone', 'app store']) and 'mobile' not in input_lower:
                return False, "Your description mentions mobile functionality. Please include mobile platforms (e.g., 'mobile android', 'mobile ios') or clarify if this is web-only."
            
            # If description mentions web but platforms don't include web
            if any(word in desc_lower for word in ['website', 'browser', 'web app', 'online']) and 'web' not in input_lower:
                return False, "Your description mentions web functionality. Please include 'web' platform or clarify the target platforms."
        
        return True, ""
    
    return True, ""

def generate_ai_summary(chat_data: dict) -> str:
    """
    Generate an AI-powered comprehensive summary of the use case.
    In production, this would call Claude API. For now, we'll create a structured summary.
    """
    
    # Extract data
    name = chat_data.get('use_case_name', '')
    description = chat_data.get('use_case_desc', '')
    criticality = chat_data.get('business_criticality', '')
    exposure = chat_data.get('app_exposure', '')
    countries = chat_data.get('countries', '')
    platforms = chat_data.get('platforms', '')
    
    # Map criticality to description
    criticality_map = {
        '1': 'Low Impact (Nice to have, minimal business disruption)',
        '2': 'Medium-Low Impact (Some business impact, can wait for fixes)',
        '3': 'Medium Impact (Moderate business impact, affects daily operations)',
        '4': 'High Impact (Significant business impact, affects revenue/customers)', 
        '5': 'Critical Impact (Mission-critical, severe business/revenue impact)'
    }
    
    criticality_desc = criticality_map.get(criticality, f'Level {criticality}')
    
    # Format countries
    countries_formatted = "Worldwide" if countries.lower().strip() == 'worldwide' else countries
    
    # Generate comprehensive summary
    summary = f"""
## 📋 Use Case Summary

**{name}** is a {exposure.lower()}-facing application with **{criticality_desc.lower()}**.

### 🎯 Purpose & Functionality
{description}

### 🌍 Geographic Scope
This application will serve: **{countries_formatted}**

### 💻 Target Platforms
**{platforms}**

### ⚡ Business Impact
- **Criticality Level**: {criticality}/5 ({criticality_desc})
- **Exposure**: {exposure.title()}-facing application
- **Compliance Scope**: {countries_formatted} regulations will apply

### 🔍 Key Considerations
{"- **Internet-facing**: Enhanced security measures and public compliance requirements needed" if exposure.lower() == 'internet' else "- **Internal application**: Focus on internal security and data governance"}
- **Multi-platform deployment**: Requires consistent experience across {platforms.lower()}
{"- **Global compliance**: Must meet international regulations and data protection laws" if countries.lower().strip() == 'worldwide' else f"- **Regional compliance**: Must comply with {countries_formatted} specific regulations"}
"""
    
    return summary.strip()

def get_dynamic_question(question_key: str, previous_answers: dict) -> str:
    """
    Generate dynamic questions based on previous answers using AI context.
    """
    base_questions = {
        "use_case_name": "Hello! Let's create a new use case together. What would you like to name your use case?",
        "use_case_desc": "Great! Now, can you describe what this use case does? What are its main functionalities?",
        "business_criticality": "How business-critical is this application? Please enter a number from 1 to 5:\n\n1 = Low Impact (Nice to have, minimal business disruption if down)\n2 = Medium-Low Impact (Some business impact, can wait for fixes)\n3 = Medium Impact (Moderate business impact, affects daily operations)\n4 = High Impact (Significant business impact, affects revenue/customers)\n5 = Critical Impact (Mission-critical, severe business/revenue impact if down)\n\nPlease enter your choice (1-5):",
        "app_exposure": "Is this an internet-facing application or internal-only? Please type 'internet' for public-facing or 'internal' for internal-only:",
        "countries": "Which countries will this application serve? You can enter comma-separated country names or type 'worldwide' for global coverage:",
        "platforms": "What platforms will your application target? Please describe the platforms (e.g., web, mobile android, mobile ios, desktop windows, wearable android watch, wearable apple watch, etc.):"
    }
    
    # Context-aware question modifications
    if question_key == "platforms" and 'use_case_desc' in previous_answers:
        desc = previous_answers['use_case_desc'].lower()
        
        if 'mobile' in desc or 'app' in desc:
            return "I noticed your description mentions mobile functionality. What specific platforms will your application target? (e.g., mobile android, mobile ios, web, etc.)"
        elif 'web' in desc or 'website' in desc or 'browser' in desc:
            return "I see this is web-related. What platforms will your application target? (e.g., web, desktop, mobile web, etc.)"
        elif 'desktop' in desc:
            return "I noticed this involves desktop functionality. What platforms will your application target? (e.g., desktop windows, desktop mac, web, etc.)"
    
    return base_questions.get(question_key, "Please provide your answer:")

if selected_tab == "Create or Update Product Use Case":
    st.header("Create or Update a Product Use Case")
    st.markdown("Use this section to create new product use cases or update existing ones. Once created, you can select and work with them in the **Product Planning** tab.")
    
    # Show any saved use case message
    if st.session_state.get('use_case_saved_message'):
        st.success(st.session_state.use_case_saved_message)
        st.session_state.use_case_saved_message = None  # Clear after showing
    
    # Check if we just created a use case - if so, don't show creation methods
    if 'simple_form_success' in st.session_state and st.session_state.simple_form_success:
        st.info("To create another use case, refresh the page or click below.")
        if st.button("Create Another Use Case", type="primary"):
            del st.session_state.simple_form_success
            st.rerun()
    else:
        # Choose creation method
        st.subheader("Choose Your Creation Method")
        creation_method = st.radio(
            "How would you like to create your use case?",
            options=["Simple Form (Name & Description)", "Interactive Chat (Detailed)"],
            index=None,
            horizontal=True,
            help="Simple form for quick creation, Interactive chat for comprehensive details"
        )
        
        st.markdown("---")
        
        if creation_method is None:
            st.info("Please select a creation method above to get started.")
        elif creation_method == "Simple Form (Name & Description)":
            st.subheader("Simple Use Case Creation")
            
            with st.form("simple_use_case_form"):
                use_case_name = st.text_input(
                    "Use case name (identifier)",
                    placeholder="e.g., checkout-service or product-search",
                    help="This will be used as the identifier for your use case"
                )
                
                use_case_desc = st.text_area(
                    "Describe your product use case:",
                    placeholder="Enter a paragraph describing your product or feature...",
                    height=200,
                    help="Provide a comprehensive description of the functionality and business value"
                )
                
                submitted = st.form_submit_button("Create Use Case", type="primary", use_container_width=True)
                
                if submitted:
                    if not use_case_name.strip() or not use_case_desc.strip():
                        st.error("Please provide both a use case name and description.")
                    else:
                        slug = _slugify(use_case_name)
                        uc_dir = os.path.join("../workspace", slug)
                        os.makedirs(uc_dir, exist_ok=True)
                        md_path = os.path.join(uc_dir, "usecase.md")
                        
                        simple_content = f"""# {use_case_name}

## Description
{use_case_desc}
"""
                        
                        with open(md_path, 'w', encoding='utf-8') as f:
                            f.write(simple_content)

                        # Set as selected use case
                        st.session_state.selected_usecase = slug
                        try:
                            entries = [d for d in os.listdir("../workspace") if os.path.isfile(os.path.join("../workspace", d, "usecase.md"))]
                            if slug in entries:
                                st.session_state.selected_usecase_index = entries.index(slug)
                        except Exception:
                            pass

                        # Set success flag and success message
                        st.session_state.simple_form_success = True
                        st.session_state.use_case_saved_message = f"Use case '{use_case_name}' created successfully! Go to the Product Planning tab to work with it."
                        st.rerun()
        
        elif creation_method == "Interactive Chat (Detailed)":
            st.subheader("Interactive Chat Creation")
            
            # Initialize chat state for use case creation
            if 'chat_step' not in st.session_state:
                st.session_state.chat_step = 0
            if 'chat_data' not in st.session_state:
                st.session_state.chat_data = {}
            if 'chat_messages' not in st.session_state:
                st.session_state.chat_messages = []

            # Chat container
            chat_container = st.container()
            
            # Define the conversation flow with AI-enhanced validation
            chat_steps = [
                {
                    "key": "use_case_name",
                    "type": "text",
                    "placeholder": "e.g., checkout-service or product-search"
                },
                {
                    "key": "use_case_desc",
                    "type": "textarea",
                    "placeholder": "Describe the functionality, features, and business purpose..."
                },
                {
                    "key": "business_criticality",
                    "type": "text",
                    "placeholder": "Enter 1, 2, 3, 4, or 5"
                },
                {
                    "key": "app_exposure",
                    "type": "text",
                    "placeholder": "internet or internal"
                },
                {
                    "key": "countries",
                    "type": "text",
                    "placeholder": "e.g., United States, Canada, Germany or worldwide"
                },
                {
                    "key": "platforms",
                    "type": "text",
                    "placeholder": "e.g., web, mobile android, mobile ios, desktop windows"
                }
            ]
            
            # Display chat messages
            with chat_container:
                # Show previous messages
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])
                
                # Current question
                if st.session_state.chat_step < len(chat_steps):
                    current_step = chat_steps[st.session_state.chat_step]
                    
                    # Get dynamic question based on context
                    dynamic_question = get_dynamic_question(current_step["key"], st.session_state.chat_data)
                    
                    # Show the question
                    with st.chat_message("assistant"):
                        st.write(dynamic_question)
                    
                    # Get user input based on type
                    user_input = None
                    
                    if current_step["type"] == "text":
                        user_input = st.text_input(
                            "Your answer:",
                            placeholder=current_step.get("placeholder", ""),
                            key=f"chat_input_{st.session_state.chat_step}"
                        )
                    elif current_step["type"] == "textarea":
                        user_input = st.text_area(
                            "Your answer:",
                            placeholder=current_step.get("placeholder", ""),
                            height=100,
                            key=f"chat_input_{st.session_state.chat_step}"
                        )
                    
                    # Continue button
                    col1, col2, col3 = st.columns([1, 1, 1])
                    with col2:
                        if st.button("Continue", key=f"continue_{st.session_state.chat_step}", use_container_width=True):
                            # Use AI-based validation
                            is_valid, error_message = validate_with_ai(current_step["key"], user_input, st.session_state.chat_data)
                            
                            if is_valid:
                                # Store the answer
                                st.session_state.chat_data[current_step["key"]] = user_input
                                
                                # Add to chat history
                                st.session_state.chat_messages.append({
                                    "role": "assistant",
                                    "content": dynamic_question
                                })
                                
                                # Format user response for display
                                response_text = str(user_input)
                                
                                st.session_state.chat_messages.append({
                                    "role": "user", 
                                    "content": response_text
                                })
                                
                                # Move to next step
                                st.session_state.chat_step += 1
                                st.rerun()
                            else:
                                # Show AI-generated error message
                                st.error(error_message)
                
                else:
                    # All questions answered - show summary and create use case
                    # Double-check that we have all required data
                    required_keys = ['use_case_name', 'use_case_desc', 'business_criticality', 'app_exposure', 'countries', 'platforms']
                    has_all_data = all(key in st.session_state.chat_data and st.session_state.chat_data[key].strip() for key in required_keys)
                    
                    if has_all_data:
                        with st.chat_message("assistant"):
                            st.write("Excellent! I've gathered all the information. Let me summarize your use case:")
                            
                            # Generate and show AI-powered summary
                            ai_summary = generate_ai_summary(st.session_state.chat_data)
                            st.markdown(ai_summary)
                            
                            st.markdown("---")
                            st.write("**Please review the summary above. What would you like to do?**")
                        
                        # Enhanced decision options
                        st.markdown("### 🎯 Next Steps")
                        
                        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                        
                        with col1:
                            if st.button("✅ Create Use Case", type="primary", use_container_width=True):
                                # Create the use case (existing logic)
                                use_case_name = st.session_state.chat_data['use_case_name']
                                use_case_desc = st.session_state.chat_data['use_case_desc']
                                business_criticality = int(st.session_state.chat_data['business_criticality'])
                                app_exposure = st.session_state.chat_data['app_exposure'].lower()
                                countries_text = st.session_state.chat_data['countries']
                                platforms_text = st.session_state.chat_data['platforms']
                                
                                # Parse countries
                                if countries_text.lower().strip() == 'worldwide':
                                    countries_display = "Worldwide"
                                else:
                                    # Split by comma and clean up
                                    countries_list = [c.strip() for c in countries_text.split(',') if c.strip()]
                                    countries_display = ', '.join(countries_list)
                                
                                # Parse platforms
                                platforms_list = [p.strip() for p in platforms_text.split(',') if p.strip()]
                                platforms_display = '\n'.join([f"- {platform}" for platform in platforms_list])
                                
                                slug = _slugify(use_case_name)
                                uc_dir = os.path.join("../workspace", slug)
                                os.makedirs(uc_dir, exist_ok=True)
                                md_path = os.path.join(uc_dir, "usecase.md")
                                
                                use_case_content = f"""# {use_case_name}

## Description
{use_case_desc}

## Business Criticality
Level: **{business_criticality}**

## Application Exposure
**Type:** {app_exposure.title()}-facing

## Geographic Coverage
**Countries to serve:** {countries_display}

## Target Platforms
{platforms_display}

## Compliance Considerations
Based on the selected countries and exposure type, compliance requirements will be analyzed during the planning phase.

*Note: {app_exposure.title()}-facing applications may have additional security and compliance requirements.*
"""
                                
                                with open(md_path, 'w', encoding='utf-8') as f:
                                    f.write(use_case_content)

                                # Set as selected use case
                                st.session_state.selected_usecase = slug
                                try:
                                    entries = [d for d in os.listdir("../workspace") if os.path.isfile(os.path.join("../workspace", d, "usecase.md"))]
                                    if slug in entries:
                                        st.session_state.selected_usecase_index = entries.index(slug)
                                except Exception:
                                    pass

                                # Reset chat
                                st.session_state.chat_step = 0
                                st.session_state.chat_data = {}
                                st.session_state.chat_messages = []
                                
                                # Success message
                                st.session_state.use_case_saved_message = f"Use case '{use_case_name}' created successfully! Go to the Product Planning tab to work with it."
                                st.rerun()
                        
                        with col2:
                            if st.button("✏️ Edit Details", use_container_width=True):
                                # Show edit options
                                st.session_state.show_edit_options = True
                                st.rerun()
                                
                        with col3:
                            if st.button("🔄 Start Over", use_container_width=True):
                                st.session_state.chat_step = 0
                                st.session_state.chat_data = {}
                                st.session_state.chat_messages = []
                                st.rerun()
                                
                        with col4:
                            if st.button("📝 Add More Info", use_container_width=True):
                                st.info("Additional details can be added after creation in the Product Planning tab.")
                        
                        # Show edit options if requested
                        if st.session_state.get('show_edit_options', False):
                            st.markdown("### ✏️ What would you like to edit?")
                            
                            edit_col1, edit_col2, edit_col3 = st.columns(3)
                            
                            with edit_col1:
                                if st.button("📝 Name & Description", use_container_width=True):
                                    st.session_state.chat_step = 0
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                                    
                                if st.button("🌍 Countries", use_container_width=True):
                                    st.session_state.chat_step = 4
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                            
                            with edit_col2:
                                if st.button("⚡ Criticality Level", use_container_width=True):
                                    st.session_state.chat_step = 2
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                                    
                                if st.button("💻 Platforms", use_container_width=True):
                                    st.session_state.chat_step = 5
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                            
                            with edit_col3:
                                if st.button("🔒 Exposure Type", use_container_width=True):
                                    st.session_state.chat_step = 3
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                                    
                                if st.button("❌ Cancel Edit", use_container_width=True):
                                    st.session_state.show_edit_options = False
                                    st.rerun()
                    else:
                        # Missing data - this should not happen, but safety check
                        st.error("Missing required information. Please restart the chat.")
    
    # Show existing use cases
    st.markdown("---")
    st.subheader("Update Existing Use Cases")
    workspace_path = "../workspace"
    if os.path.exists(workspace_path) and os.path.isdir(workspace_path):
        saved_use_cases = [d for d in os.listdir(workspace_path) if os.path.isdir(os.path.join(workspace_path, d))]
        
        if not saved_use_cases:
            st.info("No saved use cases found. Create your first use case above!")
        else:
            # Initialize the session state for edit selection if not exists
            if 'edit_usecase_selection' not in st.session_state:
                st.session_state.edit_usecase_selection = "Select a use case to edit..."
            
            # Create a dropdown to select a use case to edit
            usecase_options = ["Select a use case to edit..."] + saved_use_cases
            
            def on_edit_selection_change():
                st.session_state.edit_usecase_selection = st.session_state.edit_usecase_selector
            
            selected_usecase_to_edit = st.selectbox(
                "Choose a use case to edit:",
                usecase_options,
                index=usecase_options.index(st.session_state.edit_usecase_selection) if st.session_state.edit_usecase_selection in usecase_options else 0,
                key="edit_usecase_selector",
                on_change=on_edit_selection_change
            )
            
            if selected_usecase_to_edit and selected_usecase_to_edit != "Select a use case to edit...":
                usecase_md_path = os.path.join(workspace_path, selected_usecase_to_edit, "usecase.md")
                
                if os.path.exists(usecase_md_path):
                    try:
                        with open(usecase_md_path, 'r', encoding='utf-8') as f:
                            usecase_content = f.read()
                        
                        # Extract current name and description
                        lines = usecase_content.split('\n')
                        current_name = lines[0].replace('# ', '') if lines else selected_usecase_to_edit
                        current_description = '\n'.join(lines[2:]) if len(lines) > 2 else ""
                        
                        st.markdown(f"### Editing: {current_name}")
                        
                        with st.form(f"edit_usecase_form_{selected_usecase_to_edit}"):
                            updated_name = st.text_input(
                                "Use case name", 
                                value=current_name,
                                key=f"edit_name_{selected_usecase_to_edit}"
                            )
                            updated_description = st.text_area(
                                "Description", 
                                value=current_description, 
                                height=200,
                                key=f"edit_desc_{selected_usecase_to_edit}"
                            )
                            
                            col_save, col_cancel = st.columns(2)
                            with col_save:
                                save_btn = st.form_submit_button("💾 Update Use Case", type="primary")
                            with col_cancel:
                                cancel_btn = st.form_submit_button("❌ Cancel")
                            
                            if save_btn:
                                if updated_name.strip() and updated_description.strip():
                                    # Save the updated content
                                    with open(usecase_md_path, 'w', encoding='utf-8') as f:
                                        f.write(f"# {updated_name}\n\n{updated_description}\n")
                                    st.session_state.use_case_saved_message = f"Use case '{updated_name}' updated successfully!"
                                    # Reset the selection to default
                                    st.session_state.edit_usecase_selection = "Select a use case to edit..."
                                    st.rerun()
                                else:
                                    st.warning("Please provide both name and description.")
                            
                            if cancel_btn:
                                # Reset the selection to default
                                st.session_state.edit_usecase_selection = "Select a use case to edit..."
                                st.rerun()
                                
                    except FileNotFoundError:
                        st.error("Use case description file not found.")
                    except Exception as e:
                        st.error(f"Error reading use case description: {e}")
                else:
                    st.warning(f"Description file not found for use case '{selected_usecase_to_edit}'")
            
            # Show list of all use cases for reference
            st.markdown("#### All Use Cases:")
            for usecase in saved_use_cases:
                usecase_md_path = os.path.join(workspace_path, usecase, "usecase.md")
                if os.path.exists(usecase_md_path):
                    try:
                        with open(usecase_md_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        title = content.split('\n')[0].replace('# ', '') if content else usecase
                        st.markdown(f"• **{title}** (`{usecase}`)")
                    except Exception:
                        st.markdown(f"• `{usecase}`")
                else:
                    st.markdown(f"• `{usecase}` (no description file)")
    else:
        st.warning("The 'workspace' directory does not exist.")

elif selected_tab == "Product Planning":
    selected_usecase = st.session_state.get('selected_usecase')

    # Show any saved use case message
    if st.session_state.get('use_case_saved_message'):
        st.success(st.session_state.use_case_saved_message)
        st.session_state.use_case_saved_message = None  # Clear after showing

    if st.session_state.get('last_generation_status'):
        status_info = st.session_state.last_generation_status
        if status_info['status'] == 'success':
            st.success(status_info['message'])
        elif status_info['status'] == 'error':
            st.error(status_info['message'])
        st.session_state.last_generation_status = None # Clear after displaying

    # --- Use Case Selection Section ---
    st.header("Select the Use Case")

    workspace_path = "../workspace"
    if os.path.exists(workspace_path) and os.path.isdir(workspace_path):
        saved_use_cases = [d for d in os.listdir(workspace_path) if os.path.isdir(os.path.join(workspace_path, d))]

        if not saved_use_cases:
            st.info("No saved use cases found in the workspace directory.")
            st.markdown("👉 **Create a new use case** in the **Product Use Case** tab to get started.")
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
                    
                    # Check if we're in edit mode for this use case
                    edit_key = f"edit_mode_{st.session_state.get('selected_usecase')}"
                    
                    with st.expander("📋 Use Case Description", expanded=True):
                        col1, col2 = st.columns([4, 1])
                        
                        with col2:
                            if not st.session_state.get(edit_key, False):
                                if st.button("✏️ Edit", key=f"edit_btn_{st.session_state.get('selected_usecase')}", use_container_width=True):
                                    st.session_state[edit_key] = True
                                    st.rerun()
                        
                        with col1:
                            if st.session_state.get(edit_key, False):
                                # Extract current name and description
                                lines = usecase_content.split('\n')
                                current_name = lines[0].replace('# ', '') if lines else st.session_state.get('selected_usecase')
                                current_description = '\n'.join(lines[2:]) if len(lines) > 2 else ""
                                
                                with st.form(f"edit_usecase_form_{st.session_state.get('selected_usecase')}"):
                                    updated_name = st.text_input("Use case name", value=current_name)
                                    updated_description = st.text_area("Description", value=current_description, height=150)
                                    
                                    col_save, col_cancel = st.columns(2)
                                    with col_save:
                                        save_btn = st.form_submit_button("💾 Save", type="primary")
                                    with col_cancel:
                                        cancel_btn = st.form_submit_button("❌ Cancel")
                                    
                                    if save_btn:
                                        if updated_name.strip() and updated_description.strip():
                                            # Save the updated content
                                            with open(usecase_md_path, 'w', encoding='utf-8') as f:
                                                f.write(f"# {updated_name}\n\n{updated_description}\n")
                                            st.session_state[edit_key] = False
                                            st.session_state.use_case_saved_message = "Use case updated successfully!"
                                            st.rerun()
                                        else:
                                            st.warning("Please provide both name and description.")
                                    
                                    if cancel_btn:
                                        st.session_state[edit_key] = False
                                        st.rerun()
                            else:
                                st.markdown(usecase_content)
                                
                except FileNotFoundError:
                    st.info("Use case description not found.")
                except Exception as e:
                    st.error(f"Error reading use case description: {e}")

    else:
        st.warning("The 'workspace' directory does not exist.")

    # --- Generate Product Artifacts Section ---
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

                # Check for "Generate New Version" button click (independent of run_button)
                generate_new_version = False
                if selected_command_name:
                    command_to_run, output_file = command_map[selected_command_name]
                    if output_file:
                        report_file_path = os.path.join(usecase_path, output_file)
                        if os.path.exists(report_file_path):
                            if st.button("🔄 Generate New Version", type="primary", key=f"regenerate_{selected_command_name}"):
                                generate_new_version = True

                # Handle both regular generation and new version generation
                if (run_button and selected_command_name) or generate_new_version:
                    command_to_run, output_file = command_map[selected_command_name]

                    should_run_command = True
                    if output_file:
                        report_file_path = os.path.join(usecase_path, output_file)
                        if os.path.exists(report_file_path):
                            if not generate_new_version:
                                # Show warning only for regular generate button
                                st.warning(f"⚠️ Report '{output_file}' already exists for this use case.")
                                st.info("💡 **Tip**: Generating again will create a new version while preserving the existing report. View reports in the **Results** tab.")
                                should_run_command = False
                            else:
                                # Handle versioning for "Generate New Version" button
                                import datetime
                                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                base_name = output_file.replace('.md', '')
                                versioned_name = f"{base_name}_v{timestamp}.md"
                                versioned_path = os.path.join(usecase_path, versioned_name)
                                
                                try:
                                    # Move existing report to versioned name
                                    import shutil
                                    shutil.move(report_file_path, versioned_path)
                                    st.success(f"✅ Existing report backed up as '{versioned_name}'. Generating new version...")
                                    should_run_command = True
                                except Exception as e:
                                    st.error(f"❌ Failed to backup existing report: {e}")
                                    should_run_command = False
                        else:
                            # No existing report, proceed normally
                            should_run_command = True
                    
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

        allowed_md_files = ["ra-fr.md", "ra-nfr.md", "ra-diagrams.md", "ra-sdd.md","ra-security-controls.md"]
        report_names = ["Functional Requirements", "Non-Functional Requirements", "Architecture Diagrams", "System Design Document","Security Controls Assessment"]

        # Create mapping between report names and filenames
        file_to_report_map = dict(zip(allowed_md_files, report_names))
        report_to_file_map = dict(zip(report_names, allowed_md_files))
        
        # Get all markdown files including versioned ones
        all_files = os.listdir(usecase_path)
        current_reports = [f for f in all_files if f in allowed_md_files]
        
        # Find versioned reports
        versioned_reports = {}
        for base_file in allowed_md_files:
            base_name = base_file.replace('.md', '')
            versions = [f for f in all_files if f.startswith(f"{base_name}_v") and f.endswith('.md')]
            if versions:
                # Sort versions by timestamp (newest first)
                versions.sort(reverse=True)
                versioned_reports[base_file] = versions
        
        if not current_reports and not versioned_reports:
            st.info("No designated markdown files found in the root of this use case.")
        else:
            # Create report selection options
            available_report_names = []
            if current_reports:
                available_report_names.extend([file_to_report_map[f] for f in current_reports])
            
            selected_report_name = st.selectbox("Select a report type to view", available_report_names)
            
            if selected_report_name:
                selected_md_file = report_to_file_map[selected_report_name]
                
                # Show version selection if versioned reports exist
                if selected_md_file in versioned_reports:
                    # Initialize session state for version selection
                    version_key = f"version_select_{selected_md_file}_{st.session_state.selected_usecase}"
                    if version_key not in st.session_state:
                        st.session_state[version_key] = "Current Version"
                    
                    # Prominent section header
                    st.markdown("## 📋 Version Selection")
                    
                    version_options = ["Current Version"] + [f"Version {v.split('_v')[1].replace('.md', '')}" for v in versioned_reports[selected_md_file]]
                    
                    selected_version = st.selectbox(
                        "Select version to view",
                        version_options,
                        index=version_options.index(st.session_state[version_key]) if st.session_state[version_key] in version_options else 0,
                        key=f"version_selector_{selected_md_file}"
                    )
                    # Update session state
                    st.session_state[version_key] = selected_version
                    
                    # Show version info
                    if selected_version == "Current Version":
                        st.info(f"📄 Viewing current version: **{selected_md_file}**")
                    else:
                        st.info(f"📄 Viewing archived version: **{selected_version}**")
                    
                    if selected_version != "Current Version":
                        # Extract timestamp and find corresponding file
                        version_timestamp = selected_version.replace("Version ", "")
                        version_file = f"{selected_md_file.replace('.md', '')}_v{version_timestamp}.md"
                        selected_md_file = version_file
                        
                        col_info, col_rollback = st.columns([2, 1])
                        with col_info:
                            timestamp = version_file.split("_v")[1].replace(".md", "")
                            formatted_time = f"{timestamp[:4]}-{timestamp[4:6]}-{timestamp[6:8]} {timestamp[9:11]}:{timestamp[11:13]}:{timestamp[13:15]}"
                            st.info(f"� Generated on: {formatted_time}")
                        with col_rollback:
                            if st.button("🔄 Restore as Current", key=f"rollback_{version_file}", type="primary"):
                                try:
                                    # Get paths
                                    base_file = selected_md_file.split('_v')[0] + '.md'
                                    current_file_path = os.path.join(usecase_path, base_file)
                                    version_file_path = os.path.join(usecase_path, version_file)
                                    
                                    # Create backup of current version before rollback
                                    import datetime
                                    import shutil
                                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                                    backup_name = f"{base_file.replace('.md', '')}_v{timestamp}.md"
                                    backup_path = os.path.join(usecase_path, backup_name)
                                    
                                    # Move current to backup
                                    if os.path.exists(current_file_path):
                                        shutil.move(current_file_path, backup_path)
                                    
                                    # Copy selected version to current
                                    shutil.copy2(version_file_path, current_file_path)
                                    
                                    st.success(f"✅ **Rollback successful!** \n- Current version backed up as `{backup_name}` \n- `{version_file}` is now the current version")
                                    st.info("💡 **Tip**: The current version has been updated. You can now generate new artifacts based on this version.")
                                    
                                    # Reset version selection to current
                                    st.session_state[version_key] = "Current Version"
                                    
                                    # Wait a moment then rerun to refresh the view
                                    import time
                                    time.sleep(1)
                                    st.rerun()
                                    
                                except Exception as e:
                                    st.error(f"❌ Failed to restore version: {e}")
                else:
                    st.info(f"📄 Viewing current version: **{selected_md_file}**")
                
                # Display the selected report
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

elif selected_tab == "Azure DevOps":
    st.header("Create User Stories in Azure DevOps")
    selected_usecase = st.session_state.get('selected_usecase')

    if selected_usecase:
        usecase_path = os.path.join("../workspace", selected_usecase)

        # ADO Configuration in sidebar
        with st.sidebar:
            st.markdown("### 📤 Azure DevOps Settings")

            # Store ADO settings in session state
            if 'ado_settings' not in st.session_state:
                st.session_state.ado_settings = {
                    'organization': 'pandeymohit',
                    'project': 'devsecops',
                    'pat': '',
                    # 'area_path': '',
                    # 'iteration': 'Sprint 1'
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
            # area_path = st.text_input(
            #     "Area Path",
            #     value=st.session_state.ado_settings['area_path']
            # )
            # iteration = st.text_input(
            #     "Iteration",
            #     value=st.session_state.ado_settings['iteration']
            # )

            # Save settings
            st.session_state.ado_settings.update({
                'organization': organization,
                'project': project,
                'pat': pat,
                # 'area_path': area_path,
                # 'iteration': iteration
            })

        # Main content area
        # if organization and project and pat:
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
                            # Update the acceptance criteria section in main.py
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
                    with st.spinner("Uploading stories to Azure DevOps..."):
                        # Initialize ADO connection
                        credentials = BasicAuthentication('', pat)
                        organization_url = f"https://dev.azure.com/{organization}"
                        connection = Connection(base_url=organization_url, creds=credentials)
            
                        # Get clients
                        core_client = connection.clients.get_core_client()
                        wit_client = connection.clients.get_work_item_tracking_client()

                        # Ensure Area Path and Iteration Path exist
                        st.info("Checking and creating classification nodes if needed...")
                        # area_path = f"{project}\\{area_path}"
                        # iteration_path = f"{area_path}\\{iteration}"
                        area_path = project
                        iteration_path = f"{area_path}\\Sprint 1"
                        # if ensure_classification_nodes(st, connection, project, area_path, iteration_path):
                        if True:
                            progress_bar = st.progress(0)   
                            status_text = st.empty()

                            # Start work item creation    
                            for idx, (story_id, story) in enumerate(stories_data.items(), 1):
                                status_text.text(f"Creating story {idx}/{len(stories_data)}...")

                                time.sleep(0.5)  # Simulate network delay
                                
                                # Create work item
                                wit_create = [
                                    {"op": "add", "path": "/fields/System.Title",
                                        "value": f"{story_id}: {story['title']}"},
                                    {"op": "add", "path": "/fields/System.Description",
                                        "value": f"As a {story['as_a']}\nI want to {story['i_want']}\nSo that {story['so_that']}"},
                                    {"op": "add", "path": "/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
                                        "value": "\r\n".join([f"- {ac}" for ac in story['ac_list']])},  # Fixed line breaks and added checkbox format
                                    {"op": "add", "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints",
                                        "value": story['points']},
                                    # {"op": "add", "path": "/fields/System.AreaPath",
                                    # "value": area_path if '\\' in area_path else project},  # Use project as default if no path specified
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
                            st.error("Failed to create required paths in Azure DevOps")

            else:
                st.warning("No stories found in the requirements files.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
        # else:
        #     st.info("Please fill in all Azure DevOps settings in the sidebar to continue.")
    else:
        st.info("Please select a use case first.")
