#!/usr/bin/env python3
"""
export_data.py - gizemuzer.xyz Ziyaretçi Verilerini İndirme & Analiz Aracı
Kullanım: python3 export_data.py
Çıktı: visitors_data.json ve visitors_data.csv
"""

import os
import sys
import json
import csv
import urllib.request
import ssl
from datetime import datetime
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "visitors_data.json")
CSV_FILE = os.path.join(BASE_DIR, "visitors_data.csv")

# Renkler
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[32m"
C_CYAN = "\033[36m"
C_YELLOW = "\033[33m"
C_BEIGE = "\033[38;5;223m"
C_FOREST = "\033[38;5;65m"
C_DIM = "\033[2m"

def main():
    print()
    print(f"{C_FOREST}╔══════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_FOREST}║{C_RESET}  {C_BOLD}{C_BEIGE}GİZEM UZER — ZİYARETÇİ VERİLERİ DIŞA AKTARMA ARACI (EXPORTER){C_RESET} {C_FOREST}║{C_RESET}")
    print(f"{C_FOREST}╚══════════════════════════════════════════════════════════════════╝{C_RESET}")
    print()

    url = "https://gizemuzer.xyz/api/export"
    print(f"📡 {C_DIM}https://gizemuzer.xyz/api/export adresinden veriler çekiliyor...{C_RESET}")

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "GizemUzerExporter/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=12) as res:
            raw = res.read().decode("utf-8")
            data = json.loads(raw)
    except Exception as e:
        print(f"❌ {C_YELLOW}Veri çekilirken hata oluştu: {e}{C_RESET}")
        return

    records = data if isinstance(data, list) else data.get("records", [])

    if not records:
        print()
        print(f"ℹ️  {C_YELLOW}Henüz kaydedilmiş yeni ziyaretçi verisi bulunmuyor veya depolama senkronizasyonu bekleniyor.{C_RESET}")
        print(f"   {C_DIM}Sitenize yeni ziyaretçiler girdikçe bu komut verileri tek tek dosyalara yazacaktır.{C_RESET}")
        print()
        # Create empty template files so user can see format
        sample = [{
            "id": "sample-1",
            "timestamp": datetime.now().isoformat(),
            "ip": "127.0.0.1",
            "country": "TR",
            "city": "Istanbul",
            "region": "34",
            "path": "/blog/sirlarin-sirri-insan-zihninin-gizemi/",
            "referrer": "https://instagram.com/satirarasigzm",
            "device": "iPhone",
            "browser": "Safari",
            "screen": "390x844",
            "language": "tr-TR"
        }]
        records = sample
        print(f"💡 {C_BEIGE}Örnek şablon formatı oluşturuluyor...{C_RESET}")

    # 1. JSON olarak kaydet
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print(f"✅ {C_BOLD}JSON Dosyası Hazır:{C_RESET} {C_CYAN}{JSON_FILE}{C_RESET}")

    # 2. CSV / Excel olarak kaydet
    fieldnames = ["id", "timestamp", "ip", "country", "city", "region", "path", "referrer", "device", "browser", "screen", "language"]
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in records:
            writer.writerow(r)
    print(f"✅ {C_BOLD}CSV (Excel) Dosyası Hazır:{C_RESET} {C_GREEN}{CSV_FILE}{C_RESET}")
    print()

    # 3. İstatistiksel Özet
    countries = Counter(r.get("country", "Unknown") for r in records)
    cities = Counter(r.get("city", "Unknown") for r in records)
    devices = Counter(r.get("device", "Unknown") for r in records)
    pages = Counter(r.get("path", "/") for r in records)

    print(f"{C_BOLD}📊 VERİ ÖZETİ (Toplam {len(records)} Kayıt){C_RESET}")
    print(f"  ├─ Ülkeler:      {', '.join([f'{k} ({v})' for k, v in countries.most_common(3)])}")
    print(f"  ├─ Şehirler:     {', '.join([f'{k} ({v})' for k, v in cities.most_common(3)])}")
    print(f"  ├─ Cihazlar:     {', '.join([f'{k} ({v})' for k, v in devices.most_common(3)])}")
    print(f"  └─ Popüler Sayfa: {pages.most_common(1)[0][0] if pages else '-'}")
    print()
    print(f"🎉 {C_GREEN}Dosyalar diğer projenizde kullanılmak üzere hazır!{C_RESET}")
    print()

if __name__ == "__main__":
    main()
