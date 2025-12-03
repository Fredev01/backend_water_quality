from enum import Enum


class SensorType(str, Enum):
    COLOR = "color"
    CONDUCTIVITY = "conductivity"
    PH = "ph"
    TEMPERATURE = "temperature"
    TDS = "tds"
    TURBIDITY = "turbidity"

    def spanish(self) -> str:
        translations = {
            SensorType.COLOR: "Color",
            SensorType.CONDUCTIVITY: "Conductividad",
            SensorType.PH: "pH",
            SensorType.TEMPERATURE: "Temperatura",
            SensorType.TDS: "TDS",
            SensorType.TURBIDITY: "Turbidez",
        }
        return translations.get(self, "Desconocido")
