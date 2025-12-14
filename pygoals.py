import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

START = 1210
END = 1250

BASE_SITE = None
soup = None

print("🔍 Aktif inattv domaini aranıyor...")

# 1️⃣ AKTİF DOMAIN BUL
for i in range(START, END + 1):
    test_url = f"https://inattv{i}.xyz/"
    try:
        r = requests.get(test_url, headers=headers, timeout=6)
        r.encoding = "utf-8"  # ✅ TÜRKÇE FIX
        if r.status_code != 200:
            continue

        test_soup = BeautifulSoup(r.text, "html.parser")
        if test_soup.find("div", id="matches-tab"):
            BASE_SITE = test_url
            soup = test_soup
            print(f"✅ Aktif site bulundu: {BASE_SITE}")
            break
    except Exception as e:
        continue

if not BASE_SITE:
    print("❌ Aktif site bulunamadı")
    exit()

matches_tab = soup.find("div", id="matches-tab")
links = matches_tab.find_all("a")

items = []
seen = set()

print("\n📡 Kanallar işleniyor...\n")

for a in links:
    href = a.get("href")
    if not href or "channel.html" not in href:
        continue

    channel_url = urljoin(BASE_SITE, href)
    if channel_url in seen:
        continue
    seen.add(channel_url)

    # 🏷️ KANAL ADI
    title_div = a.find("div", class_="channel-name")
    title = title_div.get_text(strip=True) if title_div else a.get_text(strip=True)

    # ⏰ SAAT
    time_div = a.find("div", class_="channel-status")
    match_time = time_div.get_text(strip=True) if time_div else ""

    try:
        r2 = requests.get(channel_url, headers=headers, timeout=6)
        r2.encoding = "utf-8"  # ✅ TÜRKÇE FIX
        if r2.status_code != 200:
            continue

        html = r2.text

        # baseurl yakala
        m = re.search(r'const\s+baseurl\s*=\s*"([^"]+)"', html)
        if not m:
            continue
        baseurl = m.group(1)

        # id yakala
        parsed = urlparse(channel_url)
        qs = parse_qs(parsed.query)
        if "id" not in qs:
            continue
        stream_id = qs["id"][0]

        m3u8 = f"{baseurl}{stream_id}.m3u8"

        items.append({
            "service": "iptv",
            "title": title,                # ✅ TÜRKÇE TEMİZ
            "playlistURL": "",
            "media_url": m3u8,
            "url": m3u8,
            "h1Key": "accept",
            "h1Val": "*/*",
            "h2Key": "referer",
            "h2Val": BASE_SITE,
            "h3Key": "origin",
            "h3Val": BASE_SITE.rstrip("/"),
            "h4Key": "0",
            "h4Val": "0",
            "h5Key": "0",
            "h5Val": "0",
            "thumb_square": "https://i.hizliresim.com/gm27zjl.png",
            "group": match_time             # ✅ SAAT BURADA
        })

        print(f"✔ {title} [{match_time}]")

    except Exception as e:
        continue

output = {
    "list": {
        "service": "iptv",
        "title": "iptv",
        "item": items
    }
}

with open("tine1.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n🎯 inattv.json başarıyla oluşturuldu (UTF-8, Türkçe sorunsuz)")
