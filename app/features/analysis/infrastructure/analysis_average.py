from datetime import timedelta
import math
from typing import Any
from sklearn.linear_model import LinearRegression

import numpy as np
import pandas as pd
from app.features.analysis.domain.enums import PeriodEnum
from app.features.analysis.domain.interface import IPredictResult
from app.features.analysis.domain.repository import AnalysisAverageRepository
from app.features.analysis.domain.model import (
    AveragePeriod,
    AverageRange,
    AverageResult,
    AvgPeriod,
    AvgPeriodAllResult,
    AvgPeriodResult,
    AvgResult,
    AvgSensor,
    Chart,
    Period,
    PredictionParam,
)
from app.share.meter_records.domain.enums import SensorType
from app.share.meter_records.domain.model import SensorIdentifier, SensorQueryParams
from app.share.meter_records.domain.repository import (
    MeterRecordsRepository,
)


class AnalysisAverage(AnalysisAverageRepository):
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
            avg = df.resample("Y").mean()
        elif period_type == PeriodEnum.MONTHS:
            avg = df.resample("ME").mean()
        else:
            avg = df.resample("D").mean()

        return avg

    def get_analysis(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult:
        pass

    def create_average(
        self, identifier: SensorIdentifier, average_range: AverageRange
    ) -> AverageResult | list[AverageResult]:

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
                chart=[
                    Chart(
                        type="bar",
                        title=f"{sensor_type}: Average vs min/max",
                        labels=["Min", "Average", "Max"],
                        values=[min, average, max],
                    )
                ],
            )

        average_list = []

        for sensor_name in SensorType:
            if sensor_name == SensorType.COLOR:
                continue

            s_df = df[sensor_name]

            average = s_df.mean()
            min = s_df.min()
            max = s_df.max()

            average_list.append(
                AverageResult(
                    sensor=sensor_name,
                    period=Period(
                        start_date=average_range.start_date,
                        end_date=average_range.end_date,
                    ),
                    stats={"average": average, "min": min, "max": max},
                    charts=[
                        Chart(
                            type="bar",
                            title=f"{sensor_name}: Average vs min/max",
                            labels=["Min", "Average", "Max"],
                            values=[min, average, max],
                        )
                    ],
                )
            )

        return average_list

    def _safe_value(self, v):
        return None if (v is None or (isinstance(v, float) and math.isnan(v))) else v

    def create_average_period(
        self, identifier: SensorIdentifier, average_period: AveragePeriod
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

            labels_chart = []
            values_chart = []

            for index, row in df.iterrows():
                labels_chart.append(str(index))
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
                charts=[
                    Chart(
                        type="line",
                        title=f"{sensor_type.value} average by {average_period.period_type.value}",
                        labels=labels_chart,
                        values=values_chart,
                    )
                ],
            )

        averages: list[AvgPeriod] = []

        labels_chart: list[float | None] = []
        values_chart_dic: dict[SensorType, list[float | None]] = {
            SensorType.CONDUCTIVITY: [],
            SensorType.PH: [],
            SensorType.TEMPERATURE: [],
            SensorType.TDS: [],
            SensorType.TURBIDITY: [],
        }

        for index, row in df.iterrows():
            labels_chart.append(str(index))

            conductivity = self._safe_value(row["conductivity"])
            ph = self._safe_value(row["ph"])
            temperature = self._safe_value(row["temperature"])
            tds = self._safe_value(row["tds"])
            turbidity = self._safe_value(row["turbidity"])

            values_chart_dic[SensorType.CONDUCTIVITY].append(conductivity)
            values_chart_dic[SensorType.PH].append(ph)
            values_chart_dic[SensorType.TEMPERATURE].append(temperature)
            values_chart_dic[SensorType.TDS].append(tds)
            values_chart_dic[SensorType.TURBIDITY].append(turbidity)

            averages.append(
                AvgPeriod(
                    date=index,
                    averages=AvgSensor(
                        conductivity=conductivity,
                        ph=ph,
                        temperature=temperature,
                        tds=tds,
                        turbidity=turbidity,
                    ),
                )
            )

        return AvgPeriodAllResult(
            period=Period(
                start_date=average_period.start_date,
                end_date=average_period.end_date,
            ),
            period_type=average_period.period_type,
            averages=averages,
            charts=[
                Chart(
                    type="line",
                    title=f"{sensor_name.value} average by {average_period.period_type.value}",
                    labels=labels_chart,
                    values=values_chart_dic[sensor_name],
                )
                for sensor_name in SensorType
                if sensor_name != SensorType.COLOR
            ],
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
        """Predict values ​​for the next N days"""
        df[PeriodEnum.DAYS.lower()] = df["datetime"].dt.date

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
        daily_data = df.groupby(PeriodEnum.DAYS.lower()).agg(agg_param).reset_index()

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

        rows: dict[str, np.ndarray | None] = {"dates": [d.date() for d in future_dates]}

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
        df["year_month"] = df["datetime"].dt.to_period("M")
        monthly_data = df.groupby("year_month").agg(agg_param).reset_index()

        # Create numeric temporary variable
        monthly_data["month_num"] = range(len(monthly_data))

        # Regression models
        X = monthly_data["month_num"].values.reshape(-1, 1)

        # Generate future months
        last_period = monthly_data["year_month"].max()
        future_periods = [last_period + i for i in range(1, months_ahead + 1)]
        future_month_nums = range(len(monthly_data), len(monthly_data) + months_ahead)

        # Predictions
        X_future = np.array(future_month_nums).reshape(-1, 1)
        rows: dict[str, np.ndarray | None] = {"month": [str(p) for p in future_periods]}

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
        """Predict average values ​​for the next N years"""

        df[PeriodEnum.YEARS.lower()] = df["datetime"].dt.year

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

        year_column = PeriodEnum.YEARS.lower()

        # Group by year
        yearly_data = df.groupby(year_column).agg(agg_param).reset_index()

        # Create numeric temporary variable
        yearly_data["year_num"] = (
            yearly_data[year_column] - yearly_data[year_column].min()
        )

        # Regression models
        X = yearly_data["year_num"].values.reshape(-1, 1)

        # Generate future years
        last_year = yearly_data[year_column].max()
        future_years = [last_year + i for i in range(1, years_ahead + 1)]
        future_year_nums = [
            (year - yearly_data[year_column].min()) for year in future_years
        ]

        # Predictions
        X_future = np.array(future_year_nums).reshape(-1, 1)
        rows: dict[str, np.ndarray | None] = {year_column: future_years}

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

    def generate_prediction(
        self, identifier: SensorIdentifier, prediction_param: PredictionParam
    ):
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
        pred = None
        if period_type == PeriodEnum.DAYS:
            pred = self._predict_daily(
                df=df,
                days_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )
        elif period_type == PeriodEnum.MONTHS:

            pred = self._predict_monthly(
                df=df,
                months_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )
        elif period_type == PeriodEnum.YEARS:
            pred = self._predict_yearly(
                df=df,
                years_ahead=prediction_param.ahead,
                sensor=prediction_param.sensor_type,
            )

        print(pred.data)
        print(pred.pred)

        return {}
