import requests
import re
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
        if r.status_code != 200:
            continue

        test_soup = BeautifulSoup(r.text, "html.parser")
        if test_soup.find("div", id="matches-tab"):
            BASE_SITE = test_url
            soup = test_soup
            print(f"✅ Aktif site bulundu: {BASE_SITE}")
            break
    except:
        continue

if not BASE_SITE:
    print("❌ Aktif inattv sitesi bulunamadı")
    exit()

matches_tab = soup.find("div", id="matches-tab")
links = matches_tab.find_all("a")

seen = set()
entries = []

print("\n📡 Kanallar işleniyor...\n")

for a in links:
    href = a.get("href")
    title = a.get_text(strip=True)

    if not href or "channel.html" not in href:
        continue

    channel_url = urljoin(BASE_SITE, href)
    if channel_url in seen:
        continue
    seen.add(channel_url)

    try:
        r2 = requests.get(channel_url, headers=headers, timeout=6)
        if r2.status_code != 200:
            continue

        html = r2.text

        # baseurl yakala
        m = re.search(r'const\s+baseurl\s*=\s*"([^"]+)"', html)
        if not m:
            continue
        baseurl = m.group(1)

        # id al
        parsed = urlparse(channel_url)
        qs = parse_qs(parsed.query)
        if "id" not in qs:
            continue
        stream_id = qs["id"][0]

        m3u8 = f"{baseurl}{stream_id}.m3u8"

        entries.append((title, m3u8))

        print(f"✔ {title}")
        print(f"   → {m3u8}")

    except:
        continue

# 2️⃣ M3U YAZ
if entries:
    with open("inattv.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for title, m3u8 in entries:
            f.write(f"#EXTINF:-1,{title}\n")
            f.write(f"#EXTVLCOPT:http-referrer={BASE_SITE}\n")
            f.write(f"#EXTVLCOPT:http-origin={BASE_SITE}\n")
            f.write(f"{m3u8}\n")

    print("\n🎯 inattv.m3u oluşturuldu (referer + origin eklendi)")
else:
    print("❌ Hiç m3u8 bulunamadı")
