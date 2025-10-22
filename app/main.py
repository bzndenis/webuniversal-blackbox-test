"""Streamlit web application for Black-Box Functional Testing."""

import sys
import os

# CRITICAL: Set environment variable BEFORE asyncio import
# This forces asyncio to use the correct event loop from the start
if sys.platform == 'win32':
    # Hormati env yang sudah ada; jika tidak ada, pakai folder lokal .pw-browsers bila tersedia,
    # kalau tidak ada fallback ke default ('0'). Harus dilakukan sebelum import asyncio/Playwright.
    if 'PLAYWRIGHT_BROWSERS_PATH' not in os.environ:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        local_browsers_dir = os.path.join(project_root, '.pw-browsers')
        if os.path.isdir(local_browsers_dir):
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = local_browsers_dir
        else:
            os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'  # default path managed by Playwright
    # No environment variable for event loop, we'll set it programmatically

import asyncio

# CRITICAL FIX: Set event loop policy BEFORE any imports
# Windows uses ProactorEventLoop by default since Python 3.8
# Playwright requires SelectorEventLoop for subprocess management
if sys.platform == 'win32':
    # Use ProactorEventLoop on Windows (supports subprocess required by Playwright)
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Ensure there is a current loop without triggering deprecation warnings
    try:
        # Prefer get_running_loop; avoids DeprecationWarning when no loop exists
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop yet; create one under the current policy (Proactor on Windows)
        asyncio.set_event_loop(asyncio.new_event_loop())

import streamlit as st
from datetime import datetime
from pathlib import Path
import logging
import json

# Configure logging EARLY
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify event loop type on Windows
if sys.platform == 'win32':
    try:
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(current_loop)

        loop_type = type(current_loop).__name__
        policy_type = type(asyncio.get_event_loop_policy()).__name__
        logger.info(f"✓ Event Loop Type: {loop_type}")
        logger.info(f"✓ Event Loop Policy: {policy_type}")

        # Verify it's ProactorEventLoop (required for subprocess on Windows)
        from asyncio import windows_events, selector_events
        if isinstance(current_loop, windows_events.ProactorEventLoop):
            logger.info("✓ Using ProactorEventLoop - Playwright compatible")
        elif isinstance(current_loop, selector_events.SelectorEventLoop):
            logger.error("❌ ERROR: Still using SelectorEventLoop! Subprocess will FAIL on Windows")
        else:
            logger.warning("⚠️ Unexpected event loop type on Windows")
    except Exception as e:
        logger.warning(f"Could not verify event loop: {e}")

# Add app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from app.runners.crawl import crawl_site, crawl_site_with_auth
from app.runners.playwright_runner import run_page_smoke, run_yaml_scenario
from app.services.reporter import generate_all_reports
from app.services.yaml_loader import load_yaml_spec, create_sample_yaml
from app.services.heuristics import test_form_submission
from app.models.db import init_db, create_test_run, update_test_run, create_page_test, get_recent_runs

