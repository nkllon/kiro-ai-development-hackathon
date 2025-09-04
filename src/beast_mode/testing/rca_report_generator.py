"""
Beast Mode Framework - Test RCA Report Generation System
Implements comprehensive reporting for test failure RCA analysis
Requirements: 2.2, 2.3, 2.4 - Detailed reporting with actionable recommendations
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

from ..core.reflective_module import ReflectiveModule, HealthStatus
from ..analysis.rca_engine import RCAResult, RootCauseType, PreventionPattern
from .rca_integration import TestFailureData, TestRCASummaryData, TestRCAReportData


class ReportFormat(Enum):
    """Supported report output formats"""
    CONSOLE = "console"
    JSON = "json"
    MARKDOWN = "markdown"


class ReportSection(Enum):
    """Report sections for structured output"""
    HEADER = "header"
    SUMMARY = "summary"
    FAILURES = "failures"
    ROOT_CAUSES = "root_causes"
    SYSTEMATIC_FIXES = "systematic_fixes"
    RECOMMENDATIONS = "recommendations"
    PREVENTION_PATTERNS = "prevention_patterns"
    NEXT_STEPS = "next_steps"
    FOOTER = "footer"


@dataclass
class ReportConfiguration:
    """Configuration for report generation"""
    format: ReportFormat = ReportFormat.CONSOLE
    include_sections: List[ReportSection] = field(default_factory=lambda: list(ReportSection))
    max_failures_displayed: int = 10
    max_recommendations: int = 5
    include_stack_traces: bool = False
    color_output: bool = True
    verbose_mode: bool = False
    output_file: Optional[str] = None


@dataclass
class FormattedReportSection:
    """Formatted section of a report"""
    section_type: ReportSection
    title: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormattedReport:
    """Complete formatted report"""
    report_id: str
    generation_timestamp: datetime
    format: ReportFormat
    sections: List[FormattedReportSection]
    total_length: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsoleColors:
    """ANSI color codes for console output"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'
    
    @classmethod
    def colorize(cls, text: str, color: str, use_color: bool = True) -> str:
        """Apply color to text if color output is enabled"""
        if not use_color:
            return text
        return f"{color}{text}{cls.END}"


