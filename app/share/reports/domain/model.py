from pydantic import BaseModel


class ReportConfig(BaseModel):
    """Configuration for PDF report generation"""
    title: str
    author: str | None = None
    subject: str | None = None
    page_size: str = "A4"  # A4, Letter, etc.
    orientation: str = "P"  # P=Portrait, L=Landscape
    margin_left: int = 15  # mm
    margin_top: int = 15  # mm
    margin_right: int = 15  # mm


class ReportSection(BaseModel):
    """A section in the report"""
    title: str
    content: str | None = None
    level: int = 1  # Heading level (1, 2, 3)


class TableData(BaseModel):
    """Data for table generation"""
    headers: list[str]
    rows: list[list[str]]
    col_widths: list[int] | None = None  # Column widths in mm
