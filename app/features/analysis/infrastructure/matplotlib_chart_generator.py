"""Matplotlib implementation of analysis chart generator"""

from io import BytesIO
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime

from app.features.analysis.domain.chart_repository import AnalysisChartGenerator
from app.features.analysis.domain.chart_model import (
    ChartConfig,
    LineChartData,
    HeatmapData,
    BarChartData
)

# Use non-interactive backend to avoid GUI dependencies
matplotlib.use('Agg')


class MatplotlibAnalysisChartGenerator(AnalysisChartGenerator):
    """
    Matplotlib-based implementation of AnalysisChartGenerator.
    
    Generates charts in memory without disk I/O using matplotlib.
    Uses colorblind-friendly palettes and ensures readability in grayscale.
    """
    
    # Colorblind-friendly color palette (Wong 2011)
    COLORBLIND_COLORS = [
        '#0173B2',  # Blue
        '#DE8F05',  # Orange
        '#029E73',  # Green
        '#CC78BC',  # Purple
        '#CA9161',  # Brown
        '#949494',  # Gray
        '#ECE133',  # Yellow
        '#56B4E9',  # Sky blue
    ]
    
    def __init__(self):
        """Initialize the chart generator with default settings"""
        # Set default style for all charts
        plt.style.use('seaborn-v0_8-darkgrid')
    
    def generate_line_chart(
        self,
        data: LineChartData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a line chart for analysis trends.
        
        Creates a line chart with multiple series support, legend, grid,
        and proper formatting for time-based or categorical data.
        """
        try:
            # Convert mm to inches for matplotlib (1 inch = 25.4 mm)
            width_inches = config.width / 25.4
            height_inches = config.height / 25.4
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=config.dpi)
            
            # Parse x-values to check if they're dates
            parsed_x_values = self._parse_x_values(data.x_values)
            is_datetime = isinstance(parsed_x_values[0], datetime) if parsed_x_values else False
            
            # Use numeric indices for plotting to maintain proper spacing
            x_indices = np.arange(len(data.x_values))
            
            # Plot each series with colorblind-friendly colors
            # Handle None values by converting to np.nan for broken lines
            for idx, (series_name, values) in enumerate(data.series.items()):
                color = self.COLORBLIND_COLORS[idx % len(self.COLORBLIND_COLORS)]
                
                # Convert None to np.nan for matplotlib to handle gaps
                clean_values = [v if v is not None else np.nan for v in values]
                
                ax.plot(
                    x_indices,
                    clean_values,
                    marker='o',
                    label=series_name,
                    color=color,
                    linewidth=2,
                    markersize=4
                )
            
            # Set title and labels
            ax.set_title(config.title, fontsize=12, fontweight='bold', pad=15)
            if config.x_label:
                ax.set_xlabel(config.x_label, fontsize=10)
            if config.y_label:
                ax.set_ylabel(config.y_label, fontsize=10)
            
            # Format x-axis labels
            if is_datetime:
                # Custom date formatting based on period_type
                labels = self._format_date_labels(parsed_x_values, config.period_type)
                
                # Determine how many labels to show based on data size
                num_labels = len(labels)
                if num_labels <= 15:
                    # Show all labels if 15 or fewer
                    tick_positions = list(range(num_labels))
                else:
                    # Show ~10-12 labels for larger datasets
                    step = max(1, num_labels // 10)
                    tick_positions = list(range(0, num_labels, step))
                    # Always include the last position
                    if (num_labels - 1) not in tick_positions:
                        tick_positions.append(num_labels - 1)
                
                ax.set_xticks(tick_positions)
                ax.set_xticklabels([labels[i] for i in tick_positions], rotation=45, ha='right', fontsize=8)
            else:
                # For non-date values, show subset of labels
                step = max(1, len(data.x_values) // 10)
                tick_positions = list(range(0, len(data.x_values), step))
                if len(data.x_values) - 1 not in tick_positions:
                    tick_positions.append(len(data.x_values) - 1)
                
                ax.set_xticks(tick_positions)
                ax.set_xticklabels([data.x_values[i] for i in tick_positions], rotation=45, ha='right', fontsize=8)
            
            # Add grid for readability
            ax.grid(True, alpha=0.3, linestyle='--')
            
            # Add legend
            ax.legend(loc='best', framealpha=0.9, fontsize=9)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save to BytesIO
            buffer = BytesIO()
            fig.savefig(
                buffer,
                format='png',
                dpi=config.dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            # Clean up to free memory BEFORE seeking
            plt.close(fig)
            
            # Seek to start after closing figure
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            # Make sure to close figure on error too
            try:
                plt.close(fig)
            except:
                pass
            raise RuntimeError(f"Failed to generate line chart: {str(e)}") from e
    
    def generate_heatmap(
        self,
        data: HeatmapData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a heatmap for analysis comparisons.
        
        Creates a heatmap with color bar, axis labels, and optional
        annotations showing the actual values.
        """
        try:
            # Convert mm to inches for matplotlib
            width_inches = config.width / 25.4
            height_inches = config.height / 25.4
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=config.dpi)
            
            # Convert data to numpy array for easier manipulation
            data_array = np.array(data.data)
            
            # Create heatmap using colorblind-friendly colormap
            # 'viridis' is perceptually uniform and colorblind-friendly
            im = ax.imshow(
                data_array,
                cmap='viridis',
                aspect='auto',
                interpolation='nearest'
            )
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax)
            cbar.ax.tick_params(labelsize=8)
            
            # Set ticks and labels
            ax.set_xticks(np.arange(len(data.x_labels)))
            ax.set_yticks(np.arange(len(data.y_labels)))
            ax.set_xticklabels(data.x_labels, fontsize=9)
            ax.set_yticklabels(data.y_labels, fontsize=9)
            
            # Rotate x-axis labels for better readability
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
            
            # Set title and labels
            ax.set_title(config.title, fontsize=12, fontweight='bold', pad=15)
            if config.x_label:
                ax.set_xlabel(config.x_label, fontsize=10)
            if config.y_label:
                ax.set_ylabel(config.y_label, fontsize=10)
            
            # Add text annotations for values
            # Only annotate if the heatmap is not too large (to avoid clutter)
            if len(data.y_labels) <= 10 and len(data.x_labels) <= 10:
                for i in range(len(data.y_labels)):
                    for j in range(len(data.x_labels)):
                        value = data_array[i, j]
                        # Choose text color based on background intensity
                        text_color = 'white' if value < (data_array.max() + data_array.min()) / 2 else 'black'
                        ax.text(
                            j, i, f'{value:.2f}',
                            ha='center', va='center',
                            color=text_color,
                            fontsize=8
                        )
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save to BytesIO
            buffer = BytesIO()
            fig.savefig(
                buffer,
                format='png',
                dpi=config.dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            # Clean up to free memory BEFORE seeking
            plt.close(fig)
            
            # Seek to start after closing figure
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            # Make sure to close figure on error too
            try:
                plt.close(fig)
            except:
                pass
            raise RuntimeError(f"Failed to generate heatmap: {str(e)}") from e
    
    def generate_bar_chart(
        self,
        data: BarChartData,
        config: ChartConfig
    ) -> BytesIO:
        """
        Generate a bar chart for comparing values across categories.
        
        Creates grouped bar charts with multiple series support.
        """
        try:
            # Convert mm to inches for matplotlib
            width_inches = config.width / 25.4
            height_inches = config.height / 25.4
            
            # Create figure and axis
            fig, ax = plt.subplots(figsize=(width_inches, height_inches), dpi=config.dpi)
            
            # Prepare data for grouped bars
            categories = data.categories
            series_names = list(data.series.keys())
            n_categories = len(categories)
            n_series = len(series_names)
            
            # Calculate bar positions
            bar_width = 0.8 / n_series  # Total width of 0.8 divided by number of series
            x_positions = np.arange(n_categories)
            
            # Plot each series
            for idx, series_name in enumerate(series_names):
                values = data.series[series_name]
                color = self.COLORBLIND_COLORS[idx % len(self.COLORBLIND_COLORS)]
                offset = (idx - n_series / 2 + 0.5) * bar_width
                
                ax.bar(
                    x_positions + offset,
                    values,
                    bar_width,
                    label=series_name,
                    color=color,
                    alpha=0.8
                )
            
            # Set title and labels
            ax.set_title(config.title, fontsize=12, fontweight='bold', pad=15)
            if config.x_label:
                ax.set_xlabel(config.x_label, fontsize=10)
            if config.y_label:
                ax.set_ylabel(config.y_label, fontsize=10)
            
            # Set x-axis ticks and labels
            ax.set_xticks(x_positions)
            ax.set_xticklabels(categories, rotation=45, ha='right')
            
            # Add grid for readability
            ax.grid(True, alpha=0.3, linestyle='--', axis='y')
            
            # Add legend
            ax.legend(loc='best', framealpha=0.9, fontsize=9)
            
            # Adjust layout to prevent label cutoff
            plt.tight_layout()
            
            # Save to BytesIO
            buffer = BytesIO()
            fig.savefig(
                buffer,
                format='png',
                dpi=config.dpi,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none'
            )
            
            # Clean up to free memory BEFORE seeking
            plt.close(fig)
            
            # Seek to start after closing figure
            buffer.seek(0)
            
            return buffer
            
        except Exception as e:
            # Make sure to close figure on error too
            try:
                plt.close(fig)
            except:
                pass
            raise RuntimeError(f"Failed to generate bar chart: {str(e)}") from e
    
    def _format_date_labels(self, dates: list[datetime], period_type: str | None = None) -> list[str]:
        """
        Format date labels intelligently based on period type:
        - days: First and last with DD/MM/YYYY, middle with DD/MM
        - months: All with MM/YYYY
        - years: All with YYYY
        - None/default: First and last with DD/MM, middle only day (add month if changes)
        
        Args:
            dates: List of datetime objects
            period_type: Type of period ('days', 'months', 'years')
        
        Returns:
            List of formatted date strings
        """
        if not dates:
            return []
        
        if len(dates) == 1:
            if period_type == 'years':
                return [dates[0].strftime('%Y')]
            elif period_type == 'months':
                return [dates[0].strftime('%m/%Y')]
            else:
                return [dates[0].strftime('%d/%m/%Y')]
        
        labels = []
        
        if period_type == 'years':
            # All labels: only year
            labels = [date.strftime('%Y') for date in dates]
        elif period_type == 'months':
            # All labels: month/year
            labels = [date.strftime('%m/%Y') for date in dates]
        elif period_type == 'days':
            # First and last: day/month/year, middle: day/month
            for i, date in enumerate(dates):
                if i == 0 or i == len(dates) - 1:
                    labels.append(date.strftime('%d/%m/%Y'))
                else:
                    labels.append(date.strftime('%d/%m'))
        else:
            # Default: First and last with DD/MM, middle only day (add month if changes)
            prev_month = None
            for i, date in enumerate(dates):
                if i == 0 or i == len(dates) - 1:
                    labels.append(date.strftime('%d/%m'))
                else:
                    if prev_month is not None and date.month != prev_month:
                        labels.append(date.strftime('%d/%m'))
                    else:
                        labels.append(date.strftime('%d'))
                prev_month = date.month
        
        return labels
    
    def _parse_x_values(self, x_values: list[str]) -> list:
        """
        Parse x-axis values, attempting to convert to datetime if possible.
        
        Args:
            x_values: List of string values for x-axis
        
        Returns:
            List of datetime objects if parseable, otherwise original strings
        """
        try:
            # Try to parse as dates
            parsed_dates = []
            for val in x_values:
                # Try common date formats (including ISO format with T separator)
                for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%Y']:
                    try:
                        parsed_dates.append(datetime.strptime(val, fmt))
                        break
                    except ValueError:
                        continue
                else:
                    # If no format worked, return original strings
                    return x_values
            
            return parsed_dates
        
        except Exception:
            # If any error occurs, return original strings
            return x_values
