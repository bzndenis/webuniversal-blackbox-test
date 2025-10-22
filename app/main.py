"""Streamlit web application for Black-Box Functional Testing."""

import streamlit as st
import os
from datetime import datetime
import sys
from pathlib import Path

# Add app directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir.parent))

from app.runners.crawl import crawl_site
from app.runners.playwright_runner import run_page_smoke, run_yaml_scenario
from app.services.reporter import generate_all_reports
from app.services.yaml_loader import load_yaml_spec, create_sample_yaml
from app.services.heuristics import test_form_submission
from app.models.db import init_db, create_test_run, update_test_run, create_page_test, get_recent_runs
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Black-Box Testing Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
init_db()

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
        help="Choose testing mode"
    )
    
    st.divider()
    
    if test_mode == "Crawler Mode":
        st.subheader("Crawler Settings")
        base_url = st.text_input(
            "Base URL",
            value="https://example.com",
            help="Starting URL for crawling"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.number_input(
                "Max Depth",
                min_value=1,
                max_value=5,
                value=2,
                help="Maximum crawling depth"
            )
        with col2:
            max_pages = st.number_input(
                "Max Pages",
                min_value=1,
                max_value=100,
                value=10,
                help="Maximum pages to test"
            )
        
        same_origin = st.checkbox(
            "Same Origin Only",
            value=True,
            help="Only crawl URLs from the same domain"
        )
        
        with st.expander("Advanced Filters"):
            include_pattern = st.text_input(
                "Include Pattern (regex)",
                placeholder="e.g., /blog/.*",
                help="Include URLs matching this pattern"
            )
            exclude_pattern = st.text_input(
                "Exclude Pattern (regex)",
                placeholder="e.g., /admin/.*",
                help="Exclude URLs matching this pattern"
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
            value="https://example.com",
            help="URL of the page to test"
        )
    
    st.divider()
    
    # Test options
    st.subheader("Test Options")
    headless = st.checkbox("Headless Mode", value=True)
    timeout = st.slider(
        "Timeout (seconds)",
        min_value=5,
        max_value=60,
        value=10
    )
    deep_component_test = st.checkbox(
        "🔍 Deep Component Test",
        value=True,
        help="Test semua button, form, image, dan link di halaman"
    )
    test_forms = st.checkbox(
        "Test Forms Submission (Experimental)",
        value=False,
        help="Automatically detect and test form submissions"
    )
    
    st.divider()
    
    # Run button
    run_button = st.button(
        "🚀 Run Test",
        type="primary",
        use_container_width=True
    )

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
                            headless=headless
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
                    result = run_page_smoke(
                        url=url,
                        out_dir=page_dir,
                        timeout=timeout * 1000,
                        headless=headless,
                        deep_component_test=deep_component_test
                    )
                    
                    # Test forms if enabled
                    if test_forms and result.get('forms_found', 0) > 0:
                        try:
                            from playwright.sync_api import sync_playwright
                            with sync_playwright() as p:
                                browser = p.chromium.launch(headless=headless)
                                context = browser.new_context()
                                page = context.new_page()
                                page.goto(url, timeout=timeout * 1000)
                                
                                form_result = test_form_submission(page, 0)
                                result['form_test'] = form_result
                                result['forms_tested'] = 1 if form_result['success'] else 0
                                
                                context.close()
                                browser.close()
                        except Exception as e:
                            logger.error(f"Form test error: {e}")
                    
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
                    use_container_width=True,
                    hide_index=True
                )
                
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
                                        st.dataframe(btn_data, use_container_width=True)
                                
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
                                        st.dataframe(img_data, use_container_width=True)
                                
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
                                        st.dataframe(link_data, use_container_width=True)
                                
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
                                                st.dataframe(input_data, use_container_width=True)
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
        
        st.dataframe(history_data, use_container_width=True, hide_index=True)
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

