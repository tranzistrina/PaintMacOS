# PaintMacOS

Flask + HTML/CSS/JavaScript Paint для macOS.

Возможности:
- рисование мышью или трекпадом;
- цвет кисти;
- размер кисти 1-80;
- импорт изображения;
- экспорт PNG;
- очистка холста;
- копирование холста в буфер обмена.

## Запуск

cd /Users/inh/Desktop/lab/PaintMacOS
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 app.py

Открыть в браузере:

http://127.0.0.1:7789
