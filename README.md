### Домашнее задание "Взаимодействие приложений между контейнерами, docker compose"
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
Перейдите в каталог с приложением
```
cd homework_04
```
- Соберите образ
```
docker build .
```
- Запустите приложение с базой данных
```
docker-compose up -d
```
