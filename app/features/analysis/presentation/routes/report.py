"""PDF report generation routes for analysis results"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing_extensions import Annotated

from app.features.analysis.domain.chart_repository import AnalysisChartGenerator
from app.features.analysis.domain.chart_model import (
    ChartConfig,
    ChartType,
    LineChartData,
    HeatmapData,
    BarChartData,
)
from app.features.analysis.domain.repository import AnalysisResultRepository
from app.features.analysis.presentation.depends import (
    get_analysis_chart_generator,
    get_analysis_result,
    get_pdf_generator,
)
from app.share.jwt.domain.payload import UserPayload
from app.share.jwt.infrastructure.verify_access_token import verify_access_token
from app.share.meter_records.domain.enums import SensorType
from app.share.reports.domain.repository import PDFReportGenerator
from app.share.reports.domain.model import ReportConfig, ReportSection, TableData

report_router = APIRouter()


@report_router.get("/{analysis_id}/report/pdf")
async def generate_analysis_pdf_report(
    analysis_id: str,
    user: UserPayload = Depends(verify_access_token),
    analysis_repo: Annotated[
        AnalysisResultRepository,
        Depends(get_analysis_result),
    ] = None,
    chart_gen: Annotated[
        AnalysisChartGenerator,
        Depends(get_analysis_chart_generator),
    ] = None,
    pdf_gen: Annotated[
        PDFReportGenerator,
        Depends(get_pdf_generator),
    ] = None,
) -> StreamingResponse:
    """
    Generate a PDF report for an analysis.

    This endpoint creates a comprehensive PDF report containing:
    - Analysis metadata (ID, type, workspace, meter)
    - Visual charts (line charts for trends, heatmaps for correlations)
    - Data tables with analysis results

    Args:
        analysis_id: ID of the analysis to generate report for
        user: Authenticated user (injected by dependency)
        analysis_repo: Repository for fetching analysis data
        chart_gen: Chart generator for creating visualizations
        pdf_gen: PDF generator for creating the report

    Returns:
        StreamingResponse: PDF file download with appropriate headers

    Raises:
        HTTPException: 404 if analysis not found, 500 for generation errors
    """
    pdf_buffer = None

    try:
        # Fetch analysis data
        analysis_data = analysis_repo.get_analysis_by_id(
            user_id=user.uid,
            analysis_id=analysis_id,
        )

        if not analysis_data:
            raise HTTPException(
                status_code=404,
                detail="Analysis not found",
            )

        # Initialize PDF with configuration
        config = ReportConfig(
            title=f"Reporte de Análisis",
            author=user.username,
            subject="Resultados de Análisis",
        )
        pdf_gen.initialize(config)

        # Add header with title and generation timestamp
        pdf_gen.add_header(
            title="Reporte de Análisis de Calidad del Agua",
            subtitle=f"Generado el {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        )

        # Add analysis metadata section
        analysis_type_translations = {
            "average": "Promedio",
            "average_period": "Promedio por Período",
            "prediction": "Predicción",
            "correlation": "Correlación",
        }

        metadata_content = (
            f"Identificador: {analysis_id}\n"
            f"Tipo: {analysis_type_translations.get(analysis_data.get('type', ''), analysis_data.get('type', 'N/A'))}\n"
            f"Espacio de Trabajo: {analysis_data.get('workspace_name', 'N/A')}\n"
            f"Medidor: {analysis_data.get('meter_name', 'N/A')}\n"
            f"Creado: {analysis_data.get('created_at', 'N/A')}"
        )
        metadata_section = ReportSection(
            title="Información del Análisis",
            content=metadata_content,
            level=1,
        )
        pdf_gen.add_section(metadata_section)

        # Transform analysis data and generate charts/tables based on type
        analysis_type = analysis_data.get("type", "")
        result_data = analysis_data.get("data", {})

        # Generate visualizations and tables based on analysis type
        parameters = analysis_data.get("parameters", {})
        _add_analysis_content(
            pdf_gen=pdf_gen,
            chart_gen=chart_gen,
            analysis_type=analysis_type,
            result_data=result_data,
            parameters=parameters,
        )

        # Generate final PDF
        pdf_buffer = pdf_gen.generate()

        # Read the PDF content before closing the buffer
        pdf_content = pdf_buffer.read()
        pdf_buffer.close()

        # Prepare response with appropriate headers
        analysis_type_names = {
            "average": "promedio",
            "average_period": "promedio_periodo",
            "prediction": "prediccion",
            "correlation": "correlacion",
        }
        type_name = analysis_type_names.get(analysis_data.get("type", ""), "analisis")
        filename = f"reporte_{type_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        # Return the PDF content as bytes wrapped in BytesIO for streaming
        return StreamingResponse(
            iter([pdf_content]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
            },
        )

    except HTTPException:
        # Re-raise HTTP exceptions (404, 403, etc.) without modification
        raise
    except ValueError as ve:
        # Handle validation errors
        print(f"Validation error generating report for analysis {analysis_id}: {ve}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid data for report generation: {str(ve)}",
        )
    except Exception as e:
        # Log unexpected errors with full context
        print(
            f"Error generating report for analysis {analysis_id}: {e.__class__.__name__}: {e}"
        )
        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Error generating report",
        )


def _add_analysis_content(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    analysis_type: str,
    result_data: dict,
    parameters: dict,
) -> None:
    """
    Add analysis-specific content (charts and tables) to the PDF.

    Args:
        pdf_gen: PDF generator instance
        chart_gen: Chart generator instance
        analysis_type: Type of analysis (average, prediction, correlation, etc.)
        result_data: Analysis result data to visualize
        parameters: Analysis parameters (including period_type)
    """
    if not result_data:
        # Add a section indicating no data available
        no_data_section = ReportSection(
            title="Resultados del Análisis",
            content="No hay datos disponibles para este análisis.",
            level=1,
        )
        pdf_gen.add_section(no_data_section)
        return

    # Route to appropriate handler based on analysis type
    if analysis_type == "average":
        _add_average_content(pdf_gen, chart_gen, result_data)
    elif analysis_type == "average_period":
        _add_average_period_content(pdf_gen, chart_gen, result_data)
    elif analysis_type == "prediction":
        _add_prediction_content(pdf_gen, chart_gen, result_data, parameters)
    elif analysis_type == "correlation":
        _add_correlation_content(pdf_gen, chart_gen, result_data)
    else:
        # Generic handler for unknown types
        _add_generic_content(pdf_gen, result_data)


def _add_average_content(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
) -> None:
    """Add content for average analysis type."""
    pdf_gen.add_section(
        ReportSection(
            title="Resultados del Análisis de Promedio", content=None, level=1
        )
    )

    # Extract data - the actual structure has "result" array and "period"
    period = result_data.get("period", {})
    results = result_data.get("result", [])

    # Add period information
    period_content = (
        f"Fecha de Inicio: {period.get('start_date', 'N/A')}\n"
        f"Fecha de Fin: {period.get('end_date', 'N/A')}"
    )
    pdf_gen.add_section(
        ReportSection(title="Período de Análisis", content=period_content, level=2)
    )

    # Add statistics table for all sensors
    if results:
        rows = []
        for sensor_data in results:
            sensor_name = SensorType(sensor_data.get("sensor", "N/A")).spanish()
            average = sensor_data.get("average")
            min_val = sensor_data.get("min")
            max_val = sensor_data.get("max")

            avg_str = f"{average:.2f}" if isinstance(average, (int, float)) else "N/A"
            min_str = f"{min_val:.2f}" if isinstance(min_val, (int, float)) else "N/A"
            max_str = f"{max_val:.2f}" if isinstance(max_val, (int, float)) else "N/A"

            rows.append([sensor_name, avg_str, min_str, max_str])

        table = TableData(
            headers=["Sensor", "Promedio", "Mínimo", "Máximo"],
            rows=rows,
        )
        pdf_gen.add_table(table)

    # Generate bar charts for each sensor (min, avg, max)
    if results:
        for sensor_data in results:
            try:
                sensor_name = SensorType(sensor_data.get("sensor", "N/A")).spanish()
                min_val = sensor_data.get("min", 0)
                avg_val = sensor_data.get("average", 0)
                max_val = sensor_data.get("max", 0)

                # Create bar chart data
                bar_data = BarChartData(
                    categories=[sensor_name.upper()],
                    series={
                        "Mínimo": [min_val if min_val is not None else 0],
                        "Promedio": [avg_val if avg_val is not None else 0],
                        "Máximo": [max_val if max_val is not None else 0],
                    },
                )

                chart_config = ChartConfig(
                    chart_type=ChartType.BAR,
                    title=f"{sensor_name.upper()}",
                    x_label="",
                    y_label="Valor",
                    width=90,
                    height=80,
                )

                chart_image = chart_gen.generate_bar_chart(bar_data, chart_config)
                pdf_gen.add_chart(
                    chart_image, caption=f"Estadísticas de {sensor_name}", width=90
                )
            except Exception as e:
                print(f"Error generating bar chart for {sensor_name}: {e}")


def _add_average_period_content(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
) -> None:
    """Add content for average period analysis type."""
    pdf_gen.add_section(
        ReportSection(
            title="Resultados del Análisis de Promedio por Período",
            content=None,
            level=1,
        )
    )

    # Check if this is a single sensor or all sensors result
    if "sensor" in result_data:
        # Single sensor result
        _add_single_sensor_period(pdf_gen, chart_gen, result_data)
    elif "results" in result_data:
        # All sensors result
        _add_all_sensors_period(pdf_gen, chart_gen, result_data)


def _add_single_sensor_period(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
) -> None:
    """Add content for single sensor average period."""
    sensor = SensorType(result_data.get("sensor", "N/A")).spanish()
    period = result_data.get("period", {})
    period_type = result_data.get("period_type", "N/A")
    averages = result_data.get("averages", [])

    # Add period information
    period_type_translations = {
        "days": "Día",
        "months": "Mes",
        "years": "Año",
    }

    period_content = (
        f"Sensor: {sensor}\n"
        f"Tipo de Período: {period_type_translations.get(period_type, period_type)}\n"
        f"Fecha de Inicio: {period.get('start_date', 'N/A')}\n"
        f"Fecha de Fin: {period.get('end_date', 'N/A')}"
    )
    pdf_gen.add_section(
        ReportSection(title="Período de Análisis", content=period_content, level=2)
    )

    # Generate line chart if we have data (keep None values for gaps)
    if averages:
        try:
            x_values = [str(item.get("date", "")) for item in averages]
            # Keep None values to create gaps in the line
            y_values = [item.get("value") for item in averages]

            line_data = LineChartData(
                x_values=x_values,
                series={sensor: y_values},
            )

            chart_config = ChartConfig(
                chart_type=ChartType.LINE,
                title=f"{sensor.upper()} - Cantidad de valores {len([v for v in y_values if v is not None])}",
                x_label="Fecha",
                y_label="Valor",
                period_type=period_type,
            )

            chart_image = chart_gen.generate_line_chart(line_data, chart_config)
            pdf_gen.add_chart(
                chart_image,
                caption=f"Tendencia de {sensor} por {period_type_translations.get(period_type, period_type)}",
            )
        except Exception as e:
            print(f"Error generating line chart: {e}")

    # Add data table
    if averages:
        rows = []
        for item in averages[:20]:  # Limit to first 20 rows
            date = str(item.get("date", "N/A"))
            value = item.get("value")
            value_str = f"{value:.2f}" if isinstance(value, (int, float)) else "N/A"
            rows.append([date, value_str])

        table = TableData(
            headers=["Fecha", "Valor Promedio"],
            rows=rows,
        )
        pdf_gen.add_table(table)


def _add_all_sensors_period(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
) -> None:
    """Add content for all sensors average period."""
    period = result_data.get("period", {})
    period_type = result_data.get("period_type", "N/A")
    results = result_data.get("results", {})

    # Add period information
    period_type_translations = {
        "days": "Día",
        "months": "Mes",
        "years": "Año",
    }

    period_content = (
        f"Tipo de Período: {period_type_translations.get(period_type, period_type)}\n"
        f"Fecha de Inicio: {period.get('start_date', 'N/A')}\n"
        f"Fecha de Fin: {period.get('end_date', 'N/A')}"
    )
    pdf_gen.add_section(
        ReportSection(title="Período de Análisis", content=period_content, level=2)
    )

    # Generate individual line chart for each sensor
    if results:
        for sensor_type, sensor_data in results.items():
            try:
                sensor_name = SensorType(sensor_type).spanish()
                labels = sensor_data.get("labels", [])
                values = sensor_data.get("values", [])

                if not labels or not values:
                    continue

                x_values = [str(label) for label in labels]
                # Keep None values to create gaps in the line

                # Count non-null values
                non_null_count = len([v for v in values if v is not None])

                line_data = LineChartData(
                    x_values=x_values,
                    series={sensor_name: values},
                )

                chart_config = ChartConfig(
                    chart_type=ChartType.LINE,
                    title=f"{sensor_name.upper()} - Cantidad de valores {non_null_count}",
                    x_label="Fecha",
                    y_label="Valor",
                    period_type=period_type,
                )

                chart_image = chart_gen.generate_line_chart(line_data, chart_config)
                pdf_gen.add_chart(
                    chart_image,
                    caption=f"Tendencia de {sensor_name} por {period_type_translations.get(period_type, period_type)}",
                )
            except Exception as e:
                print(f"Error generating line chart for {sensor_type}: {e}")


def _add_prediction_content(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
    parameters: dict,
) -> None:
    """Add content for prediction analysis type."""
    pdf_gen.add_section(
        ReportSection(
            title="Resultados del Análisis de Predicción", content=None, level=1
        )
    )

    # Check if this is a single sensor or all sensors result
    if "sensor" in result_data:
        # Single sensor prediction
        _add_single_sensor_prediction(pdf_gen, chart_gen, result_data, parameters)
    elif "data" in result_data and "pred" in result_data:
        # All sensors prediction
        _add_all_sensors_prediction(pdf_gen, chart_gen, result_data, parameters)


def _add_single_sensor_prediction(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
    parameters: dict,
) -> None:
    """Add content for single sensor prediction."""
    sensor = SensorType(result_data.get("sensor", "N/A")).spanish()
    data = result_data.get("data", {})
    pred = result_data.get("pred", {})
    period_type = parameters.get("period_type", "days")

    pdf_gen.add_section(ReportSection(title=f"Sensor: {sensor}", content=None, level=2))

    # Generate line chart with historical and predicted data
    if data and pred:
        try:
            data_labels = data.get("labels", [])
            data_values = data.get("values", [])
            pred_labels = pred.get("labels", [])
            pred_values = pred.get("values", [])

            # Combine labels
            all_labels = [str(label) for label in data_labels + pred_labels]

            # Prepare series - keep None values for gaps
            historical_series = data_values + [None] * len(pred_values)
            predicted_series = [None] * len(data_values) + pred_values

            # Count non-null values
            hist_count = len([v for v in data_values if v is not None])
            pred_count = len([v for v in pred_values if v is not None])

            line_data = LineChartData(
                x_values=all_labels,
                series={
                    f"{sensor} (Histórico)": historical_series,
                    f"{sensor} (Predicción)": predicted_series,
                },
            )

            chart_config = ChartConfig(
                chart_type=ChartType.LINE,
                title=f"{sensor.upper()} - Histórico: {hist_count}, Predicción: {pred_count}",
                x_label="Fecha",
                y_label="Valor",
                period_type=period_type,
            )

            chart_image = chart_gen.generate_line_chart(line_data, chart_config)
            pdf_gen.add_chart(
                chart_image, caption=f"Datos históricos y predicciones de {sensor}"
            )
        except Exception as e:
            print(f"Error generating prediction chart: {e}")


def _add_all_sensors_prediction(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
    parameters: dict,
) -> None:
    """Add content for all sensors prediction."""
    data = result_data.get("data", {})
    pred = result_data.get("pred", {})
    period_type = parameters.get("period_type", "days")

    # Generate charts for each sensor
    sensors = [
        SensorType.CONDUCTIVITY,
        SensorType.PH,
        SensorType.TEMPERATURE,
        SensorType.TDS,
        SensorType.TURBIDITY,
    ]

    for idx, sensor in enumerate(sensors):
        if sensor in data and sensor in pred:
            try:
                data_labels = data.get("labels", [])
                pred_labels = pred.get("labels", [])
                data_values = data.get(sensor.lower(), [])
                pred_values = pred.get(sensor.lower(), [])

                # Skip if no data
                if not data_values and not pred_values:
                    print(f"No data for sensor {sensor}, skipping chart.")
                    continue

                # Combine labels
                all_labels = [str(label) for label in data_labels + pred_labels]

                # Prepare series - keep None values for gaps
                historical_series = data_values + [None] * len(pred_values)
                predicted_series = [None] * len(data_values) + pred_values

                # Count non-null values
                hist_count = len([v for v in data_values if v is not None])
                pred_count = len([v for v in pred_values if v is not None])

                line_data = LineChartData(
                    x_values=all_labels,
                    series={
                        f"{sensor.spanish()} (Histórico)": historical_series,
                        f"{sensor.spanish()} (Predicción)": predicted_series,
                    },
                )

                chart_config = ChartConfig(
                    chart_type=ChartType.LINE,
                    title=f"{sensor.spanish()} - Histórico: {hist_count}, Predicción: {pred_count}",
                    x_label="Fecha",
                    y_label="Valor",
                    period_type=period_type,
                )

                chart_image = chart_gen.generate_line_chart(line_data, chart_config)
                pdf_gen.add_chart(
                    chart_image, caption=f"Predicciones de {sensor.spanish()}"
                )

                # Only add page break after first chart to save space
                # if idx == 0:
                #     pdf_gen.add_page_break()
            except Exception as e:
                print(f"Error generating prediction chart for {sensor}: {e}")


def _add_correlation_content(
    pdf_gen: PDFReportGenerator,
    chart_gen: AnalysisChartGenerator,
    result_data: dict,
) -> None:
    """Add content for correlation analysis type."""
    pdf_gen.add_section(
        ReportSection(
            title="Resultados del Análisis de Correlación", content=None, level=1
        )
    )

    method = result_data.get("method", "N/A")
    sensors_type = result_data.get("sensors", [])
    sensors = [SensorType(sensor).spanish() for sensor in sensors_type]

    matrix = result_data.get("matrix", [])

    # Add method information
    method_translations = {
        "pearson": "Pearson",
        "spearman": "Spearman",
        "kendall": "Kendall",
    }

    pdf_gen.add_section(
        ReportSection(
            title="Método de Correlación",
            content=f"Método: {method_translations.get(method, method)}\nSensores: {', '.join(sensors) if sensors else 'N/A'}",
            level=2,
        )
    )

    # Generate heatmap if we have matrix data
    if matrix and sensors:
        try:
            heatmap_data = HeatmapData(
                data=matrix,
                x_labels=sensors,
                y_labels=sensors,
            )

            chart_config = ChartConfig(
                chart_type=ChartType.HEATMAP,
                title="Matriz de Correlación",
                x_label="Sensores",
                y_label="Sensores",
            )

            chart_image = chart_gen.generate_heatmap(heatmap_data, chart_config)
            pdf_gen.add_chart(
                chart_image,
                caption=f"Matriz de correlación usando el método {method_translations.get(method, method)}",
            )
        except Exception as e:
            print(f"Error generating heatmap: {e}")

    # Add correlation matrix as table
    if matrix and sensors:
        rows = []
        for i, sensor in enumerate(sensors):
            row = [sensor]
            for j in range(len(sensors)):
                value = matrix[i][j] if i < len(matrix) and j < len(matrix[i]) else 0.0
                row.append(f"{value:.3f}" if isinstance(value, (int, float)) else "N/A")
            rows.append(row)

        table = TableData(
            headers=[""] + sensors,
            rows=rows,
        )
        pdf_gen.add_table(table)


def _add_generic_content(
    pdf_gen: PDFReportGenerator,
    result_data: dict,
) -> None:
    """Add generic content for unknown analysis types."""
    pdf_gen.add_section(
        ReportSection(
            title="Resultados del Análisis",
            content=f"Datos sin procesar:\n{str(result_data)[:500]}",
            level=1,
        )
    )
