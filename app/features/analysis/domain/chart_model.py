"""Domain models for analysis chart generation"""

from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ChartType(str, Enum):
    """Types of charts supported for analysis visualization"""
    LINE = "line"
    HEATMAP = "heatmap"
    BAR = "bar"


class ChartConfig(BaseModel):
    """Configuration for chart generation"""
    chart_type: ChartType
    title: str
    width: int = Field(default=180, ge=50, le=300)  # mm for PDF, validated range
    height: int = Field(default=100, ge=50, le=300)  # mm for PDF, validated range
    dpi: int = Field(default=150, ge=72, le=300)  # DPI for image quality, validated range
    x_label: str | None = None
    y_label: str | None = None
    period_type: str | None = None  # For date formatting: 'days', 'months', 'years'

    @field_validator('width', 'height')
    @classmethod
    def validate_dimensions(cls, v: int) -> int:
        """Validate chart dimensions are within reasonable bounds"""
        if v < 50:
            raise ValueError("Chart dimension must be at least 50mm")
        if v > 300:
            raise ValueError("Chart dimension must not exceed 300mm")
        return v

    @field_validator('dpi')
    @classmethod
    def validate_dpi(cls, v: int) -> int:
        """Validate DPI is within reasonable bounds for quality and performance"""
        if v < 72:
            raise ValueError("DPI must be at least 72 for readable output")
        if v > 300:
            raise ValueError("DPI must not exceed 300 to avoid excessive memory usage")
        return v


class LineChartData(BaseModel):
    """Data for line chart visualization"""
    x_values: list[str]  # Timestamps or labels for x-axis
    series: dict[str, list[float | None]]  # series_name -> values mapping (None for gaps)

    @field_validator('series')
    @classmethod
    def validate_series_length(cls, v: dict[str, list[float | None]], info) -> dict[str, list[float | None]]:
        """Validate all series have the same length as x_values"""
        if not v:
            raise ValueError("At least one series is required")
        
        # Get x_values length from the validation context
        x_values = info.data.get('x_values', [])
        x_len = len(x_values)
        
        for series_name, values in v.items():
            if len(values) != x_len:
                raise ValueError(
                    f"Series '{series_name}' length ({len(values)}) "
                    f"must match x_values length ({x_len})"
                )
        
        return v


class BarChartData(BaseModel):
    """Data for bar chart visualization"""
    categories: list[str]  # Categories for x-axis (e.g., sensor names)
    series: dict[str, list[float]]  # series_name -> values mapping (e.g., "min", "avg", "max")

    @field_validator('series')
    @classmethod
    def validate_series_length(cls, v: dict[str, list[float]], info) -> dict[str, list[float]]:
        """Validate all series have the same length as categories"""
        if not v:
            raise ValueError("At least one series is required")
        
        # Get categories length from the validation context
        categories = info.data.get('categories', [])
        cat_len = len(categories)
        
        for series_name, values in v.items():
            if len(values) != cat_len:
                raise ValueError(
                    f"Series '{series_name}' length ({len(values)}) "
                    f"must match categories length ({cat_len})"
                )
        
        return v


class HeatmapData(BaseModel):
    """Data for heatmap visualization"""
    data: list[list[float]]  # 2D array of values
    x_labels: list[str]  # Labels for x-axis (columns)
    y_labels: list[str]  # Labels for y-axis (rows)

    @field_validator('data')
    @classmethod
    def validate_data_shape(cls, v: list[list[float]], info) -> list[list[float]]:
        """Validate data is a proper 2D array with consistent dimensions"""
        if not v:
            raise ValueError("Heatmap data cannot be empty")
        
        # Check all rows have the same length
        row_length = len(v[0])
        for i, row in enumerate(v):
            if len(row) != row_length:
                raise ValueError(
                    f"All rows must have the same length. "
                    f"Row 0 has {row_length} elements, but row {i} has {len(row)}"
                )
        
        # Validate dimensions match labels if available
        x_labels = info.data.get('x_labels', [])
        y_labels = info.data.get('y_labels', [])
        
        if x_labels and len(x_labels) != row_length:
            raise ValueError(
                f"Number of x_labels ({len(x_labels)}) "
                f"must match number of columns ({row_length})"
            )
        
        if y_labels and len(y_labels) != len(v):
            raise ValueError(
                f"Number of y_labels ({len(y_labels)}) "
                f"must match number of rows ({len(v)})"
            )
        
        return v