# Page configuration
st.set_page_config(
    page_title="Black-Box Testing Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

# Configuration file path
CONFIG_FILE = "config.json"

def save_config_to_file():
    """Save current configuration to JSON file."""
    config = {
        "test_mode": st.session_state.get("test_mode", "Single Page"),
        "base_url": st.session_state.get("base_url", "https://example.com"),
        "max_depth": st.session_state.get("max_depth", 2),
        "max_pages": st.session_state.get("max_pages", 10),
        "same_origin": st.session_state.get("same_origin", True),
        "include_pattern": st.session_state.get("include_pattern", ""),
        "exclude_pattern": st.session_state.get("exclude_pattern", ""),
        "headless": st.session_state.get("headless", True),
        "timeout": st.session_state.get("timeout", 10),
        "deep_component_test": st.session_state.get("deep_component_test", True),
        "test_forms": st.session_state.get("test_forms", False),
        "auth_enabled": st.session_state.get("auth_enabled", False),
        "login_url": st.session_state.get("login_url", ""),
        "auth_username": st.session_state.get("auth_username", ""),
        "auth_password": st.session_state.get("auth_password", ""),
        "success_indicator": st.session_state.get("success_indicator", ""),
        "last_saved": datetime.now().isoformat()
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info("Configuration saved to file")
    except Exception as e:
        logger.error(f"Failed to save config: {e}")

def load_config_from_file():
    """Load configuration from JSON file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.info("Configuration loaded from file")
            return config
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
    return None

# Initialize session state for configuration persistence
def init_session_state():
    """Initialize session state with default values or load from file."""
    # Try to load from file first
    saved_config = load_config_from_file()
    
    # Default values
    defaults = {
        'test_mode': "Single Page",
        'base_url': "https://example.com",
        'max_depth': 2,
        'max_pages': 10,
        'same_origin': True,
        'include_pattern': "",
        'exclude_pattern': "",
        'headless': True,
        'timeout': 10,
        'deep_component_test': True,
        'test_forms': False,
        'auth_enabled': False,
        'login_url': "",
        'auth_username': "",
        'auth_password': "",
        'success_indicator': ""
    }
    
    # Initialize session state with saved config or defaults
    for key, default_value in defaults.items():
        if key not in st.session_state:
            if saved_config and key in saved_config:
                st.session_state[key] = saved_config[key]
            else:
                st.session_state[key] = default_value

init_session_state()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 0.25rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.markdown('<h1 class="main-header">🔍 Black-Box Functional Testing</h1>', unsafe_allow_html=True)
st.markdown("**Automated web testing tool** for smoke tests, form validation, and custom YAML scenarios")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Mode selection
    test_mode = st.radio(
        "Test Mode",
        ["Crawler Mode", "YAML Scenario", "Single Page"],
        index=["Crawler Mode", "YAML Scenario", "Single Page"].index(st.session_state.test_mode),
        help="Choose testing mode",
        key="test_mode"
    )
    
    st.divider()
    
    if test_mode == "Crawler Mode":
        st.subheader("Crawler Settings")
        base_url = st.text_input(
            "Base URL",
            value=st.session_state.base_url,
            help="Starting URL for crawling",
            key="crawler_base_url"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.number_input(
                "Max Depth",
                min_value=1,
                max_value=5,
                value=st.session_state.max_depth,
                help="Maximum crawling depth",
                key="crawler_max_depth"
            )
        with col2:
            max_pages = st.number_input(
                "Max Pages",
                min_value=1,
                max_value=100,
                value=st.session_state.max_pages,
                help="Maximum pages to test",
                key="crawler_max_pages"
            )
        
        same_origin = st.checkbox(
            "Same Origin Only",
            value=st.session_state.same_origin,
            help="Only crawl URLs from the same domain",
            key="crawler_same_origin"
        )
        
        with st.expander("Advanced Filters"):
            include_pattern = st.text_input(
                "Include Pattern (regex)",
                value=st.session_state.include_pattern,
                placeholder="e.g., /blog/.*",
                help="Include URLs matching this pattern",
                key="crawler_include_pattern"
            )
            exclude_pattern = st.text_input(
                "Exclude Pattern (regex)",
                value=st.session_state.exclude_pattern,
                placeholder="e.g., /admin/.*",
                help="Exclude URLs matching this pattern",
                key="crawler_exclude_pattern"
            )
    
    elif test_mode == "YAML Scenario":
        st.subheader("YAML Scenario")
        yaml_file = st.file_uploader(
            "Upload YAML Spec",
            type=['yaml', 'yml'],
            help="Upload test scenario YAML file"
        )
        
        if st.button("Generate Sample YAML"):
            sample_path = "tests/sample_specs/generated_sample.yaml"
            os.makedirs(os.path.dirname(sample_path), exist_ok=True)
            create_sample_yaml(sample_path)
            st.success(f"Sample YAML created at: {sample_path}")
    
    else:  # Single Page
        st.subheader("Single Page Test")
        test_url = st.text_input(
            "Page URL",
            value=st.session_state.base_url,
            help="URL of the page to test",
            key="single_page_url"
        )
    
    st.divider()
    
    # Test options
    st.subheader("Test Options")
    headless = st.checkbox(
        "Headless Mode", 
        value=st.session_state.headless,
        key="test_headless"
    )
    
    timeout = st.slider(
        "Timeout (seconds)",
        min_value=5,
        max_value=60,
        value=st.session_state.timeout,
        key="test_timeout"
    )
    
    deep_component_test = st.checkbox(
        "🔍 Deep Component Test",
        value=st.session_state.deep_component_test,
        help="Test semua button, form, image, dan link di halaman",
        key="test_deep_component"
    )
    
    # Penetration Testing Options
    st.subheader("🔒 Penetration Testing")
    enable_xss_test = st.checkbox(
        "XSS Testing",
        value=st.session_state.get("enable_xss_test", False),
        help="Test Cross-Site Scripting vulnerabilities",
        key="enable_xss_test"
    )
    
    enable_sql_test = st.checkbox(
        "SQL Injection Testing",
        value=st.session_state.get("enable_sql_test", False),
        help="Test SQL Injection vulnerabilities",
        key="enable_sql_test"
    )
    
    test_forms = st.checkbox(
        "Test Forms Submission (Experimental)",
        value=st.session_state.test_forms,
        help="Automatically detect and test form submissions",
        key="test_forms"
    )
    
    # Safe mode option for form testing
    if test_forms:
        form_safe_mode = st.checkbox(
            "🛡️ Safe Mode (Recommended)",
            value=st.session_state.get("form_safe_mode", True),
            help="Only test form filling without submission to avoid session loss and login redirects",
            key="form_safe_mode"
        )
        
        # Information about form testing and session issues
        with st.expander("ℹ️ About Form Testing & Session Issues"):
            st.markdown("""
            **Form Testing Challenges:**
            
            - **Session Timeout**: Forms may redirect to login if session expires
            - **Authentication Loss**: Form submission can invalidate session
            - **CSRF Protection**: Some forms require valid tokens
            - **Cookie Issues**: Session cookies may be blocked or expired
            
            **Safe Mode Benefits:**
            - ✅ Tests form filling without submission
            - ✅ Avoids session loss and login redirects
            - ✅ Preserves authentication state
            - ✅ Provides detailed form analysis
            
            **CSRF Token Support:**
            - 🔐 Automatically detects CSRF tokens
            - 🔐 Adds missing CSRF tokens to forms
            - 🔐 Supports meta tag CSRF tokens
            - 🔐 Works with Laravel, Django, Rails, etc.
            
            **Auto-Safe Mode (NEW!):**
            - 🛡️ **Automatic Protection**: Even when safe mode is disabled
            - 🔍 **Smart Detection**: Identifies session issues automatically
            - ⚡ **Triggers When**: Session timeout < 15 min, no session cookies, invalid session
            - 🎯 **Form Auth Detection**: Detects forms requiring authentication
            - 📊 **Detailed Analysis**: Shows why auto-safe mode was triggered
            
            **Common Session Issues:**
            - Session timeout < 30 minutes
            - Missing session cookies
            - Invalid authentication tokens
            - Cross-site request forgery protection
            """)

    st.divider()

    # Authentication
    st.subheader("Authentication")
    def on_auth_enabled_change():
        st.session_state.auth_enabled = st.session_state.auth_enabled
        save_config_to_file()
        logger.info(f"Auth enabled changed to: {st.session_state.auth_enabled}")
    
    auth_enabled = st.checkbox(
        "Require Login", 
        value=st.session_state.auth_enabled, 
        help="Login sebelum test dijalankan",
        key="auth_enabled",
        on_change=on_auth_enabled_change
    )
    
    def on_login_url_change():
        st.session_state.login_url = st.session_state.auth_login_url
        save_config_to_file()
        logger.info(f"Login URL changed to: '{st.session_state.auth_login_url}'")
    
    login_url = st.text_input(
        "Login URL", 
        value=st.session_state.login_url, 
        help="Halaman login",
        key="auth_login_url",
        on_change=on_login_url_change
    )
    
    def on_auth_username_change():
        st.session_state.auth_username = st.session_state.auth_username
        save_config_to_file()
        logger.info(f"Auth username changed to: '{st.session_state.auth_username}'")
    
    def on_auth_password_change():
        st.session_state.auth_password = st.session_state.auth_password
        save_config_to_file()
        logger.info("Auth password changed")
    
    col_auth1, col_auth2 = st.columns(2)
    with col_auth1:
        auth_username = st.text_input(
            "Username/Email", 
            value=st.session_state.auth_username, 
            help="Kredensial login",
            key="auth_username",
            on_change=on_auth_username_change
        )
    with col_auth2:
        auth_password = st.text_input(
            "Password", 
            value=st.session_state.auth_password, 
            type="password",
            key="auth_password",
            on_change=on_auth_password_change
        )
    
    def on_success_indicator_change():
        st.session_state.success_indicator = st.session_state.auth_success_indicator
        save_config_to_file()
        logger.info(f"Success Indicator changed to: '{st.session_state.auth_success_indicator}'")
    
    success_indicator = st.text_input(
        "Success Indicator (CSS atau teks)",
        value=st.session_state.success_indicator,
        help="Misal: #dashboard atau teks 'Dashboard'",
        key="auth_success_indicator",
        on_change=on_success_indicator_change
    )
    
    auth_config = None
    if auth_enabled:
        auth_config = {
            "enabled": True,
            "url": login_url or None,
            "credentials": {"username": auth_username or None, "password": auth_password or None},
            "success_indicator": success_indicator or None,
        }
    
    st.divider()
    
    # Configuration management
    col_run, col_clear, col_save = st.columns([2, 1, 1])
    with col_run:
        run_button = st.button(
            "🚀 Run Test",
            type="primary",
            width="stretch"
        )
    with col_clear:
        if st.button("🗑️ Clear", help="Reset all configuration to defaults"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            # Remove config file
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            st.rerun()
    with col_save:
        if st.button("💾 Save", help="Save current configuration to file"):
            save_config_to_file()
            st.success("Configuration saved!")
    
    # Show config status
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            last_saved = config_data.get('last_saved', 'Unknown')
            st.caption(f"💾 Config saved: {last_saved[:19] if last_saved != 'Unknown' else 'Unknown'}")
        except:
            st.caption("💾 Config file exists")
    else:
        st.caption("⚠️ No saved config")
    
    # Auto-save configuration when authentication settings change
    if 'last_auth_config' not in st.session_state:
        st.session_state.last_auth_config = ""
    
    # Get current values from session state (not from variables)
    current_auth_enabled = st.session_state.get("auth_enabled", False)
    current_login_url = st.session_state.get("login_url", "")
    current_auth_username = st.session_state.get("auth_username", "")
    current_auth_password = st.session_state.get("auth_password", "")
    current_success_indicator = st.session_state.get("success_indicator", "")
    
    current_auth_config = f"{current_auth_enabled}_{current_login_url}_{current_auth_username}_{current_auth_password}_{current_success_indicator}"
    
    if current_auth_config != st.session_state.last_auth_config:
        logger.info(f"Auth config changed, saving... Login URL: '{current_login_url}', Success Indicator: '{current_success_indicator}'")
        save_config_to_file()
        st.session_state.last_auth_config = current_auth_config

# Main content area
tab1, tab2, tab3 = st.tabs(["📊 Test Results", "📜 History", "ℹ️ About"])

with tab1:
    if run_button:
        # Generate run ID
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        artifacts_dir = f"artifacts/{run_id}"
        os.makedirs(artifacts_dir, exist_ok=True)
        
        # Initialize results
        results = []
        urls_to_test = []
        
        try:
            # Determine URLs to test based on mode
            if test_mode == "Crawler Mode":
                st.info(f"🕷️ Starting crawler from: {base_url}")
                
                # Create database record
                db_run = create_test_run(
                    run_id=run_id,
                    base_url=base_url,
                    config={
                        "mode": "crawler",
                        "max_depth": max_depth,
                        "max_pages": max_pages
                    }
                )
                update_test_run(run_id, status="running")
                
                with st.spinner("Crawling website..."):
                    include_patterns = [include_pattern] if include_pattern else None
                    exclude_patterns = [exclude_pattern] if exclude_pattern else None
                    
                    # Use authenticated crawler if auth is enabled
                    if auth_config and auth_config.get("enabled"):
                        st.info("🔐 Using authenticated crawler with login session")
                        urls_to_test = crawl_site_with_auth(
                            base_url=base_url,
                            max_depth=max_depth,
                            max_pages=max_pages,
                            same_origin_only=same_origin,
                            include_patterns=include_patterns,
                            exclude_patterns=exclude_patterns,
                            timeout=timeout,
                            auth=auth_config,
                            headless=headless
                        )
                    else:
                        urls_to_test = crawl_site(
                            base_url=base_url,
                            max_depth=max_depth,
                            max_pages=max_pages,
                            same_origin_only=same_origin,
                            include_patterns=include_patterns,
                            exclude_patterns=exclude_patterns,
                            timeout=timeout
                        )
                
                st.success(f"✅ Found {len(urls_to_test)} pages to test")
            
            elif test_mode == "YAML Scenario":
                if yaml_file is None:
                    st.warning("⚠️ Please upload a YAML file")
                    st.stop()
                
                # Save uploaded file
                yaml_path = os.path.join(artifacts_dir, "spec.yaml")
                with open(yaml_path, 'wb') as f:
                    f.write(yaml_file.read())
                
                # Load and validate YAML
                spec = load_yaml_spec(yaml_path)
                
                st.info(f"📋 Running {len(spec.scenarios)} scenarios from YAML")
                
                # Create database record
                db_run = create_test_run(
                    run_id=run_id,
                    base_url=spec.base_url,
                    config={"mode": "yaml", "scenarios": len(spec.scenarios)}
                )
                update_test_run(run_id, status="running")
                
                # Run scenarios
                for idx, scenario in enumerate(spec.scenarios):
                    scenario_dir = os.path.join(artifacts_dir, f"scenario_{idx}")
                    os.makedirs(scenario_dir, exist_ok=True)
                    
                    st.write(f"**Scenario {idx + 1}:** {scenario.name}")
                    
                    with st.spinner(f"Executing scenario..."):
                        result = run_yaml_scenario(
                            scenario=scenario.dict(),
                            base_url=spec.base_url,
                            out_dir=scenario_dir,
                            timeout=timeout * 1000,
                            headless=headless,
                            auth=(spec.auth.dict() if (spec.auth and spec.auth.enabled) else None)
                        )
                    
                    # Display scenario result
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Steps Executed", result['steps_executed'])
                    col2.metric("Passed", result['steps_passed'])
                    col3.metric("Failed", result['steps_failed'])
                    
                    if result['errors']:
                        with st.expander("View Errors"):
                            for error in result['errors']:
                                st.error(f"Step {error['step']}: {error['error']}")
                
                st.success("✅ All scenarios completed!")
                st.stop()
            
            else:  # Single Page
                urls_to_test = [test_url]
                
                # Create database record
                db_run = create_test_run(
                    run_id=run_id,
                    base_url=test_url,
                    config={"mode": "single_page"}
                )
                update_test_run(run_id, status="running")
            
            # Test each page
            if urls_to_test:
                st.subheader(f"🧪 Testing {len(urls_to_test)} page(s)")
                
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for idx, url in enumerate(urls_to_test):
                    status_text.text(f"Testing: {url}")
                    
                    # Create page directory
                    page_dir = os.path.join(artifacts_dir, f"page_{idx:04d}")
                    os.makedirs(page_dir, exist_ok=True)
                    
                    # Run smoke test
                    form_safe_mode_value = st.session_state.get("form_safe_mode", True)
                    logger.info(f"Form safe mode from session state: {form_safe_mode_value}")
                    
                    result = run_page_smoke(
                        url=url,
                        out_dir=page_dir,
                        timeout=timeout * 1000,
                        headless=headless,
                        deep_component_test=deep_component_test,
                        test_forms=test_forms,
                        form_safe_mode=form_safe_mode_value,
                        auth=auth_config,
                        enable_xss_test=enable_xss_test,
                        enable_sql_test=enable_sql_test
                    )
                    
                    # Form testing is now handled in run_page_smoke with test_forms parameter
                    
                    results.append(result)
                    
                    # Save to database
                    create_page_test(run_id, url, result)
                    
                    # Update progress
                    progress = (idx + 1) / len(urls_to_test)
                    progress_bar.progress(progress)
                
                status_text.text("✅ Testing complete!")
                
                # Update database
                passed_count = sum(1 for r in results if r['status'] == 'PASS')
                failed_count = len(results) - passed_count
                
                update_test_run(
                    run_id,
                    status="completed",
                    total_pages=len(results),
                    passed=passed_count,
                    failed=failed_count,
                    end_time=datetime.now(),
                    artifacts_path=artifacts_dir
                )
                
                # Display summary metrics
                st.subheader("📈 Summary")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                total_console_errors = sum(len(r.get('console_errors', [])) for r in results)
                total_network_fails = sum(len(r.get('network_failures', [])) for r in results)
                load_times = [r['load_ms'] for r in results if r.get('load_ms')]
                avg_load = int(sum(load_times) / len(load_times)) if load_times else 0
                pass_rate = int((passed_count / len(results) * 100)) if results else 0
                
                col1.metric("Total Pages", len(results))
                col2.metric("Passed", passed_count, delta=f"{pass_rate}%")
                col3.metric("Failed", failed_count)
                col4.metric("Console Errors", total_console_errors)
                col5.metric("Avg Load Time", f"{avg_load}ms")
                
                # Results table
                st.subheader("📋 Detailed Results")
                
                # Prepare data for display
                display_data = []
                for r in results:
                    assertions = r.get('assertions', [])
                    assertions_passed = sum(1 for a in assertions if a.get('pass'))
                    
                    display_data.append({
                        'URL': r['url'],
                        'Status': r['status'],
                        'HTTP': r.get('http_status', 'N/A'),
                        'Load (ms)': r.get('load_ms', 'N/A'),
                        'Console Errors': len(r.get('console_errors', [])),
                        'Network Fails': len(r.get('network_failures', [])),
                        'Assertions': f"{assertions_passed}/{len(assertions)}",
                        'Forms': r.get('forms_found', 0)
                    })
                
                st.dataframe(
                    display_data,
                    width="stretch",
                    hide_index=True
                )
                
                # Show error messages if any
                errors_found = [r for r in results if r.get('status') == 'ERROR' and r.get('error')]
                if errors_found:
                    st.error("⚠️ **Errors Detected:**")
                    for r in errors_found:
                        with st.expander(f"❌ Error for {r['url'][:60]}..."):
                            st.code(r.get('error', 'Unknown error'), language="text")
                
                # Display Component Test Results (if enabled)
                if deep_component_test and results and results[0].get('component_tests'):
                    st.subheader("🔍 Detailed Component Analysis")
                    
                    for idx, r in enumerate(results):
                        if 'component_tests' in r:
                            comp = r['component_tests']
                            summary = comp.get('summary', {})
                            
                            with st.expander(f"📄 {r['url'][:80]}... - Component Details"):
                                # Summary metrics
                                col1, col2, col3, col4 = st.columns(4)
                                
                                col1.metric(
                                    "Buttons",
                                    f"{summary.get('working_buttons', 0)}/{summary.get('total_buttons', 0)}",
                                    delta="Working"
                                )
                                col2.metric(
                                    "Images",
                                    f"{summary.get('loaded_images', 0)}/{summary.get('total_images', 0)}",
                                    delta=f"{summary.get('broken_images', 0)} broken" if summary.get('broken_images', 0) > 0 else "All OK",
                                    delta_color="inverse" if summary.get('broken_images', 0) > 0 else "normal"
                                )
                                col3.metric(
                                    "Links",
                                    summary.get('valid_links', 0),
                                    delta="Valid"
                                )
                                col4.metric(
                                    "Forms",
                                    f"{summary.get('complete_forms', 0)}/{summary.get('total_forms', 0)}",
                                    delta="Complete"
                                )
                                
                                # Detailed tabs
                                tab_btn, tab_img, tab_link, tab_form = st.tabs(["Buttons", "Images", "Links", "Forms"])
                                
                                with tab_btn:
                                    buttons = comp.get('buttons', {})
                                    st.write(f"**Total Buttons:** {buttons.get('total_buttons', 0)}")
                                    st.write(f"**Clickable:** {buttons.get('clickable_buttons', 0)}")
                                    st.write(f"**Disabled:** {buttons.get('disabled_buttons', 0)}")
                                    st.write(f"**Hidden:** {buttons.get('hidden_buttons', 0)}")
                                    
                                    if buttons.get('buttons_tested'):
                                        btn_data = [{
                                            "Text": b.get('text', 'N/A'),
                                            "Status": b.get('status', 'N/A'),
                                            "Visible": b.get('visible', False),
                                            "Enabled": b.get('enabled', False)
                                        } for b in buttons['buttons_tested'][:20]]
                                        st.dataframe(btn_data, width="stretch")
                                
                                with tab_img:
                                    images = comp.get('images', {})
                                    st.write(f"**Total Images:** {images.get('total_images', 0)}")
                                    st.write(f"**Loaded:** {images.get('loaded_images', 0)}")
                                    st.write(f"**Broken:** {images.get('broken_images', 0)}")
                                    st.write(f"**Without Alt:** {images.get('images_without_alt', 0)}")
                                    
                                    if images.get('images_tested'):
                                        img_data = [{
                                            "Source": i.get('src', 'N/A')[:50],
                                            "Alt": i.get('alt', 'N/A'),
                                            "Size": f"{i.get('width', 0)}x{i.get('height', 0)}",
                                            "Status": i.get('status', 'N/A')
                                        } for i in images['images_tested'][:20]]
                                        st.dataframe(img_data, width="stretch")
                                
                                with tab_link:
                                    links = comp.get('links', {})
                                    st.write(f"**Total Links:** {links.get('total_links', 0)}")
                                    st.write(f"**Valid Links:** {links.get('valid_links', 0)}")
                                    st.write(f"**Empty Links:** {links.get('empty_links', 0)}")
                                    st.write(f"**External:** {links.get('external_links', 0)}")
                                    st.write(f"**Internal:** {links.get('internal_links', 0)}")
                                    
                                    if links.get('links_tested'):
                                        link_data = [{
                                            "Text": l.get('text', 'N/A'),
                                            "Href": l.get('href', 'N/A')[:50],
                                            "Type": l.get('type', 'N/A'),
                                            "Status": l.get('status', 'N/A')
                                        } for l in links['links_tested'][:20]]
                                        st.dataframe(link_data, width="stretch")
                                
                                with tab_form:
                                    forms = comp.get('forms', {})
                                    st.write(f"**Total Forms:** {forms.get('total_forms', 0)}")
                                    st.write(f"**With Action:** {forms.get('forms_with_action', 0)}")
                                    st.write(f"**With Submit Button:** {forms.get('forms_with_submit', 0)}")
                                    
                                    if forms.get('forms_tested'):
                                        for form_idx, form in enumerate(forms['forms_tested']):
                                            st.write(f"**Form {form_idx + 1}:**")
                                            st.write(f"- Action: `{form.get('action', 'N/A')}`")
                                            st.write(f"- Method: `{form.get('method', 'GET')}`")
                                            st.write(f"- Inputs: {form.get('input_count', 0)}")
                                            st.write(f"- Status: {form.get('status', 'N/A')}")
                                            
                                            if form.get('inputs'):
                                                input_data = [{
                                                    "Name": inp.get('name', 'N/A'),
                                                    "Type": inp.get('type', 'N/A')
                                                } for inp in form['inputs']]
                                                st.dataframe(input_data, width="stretch")
                                            st.divider()
                
                # Display Form Testing Results (if enabled)
                if test_forms and results:
                    st.subheader("📋 Form Testing Results")
                    
                    for idx, r in enumerate(results):
                        if 'form_test' in r and r['form_test']:
                            form_test = r['form_test']
                            
                            with st.expander(f"📝 Form Test Results - {r['url'][:80]}..."):
                                # Form test summary
                                col1, col2, col3 = st.columns(3)
                                
                                col1.metric(
                                    "Form Test Status",
                                    "✅ Success" if form_test.get('success') else "❌ Failed",
                                    delta="Success" if form_test.get('success') else "Failed"
                                )
                                
                                fill_result = form_test.get('fill_result', {})
                                col2.metric(
                                    "Fields Filled",
                                    fill_result.get('fields_filled', 0),
                                    delta=f"{fill_result.get('fields_failed', 0)} failed" if fill_result.get('fields_failed', 0) > 0 else "All OK"
                                )
                                
                                col3.metric(
                                    "Form Submitted",
                                    "✅ Yes" if form_test.get('submitted') else "❌ No",
                                    delta="Submitted" if form_test.get('submitted') else "Not Submitted"
                                )
                                
                                # Form test details
                                st.write("**Form Test Details:**")
                                
                                # Safe Mode indicator
                                if form_test.get('safe_mode'):
                                    if form_test.get('auto_safe_mode'):
                                        st.warning("🛡️ **Auto-Safe Mode Active** - Form filled without submission to preserve session (automatic protection)")
                                    else:
                                        st.info("🛡️ **Safe Mode Active** - Form filled without submission to preserve session")
                                    
                                    if form_test.get('safe_mode_reason'):
                                        st.write(f"**Reason:** {form_test['safe_mode_reason']}")
                                
                                    # Show detailed safe mode information
                                    if form_test.get('message'):
                                        st.write(f"**Message:** {form_test['message']}")
                                
                                # Session timeout information
                                if form_test.get('session_timeout_info'):
                                    timeout_info = form_test['session_timeout_info']
                                    if timeout_info.get('has_timeout'):
                                        st.warning(f"⏰ **Session Timeout Detected:** {timeout_info.get('timeout_minutes', 'N/A')} minutes")
                                        if timeout_info.get('warnings'):
                                            for warning in timeout_info['warnings']:
                                                st.warning(f"⚠️ {warning}")
                                
                                # Session recovery information
                                if form_test.get('session_restored'):
                                    if form_test.get('session_recovery_success'):
                                        st.success("🔄 **Session Recovery Successful** - User returned to authenticated state")
                                    else:
                                        st.error("❌ **Session Recovery Failed** - Still on login page")
                                
                                # Redirect analysis
                                if form_test.get('redirect_analysis'):
                                    redirect_analysis = form_test['redirect_analysis']
                                    st.write("**🔍 Redirect Analysis:**")
                                    st.write(f"**Cause:** {redirect_analysis.get('redirect_cause', 'Unknown')}")
                                    
                                    if redirect_analysis.get('error_messages'):
                                        st.write("**Error Messages Found:**")
                                        for error in redirect_analysis['error_messages'][:3]:  # Show first 3
                                            st.write(f"- {error.get('text', 'N/A')}")
                                    
                                    if redirect_analysis.get('recommendations'):
                                        st.write("**💡 Recommendations:**")
                                        for rec in redirect_analysis['recommendations']:
                                            st.write(f"- {rec}")
                                
                                # CSRF Token Support
                                if form_test.get('csrf_tokens_found', 0) > 0:
                                    st.success(f"🔐 **CSRF Protection:** {form_test['csrf_tokens_found']} token(s) found")
                                    if form_test.get('csrf_token_added'):
                                        st.info("🔐 **CSRF Token Added** - Token automatically added to form")
                                
                                # Success/Error indicators
                                if form_test.get('has_success_message'):
                                    st.success("✅ Success message detected on page")
                                
                                if form_test.get('has_error_message'):
                                    st.error("❌ Error message detected on page")
                                
                                # URL change
                                if form_test.get('url_changed'):
                                    st.info("🔄 URL changed after form submission")
                                
                                # Validation errors
                                if form_test.get('form_validation_errors'):
                                    st.error("⚠️ Form validation errors detected:")
                                    for error in form_test['form_validation_errors']:
                                        st.write(f"- {error.get('text', 'N/A')}")
                                
                                # Network errors
                                if form_test.get('network_errors'):
                                    st.error("🌐 Network errors during form submission:")
                                    for error in form_test['network_errors']:
                                        st.write(f"- {error.get('url', 'N/A')}: {error.get('failure', 'N/A')}")
                                
                                # Screenshot evidence
                                st.write("**📸 Screenshot Evidence:**")
                                
                                screenshot_before = form_test.get('screenshot_before_path')
                                screenshot_after = form_test.get('screenshot_after_path')
                                
                                if screenshot_before and os.path.exists(screenshot_before):
                                    st.write("**Before Form Submission:**")
                                    st.image(screenshot_before, caption="Form before submission", width="stretch")
                                
                                if screenshot_after and os.path.exists(screenshot_after):
                                    if form_test.get('safe_mode'):
                                        st.write("**After Form Filling (Safe Mode):**")
                                        st.image(screenshot_after, caption="Form after filling (submission skipped)", width="stretch")
                                    else:
                                        st.write("**After Form Submission:**")
                                        st.image(screenshot_after, caption="Form after submission", width="stretch")
                                
                                # Form test errors
                                if form_test.get('errors'):
                                    st.error("**Form Test Errors:**")
                                    for error in form_test['errors']:
                                        st.write(f"- {error}")
                                
                                st.divider()
                
                # Display Penetration Testing Results
                if (enable_xss_test or enable_sql_test) and results:
                    st.subheader("🔒 Penetration Testing Results")
                    
                    for idx, r in enumerate(results):
                        pentest_results = []
                        
                        # XSS Test Results
                        if 'xss_test' in r and r['xss_test']:
                            xss_test = r['xss_test']
                            pentest_results.append(('XSS', xss_test))
                        
                        # SQL Test Results  
                        if 'sql_test' in r and r['sql_test']:
                            sql_test = r['sql_test']
                            pentest_results.append(('SQL Injection', sql_test))
                        
                        if pentest_results:
                            with st.expander(f"🔒 Penetration Test Results - {r['url'][:80]}..."):
                                for test_type, test_data in pentest_results:
                                    st.write(f"**{test_type} Testing:**")
                                    
                                    summary = test_data.get('summary', {})
                                    vulnerabilities = summary.get('vulnerabilities_found', 0)
                                    
                                    if vulnerabilities > 0:
                                        st.error(f"🚨 **{vulnerabilities} vulnerabilities found!**")
                                        
                                        # Show detailed results
                                        form_tests = test_data.get('form_tests', [])
                                        for test in form_tests:
                                            if test.get('is_vulnerable'):
                                                st.write(f"**Input:** {test.get('input_name', 'N/A')}")
                                                st.write(f"**Payload:** `{test.get('payload', 'N/A')}`")
                                                st.write(f"**Risk Level:** {test.get('risk_level', 'N/A')}")
                                                if test.get('response_snippet'):
                                                    st.write(f"**Response:** {test.get('response_snippet', '')[:200]}...")
                                                st.divider()
                                    else:
                                        st.success(f"✅ No {test_type} vulnerabilities found")
                                    
                                    st.divider()
                
                # Generate reports
                st.subheader("📄 Export Reports")
                
                with st.spinner("Generating reports..."):
                    report_paths = generate_all_reports(results, artifacts_dir, run_id)
                
                col1, col2, col3 = st.columns(3)
                
                # HTML Report
                with col1:
                    with open(report_paths['html'], 'rb') as f:
                        st.download_button(
                            "📊 Download HTML",
                            f.read(),
                            file_name=f"report_{run_id}.html",
                            mime="text/html"
                        )
                
                # CSV Report
                with col2:
                    with open(report_paths['csv'], 'rb') as f:
                        st.download_button(
                            "📈 Download CSV",
                            f.read(),
                            file_name=f"report_{run_id}.csv",
                            mime="text/csv"
                        )
                
                # JSON Report
                with col3:
                    with open(report_paths['json'], 'rb') as f:
                        st.download_button(
                            "🔧 Download JSON",
                            f.read(),
                            file_name=f"report_{run_id}.json",
                            mime="application/json"
                        )
                
                st.success(f"✅ Reports saved to: `{artifacts_dir}`")
                
                # View HTML report inline
                with st.expander("👁️ Preview HTML Report"):
                    with open(report_paths['html'], 'r', encoding='utf-8') as f:
                        st.components.v1.html(f.read(), height=600, scrolling=True)
        
        except Exception as e:
            st.error(f"❌ Error during test execution: {str(e)}")
            logger.error(f"Test execution error: {e}", exc_info=True)
            
            if 'run_id' in locals():
                update_test_run(run_id, status="failed")
    
    else:
        # Show placeholder
        st.info("👈 Configure your test in the sidebar and click **Run Test** to start")
        
        st.markdown("""
        ### Quick Start
        
        1. **Choose a test mode**:
           - **Crawler Mode**: Automatically discover and test multiple pages
           - **YAML Scenario**: Run custom test scenarios from YAML file
           - **Single Page**: Test a single URL
        
        2. **Configure options** in the sidebar
        
        3. **Click Run Test** to start testing
        
        4. **Download reports** in HTML, CSV, or JSON format
        """)

with tab2:
    st.subheader("📜 Test History")
    
    recent_runs = get_recent_runs(limit=20)
    
    if recent_runs:
        history_data = []
        for run in recent_runs:
            duration = ""
            if run.end_time:
                delta = run.end_time - run.start_time
                duration = f"{delta.total_seconds():.1f}s"
            
            history_data.append({
                'Run ID': run.run_id,
                'Base URL': run.base_url,
                'Status': run.status,
                'Pages': run.total_pages,
                'Passed': run.passed,
                'Failed': run.failed,
                'Duration': duration,
                'Started': run.start_time.strftime("%Y-%m-%d %H:%M")
            })
        
        st.dataframe(history_data, width="stretch", hide_index=True)
    else:
        st.info("No test history yet. Run your first test!")

with tab3:
    st.subheader("ℹ️ About Black-Box Testing Tool")
    
    st.markdown("""
    ### Features
    
    - 🕷️ **Automatic Crawling**: Discover pages automatically with depth and pattern control
    - 🧪 **Smoke Testing**: Load time, HTTP status, console errors, network failures
    - ✅ **Assertions**: Title, heading, meta tags, broken images
    - 📋 **Form Testing**: Auto-detect and test forms (experimental)
    - 📝 **YAML Scenarios**: Custom test workflows with actions and assertions
    - 📊 **Rich Reports**: HTML, CSV, and JSON export formats
    - 💾 **Test History**: Track all test runs in SQLite database
    - 📸 **Screenshots**: Capture full-page screenshots for evidence
    
    ### Technologies
    
    - **Playwright**: Modern browser automation
    - **Streamlit**: Interactive web UI
    - **SQLModel**: Database ORM
    - **Jinja2**: HTML report templating
    - **Beautiful Soup**: HTML parsing for crawler
    
    ### Limitations
    
    - ⚠️ Cannot bypass CAPTCHA or authentication
    - ⚠️ Limited support for SPAs with heavy JavaScript
    - ⚠️ Form testing is experimental
    
    ### Version
    
    **v1.0.0** - Initial Release
    
    ---
    
    Made with ❤️ using Playwright and Streamlit
    """)

# Footer
st.divider()
st.markdown(
    '<div style="text-align: center; color: #666; font-size: 0.9rem;">Black-Box Testing Tool v1.0 | Powered by Playwright</div>',
    unsafe_allow_html=True
)

