# main.py
from app import app
from analytics_engine import TTRAnalyticsEngine
from data_integration import DataIntegrator

def main():
    print("Запуск ЕАИС для оценки мер ТТП...")
    
    # Инициализация компонентов системы
    analytics_engine = TTRAnalyticsEngine()
    data_integrator = DataIntegrator()
    
    print("Система готова к работе!")
    print("Доступные endpoints:")
    print("- GET  / (главная страница)")
    print("- POST /analyze (анализ мер ТТП)")
    print("- GET  /api/product-suggestions (автодополнение товаров)")
    
    # Запуск веб-сервера
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == "__main__":
    main()
