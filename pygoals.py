name: Inattv JSON Generator

on:
  schedule:
    - cron: "*/4 * * * *"   # 4 dakikada bir
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Repo checkout
        uses: actions/checkout@v4

      - name: Python kur
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Python paketleri
        run: |
          pip install requests beautifulsoup4

      - name: Scripti çalıştır
        run: |
          python pygoals.py

      # === JSON'u SUNUCUYA GÖNDER ===
      - name: Upload inattv.json via SFTP
        uses: appleboy/scp-action@v0.1.7
        with:
          host: 82.29.189.156
          port: 65002
          username: u719601221
          password: ${{ secrets.SFTP_PASSWORD }}
          source: "inattv.json"
          target: "/home/u719601221/public_html/1/"
          overwrite: true
