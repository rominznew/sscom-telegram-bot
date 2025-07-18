name: Test Telegram Bot

on:
  workflow_dispatch:  # запуск вручную

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Установить зависимости
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Запуск test_bot.py
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          CHAT_ID: ${{ secrets.CHAT_ID }}
        run: python test_bot.py
