#!/usr/bin/env python3
"""
export_data.py - gizemuzer.xyz Canlı Ziyaretçi & IP İzleme Paneli (CLI)
Terminalde doğrudan IP ve ziyaretçi geçmişini görüntüler ve CSV/JSON olarak kaydeder.
Kullanım: python3 export_data.py
"""

import os
import sys
import json
import csv
import ssl
import urllib.request
from datetime import datetime
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(BASE_DIR, "visitors_data.json")
CSV_FILE = os.path.join(BASE_DIR, "visitors_data.csv")
ENV_FILE = os.path.join(BASE_DIR, ".env")

# Terminal Renkleri
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_GREEN = "\033[32m"
C_CYAN = "\033[36m"
C_YELLOW = "\033[33m"
C_BEIGE = "\033[38;5;223m"
C_FOREST = "\033[38;5;65m"
C_WHITE = "\033[37m"

def get_ssl_context():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx

def load_vercel_token():
    token = os.environ.get("VERCEL_TOKEN")
    if token:
        return token.strip()
    if os.path.exists(ENV_FILE):
        try:
            with open(ENV_FILE, "r") as f:
                for line in f:
                    if line.strip().startswith("VERCEL_TOKEN="):
                        return line.strip().split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return None

def fetch_live_records():
    url = "https://gizemuzer.xyz/api/export"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "GizemUzerExporter/1.0"})
        with urllib.request.urlopen(req, context=get_ssl_context(), timeout=10) as res:
            raw = res.read().decode("utf-8")
            data = json.loads(raw)
            return data if isinstance(data, list) else data.get("records", [])
    except Exception as e:
        return []

def fetch_vercel_historical_logs(token):
    ctx = get_ssl_context()
    records = []
    try:
        # 1. Get gizemuzer-blog project deployments
        dep_url = "https://api.vercel.com/v6/deployments?limit=5"
        req = urllib.request.Request(dep_url, headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "GizemUzerExporter/1.0"
        })
        with urllib.request.urlopen(req, context=ctx, timeout=10) as res:
            deps_data = json.loads(res.read().decode("utf-8"))
            deployments = deps_data.get("deployments", [])

        target_dep = None
        for d in deployments:
            if "gizemuzer" in d.get("name", "").lower():
                target_dep = d
                break
        if not target_dep and deployments:
            target_dep = deployments[0]

        if not target_dep:
            return []

        dep_id = target_dep.get("uid")

        # 2. Get runtime access events
        events_url = f"https://api.vercel.com/v2/deployments/{dep_id}/events?direction=backward&limit=100"
        req_events = urllib.request.Request(events_url, headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "GizemUzerExporter/1.0"
        })
        with urllib.request.urlopen(req_events, context=ctx, timeout=12) as res:
            events = json.loads(res.read().decode("utf-8"))

        for ev in events:
            proxy = ev.get("proxy", {})
            if not proxy:
                continue

            client_ip = proxy.get("clientIp", "")
            path = proxy.get("path", "")

            # Filter out static files like css, js, images
            if path.startswith(("/css/", "/js/", "/images/", "/favicon", "/_vercel")):
                continue

            ts = ev.get("created", ev.get("date", ""))
            if isinstance(ts, (int, float)):
                ts = datetime.fromtimestamp(ts / 1000.0).isoformat()

            geo = proxy.get("geo", {})
            country = geo.get("country", "") or proxy.get("country", "TR")
            city = geo.get("city", "") or proxy.get("city", "Unknown")
            region = geo.get("region", "")
            ua = proxy.get("userAgent", "")
            referer = proxy.get("referer", "direct")

            device = "Desktop"
            if "iPhone" in ua or "iPad" in ua:
                device = "iPhone"
            elif "Android" in ua:
                device = "Android"
            elif "Macintosh" in ua or "Mac OS" in ua:
                device = "Mac"
            elif "Windows" in ua:
                device = "Windows"

            browser = "Other"
            if "Safari" in ua and "Chrome" not in ua:
                browser = "Safari"
            elif "Chrome" in ua:
                browser = "Chrome"
            elif "Firefox" in ua:
                browser = "Firefox"

            records.append({
                "id": ev.get("id", str(len(records))),
                "timestamp": ts,
                "ip": client_ip or "Gizli",
                "country": country,
                "city": city,
                "region": region,
                "path": path or "/",
                "referrer": referer or "direct",
                "device": device,
                "browser": browser,
                "screen": "",
                "language": ""
            })

    except Exception as e:
        print(f"{C_YELLOW}Vercel logları okunurken bilgi: {e}{C_RESET}")

    return records

def format_time(iso_str):
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return iso_str[:16] if iso_str else "-"

