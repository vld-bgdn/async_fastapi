### Домашнее задание "Асинхронная работа с сетью и БД"
## Установка
- Склонируейте репозиторий и перейдите в него:
```
git clone https://github.com/vld-bgdn/async_fastapi.git
cd async_fastapi
```
- Активируйте виртуальное окружение:
```
python -m venv .venv ; source .venv/bin/activate
```
- Установите зависимости через pip (для приложения и для тестов):
```
python -m pip install -r ./requirements.txt
python -m pip install -r ./requirements-dev.txt
```
- Запустите базу данных
```
docker-compose up -d
```
- Запустите приложение
```
python main.py
```
- Запустите тест
```
python -m pytest ../testing/test_homework_04/test_main.py -vv
```
