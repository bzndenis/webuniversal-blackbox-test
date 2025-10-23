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
                if 'component_tests' in test_results:
                    try:
                        story.extend(self._create_component_analysis(test_results['component_tests']))
                    except Exception as e:
                        logger.warning(f"Component analysis failed: {e}")
                        # Continue without component analysis
            
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
        """Create component analysis section."""
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
        
        summary_text = f"""
        <b>Component Testing Summary:</b><br/>
        • Total Buttons: {summary.get('total_buttons', 0)} (Working: {summary.get('working_buttons', 0)})<br/>
        • Total Images: {summary.get('total_images', 0)} (Loaded: {summary.get('loaded_images', 0)}, Broken: {summary.get('broken_images', 0)})<br/>
        • Total Links: {summary.get('total_links', 0)} (Working: {summary.get('working_links', 0)})<br/>
        • Total Forms: {summary.get('total_forms', 0)} (Complete: {summary.get('complete_forms', 0)})
        """
        
        story.append(Paragraph(summary_text, self.styles['SummaryText']))
        story.append(Spacer(1, 12))
        
        # Detailed component results with safe access
        for component_type in ['buttons', 'images', 'links', 'forms']:
            try:
                if isinstance(component_tests, dict) and component_type in component_tests:
                    story.append(Paragraph(f"<b>{component_type.title()} Analysis:</b>", self.styles['SectionHeader']))
                    
                    component_data = component_tests[component_type]
                    if isinstance(component_data, dict):
                        tested_items = component_data.get(f'{component_type}_tested', [])
                    else:
                        tested_items = []
                elif isinstance(component_tests, list):
                    # Search for component_type in the list
                    component_data = None
                    for item in component_tests:
                        if isinstance(item, dict) and component_type in item:
                            component_data = item[component_type]
                            break
                    
                    if component_data:
                        story.append(Paragraph(f"<b>{component_type.title()} Analysis:</b>", self.styles['SectionHeader']))
                        if isinstance(component_data, dict):
                            tested_items = component_data.get(f'{component_type}_tested', [])
                        else:
                            tested_items = []
                    else:
                        continue
                else:
                    continue
                
                if tested_items and isinstance(tested_items, list):
                    # Create component table
                    table_data = [['Element', 'Status', 'Details']]
                    
                    for item in tested_items[:10]:  # Limit to first 10 items
                        try:
                            if isinstance(item, dict):
                                status = item.get('status', 'Unknown')
                                details = item.get('details', 'N/A')
                                
                                # Safe text extraction
                                text = 'N/A'
                                for key in ['text', 'src', 'href']:
                                    if key in item:
                                        text = str(item[key])
                                        break
                                
                                table_data.append([
                                    text[:30] + '...' if len(text) > 30 else text,
                                    status,
                                    str(details)[:40] + '...' if len(str(details)) > 40 else str(details)
                                ])
                        except Exception as e:
                            logger.warning(f"Error processing component item: {e}")
                            continue
                    
                    if len(table_data) > 1:  # More than just header
                        table = Table(table_data, colWidths=[2*inch, 1*inch, 2*inch])
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('FONTSIZE', (0, 1), (-1, -1), 8)
                        ]))
                        
                        story.append(table)
                        story.append(Spacer(1, 12))
            except Exception as e:
                logger.warning(f"Error processing {component_type} analysis: {e}")
                continue
        
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
