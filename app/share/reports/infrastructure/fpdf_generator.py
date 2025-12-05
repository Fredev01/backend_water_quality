from io import BytesIO
from fpdf import FPDF

from app.share.reports.domain.model import (
    ReportConfig,
    ReportSection,
    TableData
)
from app.share.reports.domain.repository import PDFReportGenerator


class FPDF2ReportGenerator(PDFReportGenerator):
    """
    FPDF2-based implementation of PDFReportGenerator.
    Provides generic PDF generation capabilities reusable across all features.
    """
    
    def __init__(self):
        self.pdf: FPDF | None = None
        self.config: ReportConfig | None = None
    
    def initialize(self, config: ReportConfig) -> None:
        """
        Initialize a new PDF document
        
        Args:
            config: Report configuration
        """
        self.config = config
        self.pdf = FPDF(
            orientation=config.orientation,
            unit='mm',
            format=config.page_size
        )
        
        # Set margins
        self.pdf.set_margins(
            left=config.margin_left,
            top=config.margin_top,
            right=config.margin_right
        )
        
        # Set auto page break
        self.pdf.set_auto_page_break(auto=True, margin=15)
        
        # Add first page
        self.pdf.add_page()
        
        # Use built-in fonts with UTF-8 support
        self.pdf.set_font('Helvetica', '', 12)
        
        # Set document metadata
        if config.title:
            self.pdf.set_title(config.title)
        if config.author:
            self.pdf.set_author(config.author)
        if config.subject:
            self.pdf.set_subject(config.subject)
    
    def add_header(self, title: str, subtitle: str | None = None) -> None:
        """
        Add header section to the report
        
        Args:
            title: Main title
            subtitle: Optional subtitle
        """
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        # Main title
        self.pdf.set_font('Helvetica', 'B', 20)
        self.pdf.cell(0, 10, title, ln=True, align='C')
        self.pdf.ln(5)
        
        # Subtitle if provided
        if subtitle:
            self.pdf.set_font('Helvetica', '', 12)
            self.pdf.cell(0, 8, subtitle, ln=True, align='C')
            self.pdf.ln(5)
        
        # Reset font
        self.pdf.set_font('Helvetica', '', 12)
    
    def add_section(self, section: ReportSection) -> None:
        """
        Add a text section to the report
        
        Args:
            section: Section data
        """
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        # Determine font size based on heading level
        font_sizes = {1: 16, 2: 14, 3: 12}
        font_size = font_sizes.get(section.level, 12)
        
        # Add section title
        self.pdf.set_font('Helvetica', 'B', font_size)
        self.pdf.ln(3)  # Reduced from 5
        self.pdf.cell(0, 6, section.title, ln=True)  # Reduced from 8
        self.pdf.ln(1)  # Reduced from 2
        
        # Add section content if provided
        if section.content:
            self.pdf.set_font('Helvetica', '', 11)
            self.pdf.multi_cell(0, 5, section.content)  # Reduced from 6
            self.pdf.ln(2)  # Reduced from 3
        
        # Reset font
        self.pdf.set_font('Helvetica', '', 12)
    
    def add_table(self, table: TableData) -> None:
        """
        Add a table to the report
        
        Args:
            table: Table data with headers and rows
        """
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        # Calculate column widths
        if table.col_widths:
            col_widths = table.col_widths
        else:
            # Auto-calculate equal widths
            available_width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin
            col_widths = [available_width / len(table.headers)] * len(table.headers)
        
        # Add table headers
        self.pdf.set_font('Helvetica', 'B', 11)
        self.pdf.set_fill_color(200, 220, 255)
        
        for i, header in enumerate(table.headers):
            self.pdf.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
        self.pdf.ln()
        
        # Add table rows
        self.pdf.set_font('Helvetica', '', 10)
        for row in table.rows:
            # Check if we need a new page
            if self.pdf.get_y() > self.pdf.h - 30:
                self.pdf.add_page()
                # Re-add headers on new page
                self.pdf.set_font('Helvetica', 'B', 11)
                self.pdf.set_fill_color(200, 220, 255)
                for i, header in enumerate(table.headers):
                    self.pdf.cell(col_widths[i], 8, header, border=1, align='C', fill=True)
                self.pdf.ln()
                self.pdf.set_font('Helvetica', '', 10)
            
            for i, cell in enumerate(row):
                self.pdf.cell(col_widths[i], 7, str(cell), border=1, align='C')
            self.pdf.ln()
        
        self.pdf.ln(5)
        # Reset font
        self.pdf.set_font('Helvetica', '', 12)
    
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
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        # Calculate width if not provided
        if width is None:
            width = self.pdf.w - self.pdf.l_margin - self.pdf.r_margin - 20
        
        # Check if we need a new page
        if self.pdf.get_y() > self.pdf.h - 100:
            self.pdf.add_page()
        
        # Ensure the buffer is at the start
        chart_image.seek(0)
        
        # Add image from BytesIO
        self.pdf.image(chart_image, x=None, y=None, w=width)
        self.pdf.ln(2)  # Reduced from 5
        
        # Add caption if provided
        if caption:
            self.pdf.set_font('Helvetica', '', 9)  # Reduced from 10
            self.pdf.cell(0, 4, caption, ln=True, align='C')  # Reduced from 6
            self.pdf.ln(2)  # Reduced from 5
        
        # Reset font
        self.pdf.set_font('Helvetica', '', 12)
    
    def add_page_break(self) -> None:
        """Add a page break"""
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        self.pdf.add_page()
    
    def generate(self) -> BytesIO:
        """
        Generate the final PDF
        
        Returns:
            BytesIO: Complete PDF document in memory
        """
        if not self.pdf:
            raise RuntimeError("PDF not initialized. Call initialize() first.")
        
        # Generate PDF to BytesIO
        pdf_output = BytesIO()
        pdf_bytes = self.pdf.output()
        pdf_output.write(pdf_bytes)
        pdf_output.seek(0)
        
        return pdf_output
