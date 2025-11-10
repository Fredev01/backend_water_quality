from abc import ABC, abstractmethod
from io import BytesIO

from app.share.reports.domain.model import (
    ReportConfig,
    ReportSection,
    TableData
)


class PDFReportGenerator(ABC):
    """
    Abstract interface for PDF report generation.
    This is the base that all features will use.
    """
    
    @abstractmethod
    def initialize(self, config: ReportConfig) -> None:
        """
        Initialize a new PDF document
        
        Args:
            config: Report configuration
        """
        pass
    
    @abstractmethod
    def add_header(self, title: str, subtitle: str | None = None) -> None:
        """
        Add header section to the report
        
        Args:
            title: Main title
            subtitle: Optional subtitle
        """
        pass
    
    @abstractmethod
    def add_section(self, section: ReportSection) -> None:
        """
        Add a text section to the report
        
        Args:
            section: Section data
        """
        pass
    
    @abstractmethod
    def add_table(self, table: TableData) -> None:
        """
        Add a table to the report
        
        Args:
            table: Table data with headers and rows
        """
        pass
    
    @abstractmethod
    def add_chart(
        self,
        chart_image: BytesIO,
        caption: str | None = None,
        width: int | None = None
    ) -> None:
        """
        Add a chart image to the report
        
        Args:
            chart_image: Chart as BytesIO (PNG format)
            caption: Optional caption for the chart
            width: Optional width in mm (auto-calculated if None)
        """
        pass
    
    @abstractmethod
    def add_page_break(self) -> None:
        """Add a page break"""
        pass
    
    @abstractmethod
    def generate(self) -> BytesIO:
        """
        Generate the final PDF
        
        Returns:
            BytesIO: Complete PDF document in memory
        """
        pass
