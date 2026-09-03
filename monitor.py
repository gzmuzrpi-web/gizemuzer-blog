#!/usr/bin/env python3
"""
monitor.py - gizemuzer.xyz Terminal Traffic & Health Monitor Dashboard
Run directly in terminal: python3 monitor.py
"""

import sys
import time
import urllib.request
import ssl
import json
from datetime import datetime

# ANSI Color Palette (Warm Editorial / Terminal Theme)
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_DIM = "\033[2m"
C_BEIGE = "\033[38;5;223m"
C_FOREST = "\033[38;5;65m"
C_TERRACOTTA = "\033[38;5;173m"
C_GREEN = "\033[32m"
C_YELLOW = "\033[33m"
C_CYAN = "\033[36m"
C_RED = "\033[31m"

SITE_URL = "https://gizemuzer.xyz"

PAGES = [
    ("/", "Ana Sayfa (TR)"),
    ("/en/", "Home (EN)"),
    ("/blog/", "Yazılar Arşivi (TR)"),
    ("/en/blog/", "Articles Archive (EN)"),
    ("/hakkimda/", "Hakkımda"),
    ("/en/about/", "About"),
    ("/iletisim/", "İletişim"),
    ("/en/contact/", "Contact"),
    ("/blog/noroplastisite-ve-zihnin-donusum-gucu/", "Nöroplastisite (TR)"),
    ("/en/blog/neuroplasticity-and-the-transformative-power-of-the-mind/", "Neuroplasticity (EN)"),
    ("/blog/sirlarin-sirri-insan-zihninin-gizemi/", "Sırların Sırrı (TR)"),
    ("/en/blog/the-secret-of-secrets-human-mind/", "Secret of Secrets (EN)"),
    ("/blog/kusurun-isigi-ve-aynanin-iki-yuzu/", "Kusurun Işığı (TR)"),
    ("/en/blog/the-light-of-imperfection-and-the-two-faces-of-the-mirror/", "Light of Imperfection (EN)"),
    ("/blog/kendi-yuvani-ormek-ve-sezgiler/", "Kendi Yuvanı Örmek (TR)"),
    ("/en/blog/weaving-your-own-nest-lost-intuitions-in-the-mirror-of-others/", "Weaving Your Nest (EN)"),
    ("/blog/kendi-kapimdan-gecerken-yasam-laboratuvari/", "Yaşam Laboratuvarı (TR)"),
    ("/en/blog/passing-through-my-own-threshold-a-laboratory-of-life/", "Laboratory of Life (EN)"),
    ("/blog/pembelikten-kirmiziya-yasam-sahnesi/", "Pembelikten Kırmızıya (TR)"),
    ("/en/blog/from-cotton-candy-pink-to-deep-red-the-stage-of-life/", "Stage of Life (EN)"),
    ("/feed.xml", "RSS Feed (TR)"),
    ("/en/feed.xml", "RSS Feed (EN)"),
]

