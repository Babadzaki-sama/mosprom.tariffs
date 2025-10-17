# models.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum

class CountryType(Enum):
    FRIENDLY = "friendly"
    UNFRIENDLY = "unfriendly"
    CHINA = "china"

class TTPMeasure(Enum):
    MEASURE_1 = "Повышение ставки таможенной пошлины до уровня связывания в ВТО"
    MEASURE_2 = "Повышение ставки таможенной пошлины до 35-50%"
    MEASURE_3 = "Антидемпинговое расследование в отношении Китая"
    MEASURE_4 = "Преференциальный режим в госзакупках"
    MEASURE_5 = "Сертификация соответствия"
    MEASURE_6 = "Иные меры защиты рынка"

@dataclass
class ProductInfo:
    tnved_code: str
    product_name: str
    current_tariff_rate: float
    wto_bound_rate: float
    production_volume: float
    consumption_volume: float
    production_trend: str  # "growing", "stable", "declining"

@dataclass
class ImportData:
    total_import_volume: float
    import_by_country: Dict[CountryType, float]
    import_trends: Dict[CountryType, str]
    average_prices: Dict[CountryType, float]

@dataclass
class TTPRecommendation:
    measure: TTPMeasure
    target_countries: List[CountryType]
    justification: str
    confidence_score: float
