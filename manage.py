#!/usr/bin/env python3
"""
manage.py - gizemuzer.com Content & Site Management CLI
Enables both Gizem and Antigravity to easily create, edit, list, build, and serve blog posts.
"""

import sys
import os
import argparse
import re
from datetime import datetime
from pathlib import Path
import http.server
import socketserver

BASE_DIR = Path(__file__).resolve().parent
BLOG_DIR = BASE_DIR / "content" / "blog"
DIST_DIR = BASE_DIR / "dist"

def slugify(text):
    text = text.lower()
    text = text.replace("ı", "i").replace("ğ", "g").replace("ü", "u").replace("ş", "s").replace("ö", "o").replace("ç", "c")
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text).strip('-')
    return text

def cmd_new(args):
    title = args.title
    slug = args.slug or slugify(title)
    tags = [t.strip() for t in args.tags.split(",")] if args.tags else ["Genel"]
    excerpt = args.excerpt or f"{title} üzerine düşünceler ve notlar."
    date_str = datetime.now().strftime("%Y-%m-%d")
    filename = f"{slug}.md"
    file_path = BLOG_DIR / filename

    if file_path.exists():
        print(f"⚠️ Hata: {filename} dosyası zaten mevcut!")
        return

    tags_formatted = "[" + ", ".join(tags) + "]"
    content = f"""---
title: {title}
date: {date_str}
slug: {slug}
excerpt: {excerpt}
tags: {tags_formatted}
featured: false
draft: true
---

Yazınızın giriş paragrafını buraya yazın.

## İlk Alt Başlık

Düşüncelerinizi detaylandırın...
"""
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    print(f"✅ Yeni taslak yazı oluşturuldu:")
    print(f"   Dosya: content/blog/{filename}")
    print(f"   Slug: {slug}")
    print(f"   Durum: Taslak (draft: true)")
    print(f"\nYazıyı düzenledikten sonra yayına almak için:")
    print(f"   python3 manage.py publish {slug}")

def cmd_list(args):
    from builder import parse_frontmatter
    print("\n📚 gizemuzer.com Blog Yazıları Listesi:")
    print("-" * 75)
    print(f"{'DURUM':<10} {'TARİH':<12} {'SLUG':<30} {'BAŞLIK'}")
    print("-" * 75)
    
    posts = []
    for md_file in BLOG_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(content)
        posts.append({
            "draft": meta.get("draft", False),
            "date": str(meta.get("date", "")),
            "slug": meta.get("slug", md_file.stem),
            "title": meta.get("title", md_file.stem),
        })
    
    posts.sort(key=lambda x: x["date"], reverse=True)
    for p in posts:
        status = "📝 Taslak" if p["draft"] else "🟢 Yayında"
        print(f"{status:<10} {p['date']:<12} {p['slug']:<30} {p['title']}")
    print("-" * 75)
    print(f"Toplam {len(posts)} yazı bulundu.\n")

def cmd_publish(args):
    slug = args.slug
    found = False
    for md_file in BLOG_DIR.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        if f"slug: {slug}" in content or md_file.stem == slug:
            content = re.sub(r'draft:\s*true', 'draft: false', content)
            md_file.write_text(content, encoding="utf-8")
            print(f"🎉 '{slug}' başlıklı yazı yayınlandı (draft: false)!")
            found = True
            break
    if not found:
        print(f"❌ '{slug}' bulunamadı.")
        return

    # Rebuild
    from builder import build_site
    build_site()

def cmd_build(args):
    from builder import build_site
    build_site()

def cmd_serve(args):
    port = args.port
    from builder import build_site
    build_site()

    os.chdir(DIST_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\n🌐 Blog yerel önizleme sunucusu aktif!")
        print(f"👉 Tarayıcınızda açın: http://localhost:{port}")
        print("Durdurmak için Ctrl + C tuşlarına basın.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSunucu kapatıldı.")

def main():
    parser = argparse.ArgumentParser(description="gizemuzer.com Yönetim Aracı")
    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # new
    p_new = subparsers.add_parser("new", help="Yeni bir blog yazısı oluştur")
    p_new.add_argument("title", help="Yazı başlığı")
    p_new.add_argument("--slug", help="Özel URL slug (opsiyonel)")
    p_new.add_argument("--tags", help="Virgülle ayrılmış etiketler (örn: Teknoloji,Yapay Zeka)")
    p_new.add_argument("--excerpt", help="Kısa özet")

    # list
    subparsers.add_parser("list", help="Mevcut yazıları listele")

    # publish
    p_pub = subparsers.add_parser("publish", help="Taslak yazıyı yayına al")
    p_pub.add_argument("slug", help="Yazının slug değeri")

    # build
    subparsers.add_parser("build", help="Statik siteyi derle (dist/)")

    # serve
    p_serve = subparsers.add_parser("serve", help="Yerel önizleme sunucusunu başlat")
    p_serve.add_argument("--port", type=int, default=8080, help="Port (varsayılan: 8080)")

    args = parser.parse_args()
    if args.command == "new":
        cmd_new(args)
    elif args.command == "list":
        cmd_list(args)
    elif args.command == "publish":
        cmd_publish(args)
    elif args.command == "build":
        cmd_build(args)
    elif args.command == "serve":
        cmd_serve(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
