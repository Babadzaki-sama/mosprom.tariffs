# analytics_engine.py
import pandas as pd
import numpy as np
from typing import List, Dict
from models import *

class TTRAnalyticsEngine:
    def __init__(self):
        self.unfriendly_countries_threshold = 0.3  # 30%
        self.china_import_threshold = 0.1  # 10% роста
        self.price_difference_threshold = 0.15  # 15% разницы в ценах
        
    def check_measure_1(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №1"""
        unfriendly_share = self._calculate_unfriendly_share(import_data)
        
        conditions = [
            product.current_tariff_rate < product.wto_bound_rate,
            unfriendly_share < self.unfriendly_countries_threshold,
            import_data.import_trends.get(CountryType.UNFRIENDLY, "stable") == "declining",
            product.production_volume >= product.consumption_volume * 0.8  # 80% покрытия
        ]
        
        return all(conditions)
    
    def check_measure_2(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №2"""
        unfriendly_share = self._calculate_unfriendly_share(import_data)
        
        conditions = [
            unfriendly_share > self.unfriendly_countries_threshold,
            import_data.import_trends.get(CountryType.UNFRIENDLY, "stable") in ["stable", "growing"],
            product.production_volume >= product.consumption_volume * 0.8
        ]
        
        return all(conditions)
    
    def check_measure_3(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №3 (антидемпинг против Китая)"""
        china_import = import_data.import_by_country.get(CountryType.CHINA, 0)
        other_import = sum([v for k, v in import_data.import_by_country.items() 
                          if k != CountryType.CHINA])
        
        china_price = import_data.average_prices.get(CountryType.CHINA, 0)
        other_prices = [v for k, v in import_data.average_prices.items() 
                       if k != CountryType.CHINA]
        avg_other_price = np.mean(other_prices) if other_prices else 0
        
        conditions = [
            import_data.import_trends.get(CountryType.CHINA, "stable") == "growing",
            china_price > 0 and avg_other_price > 0,
            china_price < avg_other_price * (1 - self.price_difference_threshold),
            product.production_trend == "declining"
        ]
        
        return all(conditions)
    
    def check_measure_4(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №4 (преференции в госзакупках)"""
        # Здесь должна быть проверка по ПП РФ № 1875
        # В прототипе используем упрощенную логику
        is_in_gov_procurement_list = self._check_gov_procurement_list(product.tnved_code)
        
        conditions = [
            is_in_gov_procurement_list,
            product.production_volume >= product.consumption_volume * 0.7
        ]
        
        return conditions[0]  # Упрощенная проверка
    
    def check_measure_5(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №5 (сертификация)"""
        has_certification_requirement = self._check_certification_requirements(product.tnved_code)
        not_in_exception_list = self._check_exception_list(product.tnved_code)
        
        conditions = [
            has_certification_requirement,
            not_in_exception_list,
            import_data.import_trends.get(CountryType.UNFRIENDLY, "stable") == "growing",
            product.production_trend == "growing",
            product.production_volume >= product.consumption_volume * 0.6
        ]
        
        return all(conditions)
    
    def check_measure_6(self, product: ProductInfo, import_data: ImportData) -> bool:
        """Проверка условий для меры ТТП №6 (иные меры)"""
        conditions = [
            import_data.total_import_volume > product.production_volume,
            product.production_trend == "declining",
            not any([
                self.check_measure_1(product, import_data),
                self.check_measure_2(product, import_data),
                self.check_measure_3(product, import_data),
                self.check_measure_4(product, import_data),
                self.check_measure_5(product, import_data)
            ])
        ]
        
        return all(conditions)
    
    def _calculate_unfriendly_share(self, import_data: ImportData) -> float:
        """Расчет доли импорта из недружественных стран"""
        unfriendly_volume = import_data.import_by_country.get(CountryType.UNFRIENDLY, 0)
        total_volume = import_data.total_import_volume
        
        return unfriendly_volume / total_volume if total_volume > 0 else 0
    
    def _check_gov_procurement_list(self, tnved_code: str) -> bool:
        """Проверка наличия товара в перечне госзакупок"""
        # Заглушка для демонстрации
        gov_procurement_codes = ["847130", "850440", "854370"]  # Примеры кодов
        return tnved_code[:6] in gov_procurement_codes
    
    def _check_certification_requirements(self, tnved_code: str) -> bool:
        """Проверка требований сертификации"""
        # Заглушка для демонстрации
        certification_codes = ["870323", "841451", "851762"]
        return tnved_code[:6] in certification_codes
    
    def _check_exception_list(self, tnved_code: str) -> bool:
        """Проверка исключений по Приказу Минпромторга №411"""
        # Заглушка для демонстрации
        exception_codes = ["870899", "847149"]
        return tnved_code[:6] not in exception_codes
    
    def analyze_ttp_measures(self, product: ProductInfo, import_data: ImportData) -> List[TTPRecommendation]:
        """Основной метод анализа мер ТТП"""
        recommendations = []
        
        measure_checks = [
            (TTPMeasure.MEASURE_1, self.check_measure_1),
            (TTPMeasure.MEASURE_2, self.check_measure_2),
            (TTPMeasure.MEASURE_3, self.check_measure_3),
            (TTPMeasure.MEASURE_4, self.check_measure_4),
            (TTPMeasure.MEASURE_5, self.check_measure_5),
            (TTPMeasure.MEASURE_6, self.check_measure_6),
        ]
        
        for measure, check_function in measure_checks:
            if check_function(product, import_data):
                recommendation = self._create_recommendation(measure, product, import_data)
                recommendations.append(recommendation)
        
        return recommendations
    
    def _create_recommendation(self, measure: TTPMeasure, product: ProductInfo, 
                             import_data: ImportData) -> TTPRecommendation:
        """Создание рекомендации с обоснованием"""
        justification = self._generate_justification(measure, product, import_data)
        target_countries = self._determine_target_countries(measure, import_data)
        confidence = self._calculate_confidence(measure, product, import_data)
        
        return TTPRecommendation(
            measure=measure,
            target_countries=target_countries,
            justification=justification,
            confidence_score=confidence
        )
    
    def _generate_justification(self, measure: TTPMeasure, product: ProductInfo, 
                              import_data: ImportData) -> str:
        """Генерация текстового обоснования рекомендации"""
        justifications = {
            TTPMeasure.MEASURE_1: (
                f"Текущая ставка пошлины ({product.current_tariff_rate}%) ниже уровня ВТО "
                f"({product.wto_bound_rate}%). Доля импорта из недружественных стран снижается."
            ),
            TTPMeasure.MEASURE_2: (
                f"Высокая доля импорта из недружественных стран (>30%). "
                f"Необходима защита внутреннего рынка."
            ),
            TTPMeasure.MEASURE_3: (
                f"Выявлены признаки демпинга со стороны китайских экспортеров. "
                f"Цены ниже среднерыночных на {self._calculate_price_difference(import_data):.1f}%."
            ),
            TTPMeasure.MEASURE_4: (
                f"Товар включен в перечень госзакупок. Российское производство "
                f"покрывает {self._calculate_coverage(product):.1f}% потребления."
            ),
            TTPMeasure.MEASURE_5: (
                f"Товар подлежит обязательной сертификации. Рост импорта требует "
                f"ужесточения контроля качества."
            ),
            TTPMeasure.MEASURE_6: (
                f"Импорт превышает внутреннее производство. Требуются комплексные "
                f"меры защиты рынка."
            )
        }
        
        return justifications.get(measure, "Рекомендация основана на анализе рыночной ситуации.")
    
    def _determine_target_countries(self, measure: TTPMeasure, import_data: ImportData) -> List[CountryType]:
        """Определение целевых стран для меры"""
        if measure == TTPMeasure.MEASURE_3:
            return [CountryType.CHINA]
        elif measure in [TTPMeasure.MEASURE_1, TTPMeasure.MEASURE_2]:
            return [CountryType.UNFRIENDLY]
        else:
            return list(import_data.import_by_country.keys())
    
    def _calculate_confidence(self, measure: TTPMeasure, product: ProductInfo, 
                            import_data: ImportData) -> float:
        """Расчет уверенности в рекомендации"""
        # Упрощенный расчет confidence score
        base_confidence = 0.7
        # Добавляем факторы уверенности в зависимости от выполнения дополнительных условий
        additional_factors = 0.0
        
        if product.production_trend == "growing":
            additional_factors += 0.1
        if import_data.total_import_volume > product.production_volume * 2:
            additional_factors += 0.15
        if self._calculate_unfriendly_share(import_data) > 0.5:
            additional_factors += 0.1
            
        return min(base_confidence + additional_factors, 1.0)
    
    def _calculate_price_difference(self, import_data: ImportData) -> float:
        """Расчет разницы в ценах"""
        china_price = import_data.average_prices.get(CountryType.CHINA, 0)
        other_prices = [v for k, v in import_data.average_prices.items() 
                       if k != CountryType.CHINA]
        avg_other_price = np.mean(other_prices) if other_prices else china_price
        
        if avg_other_price > 0:
            return ((avg_other_price - china_price) / avg_other_price) * 100
        return 0
    
    def _calculate_coverage(self, product: ProductInfo) -> float:
        """Расчет покрытия потребления внутренним производством"""
        if product.consumption_volume > 0:
            return (product.production_volume / product.consumption_volume) * 100
        return 0
