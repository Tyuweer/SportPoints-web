# test_ocr_parser.py
import sys
from pathlib import Path

# Добавляем корень проекта в путь для импортов
sys.path.insert(0, str(Path(__file__).parent))

from laba_1.parsers.krai_ocr_parser import KraiOcrParser


def main():
    # Укажи точный путь к файлу Чемпионата Края
    pdf_path = Path("media/protocols/chempionat_kraya_600481_WAkYzUp.pdf")
    
    if not pdf_path.exists():
        print(f"❌ Ошибка: Файл не найден по пути {pdf_path}")
        return

    parser = KraiOcrParser()
    
    print(f"\n=== Тестирование OCR-парсера: {pdf_path.name} ===\n")
    print(" Идет распознавание и парсинг (это может занять 1-2 минуты)...")
    
    try:
        # Запускаем парсер (is_manual=True, так как это региональные соревнования)
        events = parser.parse(pdf_path, is_manual=True)
        
        if not events:
            print("⚠️ Парсер не вернул ни одной дисциплины.")
            print("💡 Совет: Проверь качество исходного PDF или настройки Tesseract.")
            return
        
        total_athletes = 0
        for event in events:
            print(f"\n🏊 Дисциплина: {event['event_name']}")
            print(f"   Эстафета: {'Да' if event.get('relay') else 'Нет'}")
            print(f"   Спортсменов: {len(event['results'])}")
            
            # Выводим первые 5 строк для проверки структуры
            for i, athlete in enumerate(event['results'][:5]):
                print(f"     [{i+1}] Место: {athlete.get('place')} | "
                      f"ФИО: {athlete.get('full_name')} | "
                      f"Год: {athlete.get('birth_year')} | "
                      f"Команда: {athlete.get('team')} | "
                      f"Результат: {athlete.get('result')} | "
                      f"Разряд: {athlete.get('rank')}")
            
            if len(event['results']) > 5:
                print(f"     ... и еще {len(event['results']) - 5} спортсменов")
                
            print("-" * 80)
            total_athletes += len(event['results'])
        
        print(f"\n✅ Итого дисциплин: {len(events)}")
        print(f"✅ Итого спортсменов: {total_athletes}")
        
        # Опционально: сохранить полный результат в JSON для детального анализа
        save = input("\nСохранить полный результат в JSON? (y/n): ").lower() == 'y'
        if save:
            import json
            output_path = Path("ocr_test_output.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, ensure_ascii=False, indent=2)
            print(f"💾 Результат сохранен в {output_path}")
            
    except Exception as e:
        print(f"\n💥 Критическая ошибка при парсинге: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()