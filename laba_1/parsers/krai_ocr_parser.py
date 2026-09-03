# parsers/krai_ocr_parser.py
import re
from pathlib import Path
from .base import IParser
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np


class KraiOcrParser(IParser):
    """
    Парсер для протоколов в виде изображений (сканы, фото).
    Использует OCR + адаптивные регулярные выражения.
    """
    
    # Конфигурация Tesseract для русского языка и таблиц
    TESSERACT_CONFIG = r'--oem 3 --psm 6 -l rus' 

    def parse(self, pdf_path: Path, is_manual: bool = False):
        events = []
        current_event = None
        
        try:
            images = convert_from_path(pdf_path, dpi=300)
        except Exception as e:
            print(f"Ошибка конвертации PDF в изображения: {e}")
            return events

        for img in images:
            processed_img = self._preprocess_image(img)
            text = pytesseract.image_to_string(processed_img, config=self.TESSERACT_CONFIG)
            
            lines = text.split('\n')
            for line in lines:
                cleaned_line = self._clean_ocr_line(line)
                if not cleaned_line:
                    continue

                # Определение заголовка дисциплины
                if self._is_event_header(cleaned_line):
                    event_name = self._normalize_event_name(cleaned_line)
                    if current_event and current_event["results"]:
                        events.append(current_event)
                    
                    current_event = {
                        "event_name": event_name,
                        "results": [],
                        "relay": "эстафета" in event_name.lower() or "4x" in event_name.lower()
                    }
                    continue

                # Парсинг строки спортсмена
                if current_event and not current_event["relay"]:
                    record = self._parse_athlete_line(cleaned_line, is_manual)
                    if record:
                        current_event["results"].append(record)

        if current_event and current_event["results"]:
            events.append(current_event)
            
        return [e for e in events if not e["relay"]]

    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Бинаризация и повышение контраста для лучшего OCR"""
        img_array = np.array(image.convert('L'))
        # Адаптивный порог лучше справляется с неравномерным освещением фото
        binary = cv2.adaptiveThreshold(
            img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 15, 8
        )
        return Image.fromarray(binary)

    def _clean_ocr_line(self, line: str) -> str:
        """Очистка артефактов OCR"""
        line = re.sub(r'[^\w\s,.:/()-]', '', line) # Удаляем спецсимволы
        line = re.sub(r'\s+', ' ', line).strip()
        return line

    def _is_event_header(self, line: str) -> bool:
        """Проверка на заголовок дисциплины (упрощенная для OCR)"""
        keywords = ["плавание", "подводное", "ныряние", "ластах", "мужчины", "женщины"]
        lower_line = line.lower()
        return any(kw in lower_line for kw in keywords) and len(line) > 15

    def _normalize_event_name(self, line: str) -> str:
        """Очистка названия дисциплины от мусора OCR"""
        # Убираем лишние слова, которые OCR мог прихватить из шапки
        line = re.sub(r'(чемпионат|края|красноярского|протокол|технических|результатов)', '', line, flags=re.IGNORECASE)
        return line.strip()

    def _parse_athlete_line(self, line: str, is_manual: bool):

      # 1. Очистка от мусора OCR (скобки, спецсимволы)
      clean_line = re.sub(r'[^\w\s.,:/-]', ' ', line)
      clean_line = re.sub(r'\s+', ' ', clean_line).strip()
      
      if not clean_line:
          return None

      # 2. Поиск даты рождения (самый надежный маркер)
      # Ищем именно формат ДД.ММ.ГГГГ
      date_match = re.search(r'(\d{2}\.\d{2}\.(?:19|20)\d{2})', clean_line)
      if not date_match:
          # Если даты нет, возможно это заголовок или мусор
          return None
          
      birth_date_str = date_match.group(1)
      birth_year = int(birth_date_str.split('.')[-1])
      date_end_idx = date_match.end()
      date_start_idx = date_match.start()

      # Текст ДО даты: Место + Разряд + ФИО
      pre_date_text = clean_line[:date_start_idx].strip()
      # Текст ПОСЛЕ даты: Команда + Результат + Норматив
      post_date_text = clean_line[date_end_idx:].strip()

      # 3. Извлечение Разряда из начала строки (до ФИО)
      rank = None
      place = None
      
      # Пробуем найти разряд в начале pre_date_text
      rank_match = re.match(r'^([A-ZА-Я]{2,4}|[IVX]+(?:\s+юн)?|[1-3](?:\s+юн)?)\s+', pre_date_text, re.IGNORECASE)
      if rank_match:
          rank_token = rank_match.group(1).upper().replace('C', 'С') # Исправляем латиницу
          # Валидация разряда
          valid_ranks = ['МС', 'КМС', 'ЗМС', 'МСМК', 'I', 'II', 'III', '1', '2', '3', 'Б/Р']
          if rank_token in valid_ranks or 'ЮН' in rank_token:
              rank = rank_token
              pre_date_text = pre_date_text[rank_match.end():].strip()
      
      # Если разряд не найден в начале, возможно это место
      # Проверяем, не является ли первый токен числом (местом)
      parts = pre_date_text.split()
      if parts and parts[0].isdigit():
          place = parts[0]
          pre_date_text = ' '.join(parts[1:])
          
          # После места может идти разряд
          if parts[1:] :
              second_part = parts[1]
              if second_part.upper() in ['МС', 'КМС', 'ЗМС', 'МСМК', 'I', 'II', 'III']:
                  rank = second_part.upper()
                  pre_date_text = ' '.join(parts[2:])

      # 4. ФИО - это всё, что осталось в pre_date_text
      full_name = pre_date_text.strip()
      # Убираем лишние буквы/цифры, которые могли прилипнуть к имени
      full_name = re.sub(r'^[\d\s]+', '', full_name).strip() 
      
      if len(full_name) < 3:
          return None

      # 5. Парсинг post_date_text (Команда + Результат)
      team = "Не определено"
      result = None
      normative = None
      points = None

      # Ищем время в post_date_text. 
      # Форматы: 00:15,77 | 15,77 | 1.15,77 | 15.77
      time_pattern = r'(\d{1,2}[.:]\d{2}[.,]\d{2}(?:[.,]\d{2})?)'
      time_match = re.search(time_pattern, post_date_text)
      
      if time_match:
          result = time_match.group(1).replace(',', '.')
          # Команда - это текст ДО времени
          team_candidate = post_date_text[:time_match.start()].strip()
          # Норматив/очки - это текст ПОСЛЕ времени
          norm_candidate = post_date_text[time_match.end():].strip()
          
          # Чистим команду
          if team_candidate:
              # Убираем цифры и точки, которые могли быть частью номера дорожки или мусором
              team = re.sub(r'^[\d\s.:]+', '', team_candidate).strip()
              if not team: team = "Не определено"
          
          # Чистим норматив
          if norm_candidate:
              # Ищем разряд в конце строки (норматив)
              norm_match = re.search(r'([A-ZА-Я]{2,4}|[IVX]+)', norm_candidate)
              if norm_match:
                  normative = norm_match.group(1).upper().replace('C', 'С')
              
              # Ищем очки (число в конце)
              points_match = re.search(r'(\d{1,2})$', norm_candidate)
              if points_match:
                  p = int(points_match.group(1))
                  if p <= 50: points = p

      else:
          # Если времени нет, возможно это DNS/DSQ или ошибка
          if 'DNS' in post_date_text.upper() or 'DSQ' in post_date_text.upper():
              result = 'DNS' if 'DNS' in post_date_text.upper() else 'DSQ'
              team = post_date_text.replace('DNS', '').replace('DSQ', '').strip()
          else:
              # Нет времени - пропускаем строку
              return None

      return {
          "place": place,
          "rank": rank,
          "full_name": full_name.title(),
          "birth_year": birth_year,
          "team": team,
          "result": result,
          "final_Result": None,
          "best_Result": result,
          "normative": normative,
          "points": points,
          "is_manual_timing": is_manual
      }