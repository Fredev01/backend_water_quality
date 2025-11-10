"""Abstract interface for analysis chart generation"""

from abc import ABC, abstractmethod
from io import BytesIO

from app.features.analysis.domain.chart_model import (
    ChartConfig,
    LineChartData,
    HeatmapData,
    BarChartData
)


class AnalysisChartGenerator(ABC):
    """
    Abstract interface for generating charts from analysis data.
    
    This interface defines the contract for creating visual representations
    of water quality analysis results. Implementations should generate charts
    in memory without disk I/O and return them as BytesIO objects in PNG format.
    """
    
    @abstractmethod
    def generate_line_chart(
        self,
        data: LineChartData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a line chart for analysis trends over time.
        
        Line charts are used to visualize how water quality parameters
        (pH, temperature, turbidity, etc.) change over time or across
        different measurement points. Multiple series can be plotted
        on the same chart for comparison.
        
        Args:
            data: Line chart data containing x-axis values and one or more
                  data series. Each series represents a different parameter
                  or measurement type.
            config: Chart configuration including dimensions, DPI, title,
                   and axis labels.
        
        Returns:
            BytesIO: Chart image in PNG format, ready to be embedded in
                    a PDF document or served as a response. The BytesIO
                    object's position is reset to the beginning.
        
        Raises:
            ValueError: If data is invalid or incompatible with chart type
            RuntimeError: If chart generation fails due to rendering issues
        
        Example:
            >>> data = LineChartData(
            ...     x_values=["2024-01-01", "2024-01-02", "2024-01-03"],
            ...     series={
            ...         "pH": [7.2, 7.3, 7.1],
            ...         "Temperature": [25.1, 25.3, 25.2]
            ...     }
            ... )
            >>> config = ChartConfig(
            ...     chart_type=ChartType.LINE,
            ...     title="Water Quality Trends",
            ...     x_label="Date",
            ...     y_label="Value"
            ... )
            >>> chart_image = generator.generate_line_chart(data, config)
        """
        pass
    
    @abstractmethod
    def generate_heatmap(
        self,
        data: HeatmapData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a heatmap for analysis comparisons and correlations.
        
        Heatmaps are used to visualize relationships between different
        water quality parameters or to show patterns across time and
        measurement points. Color intensity represents the magnitude
        of values or correlation strength.
        
        Args:
            data: Heatmap data containing a 2D array of values and labels
                  for both axes. Typically used for correlation matrices
                  or time-series comparisons.
            config: Chart configuration including dimensions, DPI, title,
                   and axis labels.
        
        Returns:
            BytesIO: Heatmap image in PNG format, ready to be embedded in
                    a PDF document or served as a response. The BytesIO
                    object's position is reset to the beginning.
        
        Raises:
            ValueError: If data is invalid or incompatible with chart type
            RuntimeError: If chart generation fails due to rendering issues
        
        Example:
            >>> data = HeatmapData(
            ...     data=[[1.0, 0.8, 0.3], [0.8, 1.0, 0.5], [0.3, 0.5, 1.0]],
            ...     x_labels=["pH", "Temperature", "Turbidity"],
            ...     y_labels=["pH", "Temperature", "Turbidity"]
            ... )
            >>> config = ChartConfig(
            ...     chart_type=ChartType.HEATMAP,
            ...     title="Parameter Correlation Matrix",
            ...     x_label="Parameters",
            ...     y_label="Parameters"
            ... )
            >>> heatmap_image = generator.generate_heatmap(data, config)
        """
        pass
    
    @abstractmethod
    def generate_bar_chart(
        self,
        data: BarChartData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a bar chart for comparing values across categories.
        
        Bar charts are used to compare different metrics (min, avg, max)
        for water quality parameters or to show comparisons between
        different sensors or time periods.
        
        Args:
            data: Bar chart data containing categories and one or more
                  data series. Each series represents a different metric.
            config: Chart configuration including dimensions, DPI, title,
                   and axis labels.
        
        Returns:
            BytesIO: Chart image in PNG format, ready to be embedded in
                    a PDF document. The BytesIO object's position is
                    reset to the beginning.
        
        Raises:
            ValueError: If data is invalid or incompatible with chart type
            RuntimeError: If chart generation fails due to rendering issues
        """
        pass