class RCAReportGenerator(ReflectiveModule):
    """
    Comprehensive RCA report generation system for test failures
    Formats analysis results with clear sections and actionable recommendations
    Requirements: 2.2, 2.3, 2.4
    """
    
    def __init__(self):
        super().__init__("rca_report_generator")
        
        # Report generation metrics
        self.reports_generated = 0
        self.console_reports = 0
        self.json_reports = 0
        self.markdown_reports = 0
        self.total_generation_time = 0.0
        
        # Default configuration
        self.default_config = ReportConfiguration(
            format=ReportFormat.CONSOLE,
            include_sections=list(ReportSection),
            max_failures_displayed=10,
            max_recommendations=5,
            include_stack_traces=False,
            color_output=True,
            verbose_mode=False
        )
        
        self._update_health_indicator(
            "rca_report_generator_readiness",
            HealthStatus.HEALTHY,
            "ready",
            "RCA report generator ready for formatting analysis results"
        )
        
    def get_module_status(self) -> Dict[str, Any]:
        """Operational visibility for external systems"""
        return {
            "module_name": self.module_name,
            "status": "operational" if self.is_healthy() else "degraded",
            "reports_generated": self.reports_generated,
            "console_reports": self.console_reports,
            "json_reports": self.json_reports,
            "markdown_reports": self.markdown_reports,
            "average_generation_time": self.total_generation_time / max(1, self.reports_generated),
            "degradation_active": self._degradation_active
        }
        
    def is_healthy(self) -> bool:
        """Health assessment for report generation capability"""
        return not self._degradation_active
        
    def get_health_indicators(self) -> Dict[str, Any]:
        """Detailed health metrics for operational visibility"""
        return {
            "generation_capability": {
                "status": "healthy" if not self._degradation_active else "degraded",
                "reports_generated": self.reports_generated,
                "success_rate": 1.0 if self.reports_generated > 0 else 0.0
            },
            "format_support": {
                "console_reports": self.console_reports,
                "json_reports": self.json_reports,
                "markdown_reports": self.markdown_reports,
                "all_formats_supported": True
            },
            "performance": {
                "status": "healthy" if self.total_generation_time / max(1, self.reports_generated) < 5.0 else "degraded",
                "average_generation_time": self.total_generation_time / max(1, self.reports_generated),
                "generation_speed": "fast"
            }
        }
        
    def _get_primary_responsibility(self) -> str:
        """Single responsibility: RCA report generation and formatting"""
        return "rca_report_generation_and_formatting"
        
    def generate_report(
        self, 
        rca_report: TestRCAReportData, 
        config: Optional[ReportConfiguration] = None
    ) -> FormattedReport:
        """
        Generate formatted RCA report from analysis results
        Requirements: 2.2, 2.3, 2.4 - Comprehensive reporting with actionable recommendations
        """
        start_time = time.time()
        self.reports_generated += 1
        
        try:
            # Use provided config or default
            report_config = config or self.default_config
            
            self.logger.info(f"Generating {report_config.format.value} report for {rca_report.total_failures} test failures")
            
            # Generate report ID
            report_id = f"rca_report_{int(time.time())}_{report_config.format.value}"
            
            # Generate all requested sections
            sections = []
            for section_type in report_config.include_sections:
                try:
                    section = self._generate_section(section_type, rca_report, report_config)
                    if section:
                        sections.append(section)
                except Exception as e:
                    self.logger.error(f"Failed to generate section {section_type}: {e}")
                    # Add error section
                    error_section = FormattedReportSection(
                        section_type=section_type,
                        title=f"Error in {section_type.value}",
                        content=f"Section generation failed: {e}",
                        metadata={"error": str(e)}
                    )
                    sections.append(error_section)
                    
            # Calculate total report length
            total_length = sum(len(section.content) for section in sections)
            
            # Create formatted report
            formatted_report = FormattedReport(
                report_id=report_id,
                generation_timestamp=datetime.now(),
                format=report_config.format,
                sections=sections,
                total_length=total_length,
                metadata={
                    "total_failures": rca_report.total_failures,
                    "failures_analyzed": rca_report.failures_analyzed,
                    "systematic_fixes": rca_report.summary.systematic_fixes_available,
                    "confidence_score": rca_report.summary.confidence_score,
                    "generation_config": asdict(report_config)
                }
            )
            
            # Update metrics
            if report_config.format == ReportFormat.CONSOLE:
                self.console_reports += 1
            elif report_config.format == ReportFormat.JSON:
                self.json_reports += 1
            elif report_config.format == ReportFormat.MARKDOWN:
                self.markdown_reports += 1
                
            generation_time = time.time() - start_time
            self.total_generation_time += generation_time
            
            self.logger.info(f"Report generated: {len(sections)} sections, {total_length} chars in {generation_time:.3f}s")
            
            # Save to file if requested
            if report_config.output_file:
                self._save_report_to_file(formatted_report, report_config.output_file)
                
            return formatted_report
            
        except Exception as e:
            self.logger.error(f"Report generation failed: {e}")
            # Return minimal error report
            error_section = FormattedReportSection(
                section_type=ReportSection.HEADER,
                title="Report Generation Error",
                content=f"Failed to generate report: {e}",
                metadata={"error": str(e)}
            )
            
            return FormattedReport(
                report_id=f"error_report_{int(time.time())}",
                generation_timestamp=datetime.now(),
                format=config.format if config else ReportFormat.CONSOLE,
                sections=[error_section],
                total_length=len(error_section.content),
                metadata={"generation_error": str(e)}
            )
            
    def format_for_console(self, rca_report: TestRCAReportData, use_colors: bool = True) -> str:
        """
        Format RCA report for console output with clear sections
        Requirements: 2.3 - Console output formatting with clear sections
        """
        try:
            config = ReportConfiguration(
                format=ReportFormat.CONSOLE,
                color_output=use_colors,
                include_sections=list(ReportSection)
            )
            
            formatted_report = self.generate_report(rca_report, config)
            
            # Combine all sections into console output
            console_output = []
            for section in formatted_report.sections:
                console_output.append(section.content)
                console_output.append("")  # Add spacing between sections
                
            return "\n".join(console_output)
            
        except Exception as e:
            self.logger.error(f"Console formatting failed: {e}")
            return f"Console formatting error: {e}"
            
    def generate_json_report(self, rca_report: TestRCAReportData) -> Dict[str, Any]:
        """
        Generate JSON report for CI/CD integration
        Requirements: 2.4 - JSON report generation for different use cases
        """
        try:
            config = ReportConfiguration(format=ReportFormat.JSON)
            formatted_report = self.generate_report(rca_report, config)
            
            # Convert to JSON-serializable format
            json_data = {
                "report_metadata": {
                    "report_id": formatted_report.report_id,
                    "generation_timestamp": formatted_report.generation_timestamp.isoformat(),
                    "format": formatted_report.format.value,
                    "total_length": formatted_report.total_length
                },
                "analysis_summary": {
                    "total_failures": rca_report.total_failures,
                    "failures_analyzed": rca_report.failures_analyzed,
                    "analysis_timestamp": rca_report.analysis_timestamp.isoformat(),
                    "confidence_score": rca_report.summary.confidence_score,
                    "systematic_fixes_available": rca_report.summary.systematic_fixes_available,
                    "pattern_matches_found": rca_report.summary.pattern_matches_found,
                    "estimated_fix_time_minutes": rca_report.summary.estimated_fix_time_minutes
                },
                "root_causes": [
                    {
                        "type": cause_type.value,
                        "count": count
                    }
                    for cause_type, count in rca_report.summary.most_common_root_causes
                ],
                "critical_issues": rca_report.summary.critical_issues,
                "recommendations": rca_report.recommendations,
                "next_steps": rca_report.next_steps,
                "prevention_patterns": [
                    {
                        "pattern_id": pattern.pattern_id,
                        "pattern_name": pattern.pattern_name,
                        "prevention_steps": pattern.prevention_steps
                    }
                    for pattern in rca_report.prevention_patterns
                ],
                "rca_results": [
                    {
                        "failure_id": result.failure.failure_id,
                        "component": result.failure.component,
                        "root_causes_count": len(result.root_causes),
                        "systematic_fixes_count": len(result.systematic_fixes),
                        "analysis_time_seconds": result.total_analysis_time_seconds,
                        "confidence_score": result.rca_confidence_score
                    }
                    for result in rca_report.rca_results
                ]
            }
            
            return json_data
            
        except Exception as e:
            self.logger.error(f"JSON report generation failed: {e}")
            return {
                "error": f"JSON report generation failed: {e}",
                "timestamp": datetime.now().isoformat()
            }
            
    def generate_markdown_report(self, rca_report: TestRCAReportData) -> str:
        """
        Generate markdown report for documentation
        Requirements: 2.4 - Markdown report generation for different use cases
        """
        try:
            config = ReportConfiguration(
                format=ReportFormat.MARKDOWN,
                color_output=False,  # No colors in markdown
                include_sections=list(ReportSection)
            )
            
            formatted_report = self.generate_report(rca_report, config)
            
            # Combine sections into markdown
            markdown_content = []
            for section in formatted_report.sections:
                markdown_content.append(section.content)
                markdown_content.append("")  # Add spacing
                
            return "\n".join(markdown_content)
            
        except Exception as e:
            self.logger.error(f"Markdown report generation failed: {e}")
            return f"# Markdown Report Generation Error\n\nError: {e}"
            
    # Private helper methods for section generation
    
    def _generate_section(
        self, 
        section_type: ReportSection, 
        rca_report: TestRCAReportData, 
        config: ReportConfiguration
    ) -> Optional[FormattedReportSection]:
        """Generate specific report section based on type"""
        
        section_generators = {
            ReportSection.HEADER: self._generate_header_section,
            ReportSection.SUMMARY: self._generate_summary_section,
            ReportSection.FAILURES: self._generate_failures_section,
            ReportSection.ROOT_CAUSES: self._generate_root_causes_section,
            ReportSection.SYSTEMATIC_FIXES: self._generate_fixes_section,
            ReportSection.RECOMMENDATIONS: self._generate_recommendations_section,
            ReportSection.PREVENTION_PATTERNS: self._generate_patterns_section,
            ReportSection.NEXT_STEPS: self._generate_next_steps_section,
            ReportSection.FOOTER: self._generate_footer_section
        }
        
        generator = section_generators.get(section_type)
        if generator:
            return generator(rca_report, config)
        else:
            self.logger.warning(f"Unknown section type: {section_type}")
            return None
            
    def _generate_header_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate report header section"""
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🔍 Test RCA Analysis Report", ConsoleColors.BOLD + ConsoleColors.CYAN, config.color_output)
            separator = ConsoleColors.colorize("=" * 60, ConsoleColors.CYAN, config.color_output)
            timestamp = f"Generated: {rca_report.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            
            content = f"{separator}\n{title}\n{separator}\n{timestamp}\n"
            
        elif config.format == ReportFormat.MARKDOWN:
            content = f"# 🔍 Test RCA Analysis Report\n\n**Generated:** {rca_report.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
        else:  # JSON format
            content = json.dumps({
                "section": "header",
                "title": "Test RCA Analysis Report",
                "timestamp": rca_report.analysis_timestamp.isoformat()
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.HEADER,
            title="Report Header",
            content=content,
            metadata={"timestamp": rca_report.analysis_timestamp.isoformat()}
        )
        
    def _generate_summary_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate summary section with key metrics"""
        summary = rca_report.summary
        
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("📊 Analysis Summary", ConsoleColors.BOLD + ConsoleColors.YELLOW, config.color_output)
            
            # Format metrics with colors
            total_failures = ConsoleColors.colorize(str(rca_report.total_failures), ConsoleColors.RED, config.color_output)
            analyzed = ConsoleColors.colorize(str(rca_report.failures_analyzed), ConsoleColors.GREEN, config.color_output)
            fixes = ConsoleColors.colorize(str(summary.systematic_fixes_available), ConsoleColors.BLUE, config.color_output)
            confidence = ConsoleColors.colorize(f"{summary.confidence_score:.1%}", ConsoleColors.MAGENTA, config.color_output)
            time_est = ConsoleColors.colorize(f"{summary.estimated_fix_time_minutes} min", ConsoleColors.CYAN, config.color_output)
            
            content = f"""{title}
• Total Failures: {total_failures}
• Failures Analyzed: {analyzed}
• Systematic Fixes Available: {fixes}
• Pattern Matches Found: {summary.pattern_matches_found}
• Analysis Confidence: {confidence}
• Estimated Fix Time: {time_est}"""

            # Add critical issues if any
            if summary.critical_issues:
                critical_title = ConsoleColors.colorize("⚠️  Critical Issues:", ConsoleColors.BOLD + ConsoleColors.RED, config.color_output)
                critical_list = "\n".join([f"  • {issue}" for issue in summary.critical_issues[:3]])
                content += f"\n\n{critical_title}\n{critical_list}"
                
        elif config.format == ReportFormat.MARKDOWN:
            content = f"""## 📊 Analysis Summary

- **Total Failures:** {rca_report.total_failures}
- **Failures Analyzed:** {rca_report.failures_analyzed}
- **Systematic Fixes Available:** {summary.systematic_fixes_available}
- **Pattern Matches Found:** {summary.pattern_matches_found}
- **Analysis Confidence:** {summary.confidence_score:.1%}
- **Estimated Fix Time:** {summary.estimated_fix_time_minutes} minutes"""

            if summary.critical_issues:
                content += "\n\n### ⚠️ Critical Issues\n"
                content += "\n".join([f"- {issue}" for issue in summary.critical_issues[:3]])
                
        else:  # JSON format
            content = json.dumps({
                "section": "summary",
                "metrics": {
                    "total_failures": rca_report.total_failures,
                    "failures_analyzed": rca_report.failures_analyzed,
                    "systematic_fixes_available": summary.systematic_fixes_available,
                    "pattern_matches_found": summary.pattern_matches_found,
                    "confidence_score": summary.confidence_score,
                    "estimated_fix_time_minutes": summary.estimated_fix_time_minutes,
                    "critical_issues": summary.critical_issues
                }
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.SUMMARY,
            title="Analysis Summary",
            content=content,
            metadata={"confidence_score": summary.confidence_score}
        )
        
    def _generate_failures_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate failures overview section"""
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🚨 Test Failures Overview", ConsoleColors.BOLD + ConsoleColors.RED, config.color_output)
            
            content_lines = [title]
            
            # Group failures by type
            failure_groups = rca_report.grouped_failures
            for group_name, failures in list(failure_groups.items())[:config.max_failures_displayed]:
                group_title = ConsoleColors.colorize(f"📁 {group_name} ({len(failures)} failures)", ConsoleColors.YELLOW, config.color_output)
                content_lines.append(f"\n{group_title}")
                
                for failure in failures[:3]:  # Show max 3 per group
                    test_name = ConsoleColors.colorize(failure.test_name, ConsoleColors.WHITE, config.color_output)
                    content_lines.append(f"  • {test_name}")
                    content_lines.append(f"    File: {failure.test_file}")
                    content_lines.append(f"    Type: {failure.failure_type}")
                    
                    if config.include_stack_traces and failure.stack_trace:
                        content_lines.append(f"    Error: {failure.error_message[:100]}...")
                        
                if len(failures) > 3:
                    content_lines.append(f"    ... and {len(failures) - 3} more")
                    
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 🚨 Test Failures Overview\n"
            
            failure_groups = rca_report.grouped_failures
            for group_name, failures in list(failure_groups.items())[:config.max_failures_displayed]:
                content += f"\n### 📁 {group_name} ({len(failures)} failures)\n"
                
                for failure in failures[:3]:
                    content += f"- **{failure.test_name}**\n"
                    content += f"  - File: `{failure.test_file}`\n"
                    content += f"  - Type: {failure.failure_type}\n"
                    
                if len(failures) > 3:
                    content += f"  - ... and {len(failures) - 3} more\n"
                    
        else:  # JSON format
            failure_data = {}
            for group_name, failures in rca_report.grouped_failures.items():
                failure_data[group_name] = [
                    {
                        "test_name": f.test_name,
                        "test_file": f.test_file,
                        "failure_type": f.failure_type,
                        "error_message": f.error_message[:200] + "..." if len(f.error_message) > 200 else f.error_message
                    }
                    for f in failures[:config.max_failures_displayed]
                ]
                
            content = json.dumps({
                "section": "failures",
                "grouped_failures": failure_data
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.FAILURES,
            title="Test Failures Overview",
            content=content,
            metadata={"total_groups": len(rca_report.grouped_failures)}
        )
        
    def _generate_root_causes_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate root causes analysis section"""
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🎯 Root Cause Analysis", ConsoleColors.BOLD + ConsoleColors.MAGENTA, config.color_output)
            content_lines = [title]
            
            if rca_report.summary.most_common_root_causes:
                content_lines.append("\nMost Common Root Causes:")
                for cause_type, count in rca_report.summary.most_common_root_causes[:5]:
                    cause_name = ConsoleColors.colorize(cause_type.value.replace('_', ' ').title(), ConsoleColors.WHITE, config.color_output)
                    count_str = ConsoleColors.colorize(f"({count})", ConsoleColors.CYAN, config.color_output)
                    content_lines.append(f"  • {cause_name} {count_str}")
            else:
                content_lines.append("\nNo specific root causes identified.")
                
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 🎯 Root Cause Analysis\n"
            
            if rca_report.summary.most_common_root_causes:
                content += "\n### Most Common Root Causes\n"
                for cause_type, count in rca_report.summary.most_common_root_causes[:5]:
                    cause_name = cause_type.value.replace('_', ' ').title()
                    content += f"- **{cause_name}** ({count} occurrences)\n"
            else:
                content += "\nNo specific root causes identified.\n"
                
        else:  # JSON format
            content = json.dumps({
                "section": "root_causes",
                "most_common_root_causes": [
                    {
                        "cause_type": cause_type.value,
                        "count": count,
                        "cause_name": cause_type.value.replace('_', ' ').title()
                    }
                    for cause_type, count in rca_report.summary.most_common_root_causes
                ]
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.ROOT_CAUSES,
            title="Root Cause Analysis",
            content=content,
            metadata={"root_causes_count": len(rca_report.summary.most_common_root_causes)}
        )
        
    def _generate_fixes_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate systematic fixes section"""
        all_fixes = []
        for result in rca_report.rca_results:
            all_fixes.extend(result.systematic_fixes)
            
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🔧 Systematic Fixes", ConsoleColors.BOLD + ConsoleColors.GREEN, config.color_output)
            content_lines = [title]
            
            if all_fixes:
                content_lines.append(f"\nAvailable Fixes ({len(all_fixes)}):")
                for i, fix in enumerate(all_fixes[:5], 1):
                    fix_title = ConsoleColors.colorize(f"{i}. {fix.fix_description}", ConsoleColors.WHITE, config.color_output)
                    content_lines.append(f"\n{fix_title}")
                    content_lines.append(f"   Root Cause: {fix.root_cause.cause_type.value}")
                    content_lines.append(f"   Estimated Time: {fix.estimated_time_minutes} minutes")
                    
                    if config.verbose_mode and fix.implementation_steps:
                        content_lines.append("   Steps:")
                        for step in fix.implementation_steps[:3]:
                            content_lines.append(f"     • {step}")
                            
                if len(all_fixes) > 5:
                    content_lines.append(f"\n... and {len(all_fixes) - 5} more fixes available")
            else:
                content_lines.append("\nNo systematic fixes generated.")
                
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 🔧 Systematic Fixes\n"
            
            if all_fixes:
                content += f"\n### Available Fixes ({len(all_fixes)})\n"
                for i, fix in enumerate(all_fixes[:5], 1):
                    content += f"\n{i}. **{fix.fix_description}**\n"
                    content += f"   - Root Cause: {fix.root_cause.cause_type.value}\n"
                    content += f"   - Estimated Time: {fix.estimated_time_minutes} minutes\n"
                    
                    if fix.implementation_steps:
                        content += "   - Implementation Steps:\n"
                        for step in fix.implementation_steps[:3]:
                            content += f"     - {step}\n"
                            
                if len(all_fixes) > 5:
                    content += f"\n... and {len(all_fixes) - 5} more fixes available\n"
            else:
                content += "\nNo systematic fixes generated.\n"
                
        else:  # JSON format
            fixes_data = [
                {
                    "fix_id": fix.fix_id,
                    "description": fix.fix_description,
                    "root_cause_type": fix.root_cause.cause_type.value,
                    "estimated_time_minutes": fix.estimated_time_minutes,
                    "implementation_steps": fix.implementation_steps,
                    "validation_criteria": fix.validation_criteria
                }
                for fix in all_fixes
            ]
            
            content = json.dumps({
                "section": "systematic_fixes",
                "total_fixes": len(all_fixes),
                "fixes": fixes_data
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.SYSTEMATIC_FIXES,
            title="Systematic Fixes",
            content=content,
            metadata={"total_fixes": len(all_fixes)}
        )
        
    def _generate_recommendations_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate actionable recommendations section"""
        recommendations = rca_report.recommendations[:config.max_recommendations]
        
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("💡 Actionable Recommendations", ConsoleColors.BOLD + ConsoleColors.BLUE, config.color_output)
            content_lines = [title]
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    rec_text = ConsoleColors.colorize(f"{i}. {rec}", ConsoleColors.WHITE, config.color_output)
                    content_lines.append(f"\n{rec_text}")
            else:
                content_lines.append("\nNo specific recommendations available.")
                
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 💡 Actionable Recommendations\n"
            
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    content += f"{i}. {rec}\n"
            else:
                content += "\nNo specific recommendations available.\n"
                
        else:  # JSON format
            content = json.dumps({
                "section": "recommendations",
                "recommendations": recommendations
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.RECOMMENDATIONS,
            title="Actionable Recommendations",
            content=content,
            metadata={"recommendations_count": len(recommendations)}
        )
        
    def _generate_patterns_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate prevention patterns section"""
        patterns = rca_report.prevention_patterns
        
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🛡️  Prevention Patterns", ConsoleColors.BOLD + ConsoleColors.CYAN, config.color_output)
            content_lines = [title]
            
            if patterns:
                content_lines.append(f"\nFound {len(patterns)} prevention patterns:")
                for pattern in patterns[:3]:
                    pattern_name = ConsoleColors.colorize(pattern.pattern_name, ConsoleColors.WHITE, config.color_output)
                    content_lines.append(f"\n• {pattern_name}")
                    if pattern.prevention_steps:
                        content_lines.append("  Prevention Steps:")
                        for step in pattern.prevention_steps[:2]:
                            content_lines.append(f"    - {step}")
                            
                if len(patterns) > 3:
                    content_lines.append(f"\n... and {len(patterns) - 3} more patterns")
            else:
                content_lines.append("\nNo prevention patterns identified.")
                
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 🛡️ Prevention Patterns\n"
            
            if patterns:
                content += f"\nFound {len(patterns)} prevention patterns:\n"
                for pattern in patterns[:3]:
                    content += f"\n### {pattern.pattern_name}\n"
                    if pattern.prevention_steps:
                        content += "Prevention Steps:\n"
                        for step in pattern.prevention_steps:
                            content += f"- {step}\n"
                            
                if len(patterns) > 3:
                    content += f"\n... and {len(patterns) - 3} more patterns\n"
            else:
                content += "\nNo prevention patterns identified.\n"
                
        else:  # JSON format
            patterns_data = [
                {
                    "pattern_id": p.pattern_id,
                    "pattern_name": p.pattern_name,
                    "prevention_steps": p.prevention_steps,
                    "detection_criteria": p.detection_criteria
                }
                for p in patterns
            ]
            
            content = json.dumps({
                "section": "prevention_patterns",
                "total_patterns": len(patterns),
                "patterns": patterns_data
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.PREVENTION_PATTERNS,
            title="Prevention Patterns",
            content=content,
            metadata={"patterns_count": len(patterns)}
        )
        
    def _generate_next_steps_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate next steps section"""
        next_steps = rca_report.next_steps
        
        if config.format == ReportFormat.CONSOLE:
            title = ConsoleColors.colorize("🚀 Next Steps", ConsoleColors.BOLD + ConsoleColors.GREEN, config.color_output)
            content_lines = [title]
            
            if next_steps:
                for i, step in enumerate(next_steps, 1):
                    step_text = ConsoleColors.colorize(f"{i}. {step}", ConsoleColors.WHITE, config.color_output)
                    content_lines.append(f"\n{step_text}")
            else:
                content_lines.append("\nNo specific next steps identified.")
                
            content = "\n".join(content_lines)
            
        elif config.format == ReportFormat.MARKDOWN:
            content = "## 🚀 Next Steps\n"
            
            if next_steps:
                for i, step in enumerate(next_steps, 1):
                    content += f"{i}. {step}\n"
            else:
                content += "\nNo specific next steps identified.\n"
                
        else:  # JSON format
            content = json.dumps({
                "section": "next_steps",
                "next_steps": next_steps
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.NEXT_STEPS,
            title="Next Steps",
            content=content,
            metadata={"steps_count": len(next_steps)}
        )
        
    def _generate_footer_section(self, rca_report: TestRCAReportData, config: ReportConfiguration) -> FormattedReportSection:
        """Generate report footer section"""
        if config.format == ReportFormat.CONSOLE:
            separator = ConsoleColors.colorize("=" * 60, ConsoleColors.CYAN, config.color_output)
            footer_text = ConsoleColors.colorize("Beast Mode RCA Analysis Complete", ConsoleColors.BOLD, config.color_output)
            confidence = f"Overall Confidence: {rca_report.summary.confidence_score:.1%}"
            
            content = f"{separator}\n{footer_text}\n{confidence}\n{separator}"
            
        elif config.format == ReportFormat.MARKDOWN:
            content = f"---\n\n**Beast Mode RCA Analysis Complete**  \nOverall Confidence: {rca_report.summary.confidence_score:.1%}\n"
            
        else:  # JSON format
            content = json.dumps({
                "section": "footer",
                "analysis_complete": True,
                "overall_confidence": rca_report.summary.confidence_score,
                "timestamp": datetime.now().isoformat()
            }, indent=2)
            
        return FormattedReportSection(
            section_type=ReportSection.FOOTER,
            title="Report Footer",
            content=content,
            metadata={"confidence": rca_report.summary.confidence_score}
        )
        
    def _save_report_to_file(self, report: FormattedReport, output_file: str) -> None:
        """Save formatted report to file"""
        try:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Combine all sections
            full_content = []
            for section in report.sections:
                full_content.append(section.content)
                
            content = "\n\n".join(full_content)
            
            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info(f"Report saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save report to {output_file}: {e}")


# Type aliases for external use
TestRCAReport = TestRCAReportData
TestRCASummary = TestRCASummaryData