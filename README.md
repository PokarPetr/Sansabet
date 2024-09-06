# Sansabet
Рефакторинг парсеров Sansabet
1. Цель проекта
Объединить функциональность парсеров предматчевых и live-событий Sansabet в единый парсер, который будет отправлять данные на заданный порт localhost.
2. Требования к функциональности
2.1. Объединение парсеров

Создать модуль, объединяющий функциональность pars_sansa.py и pars_sansa_live.py.
Обеспечить парсинг как предматчевых, так и live-событий.

2.2. Отправка данных

Реализовать механизм отправки собранных данных на заданный порт localhost.
Использовать асинхронный сервер (например, на базе asyncio) для отправки данных.

2.3. Форматирование данных

Унифицировать формат данных для предматчевых и live-событий.
Структура данных должна включать поля стандарта.

2.4. Конфигурация

Создать конфигурационный файл для настройки параметров парсера:

Порт для отправки данных
Интервалы обновления для предматчевых и live-событий
Список видов спорта для парсинга


2.5. Обработка ошибок и логирование

Реализовать систему логирования.
Обеспечить корректную обработку ошибок и исключений.

3. Интерфейс и протокол передачи данных
3.1. Формат сообщений

Использовать JSON для форматирования отправляемых данных.
Структура сообщения должна соответсвовать 
{
  "event_id": 1596508032,
  "match_name": "Nieciecza vs Korona Kielce",
  "start_time": 1725618600.0,
  "home_team": "Nieciecza",
  "away_team": "Korona Kielce",
  "league_id": 1863,
  "league": "Club Friendlies",
  "country": "World",
  "sport": "Football",
  "type": "PreMatch",
  "outcomes": '[
    {
      "type_name": "1X2",
      "type": "1",
      "line": 0,
      "odds": 2.49
    },
    {
      "type_name": "Asian Handicap",
      "type": "AH1",
      "line": 0.0,
      "odds": 1.862
    },
    {
      "type_name": "Total Goals",
      "type": "O",
      "line": 2.75,
      "odds": 1.793
    },
    // ... другие исходы
  ]',
  "time": 1725607715.9000313
}

4. Протокол передачи

Использовать WebSocket для отправки данных на заданный порт.
