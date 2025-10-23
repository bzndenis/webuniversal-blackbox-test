"""
PDF Report Generator untuk Black-Box Testing Application.

Menggunakan ReportLab untuk menghasilkan laporan PDF yang profesional
dengan format yang mudah dibaca dan struktur yang jelas.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.platypus.flowables import HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import logging

logger = logging.getLogger(__name__)


class PDFReporter:
    """Generator laporan PDF profesional untuk hasil testing."""
    
    def __init__(self, output_dir: str):
        """
        Inisialisasi PDF Reporter.
        
        Args:
            output_dir: Direktori untuk menyimpan file PDF
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self) -> None:
        """Setup custom styles untuk laporan PDF."""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.darkblue
        ))
        
        # Section header
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            spaceAfter=8,
            spaceBefore=16,
            textColor=colors.darkgreen
        ))
        
        # Summary style
        self.styles.add(ParagraphStyle(
            name='SummaryText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Error style
        self.styles.add(ParagraphStyle(
            name='ErrorText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.red,
            spaceAfter=4
        ))
        
        # Success style
        self.styles.add(ParagraphStyle(
            name='SuccessText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.green,
            spaceAfter=4
        ))
        
        # Info style
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.blue,
            spaceAfter=4
        ))
    
    def generate_report(self, run_id: str, test_results: Dict[str, Any]) -> str:
        """
        Generate laporan PDF dari hasil testing.
        
        Args:
            run_id: ID untuk run testing
            test_results: Data hasil testing
            
        Returns:
            Path ke file PDF yang dihasilkan
        """
        try:
            # Debug: Log data structure for troubleshooting
            logger.info(f"PDF generation started for run_id: {run_id}")
            logger.info(f"Test results keys: {list(test_results.keys()) if isinstance(test_results, dict) else 'Not a dict'}")
            
            # Log specific problematic fields
            if 'summary' in test_results:
                summary_type = type(test_results['summary']).__name__
                logger.info(f"Summary type: {summary_type}")
                if isinstance(test_results['summary'], list):
                    logger.info(f"Summary list length: {len(test_results['summary'])}")
            
            if 'component_tests' in test_results:
                comp_type = type(test_results['component_tests']).__name__
                logger.info(f"Component tests type: {comp_type}")
                if isinstance(test_results['component_tests'], list):
                    logger.info(f"Component tests list length: {len(test_results['component_tests'])}")
            pdf_path = self.output_dir / f"report_{run_id}.pdf"
            
            # Create PDF document
            doc = SimpleDocTemplate(
                str(pdf_path),
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            # Build content
            story = []
            
            # Header
            story.extend(self._create_header(run_id, test_results))
            
            # Check if this is a stress test
            is_stress_test = False
            if 'summary' in test_results:
                summary = test_results['summary']
                # Check if summary is a dict and has stress test specific keys
                if isinstance(summary, dict) and 'total_requests' in summary:
                    is_stress_test = True
            
            if is_stress_test:
                # Stress test report
                try:
                    story.extend(self._create_stress_test_summary(test_results))
                    story.extend(self._create_stress_test_details(test_results))
                except Exception as e:
                    logger.error(f"Stress test sections failed: {e}")
                    # Fallback to basic summary
                    story.extend(self._create_executive_summary(test_results))
            else:
                # Regular test report
                try:
                    story.extend(self._create_executive_summary(test_results))
                    story.extend(self._create_test_overview(test_results))
                    story.extend(self._create_detailed_results(test_results))
                except Exception as e:
                    logger.error(f"Regular test sections failed: {e}")
                    # Add basic error message
                    story.append(Paragraph("Error generating detailed report sections.", self.styles['ErrorText']))
                
                # Component Analysis (if available)
                # Check if component_tests exist in page_results
                page_results = test_results.get('page_results', [])
                has_component_tests = False
                for page in page_results:
                    if isinstance(page, dict) and 'component_tests' in page:
                        has_component_tests = True
                        break
                
                if has_component_tests:
                    try:
                        story.extend(self._create_component_analysis_from_pages(page_results))
                    except Exception as e:
                        logger.warning(f"Component analysis failed: {e}")
                        # Continue without component analysis
                
                # Penetration Testing Results (if available)
                try:
                    story.extend(self._create_penetration_testing_results(test_results))
                except Exception as e:
                    logger.warning(f"Penetration testing results failed: {e}")
                    # Continue without penetration testing results
                
                # Assertion Results (if available)
                try:
                    story.extend(self._create_assertion_results(test_results))
                except Exception as e:
                    logger.warning(f"Assertion results failed: {e}")
                    # Continue without assertion results
                
                # Form Testing Results (if available)
                try:
                    story.extend(self._create_form_testing_results(test_results))
                except Exception as e:
                    logger.warning(f"Form testing results failed: {e}")
                    # Continue without form testing results
            
            # Screenshots Section
            try:
                story.extend(self._create_screenshots_section(test_results))
            except Exception as e:
                logger.warning(f"Screenshots section failed: {e}")
                # Continue without screenshots section
            
            # Recommendations
            try:
                story.extend(self._create_recommendations(test_results))
            except Exception as e:
                logger.warning(f"Recommendations section failed: {e}")
                # Add basic recommendations
                story.append(Paragraph("RECOMMENDATIONS", self.styles['CustomSubtitle']))
                story.append(Paragraph("• Review test results for any issues", self.styles['SummaryText']))
            
            # Footer
            story.extend(self._create_footer())
            
            # Build PDF
            doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            logger.info(f"PDF report generated: {pdf_path}")
            return str(pdf_path)
            
        except Exception as e:
            logger.error(f"Error generating PDF report: {e}")
            raise
    
    def _create_header(self, run_id: str, test_results: Dict[str, Any]) -> List:
        """Create header section."""
        story = []
        
        # Title
        story.append(Paragraph("BLACK-BOX FUNCTIONAL TESTING REPORT", self.styles['CustomTitle']))
        story.append(Spacer(1, 12))
        
        # Report info
        report_date = datetime.now().strftime("%d %B %Y, %H:%M:%S")
        story.append(Paragraph(f"<b>Report ID:</b> {run_id}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Generated:</b> {report_date}", self.styles['Normal']))
        story.append(Paragraph(f"<b>Test Mode:</b> {test_results.get('test_mode', 'Unknown')}", self.styles['Normal']))
        
        if 'base_url' in test_results:
            story.append(Paragraph(f"<b>Target URL:</b> {test_results['base_url']}", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.darkblue))
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_executive_summary(self, test_results: Dict[str, Any]) -> List:
        """Create executive summary section."""
        story = []
        
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Calculate summary metrics with safe access
        total_pages = test_results.get('total_pages', 0)
        passed_pages = test_results.get('passed_pages', 0)
        failed_pages = test_results.get('failed_pages', 0)
        error_pages = test_results.get('error_pages', 0)
        
        # Handle case where summary might be a list or different structure
        if 'summary' in test_results and isinstance(test_results['summary'], dict):
            summary = test_results['summary']
            total_pages = summary.get('total_pages', total_pages)
            passed_pages = summary.get('passed_pages', passed_pages)
            failed_pages = summary.get('failed_pages', failed_pages)
            error_pages = summary.get('error_pages', error_pages)
        
        pass_rate = (passed_pages / total_pages * 100) if total_pages > 0 else 0
        
        # Summary text
        summary_text = f"""
        This report presents the results of comprehensive black-box functional testing 
        conducted on {total_pages} web pages. The testing achieved a {pass_rate:.1f}% success rate, 
        with {passed_pages} pages passing all tests, {failed_pages} pages failing one or more tests, 
        and {error_pages} pages encountering errors during testing.
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Pages Tested', str(total_pages), 'Info'],
            ['Passed Tests', str(passed_pages), 'Success' if passed_pages > 0 else 'Error'],
            ['Failed Tests', str(failed_pages), 'Error' if failed_pages > 0 else 'Success'],
            ['Error Pages', str(error_pages), 'Error' if error_pages > 0 else 'Success'],
            ['Success Rate', f"{pass_rate:.1f}%", 'Success' if pass_rate >= 80 else 'Error']
        ]
        
        table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_test_overview(self, test_results: Dict[str, Any]) -> List:
        """Create test overview section."""
        story = []
        
        story.append(Paragraph("TEST OVERVIEW", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Test configuration
        config_text = f"""
        <b>Test Configuration:</b><br/>
        • Headless Mode: {test_results.get('headless', 'N/A')}<br/>
        • Timeout: {test_results.get('timeout', 'N/A')} seconds<br/>
        • Max Depth: {test_results.get('max_depth', 'N/A')}<br/>
        • Max Pages: {test_results.get('max_pages', 'N/A')}<br/>
        • Deep Component Testing: {test_results.get('deep_component_test', 'N/A')}
        """
        
        story.append(Paragraph(config_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Test duration
        if 'start_time' in test_results and 'end_time' in test_results:
            duration = test_results['end_time'] - test_results['start_time']
            duration_text = f"<b>Test Duration:</b> {duration.total_seconds():.2f} seconds"
            story.append(Paragraph(duration_text, self.styles['SummaryText']))
            story.append(Spacer(1, 12))
        
        return story
    
    def _create_detailed_results(self, test_results: Dict[str, Any]) -> List:
        """Create detailed results section."""
        story = []
        
        story.append(Paragraph("DETAILED TEST RESULTS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Get page results with safe access
        page_results = test_results.get('page_results', [])
        
        # Handle case where page_results might be in different structure
        if not page_results and 'results' in test_results:
            page_results = test_results.get('results', [])
        
        if not page_results:
            story.append(Paragraph("No detailed results available.", self.styles['SummaryText']))
            return story
        
        # Create results table
        table_data = [['Page', 'URL', 'Status', 'Load Time', 'Errors', 'Screenshots']]
        
        for i, page in enumerate(page_results[:20]):  # Limit to first 20 pages
            status = page.get('status', 'Unknown')
            status_color = 'Success' if status == 'passed' else 'Error' if status == 'failed' else 'Info'
            
            load_time = f"{page.get('load_time', 0):.2f}s"
            error_count = len(page.get('errors', []))
            screenshot_count = len(page.get('screenshots', []))
            
            table_data.append([
                f"Page {i+1}",
                page.get('url', 'N/A')[:50] + '...' if len(page.get('url', '')) > 50 else page.get('url', 'N/A'),
                status,
                load_time,
                str(error_count),
                str(screenshot_count)
            ])
        
        table = Table(table_data, colWidths=[0.8*inch, 2.5*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        story.append(table)
        
        if len(page_results) > 20:
            story.append(Spacer(1, 8))
            story.append(Paragraph(f"<i>Showing first 20 of {len(page_results)} pages. See full report for complete details.</i>", 
                                self.styles['SummaryText']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_component_analysis(self, component_tests: Any) -> List:
        """Create comprehensive component analysis section."""
        story = []
        
        story.append(Paragraph("COMPONENT ANALYSIS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Component summary with safe access
        summary = {}
        try:
            if isinstance(component_tests, dict):
                summary = component_tests.get('summary', {})
            elif isinstance(component_tests, list) and len(component_tests) > 0:
                # Handle case where component_tests is a list
                if isinstance(component_tests[0], dict):
                    summary = component_tests[0].get('summary', {})
                else:
                    # If first element is not dict, try to find summary in the list
                    for item in component_tests:
                        if isinstance(item, dict) and 'summary' in item:
                            summary = item.get('summary', {})
                            break
            else:
                logger.warning(f"Unexpected component_tests type: {type(component_tests)}")
                story.append(Paragraph("Component analysis data format not recognized.", self.styles['SummaryText']))
                return story
        except Exception as e:
            logger.error(f"Error processing component_tests: {e}")
            story.append(Paragraph("Error processing component analysis data.", self.styles['ErrorText']))
            return story
        
        # Enhanced summary with more details
        summary_text = f"""
        <b>Component Testing Summary:</b><br/>
        • <b>Buttons:</b> {summary.get('total_buttons', 0)} total (Working: {summary.get('working_buttons', 0)}, Disabled: {summary.get('disabled_buttons', 0)}, Hidden: {summary.get('hidden_buttons', 0)})<br/>
        • <b>Images:</b> {summary.get('total_images', 0)} total (Loaded: {summary.get('loaded_images', 0)}, Broken: {summary.get('broken_images', 0)}, No Alt: {summary.get('images_without_alt', 0)})<br/>
        • <b>Links:</b> {summary.get('total_links', 0)} total (Working: {summary.get('working_links', 0)}, External: {summary.get('external_links', 0)}, Empty: {summary.get('empty_links', 0)})<br/>
        • <b>Forms:</b> {summary.get('total_forms', 0)} total (Complete: {summary.get('complete_forms', 0)}, Incomplete: {summary.get('incomplete_forms', 0)})<br/>
        • <b>Interactive Elements:</b> {summary.get('total_interactive', 0)} total (Checkboxes: {summary.get('checkboxes', 0)}, Radio: {summary.get('radio_buttons', 0)}, Select: {summary.get('select_elements', 0)})
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed component results with enhanced information
        for component_type in ['buttons', 'images', 'links', 'forms', 'interactive']:
            try:
                component_data = None
                tested_items = []
                
                if isinstance(component_tests, dict) and component_type in component_tests:
                    component_data = component_tests[component_type]
                elif isinstance(component_tests, list):
                    # Search for component_type in the list
                    for item in component_tests:
                        if isinstance(item, dict) and component_type in item:
                            component_data = item[component_type]
                            break
                
                if component_data and isinstance(component_data, dict):
                    story.append(Paragraph(f"<b>{component_type.title()} Detailed Analysis:</b>", self.styles['SectionHeader']))
                    
                    # Get tested items
                    tested_items = component_data.get(f'{component_type}_tested', [])
                    
                    if tested_items and isinstance(tested_items, list):
                        # Create enhanced component table based on type
                        if component_type == 'buttons':
                            table_data = [['Button Text', 'Status', 'Visible', 'Enabled', 'Type']]
                            for item in tested_items[:15]:  # Show more items
                                if isinstance(item, dict):
                                    text = item.get('text', 'N/A')[:25] + '...' if len(item.get('text', '')) > 25 else item.get('text', 'N/A')
                                    status = item.get('status', 'Unknown')
                                    visible = 'Yes' if item.get('visible', False) else 'No'
                                    enabled = 'Yes' if item.get('enabled', False) else 'No'
                                    button_type = item.get('type', 'button')
                                    
                                    table_data.append([text, status, visible, enabled, button_type])
                        
                        elif component_type == 'images':
                            table_data = [['Image Source', 'Status', 'Size', 'Alt Text', 'Loading']]
                            for item in tested_items[:15]:
                                if isinstance(item, dict):
                                    src = item.get('src', 'N/A')[:30] + '...' if len(item.get('src', '')) > 30 else item.get('src', 'N/A')
                                    status = item.get('status', 'Unknown')
                                    size = f"{item.get('width', 0)}x{item.get('height', 0)}"
                                    alt = item.get('alt', 'N/A')[:20] + '...' if len(item.get('alt', '')) > 20 else item.get('alt', 'N/A')
                                    loading = 'Loaded' if item.get('status') == 'loaded' else 'Broken'
                                    
                                    table_data.append([src, status, size, alt, loading])
                        
                        elif component_type == 'links':
                            table_data = [['Link Text/URL', 'Status', 'Type', 'Target', 'Accessible']]
                            for item in tested_items[:15]:
                                if isinstance(item, dict):
                                    text = item.get('text', item.get('href', 'N/A'))[:25] + '...' if len(item.get('text', item.get('href', ''))) > 25 else item.get('text', item.get('href', 'N/A'))
                                    status = item.get('status', 'Unknown')
                                    link_type = 'Internal' if item.get('internal', False) else 'External'
                                    target = item.get('target', '_self')
                                    accessible = 'Yes' if item.get('accessible', False) else 'No'
                                    
                                    table_data.append([text, status, link_type, target, accessible])
                        
                        elif component_type == 'forms':
                            table_data = [['Form Action', 'Status', 'Method', 'Inputs', 'Submit Button']]
                            for item in tested_items[:10]:
                                if isinstance(item, dict):
                                    action = item.get('action', 'N/A')[:20] + '...' if len(item.get('action', '')) > 20 else item.get('action', 'N/A')
                                    status = item.get('status', 'Unknown')
                                    method = item.get('method', 'GET')
                                    inputs = str(item.get('input_count', 0))
                                    submit = 'Yes' if item.get('has_submit', False) else 'No'
                                    
                                    table_data.append([action, status, method, inputs, submit])
                        
                        elif component_type == 'interactive':
                            table_data = [['Element Type', 'Status', 'Value', 'Checked', 'Options']]
                            for item in tested_items[:15]:
                                if isinstance(item, dict):
                                    element_type = item.get('type', 'N/A')
                                    status = item.get('status', 'Unknown')
                                    value = str(item.get('value', 'N/A'))[:15] + '...' if len(str(item.get('value', ''))) > 15 else str(item.get('value', 'N/A'))
                                    checked = 'Yes' if item.get('checked', False) else 'No'
                                    options = str(item.get('option_count', 0))
                                    
                                    table_data.append([element_type, status, value, checked, options])
                        
                        # Create table with appropriate styling
                        if len(table_data) > 1:  # More than just header
                            col_widths = [1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch] if len(table_data[0]) == 5 else [2*inch, 1*inch, 1.5*inch]
                            
                            table = Table(table_data, colWidths=col_widths)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 8),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('FONTSIZE', (0, 1), (-1, -1), 7),
                                ('VALIGN', (0, 0), (-1, -1), 'TOP')
                            ]))
                            
                            story.append(table)
                            story.append(Spacer(1, 8))
                            
                            # Add summary for this component type
                            if component_type == 'buttons':
                                working = len([item for item in tested_items if item.get('status') == 'working'])
                                disabled = len([item for item in tested_items if item.get('status') == 'disabled'])
                                story.append(Paragraph(f"<b>Summary:</b> {working} working, {disabled} disabled buttons found.", self.styles['InfoText']))
                            elif component_type == 'images':
                                loaded = len([item for item in tested_items if item.get('status') == 'loaded'])
                                broken = len([item for item in tested_items if item.get('status') == 'broken'])
                                story.append(Paragraph(f"<b>Summary:</b> {loaded} loaded, {broken} broken images found.", self.styles['InfoText']))
                            elif component_type == 'links':
                                working = len([item for item in tested_items if item.get('status') == 'working'])
                                broken = len([item for item in tested_items if item.get('status') == 'broken'])
                                story.append(Paragraph(f"<b>Summary:</b> {working} working, {broken} broken links found.", self.styles['InfoText']))
                            
                            story.append(Spacer(1, 12))
            except Exception as e:
                logger.warning(f"Error processing {component_type} analysis: {e}")
                continue
        
        return story
    
    def _create_component_analysis_from_pages(self, page_results: List[Dict[str, Any]]) -> List:
        """Create component analysis from page results."""
        story = []
        
        story.append(Paragraph("DETAILED COMPONENT ANALYSIS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Aggregate component data from all pages
        total_buttons = 0
        total_images = 0
        total_links = 0
        total_forms = 0
        total_interactive = 0
        
        working_buttons = 0
        loaded_images = 0
        broken_images = 0
        working_links = 0
        complete_forms = 0
        
        all_component_data = {
            'buttons': [],
            'images': [],
            'links': [],
            'forms': [],
            'interactive': []
        }
        
        for page_idx, page in enumerate(page_results):
            if not isinstance(page, dict) or 'component_tests' not in page:
                continue
                
            page_url = page.get('url', f'Page {page_idx + 1}')
            component_tests = page['component_tests']
            
            if not isinstance(component_tests, dict):
                continue
            
            # Extract summary data
            summary = component_tests.get('summary', {})
            total_buttons += summary.get('total_buttons', 0)
            total_images += summary.get('total_images', 0)
            total_links += summary.get('total_links', 0)
            total_forms += summary.get('total_forms', 0)
            total_interactive += summary.get('total_interactive', 0)
            
            working_buttons += summary.get('working_buttons', 0)
            loaded_images += summary.get('loaded_images', 0)
            broken_images += summary.get('broken_images', 0)
            working_links += summary.get('working_links', 0)
            complete_forms += summary.get('complete_forms', 0)
            
            # Collect detailed component data
            for component_type in ['buttons', 'images', 'links', 'forms', 'interactive']:
                if component_type in component_tests:
                    component_data = component_tests[component_type]
                    if isinstance(component_data, dict):
                        tested_items = component_data.get(f'{component_type}_tested', [])
                        if isinstance(tested_items, list):
                            # Add page context to each item
                            for item in tested_items:
                                if isinstance(item, dict):
                                    item['page_url'] = page_url
                                    item['page_idx'] = page_idx
                            all_component_data[component_type].extend(tested_items)
        
        # Overall summary
        summary_text = f"""
        <b>Overall Component Testing Summary:</b><br/>
        • <b>Buttons:</b> {total_buttons} total (Working: {working_buttons}, Disabled: {total_buttons - working_buttons})<br/>
        • <b>Images:</b> {total_images} total (Loaded: {loaded_images}, Broken: {broken_images})<br/>
        • <b>Links:</b> {total_links} total (Working: {working_links}, Broken: {total_links - working_links})<br/>
        • <b>Forms:</b> {total_forms} total (Complete: {complete_forms}, Incomplete: {total_forms - complete_forms})<br/>
        • <b>Interactive Elements:</b> {total_interactive} total
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed component analysis for each type
        for component_type in ['buttons', 'images', 'links', 'forms', 'interactive']:
            component_items = all_component_data[component_type]
            
            if not component_items:
                continue
                
            story.append(Paragraph(f"<b>{component_type.title()} Detailed Analysis:</b>", self.styles['SectionHeader']))
            story.append(Spacer(1, 8))
            
            # Create detailed table based on component type
            if component_type == 'buttons':
                table_data = [['Page', 'Button Text', 'Status', 'Visible', 'Enabled', 'Type']]
                for item in component_items[:20]:  # Limit to first 20
                    if isinstance(item, dict):
                        page_url = item.get('page_url', 'N/A')[:30] + '...' if len(item.get('page_url', '')) > 30 else item.get('page_url', 'N/A')
                        text = item.get('text', 'N/A')[:20] + '...' if len(item.get('text', '')) > 20 else item.get('text', 'N/A')
                        status = item.get('status', 'Unknown')
                        visible = 'Yes' if item.get('visible', False) else 'No'
                        enabled = 'Yes' if item.get('enabled', False) else 'No'
                        button_type = item.get('type', 'button')
                        
                        table_data.append([page_url, text, status, visible, enabled, button_type])
            
            elif component_type == 'images':
                table_data = [['Page', 'Image Source', 'Status', 'Size', 'Alt Text']]
                for item in component_items[:20]:
                    if isinstance(item, dict):
                        page_url = item.get('page_url', 'N/A')[:30] + '...' if len(item.get('page_url', '')) > 30 else item.get('page_url', 'N/A')
                        src = item.get('src', 'N/A')[:25] + '...' if len(item.get('src', '')) > 25 else item.get('src', 'N/A')
                        status = item.get('status', 'Unknown')
                        size = f"{item.get('width', 0)}x{item.get('height', 0)}"
                        alt = item.get('alt', 'N/A')[:15] + '...' if len(item.get('alt', '')) > 15 else item.get('alt', 'N/A')
                        
                        table_data.append([page_url, src, status, size, alt])
            
            elif component_type == 'links':
                table_data = [['Page', 'Link Text/URL', 'Status', 'Type', 'Target']]
                for item in component_items[:20]:
                    if isinstance(item, dict):
                        page_url = item.get('page_url', 'N/A')[:30] + '...' if len(item.get('page_url', '')) > 30 else item.get('page_url', 'N/A')
                        text = item.get('text', item.get('href', 'N/A'))[:20] + '...' if len(item.get('text', item.get('href', ''))) > 20 else item.get('text', item.get('href', 'N/A'))
                        status = item.get('status', 'Unknown')
                        link_type = 'Internal' if item.get('internal', False) else 'External'
                        target = item.get('target', '_self')
                        
                        table_data.append([page_url, text, status, link_type, target])
            
            elif component_type == 'forms':
                table_data = [['Page', 'Form Action', 'Status', 'Method', 'Inputs', 'Submit']]
                for item in component_items[:15]:
                    if isinstance(item, dict):
                        page_url = item.get('page_url', 'N/A')[:30] + '...' if len(item.get('page_url', '')) > 30 else item.get('page_url', 'N/A')
                        action = item.get('action', 'N/A')[:15] + '...' if len(item.get('action', '')) > 15 else item.get('action', 'N/A')
                        status = item.get('status', 'Unknown')
                        method = item.get('method', 'GET')
                        inputs = str(item.get('input_count', 0))
                        submit = 'Yes' if item.get('has_submit', False) else 'No'
                        
                        table_data.append([page_url, action, status, method, inputs, submit])
            
            elif component_type == 'interactive':
                table_data = [['Page', 'Element Type', 'Status', 'Value', 'Checked']]
                for item in component_items[:20]:
                    if isinstance(item, dict):
                        page_url = item.get('page_url', 'N/A')[:30] + '...' if len(item.get('page_url', '')) > 30 else item.get('page_url', 'N/A')
                        element_type = item.get('type', 'N/A')
                        status = item.get('status', 'Unknown')
                        value = str(item.get('value', 'N/A'))[:15] + '...' if len(str(item.get('value', ''))) > 15 else str(item.get('value', 'N/A'))
                        checked = 'Yes' if item.get('checked', False) else 'No'
                        
                        table_data.append([page_url, element_type, status, value, checked])
            
            # Create table
            if len(table_data) > 1:  # More than just header
                col_widths = [1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch] if len(table_data[0]) == 6 else [1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 0.8*inch]
                
                table = Table(table_data, colWidths=col_widths)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 7),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTSIZE', (0, 1), (-1, -1), 6),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP')
                ]))
                
                story.append(table)
                story.append(Spacer(1, 8))
                
                # Add summary for this component type
                if component_type == 'buttons':
                    working = len([item for item in component_items if item.get('status') == 'working'])
                    disabled = len([item for item in component_items if item.get('status') == 'disabled'])
                    story.append(Paragraph(f"<b>Summary:</b> {working} working, {disabled} disabled buttons found.", self.styles['InfoText']))
                elif component_type == 'images':
                    loaded = len([item for item in component_items if item.get('status') == 'loaded'])
                    broken = len([item for item in component_items if item.get('status') == 'broken'])
                    story.append(Paragraph(f"<b>Summary:</b> {loaded} loaded, {broken} broken images found.", self.styles['InfoText']))
                elif component_type == 'links':
                    working = len([item for item in component_items if item.get('status') == 'working'])
                    broken = len([item for item in component_items if item.get('status') == 'broken'])
                    story.append(Paragraph(f"<b>Summary:</b> {working} working, {broken} broken links found.", self.styles['InfoText']))
                
                story.append(Spacer(1, 12))
        
        return story
    
    def _create_penetration_testing_results(self, test_results: Dict[str, Any]) -> List:
        """Create penetration testing results section."""
        story = []
        
        # Check if there are any penetration testing results
        page_results = test_results.get('page_results', [])
        if not page_results:
            return story
        
        has_pentest_results = False
        for page in page_results:
            if isinstance(page, dict) and ('xss_test' in page or 'sql_test' in page):
                has_pentest_results = True
                break
        
        if not has_pentest_results:
            return story
        
        story.append(Paragraph("PENETRATION TESTING RESULTS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Summary of penetration testing
        total_vulnerabilities = 0
        xss_vulnerabilities = 0
        sql_vulnerabilities = 0
        
        for page in page_results:
            if isinstance(page, dict):
                if 'xss_test' in page and page['xss_test']:
                    xss_test = page['xss_test']
                    if isinstance(xss_test, dict) and 'summary' in xss_test:
                        xss_vulnerabilities += xss_test['summary'].get('vulnerabilities_found', 0)
                
                if 'sql_test' in page and page['sql_test']:
                    sql_test = page['sql_test']
                    if isinstance(sql_test, dict) and 'summary' in sql_test:
                        sql_vulnerabilities += sql_test['summary'].get('vulnerabilities_found', 0)
        
        total_vulnerabilities = xss_vulnerabilities + sql_vulnerabilities
        
        summary_text = f"""
        <b>Security Testing Summary:</b><br/>
        • <b>Total Vulnerabilities Found:</b> {total_vulnerabilities}<br/>
        • <b>XSS Vulnerabilities:</b> {xss_vulnerabilities}<br/>
        • <b>SQL Injection Vulnerabilities:</b> {sql_vulnerabilities}<br/>
        • <b>Security Status:</b> {'🚨 HIGH RISK' if total_vulnerabilities > 0 else '✅ SECURE'}
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed penetration testing results
        for page_idx, page in enumerate(page_results):
            if not isinstance(page, dict):
                continue
                
            page_url = page.get('url', f'Page {page_idx + 1}')
            page_pentest_results = []
            
            # XSS Test Results
            if 'xss_test' in page and page['xss_test']:
                xss_test = page['xss_test']
                if isinstance(xss_test, dict):
                    page_pentest_results.append(('XSS', xss_test))
            
            # SQL Test Results
            if 'sql_test' in page and page['sql_test']:
                sql_test = page['sql_test']
                if isinstance(sql_test, dict):
                    page_pentest_results.append(('SQL Injection', sql_test))
            
            if page_pentest_results:
                story.append(Paragraph(f"<b>Security Test Results - {page_url[:60]}...</b>", self.styles['SectionHeader']))
                story.append(Spacer(1, 8))
                
                for test_type, test_data in page_pentest_results:
                    if isinstance(test_data, dict) and 'summary' in test_data:
                        summary = test_data['summary']
                        vulnerabilities = summary.get('vulnerabilities_found', 0)
                        
                        if vulnerabilities > 0:
                            story.append(Paragraph(f"🚨 <b>{test_type} Vulnerabilities Found: {vulnerabilities}</b>", self.styles['ErrorText']))
                            
                            # Show detailed results
                            form_tests = test_data.get('form_tests', [])
                            if form_tests and isinstance(form_tests, list):
                                story.append(Paragraph(f"<b>Vulnerable Inputs:</b>", self.styles['InfoText']))
                                
                                for test in form_tests[:5]:  # Limit to first 5
                                    if isinstance(test, dict) and test.get('is_vulnerable'):
                                        input_name = test.get('input_name', 'N/A')
                                        payload = test.get('payload', 'N/A')
                                        risk_level = test.get('risk_level', 'N/A')
                                        
                                        story.append(Paragraph(f"• <b>Input:</b> {input_name}", self.styles['InfoText']))
                                        story.append(Paragraph(f"  <b>Payload:</b> {payload}", self.styles['InfoText']))
                                        story.append(Paragraph(f"  <b>Risk Level:</b> {risk_level}", self.styles['InfoText']))
                                        story.append(Spacer(1, 4))
                        else:
                            story.append(Paragraph(f"✅ No {test_type} vulnerabilities found", self.styles['SuccessText']))
                    
                    story.append(Spacer(1, 8))
        
        return story
    
    def _create_assertion_results(self, test_results: Dict[str, Any]) -> List:
        """Create assertion results section."""
        story = []
        
        # Check if there are any assertion results
        page_results = test_results.get('page_results', [])
        if not page_results:
            return story
        
        has_assertions = False
        for page in page_results:
            if isinstance(page, dict) and 'assertions' in page:
                has_assertions = True
                break
        
        if not has_assertions:
            return story
        
        story.append(Paragraph("ASSERTION TESTING RESULTS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Summary of assertions
        total_assertions = 0
        passed_assertions = 0
        failed_assertions = 0
        
        for page in page_results:
            if isinstance(page, dict) and 'assertions' in page:
                assertions = page['assertions']
                if isinstance(assertions, list):
                    for assertion in assertions:
                        if isinstance(assertion, dict):
                            total_assertions += 1
                            if assertion.get('pass', False):
                                passed_assertions += 1
                            else:
                                failed_assertions += 1
        
        success_rate = (passed_assertions/total_assertions*100) if total_assertions > 0 else 0
        summary_text = f"""
        <b>Assertion Testing Summary:</b><br/>
        • <b>Total Assertions:</b> {total_assertions}<br/>
        • <b>Passed:</b> {passed_assertions}<br/>
        • <b>Failed:</b> {failed_assertions}<br/>
        • <b>Success Rate:</b> {success_rate:.1f}%
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed assertion results
        for page_idx, page in enumerate(page_results):
            if not isinstance(page, dict) or 'assertions' not in page:
                continue
            
            page_url = page.get('url', f'Page {page_idx + 1}')
            assertions = page.get('assertions', [])
            
            if assertions and isinstance(assertions, list):
                story.append(Paragraph(f"<b>Assertion Results - {page_url[:60]}...</b>", self.styles['SectionHeader']))
                story.append(Spacer(1, 8))
                
                # Create assertion table
                table_data = [['Assertion', 'Status', 'Expected', 'Actual']]
                
                for assertion in assertions:
                    if isinstance(assertion, dict):
                        assert_name = assertion.get('assert', 'Unknown')
                        passed = assertion.get('pass', False)
                        expected = assertion.get('expected', 'N/A')
                        actual = assertion.get('actual', 'N/A')
                        
                        status = '✅ PASS' if passed else '❌ FAIL'
                        
                        table_data.append([
                            assert_name,
                            status,
                            str(expected)[:30] + '...' if len(str(expected)) > 30 else str(expected),
                            str(actual)[:30] + '...' if len(str(actual)) > 30 else str(actual)
                        ])
                
                if len(table_data) > 1:  # More than just header
                    table = Table(table_data, colWidths=[1.5*inch, 0.8*inch, 1.5*inch, 1.5*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('FONTSIZE', (0, 1), (-1, -1), 7)
                    ]))
                    
                    story.append(table)
                    story.append(Spacer(1, 12))
        
        return story
    
    def _create_form_testing_results(self, test_results: Dict[str, Any]) -> List:
        """Create form testing results section with screenshots."""
        story = []
        
        # Check if there are any form testing results
        page_results = test_results.get('page_results', [])
        if not page_results:
            return story
        
        has_form_results = False
        for page in page_results:
            if isinstance(page, dict) and 'form_test' in page:
                has_form_results = True
                break
        
        if not has_form_results:
            return story
        
        story.append(Paragraph("FORM TESTING RESULTS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Summary of form testing
        total_forms_tested = 0
        successful_forms = 0
        failed_forms = 0
        
        for page in page_results:
            if isinstance(page, dict) and 'form_test' in page:
                form_test = page['form_test']
                if isinstance(form_test, dict):
                    total_forms_tested += 1
                    if form_test.get('success', False):
                        successful_forms += 1
                    else:
                        failed_forms += 1
        
        success_rate = (successful_forms/total_forms_tested*100) if total_forms_tested > 0 else 0
        summary_text = f"""
        <b>Form Testing Summary:</b><br/>
        • <b>Total Forms Tested:</b> {total_forms_tested}<br/>
        • <b>Successful Forms:</b> {successful_forms}<br/>
        • <b>Failed Forms:</b> {failed_forms}<br/>
        • <b>Success Rate:</b> {success_rate:.1f}%
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed form testing results
        for page_idx, page in enumerate(page_results):
            if not isinstance(page, dict) or 'form_test' not in page:
                continue
                
            page_url = page.get('url', f'Page {page_idx + 1}')
            form_test = page['form_test']
            
            if not isinstance(form_test, dict):
                continue
            
            story.append(Paragraph(f"<b>Form Test Results - {page_url[:60]}...</b>", self.styles['SectionHeader']))
            story.append(Spacer(1, 8))
            
            # Form test details
            success = form_test.get('success', False)
            status_text = "✅ SUCCESS" if success else "❌ FAILED"
            story.append(Paragraph(f"<b>Status:</b> {status_text}", self.styles['SuccessText'] if success else self.styles['ErrorText']))
            
            # Form details
            form_details = form_test.get('form_details', {})
            if form_details:
                story.append(Paragraph(f"<b>Form Details:</b>", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Action:</b> {form_details.get('action', 'N/A')}", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Method:</b> {form_details.get('method', 'N/A')}", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Inputs Found:</b> {form_details.get('input_count', 0)}", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Submit Button:</b> {'Yes' if form_details.get('has_submit', False) else 'No'}", self.styles['InfoText']))
            
            # Form filling results
            filling_results = form_test.get('filling_results', {})
            if filling_results:
                story.append(Paragraph(f"<b>Form Filling Results:</b>", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Fields Filled:</b> {filling_results.get('fields_filled', 0)}", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Fields Failed:</b> {filling_results.get('fields_failed', 0)}", self.styles['InfoText']))
                story.append(Paragraph(f"• <b>Safe Mode:</b> {'Yes' if filling_results.get('safe_mode', False) else 'No'}", self.styles['InfoText']))
            
            # Screenshots
            screenshots = form_test.get('screenshots', [])
            if screenshots and isinstance(screenshots, list):
                story.append(Paragraph(f"<b>Screenshots Captured:</b> {len(screenshots)}", self.styles['InfoText']))
                
                # List screenshot files
                for i, screenshot in enumerate(screenshots[:3]):  # Limit to first 3 screenshots
                    if isinstance(screenshot, str):
                        screenshot_name = screenshot.split('/')[-1] if '/' in screenshot else screenshot
                        story.append(Paragraph(f"• {screenshot_name}", self.styles['InfoText']))
            
            # Error details if failed
            if not success:
                error_details = form_test.get('error_details', {})
                if error_details:
                    story.append(Paragraph(f"<b>Error Details:</b>", self.styles['ErrorText']))
                    error_message = error_details.get('error_message', 'Unknown error')
                    story.append(Paragraph(f"• {error_message}", self.styles['ErrorText']))
            
            story.append(Spacer(1, 12))
        
        return story
    
    def _create_screenshots_section(self, test_results: Dict[str, Any]) -> List:
        """Create screenshots section."""
        story = []
        
        story.append(Paragraph("SCREENSHOTS & EVIDENCE", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Count screenshots with safe access
        page_results = test_results.get('page_results', [])
        if not page_results and 'results' in test_results:
            page_results = test_results.get('results', [])
        
        total_screenshots = 0
        if isinstance(page_results, list):
            for page in page_results:
                if isinstance(page, dict):
                    screenshots = page.get('screenshots', [])
                    if isinstance(screenshots, list):
                        total_screenshots += len(screenshots)
        
        if total_screenshots > 0:
            story.append(Paragraph(f"<b>Total Screenshots Captured:</b> {total_screenshots}", self.styles['SummaryText']))
            story.append(Paragraph("Screenshots are available in the artifacts directory for detailed analysis.", 
                                 self.styles['SummaryText']))
        else:
            story.append(Paragraph("No screenshots were captured during this test run.", self.styles['SummaryText']))
        
        story.append(Spacer(1, 12))
        
        return story
    
    def _create_recommendations(self, test_results: Dict[str, Any]) -> List:
        """Create recommendations section."""
        story = []
        
        story.append(Paragraph("RECOMMENDATIONS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Analyze results and provide recommendations
        recommendations = []
        
        # Safe access to test results
        total_pages = test_results.get('total_pages', 0)
        failed_pages = test_results.get('failed_pages', 0)
        error_pages = test_results.get('error_pages', 0)
        
        # Handle case where summary might be a dict with these values
        if 'summary' in test_results and isinstance(test_results['summary'], dict):
            summary = test_results['summary']
            total_pages = summary.get('total_pages', total_pages)
            failed_pages = summary.get('failed_pages', failed_pages)
            error_pages = summary.get('error_pages', error_pages)
        
        if failed_pages > 0:
            recommendations.append(f"• {failed_pages} pages failed testing - investigate and fix identified issues")
        
        if error_pages > 0:
            recommendations.append(f"• {error_pages} pages encountered errors - check server availability and page accessibility")
        
        # Component-specific recommendations with safe access
        if 'component_tests' in test_results:
            component_tests = test_results['component_tests']
            
            # Handle different component_tests structures
            summary = {}
            if isinstance(component_tests, dict):
                summary = component_tests.get('summary', {})
            elif isinstance(component_tests, list) and len(component_tests) > 0:
                if isinstance(component_tests[0], dict):
                    summary = component_tests[0].get('summary', {})
            
            if isinstance(summary, dict):
                broken_images = summary.get('broken_images', 0)
                if broken_images > 0:
                    recommendations.append(f"• {broken_images} broken images detected - fix image sources and alt text")
                
                incomplete_forms = summary.get('total_forms', 0) - summary.get('complete_forms', 0)
                if incomplete_forms > 0:
                    recommendations.append(f"• {incomplete_forms} incomplete forms detected - ensure all forms have proper action and submit elements")
        
        if not recommendations:
            recommendations.append("• All tests passed successfully - maintain current quality standards")
            recommendations.append("• Continue regular testing to ensure ongoing quality")
        
        for rec in recommendations:
            story.append(Paragraph(rec, self.styles['SummaryText']))
        
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_footer(self) -> List:
        """Create footer section."""
        story = []
        
        story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
        story.append(Spacer(1, 12))
        
        footer_text = f"""
        <i>This report was generated by Black-Box Functional Testing Application<br/>
        Generated on {datetime.now().strftime("%d %B %Y at %H:%M:%S")}<br/>
        For technical support, please refer to the application documentation.</i>
        """
        
        story.append(Paragraph(footer_text, self.styles['SummaryText']))
        
        return story
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.darkblue)
        canvas.drawString(72, A4[1] - 50, "Black-Box Testing Report")
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawString(72, 50, f"Page {doc.page}")
        canvas.drawRightString(A4[0] - 72, 50, datetime.now().strftime("%d/%m/%Y"))
        
        canvas.restoreState()
    
    def _create_stress_test_summary(self, test_results: Dict[str, Any]) -> List:
        """Create stress test summary section."""
        story = []
        
        story.append(Paragraph("STRESS TEST SUMMARY", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Get summary data
        summary = test_results.get('summary', {})
        config = test_results.get('config', {})
        
        # Summary text
        total_requests = summary.get('total_requests', 0)
        successful_requests = summary.get('successful_requests', 0)
        failed_requests = summary.get('failed_requests', 0)
        success_rate = summary.get('success_rate', 0)
        avg_response_time = summary.get('avg_response_time', 0)
        
        summary_text = f"""
        This stress test was conducted with {config.get('concurrent_users', 'N/A')} concurrent users 
        over a duration of {config.get('duration_seconds', 'N/A')} seconds. The test achieved a 
        {success_rate:.1f}% success rate with {successful_requests} successful requests out of 
        {total_requests} total requests. The average response time was {avg_response_time:.2f} seconds.
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Value', 'Status'],
            ['Total Requests', str(total_requests), 'Info'],
            ['Successful Requests', str(successful_requests), 'Success' if successful_requests > 0 else 'Error'],
            ['Failed Requests', str(failed_requests), 'Error' if failed_requests > 0 else 'Success'],
            ['Success Rate', f"{success_rate:.1f}%", 'Success' if success_rate >= 80 else 'Error'],
            ['Avg Response Time', f"{avg_response_time:.2f}s", 'Success' if avg_response_time < 2.0 else 'Error'],
            ['Requests/Second', f"{summary.get('requests_per_second', 0):.1f}", 'Info']
        ]
        
        table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 20))
        
        return story
    
    def _create_stress_test_details(self, test_results: Dict[str, Any]) -> List:
        """Create stress test detailed results section."""
        story = []
        
        story.append(Paragraph("DETAILED PERFORMANCE METRICS", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 12))
        
        # Get summary data
        summary = test_results.get('summary', {})
        config = test_results.get('config', {})
        
        # Performance metrics table
        perf_data = [
            ['Performance Metric', 'Value'],
            ['Min Response Time', f"{summary.get('min_response_time', 0):.3f}s"],
            ['Max Response Time', f"{summary.get('max_response_time', 0):.3f}s"],
            ['P95 Response Time', f"{summary.get('p95_response_time', 0):.3f}s"],
            ['P99 Response Time', f"{summary.get('p99_response_time', 0):.3f}s"],
            ['Total Duration', f"{summary.get('total_duration', 0):.2f}s"],
            ['Concurrent Users', str(config.get('concurrent_users', 'N/A'))],
            ['Ramp Up Time', f"{config.get('ramp_up_seconds', 'N/A')}s"],
            ['Ramp Down Time', f"{config.get('ramp_down_seconds', 'N/A')}s"],
            ['Think Time', f"{config.get('think_time_seconds', 'N/A')}s"]
        ]
        
        table = Table(perf_data, colWidths=[2.5*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ]))
        
        story.append(table)
        story.append(Spacer(1, 12))
        
        # Error analysis
        errors = summary.get('errors', {})
        if errors:
            story.append(Paragraph("ERROR ANALYSIS", self.styles['SectionHeader']))
            story.append(Spacer(1, 8))
            
            error_data = [['Error Type', 'Count']]
            for error_type, count in errors.items():
                error_data.append([error_type, str(count)])
            
            error_table = Table(error_data, colWidths=[3*inch, 1.5*inch])
            error_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 10)
            ]))
            
            story.append(error_table)
        
        story.append(Spacer(1, 20))
        
        return story
