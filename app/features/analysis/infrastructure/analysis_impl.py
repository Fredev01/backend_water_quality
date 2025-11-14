import math
import numpy as np
import pandas as pd
from typing import Any
from datetime import date, datetime, timedelta
from sklearn.linear_model import LinearRegression
from app.features.analysis.domain.enums import PeriodEnum
from app.features.analysis.domain.interface import IPredictResult
from app.features.analysis.domain.models.average import (
    AverageResultAll,
    AverageStatsSensor,
    AvgPeriodParam,
    AverageRange,
    AverageResult,
    AvgPeriodAllResult,
    AvgPeriodResult,
    AvgResult,
    AvgSensor,
    AvgValues,
    Period,
)
from app.features.analysis.domain.models.correlation import (
    CorrelationParams,
    CorrelationResult,
)
from app.features.analysis.domain.models.prediction import (
    PredData,
    PredictionData,
    PredictionParam,
    PredictionResult,
    PredictionResultAll,
)
from app.features.analysis.domain.repository import AnalysisRepository

from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import (
    MeterRecordsRepository,
)


class AnalysisAverage(AnalysisRepository):
    def __init__(self, record_repo: MeterRecordsRepository):
        self.record_repo: MeterRecordsRepository = record_repo

    def _get_df(
        self, identifier: SensorIdentifier, params: SensorQueryParams, by_datetime=False
    ):
        records = self.record_repo.query_records(identifier=identifier, params=params)

        rows = []
        sensor_type = params.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("El análisis de color no está soportado")

        for ts, sensors in records.items():
            row = {"timestamp": int(ts)}
            if sensor_type is not None:
                sensor_record = getattr(sensors, sensor_type.value)
                row[sensor_type.value] = sensor_record.value if sensor_record else None

            else:
                for st in SensorType:
                    if st == SensorType.COLOR:
                        continue
                    sensor_record = getattr(sensors, st.value)
                    row[st.value] = sensor_record.value if sensor_record else None

            rows.append(row)

        df = pd.DataFrame(rows)

        if by_datetime:

            df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

        return df

    def _get_df_period(
        self,
        identifier: SensorIdentifier,
        params: SensorQueryParams,
        period_type: PeriodEnum = PeriodEnum.DAYS,
    ):

        df = (
            self._get_df(identifier=identifier, params=params, by_datetime=True)
            .set_index("datetime")
            .sort_index()
        )

        avg: pd.DataFrame

        if period_type == PeriodEnum.YEARS:
            avg = df.resample("YE").mean()
        elif period_type == PeriodEnum.MONTHS:
            avg = df.resample("ME").mean()
        else:
            avg = df.resample("D").mean()

        return avg

    def generate_average(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult | AverageResultAll:

        df = self._get_df(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=average_range.start_date,
                end_date=average_range.end_date,
                sensor_type=average_range.sensor_type,
                ignore_limit=True,
            ),
        )

        sensor_type = average_range.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("Sensor de color no esta implementado")

        if sensor_type is not None:

            average = df[sensor_type.value].mean()
            min = df[sensor_type.value].min()
            max = df[sensor_type.value].max()

            return AverageResult(
                sensor=sensor_type,
                period={
                    "start_date": average_range.start_date,
                    "end_date": average_range.end_date,
                },
                stats={"average": average, "min": min, "max": max},
            )

        result_all = AverageResultAll(
            period=Period(
                start_date=average_range.start_date,
                end_date=average_range.end_date,
            ),
            result=[],
        )

        for sensor_name in SensorType:
            if sensor_name == SensorType.COLOR:
                continue

            s_df = df[sensor_name]

            average = s_df.mean()
            min = s_df.min()
            max = s_df.max()

            result_all.result.append(
                AverageStatsSensor(
                    sensor=sensor_name, average=average, min=min, max=max
                )
            )

        return result_all

    def _safe_value(self, v):
        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    def generate_average_period(
        self, identifier: SensorIdentifier, average_period: AvgPeriodParam
    ) -> AvgPeriodAllResult | AvgPeriodResult:

        df = self._get_df_period(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=average_period.start_date,
                end_date=average_period.end_date,
                sensor_type=average_period.sensor_type,
                ignore_limit=True,
            ),
            period_type=average_period.period_type,
        )

        sensor_type = average_period.sensor_type

        if sensor_type == SensorType.COLOR:
            raise ValueError("Sensor de color no esta implementado")

        if sensor_type is not None:
            averages: list[AvgResult] = []

            values_chart = []

            for index, row in df.iterrows():
                value = self._safe_value(row[sensor_type])
                values_chart.append(value)
                averages.append(AvgResult(date=index, value=value))

            return AvgPeriodResult(
                sensor=sensor_type,
                period=Period(
                    start_date=average_period.start_date,
                    end_date=average_period.end_date,
                ),
                period_type=average_period.period_type,
                averages=averages,
            )

        result_avg = AvgSensor(
            conductivity=AvgValues(
                labels=[],
                values=[],
            ),
            ph=AvgValues(
                labels=[],
                values=[],
            ),
            tds=AvgValues(
                labels=[],
                values=[],
            ),
            temperature=AvgValues(
                labels=[],
                values=[],
            ),
            turbidity=AvgValues(
                labels=[],
                values=[],
            ),
        )

        labels = df.index.to_list()
        for s_type in SensorType:
            if s_type == SensorType.COLOR:
                continue

            sensor_name = s_type.value
            avg_values_model = getattr(result_avg, sensor_name)

            avg_values_model.labels = labels

            values_list = [self._safe_value(v) for v in df[sensor_name].to_list()]
            avg_values_model.values = values_list

            print(avg_values_model)

        return AvgPeriodAllResult(
            period=Period(
                start_date=average_period.start_date,
                end_date=average_period.end_date,
            ),
            period_type=average_period.period_type,
            results=result_avg,
        )

    def _predict_by_sensor(
        self,
        serie: pd.Series,
        X: np.ndarray[tuple[int, int], np.dtype[Any]],
        X_future: np.ndarray[tuple[int, int], np.dtype[Any]],
    ) -> np.ndarray[Any, np.dtype[Any]]:
        model = LinearRegression()
        model.fit(X, serie)

        return model.predict(X_future)

    def _predict_daily(
        self, df: pd.DataFrame, days_ahead=10, sensor: SensorType = None
    ) -> IPredictResult:
        """Predict values for the next N days"""
        column_group = PeriodEnum.DAYS.value
        df[column_group] = df["datetime"].dt.date

        agg_param: dict[str, str] = {"datetime": "first"}

        if sensor == SensorType.COLOR:
            raise ValueError("No hay implementación para el sensor de color")

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                agg_param[sensor_type.lower()] = "mean"

        else:
            agg_param[sensor.lower()] = "mean"

        # Group by day
        daily_data = df.groupby(column_group).agg(agg_param).reset_index()

        # Create numeric temporary variable
        daily_data["day_num"] = (
            daily_data["datetime"] - daily_data["datetime"].min()
        ).dt.days

        # Regression models
        X = daily_data["day_num"].values.reshape(-1, 1)

        # Generate future dates
        last_date = daily_data["datetime"].max()
        future_dates: list[pd.Timestamp] = [
            last_date + timedelta(days=i) for i in range(1, days_ahead + 1)
        ]
        future_day_nums = [
            (date - daily_data["datetime"].min()).days for date in future_dates
        ]

        # Predictions
        X_future = np.array(future_day_nums).reshape(-1, 1)

        rows: dict[str, np.ndarray | None] = {
            column_group: [d.date() for d in future_dates]
        }

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                rows[sensor_type.lower()] = self._predict_by_sensor(
                    serie=daily_data[sensor_type.lower()], X=X, X_future=X_future
                )
        else:
            rows[sensor.lower()] = self._predict_by_sensor(
                serie=daily_data[sensor.lower()], X=X, X_future=X_future
            )

        predictions_df = pd.DataFrame(rows)

        return IPredictResult(data=daily_data, pred=predictions_df)

    def _predict_monthly(
        self, df: pd.DataFrame, months_ahead=10, sensor: SensorType = None
    ) -> IPredictResult:
        """Predict average values for the next N months"""

        agg_param: dict[str, str] = {"datetime": "first"}

        column_group = PeriodEnum.MONTHS.value

        if sensor == SensorType.COLOR:
            raise ValueError("No hay implementación para el sensor de color")

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                agg_param[sensor_type.lower()] = "mean"

        else:
            agg_param[sensor.lower()] = "mean"

        # Group by month
        df[column_group] = df["datetime"].dt.to_period("M")
        monthly_data = df.groupby(column_group).agg(agg_param).reset_index()

        # Create numeric temporary variable
        monthly_data["month_num"] = range(len(monthly_data))

        # Regression models
        X = monthly_data["month_num"].values.reshape(-1, 1)

        # Generate future months
        last_period = monthly_data[column_group].max()
        future_periods = [last_period + i for i in range(1, months_ahead + 1)]
        future_month_nums = range(len(monthly_data), len(monthly_data) + months_ahead)

        # Predictions
        X_future = np.array(future_month_nums).reshape(-1, 1)
        rows: dict[str, np.ndarray | None] = {
            column_group: [str(p) for p in future_periods]
        }

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                rows[sensor_type.lower()] = self._predict_by_sensor(
                    serie=monthly_data[sensor_type.lower()], X=X, X_future=X_future
                )
        else:
            rows[sensor.lower()] = self._predict_by_sensor(
                serie=monthly_data[sensor.lower()], X=X, X_future=X_future
            )

        predictions_df = pd.DataFrame(rows)

        return IPredictResult(data=monthly_data, pred=predictions_df)

    def _predict_yearly(
        self, df: pd.DataFrame, years_ahead=10, sensor: SensorType = None
    ) -> IPredictResult:
        """Predict average values for the next N years"""

        column_group = PeriodEnum.YEARS.value

        df[column_group] = df["datetime"].dt.year

        agg_param: dict[str, str] = {"datetime": "first"}

        if sensor == SensorType.COLOR:
            raise ValueError("No hay implementación para el sensor de color")

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                agg_param[sensor_type.lower()] = "mean"

        else:
            agg_param[sensor.lower()] = "mean"

        # Group by year
        yearly_data = df.groupby(column_group).agg(agg_param).reset_index()

        # Create numeric temporary variable
        yearly_data["year_num"] = (
            yearly_data[column_group] - yearly_data[column_group].min()
        )

        # Regression models
        X = yearly_data["year_num"].values.reshape(-1, 1)

        # Generate future years
        last_year = yearly_data[column_group].max()
        future_years = [last_year + i for i in range(1, years_ahead + 1)]
        future_year_nums = [
            (year - yearly_data[column_group].min()) for year in future_years
        ]

        # Predictions
        X_future = np.array(future_year_nums).reshape(-1, 1)
        rows: dict[str, np.ndarray | None] = {column_group: future_years}

        if sensor is None:
            for sensor_type in SensorType:
                if sensor_type == SensorType.COLOR:
                    continue
                rows[sensor_type.lower()] = self._predict_by_sensor(
                    serie=yearly_data[sensor_type.lower()], X=X, X_future=X_future
                )
        else:
            rows[sensor.lower()] = self._predict_by_sensor(
                serie=yearly_data[sensor.lower()], X=X, X_future=X_future
            )

        predictions_df = pd.DataFrame(rows)

        return IPredictResult(data=yearly_data, pred=predictions_df)

    def _date_validate(self, value: Any) -> str:
        if isinstance(value, (pd.Period, int)):
            return str(value)
        elif isinstance(value, (float, np.float64)):
            return str(int(value))
        elif isinstance(value, (datetime, date)):
            return str(value)
        elif isinstance(value, str):
            return value
        return ""

    def generate_prediction(
        self, identifier: SensorIdentifier, prediction_param: PredictionParam
    ) -> PredictionResult | PredictionResultAll:
        df = self._get_df(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=prediction_param.start_date,
                end_date=prediction_param.end_date,
                sensor_type=prediction_param.sensor_type,
                ignore_limit=True,
            ),
            by_datetime=True,
        )
        period_type = prediction_param.period_type
        pred_r: IPredictResult

        if period_type == PeriodEnum.MONTHS:

            pred_r = self._predict_monthly(
                df=df,
                months_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )
        elif period_type == PeriodEnum.YEARS:
            pred_r = self._predict_yearly(
                df=df,
                years_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )
        else:
            pred_r = self._predict_daily(
                df=df,
                days_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )

        period_type_str = period_type.value

        if prediction_param.sensor_type is not None:
            data_labels: list = []
            data_values: list = []
            for index, row in pred_r.data.iterrows():
                data_labels.append(self._date_validate(row[period_type_str]))
                data_values.append(
                    self._safe_value(row[prediction_param.sensor_type.value])
                )
            pred_labels: list = []
            pred_values: list = []
            for index, row in pred_r.pred.iterrows():
                pred_labels.append(self._date_validate(row[period_type_str]))
                pred_values.append(
                    self._safe_value(row[prediction_param.sensor_type.value])
                )

            return PredictionResult(
                sensor=prediction_param.sensor_type.value,
                data=PredData(labels=data_labels, values=data_values),
                pred=PredData(labels=pred_labels, values=pred_values),
            )

        all_data: PredictionData = PredictionData(
            labels=[], conductivity=[], ph=[], temperature=[], tds=[], turbidity=[]
        )
        all_pred: PredictionData = PredictionData(
            labels=[], conductivity=[], ph=[], temperature=[], tds=[], turbidity=[]
        )

        for index, row in pred_r.data.iterrows():

            all_data.labels.append(self._date_validate(row[period_type_str]))
            all_data.conductivity.append(
                self._safe_value(row[SensorType.CONDUCTIVITY.value])
            )
            all_data.ph.append(self._safe_value(row[SensorType.PH.value]))
            all_data.temperature.append(
                self._safe_value(row[SensorType.TEMPERATURE.value])
            )
            all_data.tds.append(self._safe_value(row[SensorType.TDS.value]))
            all_data.turbidity.append(self._safe_value(row[SensorType.TURBIDITY.value]))

        for index, row in pred_r.pred.iterrows():

            all_pred.labels.append(self._date_validate(row[period_type_str]))
            all_pred.conductivity.append(
                self._safe_value(row[SensorType.CONDUCTIVITY.value])
            )
            all_pred.ph.append(self._safe_value(row[SensorType.PH.value]))
            all_pred.temperature.append(
                self._safe_value(row[SensorType.TEMPERATURE.value])
            )
            all_pred.tds.append(self._safe_value(row[SensorType.TDS.value]))
            all_pred.turbidity.append(self._safe_value(row[SensorType.TURBIDITY.value]))

        return PredictionResultAll(data=all_data, pred=all_pred)

    def generate_correlation(
        self,
        identifier: SensorIdentifier,
        correlation_params: CorrelationParams,
    ) -> CorrelationResult:
        """
        Genera la matriz de correlación entre sensores seleccionados.
        """
        # Validar lista de sensores
        if not correlation_params.sensors or len(correlation_params.sensors) < 2:
            raise ValueError("Se requieren al menos 2 sensores para correlación")

        if SensorType.COLOR in correlation_params.sensors:
            raise ValueError("El sensor de color no es soportado en correlación")

        # Obtener el DataFrame filtrado
        df = self._get_df_period(
            identifier=identifier,
            params=SensorQueryParams(
                start_date=correlation_params.start_date,
                end_date=correlation_params.end_date,
                ignore_limit=True,
            ),
            period_type=correlation_params.period_type,
        )

        sensor_names = [
            s.value for s in correlation_params.sensors if s != SensorType.COLOR
        ]

        df = df[sensor_names]
        # Calcular matriz de correlación
        method = correlation_params.method.value
        corr_matrix = df.corr(method=method)

        # Convertir a lista para JSON
        matrix_values = corr_matrix.values.tolist()
        sensor_labels = list(corr_matrix.columns)

        # Construir resultado
        return CorrelationResult(
            method=method,
            sensors=sensor_labels,
            matrix=matrix_values,
        )
