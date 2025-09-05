from pandas import DataFrame


class IPredictResult:
    def __init__(self, data: DataFrame, pred: DataFrame):
        self.data: DataFrame = data
        self.pred: DataFrame = pred