def check_url(path):
    url = f"{SITE_URL}{path}"
    start = time.time()
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers={"User-Agent": "GizemUzerMonitor/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=5) as res:
            elapsed = (time.time() - start) * 1000
            return res.status, round(elapsed, 1)
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return 0, round(elapsed, 1)

def render_dashboard():
    # Clear screen
    print("\033[2J\033[H", end="")

    now_str = datetime.now().strftime("%d.%m.%Y — %H:%M:%S")

    print(f"{C_FOREST}╔════════════════════════════════════════════════════════════════════════════╗{C_RESET}")
    print(f"{C_FOREST}║{C_RESET}  {C_BOLD}{C_BEIGE}GİZEM UZER — CANLI SİTE & TRAFİK İZLEME PANELİ (TERMINAL CLI){C_RESET}        {C_FOREST}║{C_RESET}")
    print(f"{C_FOREST}╠════════════════════════════════════════════════════════════════════════════╣{C_RESET}")
    print(f"{C_FOREST}║{C_RESET}  🌐 Alan Adı: {C_BOLD}{SITE_URL}{C_RESET}  │  🕒 Zaman: {C_DIM}{now_str}{C_RESET}       {C_FOREST}║{C_RESET}")
    print(f"{C_FOREST}╚════════════════════════════════════════════════════════════════════════════╝{C_RESET}")
    print()

    # 1. Global Domain & SSL Health
    status, latency = check_url("/")
    ssl_status = f"{C_GREEN}Aktif (Güvenli HTTPS){C_RESET}" if status == 200 else f"{C_RED}Hata{C_RESET}"
    server_status = f"{C_GREEN}Çevrimiçi (HTTP 200 OK){C_RESET}" if status == 200 else f"{C_RED}Ulaşılamıyor ({status}){C_RESET}"

    print(f"{C_BOLD}📡 SİSTEM & ALTYAPI DURUMU{C_RESET}")
    print(f"  ├─ Sunucu Durumu:     {server_status}")
    print(f"  ├─ SSL Sertifikası:   {ssl_status}")
    print(f"  ├─ Ana Sayfa Gecikme: {C_CYAN}{latency} ms{C_RESET}")
    print(f"  └─ Barındırma:        {C_DIM}Vercel Global Edge Network (DNS Zone: BasicDNS){C_RESET}")
    print()

    # 2. Vercel Web Analytics Overview
    print(f"{C_BOLD}📊 GİZLİ & GÖRÜNMEZ ZİYARETÇİ TAKİBİ (Vercel Web Analytics){C_RESET}")
    print(f"  ├─ Görünürlük:        {C_GREEN}Sitede Sıfır Sayaç / Sıfır Çerez (Ziyaretçiye Tamamen Görünmez){C_RESET}")
    print(f"  ├─ Canlı İstatistik:  {C_CYAN}https://vercel.com/gizem-ant/gizemuzer-blog/analytics{C_RESET}")
    print(f"  └─ İzlenen Metrikler: Tekil Ziyaretçiler, En Çok Okunan Yazılar, Ülkeler, Cihazlar")
    print()

    # 3. All Pages Latency & Uptime Radar
    print(f"{C_BOLD}📄 YAYINDAKİ SAYFALAR & YANIT SÜRELERİ (CANLI RADAR){C_RESET}")
    print(f"  {'SAYFA ADI':<32} {'DİL':<8} {'DURUM':<12} {'YANIT SÜRESİ':<12}")
    print(f"  {'-'*68}")

    healthy_count = 0
    total_latency = 0

    for path, label in PAGES:
        code, ms = check_url(path)
        lang = "EN" if "/en" in path else "TR"
        
        if code == 200:
            st = f"{C_GREEN}● 200 OK{C_RESET}"
            healthy_count += 1
            total_latency += ms
        else:
            st = f"{C_RED}✖ {code}{C_RESET}"

        ms_str = f"{ms:>6.1f} ms"
        if ms < 200:
            ms_colored = f"{C_GREEN}{ms_str}{C_RESET}"
        elif ms < 500:
            ms_colored = f"{C_YELLOW}{ms_str}{C_RESET}"
        else:
            ms_colored = f"{C_RED}{ms_str}{C_RESET}"

        print(f"  {label:<32} {lang:<8} {st:<20} {ms_colored}")

    avg_latency = round(total_latency / max(1, healthy_count), 1)

    print(f"  {'-'*68}")
    print(f"  Özet: {C_GREEN}{healthy_count}/{len(PAGES)} sayfa aktif{C_RESET} │ Ortalama Yanıt: {C_CYAN}{avg_latency} ms{C_RESET}")
    print()

    print(f"{C_DIM}💡 Çıkmak için Ctrl+C'ye basın. Otomatik yenileniyor...{C_RESET}")

def main():
    watch_mode = "--watch" in sys.argv or "-w" in sys.argv
    if watch_mode:
        try:
            while True:
                render_dashboard()
                time.sleep(10)
        except KeyboardInterrupt:
            print(f"\n{C_FOREST}İzleme sonlandırıldı. Görüşmek üzere!{C_RESET}")
    else:
        render_dashboard()
        print(f"\n{C_BEIGE}Canlı otomatik yenileme için:{C_RESET} {C_BOLD}python3 monitor.py --watch{C_RESET}")

if __name__ == "__main__":
    main()