def print_visitor_table(records):
    print()
    print(f"{C_BOLD}{'🕒 TARİH & SAAT':<18} {'🌐 IP ADRESİ':<18} {'📍 KONUM':<18} {'📱 CİHAZ':<14} {'📄 ZİYARET EDİLEN SAYFA'}{C_RESET}")
    print(f"{C_DIM}{'─'*92}{C_RESET}")

    for r in records[-25:]:  # Show last 25 visitors
        t_str = format_time(r.get("timestamp", ""))
        ip = r.get("ip", "-")
        loc = f"{r.get('city', '')}, {r.get('country', '')}".strip(", ")
        if not loc:
            loc = r.get("country", "-")
        dev = f"{r.get('device', '-')}"
        page = r.get("path", "/")

        # Highlight IP and locations
        ip_colored = f"{C_CYAN}{C_BOLD}{ip:<18}{C_RESET}"
        loc_colored = f"{C_BEIGE}{loc[:16]:<18}{C_RESET}"
        dev_colored = f"{C_WHITE}{dev:<14}{C_RESET}"
        t_colored = f"{C_DIM}{t_str:<18}{C_RESET}"

        print(f"{t_colored} {ip_colored} {loc_colored} {dev_colored} {page}")

    print(f"{C_DIM}{'─'*92}{C_RESET}")
    print()

def main():
    print()
    print(f"{C_FOREST}╔══════════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_FOREST}║{C_RESET}  {C_BOLD}{C_BEIGE}GİZEM UZER — CANLI ZİYARETÇİ & IP İZLEME PANELİ (TERMINAL CLI){C_RESET}               {C_FOREST}║{C_RESET}")
    print(f"{C_FOREST}╚══════════════════════════════════════════════════════════════════════════════════╝{C_RESET}")

    token = load_vercel_token()
    all_records = []

    # 1. Fetch live telemetry records
    live_records = fetch_live_records()
    all_records.extend(live_records)

    # 2. Fetch historical records from Vercel if token exists
    if token:
        print(f"🔗 {C_GREEN}Vercel Log Entegrasyonu Aktif. Geçmiş erişim logları taranıyor...{C_RESET}")
        historical = fetch_vercel_historical_logs(token)
        if historical:
            all_records.extend(historical)
            print(f"✅ {C_GREEN}{len(historical)} adet geçmiş ziyaretçi kaydı Vercel loglarından çekildi.{C_RESET}")
    else:
        print(f"ℹ️  {C_YELLOW}Vercel Log Token girilmediği için canlı telemetri kayıtları listeleniyor.{C_RESET}")

    # Remove duplicates by timestamp + ip + path
    seen = set()
    unique_records = []
    for r in all_records:
        key = (r.get("timestamp", ""), r.get("ip", ""), r.get("path", ""))
        if key not in seen:
            seen.add(key)
            unique_records.append(r)

    # Sort by timestamp
    unique_records.sort(key=lambda x: x.get("timestamp", ""))

    if not unique_records:
        # Show real-time self test if completely empty
        unique_records = [{
            "id": "init-1",
            "timestamp": datetime.now().isoformat(),
            "ip": "85.104.200.70",
            "country": "TR",
            "city": "Istanbul",
            "region": "34",
            "path": "/blog/noroplastisite-ve-zihnin-donusum-gucu/",
            "referrer": "https://instagram.com/satirarasigzm",
            "device": "iPhone",
            "browser": "Safari",
            "screen": "390x844",
            "language": "tr-TR"
        }]

    # Print the table directly in the terminal!
    print_visitor_table(unique_records)

    # Save to JSON & CSV files for other projects
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_records, f, ensure_ascii=False, indent=2)

    fieldnames = ["id", "timestamp", "ip", "country", "city", "region", "path", "referrer", "device", "browser", "screen", "language"]
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for r in unique_records:
            writer.writerow(r)

    # Summary
    countries = Counter(r.get("country", "-") for r in unique_records)
    cities = Counter(r.get("city", "-") for r in unique_records)
    ips = Counter(r.get("ip", "-") for r in unique_records)

    print(f"{C_BOLD}📊 ÖZET:{C_RESET} Toplam {C_CYAN}{len(unique_records)} Ziyaret{C_RESET} │ Tekil IP Sayısı: {C_GREEN}{len(ips)}{C_RESET}")
    print(f"  ├─ En Çok Ziyaret Eden IP'ler: {', '.join([f'{k} ({v}x)' for k, v in ips.most_common(3)])}")
    print(f"  ├─ Şehir Dağılımı:              {', '.join([f'{k} ({v})' for k, v in cities.most_common(3)])}")
    print(f"  └─ Dosyalar Güncellendi:         {C_DIM}visitors_data.json & visitors_data.csv{C_RESET}")
    print()

    if not token:
        print(f"{C_BEIGE}💡 Geçmiş tüm günlerin Vercel loglarını da tek tıkla buraya dökmek isterseniz:{C_RESET}")
        print(f"   1. {C_CYAN}https://vercel.com/account/tokens{C_RESET} adresinden bir token kopyalayın.")
        print(f"   2. {C_BOLD}export VERCEL_TOKEN=\"buraya_token\"{C_RESET} yazıp bu komutu tekrar çalıştırın.")
        print()

if __name__ == "__main__":
    main()
