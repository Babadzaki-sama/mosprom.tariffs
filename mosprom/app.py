# app.py
from flask import Flask, render_template, request, jsonify
import json
from analytics_engine import TTRAnalyticsEngine
from models import *

app = Flask(__name__)
analytics_engine = TTRAnalyticsEngine()

# Мок-данные для демонстрации
def get_mock_product_data(tnved_code: str) -> ProductInfo:
    """Получение мок-данных о продукте"""
    mock_data = {
        "847130": ProductInfo(
            tnved_code="847130",
            product_name="Ноутбуки",
            current_tariff_rate=5.0,
            wto_bound_rate=8.5,
            production_volume=500000,
            consumption_volume=600000,
            production_trend="growing"
        ),
        "870323": ProductInfo(
            tnved_code="870323",
            product_name="Легковые автомобили",
            current_tariff_rate=15.0,
            wto_bound_rate=17.0,
            production_volume=800000,
            consumption_volume=1200000,
            production_trend="stable"
        )
    }
    return mock_data.get(tnved_code[:6], mock_data["847130"])

def get_mock_import_data(tnved_code: str) -> ImportData:
    """Получение мок-данных об импорте"""
    return ImportData(
        total_import_volume=800000,
        import_by_country={
            CountryType.UNFRIENDLY: 350000,
            CountryType.CHINA: 250000,
            CountryType.FRIENDLY: 200000
        },
        import_trends={
            CountryType.UNFRIENDLY: "growing",
            CountryType.CHINA: "growing", 
            CountryType.FRIENDLY: "stable"
        },
        average_prices={
            CountryType.UNFRIENDLY: 1200.0,
            CountryType.CHINA: 800.0,
            CountryType.FRIENDLY: 1100.0
        }
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_ttp():
    try:
        data = request.json
        tnved_code = data.get('tnved_code', '')
        product_name = data.get('product_name', '')
        
        # Получаем данные (в реальной системе - из внешних источников)
        product_info = get_mock_product_data(tnved_code)
        import_data = get_mock_import_data(tnved_code)
        
        # Анализ мер ТТП
        recommendations = analytics_engine.analyze_ttp_measures(product_info, import_data)
        
        # Форматируем ответ
        result = {
            'product_name': product_name,
            'tnved_code': tnved_code,
            'recommendations': []
        }
        
        for rec in recommendations:
            result['recommendations'].append({
                'measure': rec.measure.value,
                'target_countries': [country.value for country in rec.target_countries],
                'justification': rec.justification,
                'confidence_score': round(rec.confidence_score, 2),
                'coverage_percentage': analytics_engine._calculate_coverage(product_info)
            })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/product-suggestions', methods=['GET'])
def product_suggestions():
    """API для автодополнения товаров"""
    query = request.args.get('query', '').lower()
    
    # Мок-данные товаров
    products = [
        {"code": "847130", "name": "Ноутбуки портативные"},
        {"code": "870323", "name": "Автомобили легковые"},
        {"code": "841451", "name": "Кондиционеры"},
        {"code": "851762", "name": "Модемы и роутеры"},
        {"code": "854370", "name": "Микросхемы и процессоры"}
    ]
    
    suggestions = [p for p in products if query in p['name'].lower() or query in p['code']]
    return jsonify(suggestions[:5])

if __name__ == '__main__':
    app.run(debug=True)
