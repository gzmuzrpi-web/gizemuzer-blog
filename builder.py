#!/usr/bin/env python3
"""
builder.py - gizemuzer.xyz Bilingual Static Site Generator (TR & EN)
Zero external dependencies, fast, semantic, high accessibility, and full i18n routing.
"""

import os
import re
import shutil
import html
from datetime import datetime
from pathlib import Path

SITE_URL = "https://gizemuzer.xyz"
AUTHOR_NAME = "Gizem Uzer"

BASE_DIR = Path(__file__).resolve().parent
CONTENT_DIR = BASE_DIR / "content"
BLOG_DIR = CONTENT_DIR / "blog"
BLOG_EN_DIR = CONTENT_DIR / "blog" / "en"
PAGES_DIR = CONTENT_DIR / "pages"
PAGES_EN_DIR = CONTENT_DIR / "pages" / "en"
STATIC_DIR = BASE_DIR / "static"
DIST_DIR = BASE_DIR / "dist"

MONTHS_TR = {
    1: "Ocak", 2: "Şubat", 3: "Mart", 4: "Nisan", 5: "Mayıs", 6: "Haziran",
    7: "Temmuz", 8: "Ağustos", 9: "Eylül", 10: "Ekim", 11: "Kasım", 12: "Aralık"
}

MONTHS_EN = {
    1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"
}

I18N = {
    "tr": {
        "site_title": "Gizem Uzer",
        "site_tagline": "Düşünceler, yazılar ve dijital bahçe",
        "site_description": "Gizem Uzer'in edebiyat, sade yaşam, gözlemler ve yaratıcı üretim üzerine kişisel notları ve denemeleri.",
        "author_bio": "Düşüncelerini, edebiyata ve hayata dair gözlemlerini dijital bahçesinde paylaşan bir yazar.",
        "nav_home": "Ana Sayfa",
        "nav_blog": "Yazılar",
        "nav_about": "Hakkımda",
        "nav_contact": "İletişim",
        "all_essays": "Tüm Yazılara Dön",
        "read_time_suffix": "okuma",
        "read_more": "Devamını Oku →",
        "explore_post": "Yazıyı İncele →",
        "featured": "Öne Çıkan Düşünceler",
        "view_all": "Tümünü Gör →",
        "recent": "Son Eklenenler",
        "archive": "Arşive Git →",
        "hero_tag": "✨ Kişisel Blog & Dijital Bahçe",
        "hero_title": "Düşünceler, yazılar ve keşifler.",
        "hero_lead": "Merhaba, ben <strong>Gizem Uzer</strong>. Edebiyat, hayat, içsel yolculuklar ve felsefe üzerine fikirlerimi demlediğim kişisel alanıma hoş geldiniz.",
        "hero_btn_explore": "Yazıları Keşfet →",
        "hero_btn_about": "Hakkımda",
        "filter_all": "Tümü",
        "search_placeholder": "Yazılarda ara (başlık veya konu)...",
        "blog_title": "Yazılar & Düşünceler",
        "blog_desc": "Edebiyat, gözlemler, içsel yolculuklar ve hayata dair notlar.",
        "newsletter_title": "Yeni Yazılardan Haberdar Olun",
        "newsletter_desc": "Yalnızca gerçekten paylaşmaya değer yeni bir düşünce ya da deneme yayınladığımda gelen sakin bir e-posta bülteni.",
        "newsletter_placeholder": "E-posta adresiniz...",
        "newsletter_btn": "Abone Ol",
        "newsletter_alert": "Teşekkürler! Bülten listesine eklendiniz.",
        "footer_rights": "Tüm hakları saklıdır.",
        "footer_email": "E-posta",
        "footer_rss": "RSS",
        "switch_prompt": "🌐 This article is also available in English:",
        "switch_action": "Read in English ➔",
    },
    "en": {
        "site_title": "Gizem Uzer",
        "site_tagline": "Reflections, articles & digital garden",
        "site_description": "Personal articles, reflections on literature, authenticity, and human nature by Gizem Uzer.",
        "author_bio": "A writer exploring thoughts, literature, and human nature in her quiet digital garden.",
        "nav_home": "Home",
        "nav_blog": "Articles",
        "nav_about": "About",
        "nav_contact": "Contact",
        "all_essays": "Back to All Articles",
        "read_time_suffix": "read",
        "read_more": "Read More →",
        "explore_post": "Read Article →",
        "featured": "Featured Articles",
        "view_all": "View All →",
        "recent": "Recent Articles",
        "archive": "Go to Archive →",
        "hero_tag": "✨ Personal Space & Digital Garden",
        "hero_title": "Thoughts, articles and discoveries.",
        "hero_lead": "Hello, I am <strong>Gizem Uzer</strong>. Welcome to my personal sanctuary where ideas on literature, human nature, and life’s subtle nuances steep without haste.",
        "hero_btn_explore": "Explore Articles →",
        "hero_btn_about": "About Me",
        "filter_all": "All",
        "search_placeholder": "Search articles (title or topic)...",
        "blog_title": "Articles & Reflections",
        "blog_desc": "Notes on literature, personal philosophy, human nature, and life.",
        "newsletter_title": "Stay Connected",
        "newsletter_desc": "A quiet email note, sent only when a new piece truly worth sharing is published.",
        "newsletter_placeholder": "Your email address...",
        "newsletter_btn": "Subscribe",
        "newsletter_alert": "Thank you! You have been added to the newsletter.",
        "footer_rights": "All rights reserved.",
        "footer_email": "Email",
        "footer_rss": "RSS",
        "switch_prompt": "🌐 Bu yazıyı Türkçe oku:",
        "switch_action": "Türkçe Oku ➔",
    }
}

def format_date(date_val, lang="tr"):
    if isinstance(date_val, str):
        try:
            dt = datetime.strptime(date_val.strip(), "%Y-%m-%d")
        except ValueError:
            return date_val
    elif isinstance(date_val, datetime):
        dt = date_val
    else:
        return str(date_val)

    if lang == "tr":
        return f"{dt.day} {MONTHS_TR.get(dt.month, '')} {dt.year}"
    else:
        return f"{MONTHS_EN.get(dt.month, '')} {dt.day}, {dt.year}"

def parse_frontmatter(content):
    metadata = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            raw_meta = parts[1]
            body = parts[2]
            for line in raw_meta.strip().splitlines():
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip()
                    if val.lower() == "true":
                        metadata[key] = True
                    elif val.lower() == "false":
                        metadata[key] = False
                    elif val.startswith("[") and val.endswith("]"):
                        items = [x.strip() for x in val[1:-1].split(",") if x.strip()]
                        metadata[key] = items
                    else:
                        metadata[key] = val
    return metadata, body.strip()

def calculate_reading_time(text, lang="tr"):
    words = len(text.split())
    minutes = max(1, round(words / 180))
    suffix = I18N[lang]["read_time_suffix"]
    return f"{minutes} dk {suffix}" if lang == "tr" else f"{minutes} min {suffix}"

def markdown_to_html(md_text):
    lines = md_text.splitlines()
    html_out = []
    in_code_block = False
    code_lang = ""
    code_buffer = []
    in_list = False
    list_tag = "ul"
    in_quote = False
    quote_buffer = []

    def flush_list():
        nonlocal in_list, list_tag
        if in_list:
            html_out.append(f"</{list_tag}>")
            in_list = False

    def flush_quote():
        nonlocal in_quote, quote_buffer
        if in_quote:
            content = " ".join(quote_buffer)
            html_out.append(f"<blockquote>{inline_markdown(content)}</blockquote>")
            quote_buffer = []
            in_quote = False

    def inline_markdown(text):
        # Images: ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img src="\2" alt="\1" loading="lazy">', text)
        # Bold: **text**
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        # Italic: *text*
        text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
        # Inline code: `code`
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Links: [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        return text

    for line in lines:
        stripped = line.strip()

        # Code block
        if stripped.startswith("```"):
            if in_code_block:
                escaped = html.escape("\n".join(code_buffer))
                html_out.append(f'<pre><code class="language-{code_lang}">{escaped}</code></pre>')
                code_buffer = []
                in_code_block = False
            else:
                flush_list()
                flush_quote()
                code_lang = stripped[3:].strip()
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        # Horizontal rule
        if re.match(r'^(---|___|\*\*\*)$', stripped):
            flush_list()
            flush_quote()
            html_out.append("<hr>")
            continue

        # Blockquote
        if stripped.startswith(">"):
            flush_list()
            in_quote = True
            quote_buffer.append(stripped[1:].strip())
            continue
        elif in_quote:
            if stripped == "":
                flush_quote()
                continue
            else:
                quote_buffer.append(stripped)
                continue

        # Headings
        if stripped.startswith("### "):
            flush_list()
            flush_quote()
            html_out.append(f"<h3>{inline_markdown(stripped[4:])}</h3>")
            continue
        elif stripped.startswith("## "):
            flush_list()
            flush_quote()
            html_out.append(f"<h2>{inline_markdown(stripped[3:])}</h2>")
            continue
        elif stripped.startswith("# "):
            flush_list()
            flush_quote()
            html_out.append(f"<h1>{inline_markdown(stripped[2:])}</h1>")
            continue

        # Lists
        ul_match = re.match(r'^[-*+]\s+(.+)$', stripped)
        ol_match = re.match(r'^\d+\.\s+(.+)$', stripped)

        if ul_match or ol_match:
            flush_quote()
            cur_tag = "ol" if ol_match else "ul"
            item_content = (ol_match or ul_match).group(1)

            if not in_list or list_tag != cur_tag:
                flush_list()
                list_tag = cur_tag
                html_out.append(f"<{list_tag}>")
                in_list = True

            html_out.append(f"  <li>{inline_markdown(item_content)}</li>")
            continue
        else:
            flush_list()

        # Paragraphs
        if stripped == "":
            flush_quote()
            continue

        flush_quote()
        html_out.append(f"<p>{inline_markdown(stripped)}</p>")

    flush_list()
    flush_quote()
    return "\n".join(html_out)

def render_base(title, description, content_html, lang="tr", active_nav="home", canonical_path="/", extra_head="", switch_url=None):
    t = I18N[lang]
    canonical_url = f"{SITE_URL}{canonical_path}"
    full_title = f"{title} — {t['site_title']}" if title != t['site_title'] else f"{t['site_title']} — {t['site_tagline']}"

    prefix = "" if lang == "tr" else "/en"
    home_url = "/" if lang == "tr" else "/en/"
    blog_url = f"{prefix}/blog/"
    about_url = "/hakkimda/" if lang == "tr" else "/en/about/"
    contact_url = "/iletisim/" if lang == "tr" else "/en/contact/"

    nav_links = [
        (home_url, t["nav_home"], "home"),
        (blog_url, t["nav_blog"], "blog"),
        (about_url, t["nav_about"], "about"),
        (contact_url, t["nav_contact"], "contact")
    ]

    nav_items_html = []
    for url, label, key in nav_links:
        active_class = ' class="active"' if active_nav == key else ''
        nav_items_html.append(f'<a href="{url}"{active_class}>{label}</a>')
    nav_html = "\n".join(nav_items_html)

    # Calculate Language Switcher URL
    if switch_url:
        other_lang_url = switch_url
    else:
        if lang == "tr":
            other_lang_url = "/en" + canonical_path if canonical_path != "/" else "/en/"
        else:
            other_lang_url = canonical_path.replace("/en", "", 1) or "/"

    tr_target = canonical_path if lang == "tr" else other_lang_url
    en_target = other_lang_url if lang == "tr" else canonical_path

    lang_switcher_html = f"""
    <div class="lang-switcher">
      <a href="{tr_target}" class="lang-btn {'active' if lang == 'tr' else ''}">TR</a>
      <span class="lang-sep">/</span>
      <a href="{en_target}" class="lang-btn {'active' if lang == 'en' else ''}">EN</a>
    </div>
    """

    feed_url = "/feed.xml" if lang == "tr" else "/en/feed.xml"

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(full_title)}</title>
  <meta name="description" content="{html.escape(description)}">
  <link rel="canonical" href="{canonical_url}">
  
  <!-- Open Graph / Facebook -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{html.escape(full_title)}">
  <meta property="og:description" content="{html.escape(description)}">
  <meta property="og:site_name" content="{t['site_title']}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{html.escape(full_title)}">
  <meta name="twitter:description" content="{html.escape(description)}">

  <!-- RSS & Sitemap -->
  <link rel="alternate" type="application/rss+xml" title="{t['site_title']} RSS Feed" href="{feed_url}">
  <link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml">

  <!-- Styles -->
  <link rel="stylesheet" href="/css/style.css">
  {extra_head}
</head>
<body>
  <div id="reading-progress"></div>

  <header class="site-header">
    <div class="container nav-wrap">
      <a href="{home_url}" class="site-logo">
        <span class="dot"></span>
        <span>{t['site_title']}</span>
      </a>

      <div class="nav-actions">
        <nav class="main-nav">
          {nav_html}
        </nav>
        {lang_switcher_html}
        <button id="theme-toggle" class="theme-toggle-btn" aria-label="Toggle theme">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
        </button>
      </div>
    </div>
  </header>

  <main>
    {content_html}
  </main>

  <footer class="site-footer">
    <div class="container footer-content">
      <p>&copy; {datetime.now().year} {t['site_title']}. {t['footer_rights']}</p>
      <div class="footer-links">
        <a href="mailto:gzmuzr@gizemuzer.xyz">{t['footer_email']}</a>
        <a href="https://instagram.com/satirarasigzm" target="_blank" rel="noopener">Instagram</a>
        <a href="{feed_url}">{t['footer_rss']}</a>
      </div>
    </div>
  </footer>

  <script src="/js/main.js"></script>
</body>
</html>"""

def load_posts_from_dir(directory, lang="tr"):
    posts = []
    if not directory.exists():
        return posts

    for md_file in directory.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)

        if meta.get("draft", False):
            continue

        slug = meta.get("slug", md_file.stem)
        title = meta.get("title", slug.replace("-", " ").title())
        date_str = str(meta.get("date", "2026-09-01"))
        excerpt = meta.get("excerpt", "")
        tags = meta.get("tags", [])
        featured = meta.get("featured", False)
        translation = meta.get("translation", "")
        reading_time = calculate_reading_time(body, lang=lang)
        html_body = markdown_to_html(body)

        posts.append({
            "slug": slug,
            "title": title,
            "date": date_str,
            "date_formatted": format_date(date_str, lang=lang),
            "excerpt": excerpt,
            "tags": tags,
            "featured": featured,
            "translation": translation,
            "lang": lang,
            "reading_time": reading_time,
            "body_html": html_body,
            "raw_body": body
        })

    posts.sort(key=lambda x: x["date"], reverse=True)
    return posts

def build_site():
    print(f"🚀 Blog derleniyor (TR & EN): {SITE_URL}")
    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    # 1. Copy static assets
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST_DIR, dirs_exist_ok=True)

    # 2. Parse Posts for both languages
    posts_tr = load_posts_from_dir(BLOG_DIR, lang="tr")
    posts_en = load_posts_from_dir(BLOG_EN_DIR, lang="en")

    # Map for easy translation lookup
    tr_by_slug = {p["slug"]: p for p in posts_tr}
    en_by_slug = {p["slug"]: p for p in posts_en}

    # 3. Generate Individual Post Pages
    def generate_posts(posts_list, lang):
        t = I18N[lang]
        prefix = "" if lang == "tr" else "/en"
        all_tags = set()

        for idx, p in enumerate(posts_list):
            for tg in p["tags"]:
                all_tags.add(tg)

            prev_p = posts_list[idx + 1] if idx + 1 < len(posts_list) else None
            next_p = posts_list[idx - 1] if idx > 0 else None

            tags_html = "".join([f'<a href="{prefix}/blog/?tag={html.escape(tg)}" class="tag-pill">#{tg}</a>' for tg in p["tags"]])

            nav_links_html = '<div style="display: flex; justify-content: space-between; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid var(--border); font-size: 0.95rem;">'
            if prev_p:
                nav_links_html += f'<a href="{prefix}/blog/{prev_p["slug"]}/" style="color: var(--text-muted); text-decoration: none;">← {html.escape(prev_p["title"])}</a>'
            else:
                nav_links_html += '<span></span>'
            if next_p:
                nav_links_html += f'<a href="{prefix}/blog/{next_p["slug"]}/" style="color: var(--text-muted); text-decoration: none;">{html.escape(next_p["title"])} →</a>'
            nav_links_html += '</div>'

            # Translation notice
            trans_slug = p.get("translation", "")
            trans_html = ""
            switch_url = None
            if trans_slug:
                if lang == "tr":
                    switch_url = f"/en/blog/{trans_slug}/"
                    trans_html = f"""
                    <div class="translation-notice">
                      <span>{t['switch_prompt']}</span>
                      <a href="{switch_url}">{t['switch_action']}</a>
                    </div>
                    """
                else:
                    switch_url = f"/blog/{trans_slug}/"
                    trans_html = f"""
                    <div class="translation-notice">
                      <span>{t['switch_prompt']}</span>
                      <a href="{switch_url}">{t['switch_action']}</a>
                    </div>
                    """

            article_html = f"""
            <article class="container">
              <header class="article-header">
                <a href="{prefix}/blog/" class="article-back-link">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
                  {t['all_essays']}
                </a>
                {trans_html}
                <h1>{html.escape(p["title"])}</h1>
                <div class="article-meta-bar">
                  <div class="author-chip">
                    <span class="author-avatar-sm">GU</span>
                    <span>{AUTHOR_NAME}</span>
                  </div>
                  <span>•</span>
                  <time datetime="{p["date"]}">{p["date_formatted"]}</time>
                  <span>•</span>
                  <span>{p["reading_time"]}</span>
                </div>
              </header>

              <div class="prose">
                {p["body_html"]}
              </div>

              <div class="post-tags">
                {tags_html}
              </div>

              <div class="author-card">
                <div class="author-card-avatar">GU</div>
                <div class="author-card-info">
                  <h4>{AUTHOR_NAME}</h4>
                  <p>{t['author_bio']}</p>
                </div>
              </div>

              {nav_links_html}
            </article>
            """

            out_dir = (DIST_DIR / "blog" / p["slug"]) if lang == "tr" else (DIST_DIR / "en" / "blog" / p["slug"])
            out_dir.mkdir(parents=True, exist_ok=True)
            canonical = f"/blog/{p['slug']}/" if lang == "tr" else f"/en/blog/{p['slug']}/"
            
            full_page = render_base(
                title=p["title"],
                description=p["excerpt"],
                content_html=article_html,
                lang=lang,
                active_nav="blog",
                canonical_path=canonical,
                switch_url=switch_url
            )
            (out_dir / "index.html").write_text(full_page, encoding="utf-8")

        return all_tags

    tags_tr = generate_posts(posts_tr, "tr")
    tags_en = generate_posts(posts_en, "en")

    # 4. Generate Blog Listing Pages
    def generate_blog_index(posts_list, tags_set, lang):
        t = I18N[lang]
        prefix = "" if lang == "tr" else "/en"

        tag_chips = [f'<button class="filter-chip active" data-tag="all">{t["filter_all"]}</button>']
        for tg in sorted(tags_set):
            tag_chips.append(f'<button class="filter-chip" data-tag="{html.escape(tg)}">#{html.escape(tg)}</button>')
        tag_chips_html = "\n".join(tag_chips)

        cards_html = []
        for p in posts_list:
            tags_data = ",".join(p["tags"])
            tags_badges = "".join([f'<span class="tag">#{tg}</span>' for tg in p["tags"]])
            card = f"""
            <a href="{prefix}/blog/{p["slug"]}/" class="post-card" data-title="{html.escape(p["title"].lower())}" data-excerpt="{html.escape(p["excerpt"].lower())}" data-tags="{html.escape(tags_data)}">
              <div class="post-card-meta">
                <time datetime="{p["date"]}">{p["date_formatted"]}</time>
                <span>•</span>
                <span>{p["reading_time"]}</span>
                {tags_badges}
              </div>
              <h3>{html.escape(p["title"])}</h3>
              <p class="excerpt">{html.escape(p["excerpt"])}</p>
              <div class="post-card-footer">
                <span>{t["read_more"]}</span>
              </div>
            </a>
            """
            cards_html.append(card)

        blog_index_html = f"""
        <div class="container" style="padding-top: 3.5rem; padding-bottom: 4rem;">
          <h1 style="font-size: 2.4rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 0.5rem;">{t['blog_title']}</h1>
          <p style="font-size: 1.15rem; color: var(--text-muted); margin-bottom: 2rem;">{t['blog_desc']}</p>

          <div class="search-box">
            <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input type="text" id="blog-search" class="search-input" placeholder="{t['search_placeholder']}">
          </div>

          <div class="filter-tags">
            {tag_chips_html}
          </div>

          <div class="post-list" id="post-list">
            {"".join(cards_html)}
          </div>
        </div>
        """

        out_dir = (DIST_DIR / "blog") if lang == "tr" else (DIST_DIR / "en" / "blog")
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = "/blog/" if lang == "tr" else "/en/blog/"
        switch_url = "/en/blog/" if lang == "tr" else "/blog/"

        (out_dir / "index.html").write_text(
            render_base(t["nav_blog"], t["blog_desc"], blog_index_html, lang=lang, active_nav="blog", canonical_path=canonical, switch_url=switch_url),
            encoding="utf-8"
        )

    generate_blog_index(posts_tr, tags_tr, "tr")
    generate_blog_index(posts_en, tags_en, "en")

    # 5. Generate Home Pages
    def generate_home(posts_list, lang):
        t = I18N[lang]
        prefix = "" if lang == "tr" else "/en"
        about_link = "/hakkimda/" if lang == "tr" else "/en/about/"

        featured_cards = []
        for p in [x for x in posts_list if x["featured"]][:2]:
            tags_badges = "".join([f'<span class="tag">#{tg}</span>' for tg in p["tags"]])
            card = f"""
            <a href="{prefix}/blog/{p["slug"]}/" class="post-card">
              <div class="post-card-meta">
                <time datetime="{p["date"]}">{p["date_formatted"]}</time>
                <span>•</span>
                <span>{p["reading_time"]}</span>
                {tags_badges}
              </div>
              <h3>{html.escape(p["title"])}</h3>
              <p class="excerpt">{html.escape(p["excerpt"])}</p>
              <div class="post-card-footer">
                <span>{t["read_more"]}</span>
              </div>
            </a>
            """
            featured_cards.append(card)

        recent_cards = []
        for p in posts_list[:3]:
            tags_badges = "".join([f'<span class="tag">#{tg}</span>' for tg in p["tags"]])
            card = f"""
            <a href="{prefix}/blog/{p["slug"]}/" class="post-card">
              <div class="post-card-meta">
                <time datetime="{p["date"]}">{p["date_formatted"]}</time>
                <span>•</span>
                <span>{p["reading_time"]}</span>
                {tags_badges}
              </div>
              <h3>{html.escape(p["title"])}</h3>
              <p class="excerpt">{html.escape(p["excerpt"])}</p>
              <div class="post-card-footer">
                <span>{t["explore_post"]}</span>
              </div>
            </a>
            """
            recent_cards.append(card)

        home_html = f"""
        <section class="hero container">
          <div class="hero-tag">{t['hero_tag']}</div>
          <h1>{t['hero_title']}</h1>
          <p class="lead">{t['hero_lead']}</p>
          <div class="hero-meta">
            <a href="{prefix}/blog/" class="btn btn-primary">{t['hero_btn_explore']}</a>
            <a href="{about_link}" class="btn btn-secondary">{t['hero_btn_about']}</a>
          </div>
        </section>

        <div class="container">
          <div class="section-header">
            <h2>{t['featured']}</h2>
            <a href="{prefix}/blog/" class="view-all">{t['view_all']}</a>
          </div>
          <div class="post-list">
            {"".join(featured_cards)}
          </div>

          <div class="section-header">
            <h2>{t['recent']}</h2>
            <a href="{prefix}/blog/" class="view-all">{t['archive']}</a>
          </div>
          <div class="post-list">
            {"".join(recent_cards)}
          </div>

          <div class="newsletter-card">
            <h3>{t['newsletter_title']}</h3>
            <p>{t['newsletter_desc']}</p>
            <form class="newsletter-form" onsubmit="event.preventDefault(); alert('{t['newsletter_alert']}');">
              <input type="email" placeholder="{t['newsletter_placeholder']}" required>
              <button type="submit" class="btn btn-primary">{t['newsletter_btn']}</button>
            </form>
          </div>
        </div>
        """

        out_file = (DIST_DIR / "index.html") if lang == "tr" else (DIST_DIR / "en" / "index.html")
        out_file.parent.mkdir(parents=True, exist_ok=True)
        canonical = "/" if lang == "tr" else "/en/"
        switch_url = "/en/" if lang == "tr" else "/"

        out_file.write_text(
            render_base(t["site_title"], t["site_description"], home_html, lang=lang, active_nav="home", canonical_path=canonical, switch_url=switch_url),
            encoding="utf-8"
        )

    generate_home(posts_tr, "tr")
    generate_home(posts_en, "en")

    # 6. Generate About Pages
    def generate_about(file_path, lang):
        t = I18N[lang]
        title = "Hakkımda" if lang == "tr" else "About"
        subtitle = "Gizem Uzer kimdir?" if lang == "tr" else "Who is Gizem Uzer?"
        body_html = ""
        if file_path.exists():
            meta, body = parse_frontmatter(file_path.read_text(encoding="utf-8"))
            title = meta.get("title", title)
            subtitle = meta.get("subtitle", subtitle)
            body_html = markdown_to_html(body)

        about_page_html = f"""
        <div class="container" style="padding: 3.5rem 1.5rem 5rem;">
          <header class="article-header" style="margin-bottom: 2rem;">
            <h1 style="font-size: 2.6rem;">{html.escape(title)}</h1>
            <p style="font-size: 1.2rem; color: var(--text-muted);">{html.escape(subtitle)}</p>
          </header>
          <div class="prose">
            {body_html}
          </div>
        </div>
        """

        out_dir = (DIST_DIR / "hakkimda") if lang == "tr" else (DIST_DIR / "en" / "about")
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = "/hakkimda/" if lang == "tr" else "/en/about/"
        switch_url = "/en/about/" if lang == "tr" else "/hakkimda/"

        (out_dir / "index.html").write_text(
            render_base(title, subtitle, about_page_html, lang=lang, active_nav="about", canonical_path=canonical, switch_url=switch_url),
            encoding="utf-8"
        )

    generate_about(PAGES_DIR / "about.md", "tr")
    generate_about(PAGES_EN_DIR / "about.md", "en")

    # 7. Generate Contact Pages
    def generate_contact(file_path, lang):
        t = I18N[lang]
        title = "İletişim" if lang == "tr" else "Contact"
        subtitle = "Bağlantıda kalalım" if lang == "tr" else "Let's connect"
        body_html = ""
        if file_path.exists():
            meta, body = parse_frontmatter(file_path.read_text(encoding="utf-8"))
            title = meta.get("title", title)
            subtitle = meta.get("subtitle", subtitle)
            body_html = markdown_to_html(body)

        contact_page_html = f"""
        <div class="container" style="padding: 3.5rem 1.5rem 5rem;">
          <header class="article-header" style="margin-bottom: 2rem;">
            <h1 style="font-size: 2.6rem;">{html.escape(title)}</h1>
            <p style="font-size: 1.2rem; color: var(--text-muted);">{html.escape(subtitle)}</p>
          </header>
          <div class="prose">
            {body_html}
          </div>
        </div>
        """

        out_dir = (DIST_DIR / "iletisim") if lang == "tr" else (DIST_DIR / "en" / "contact")
        out_dir.mkdir(parents=True, exist_ok=True)
        canonical = "/iletisim/" if lang == "tr" else "/en/contact/"
        switch_url = "/en/contact/" if lang == "tr" else "/iletisim/"

        (out_dir / "index.html").write_text(
            render_base(title, subtitle, contact_page_html, lang=lang, active_nav="contact", canonical_path=canonical, switch_url=switch_url),
            encoding="utf-8"
        )

    generate_contact(PAGES_DIR / "contact.md", "tr")
    generate_contact(PAGES_EN_DIR / "contact.md", "en")

    # 8. Generate RSS 2.0 Feeds
    def generate_rss(posts_list, lang, out_file):
        t = I18N[lang]
        prefix = "" if lang == "tr" else "/en"
        items = []
        for p in posts_list:
            dt = datetime.strptime(p["date"], "%Y-%m-%d")
            pub_date = dt.strftime("%a, %d %b %Y 00:00:00 +0300")
            item_xml = f"""    <item>
      <title>{html.escape(p["title"])}</title>
      <link>{SITE_URL}{prefix}/blog/{p["slug"]}/</link>
      <guid isPermaLink="true">{SITE_URL}{prefix}/blog/{p["slug"]}/</guid>
      <pubDate>{pub_date}</pubDate>
      <description>{html.escape(p["excerpt"])}</description>
    </item>"""
            items.append(item_xml)

        feed_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{t['site_title']}</title>
    <link>{SITE_URL}{prefix}/</link>
    <description>{t['site_description']}</description>
    <language>{lang}</language>
    <atom:link href="{SITE_URL}{prefix}/feed.xml" rel="self" type="application/rss+xml"/>
    {"\n".join(items)}
  </channel>
</rss>"""
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_text(feed_xml, encoding="utf-8")

    generate_rss(posts_tr, "tr", DIST_DIR / "feed.xml")
    generate_rss(posts_en, "en", DIST_DIR / "en" / "feed.xml")

    # 9. Unified Sitemap (/sitemap.xml)
    sitemap_urls = [
        f"  <url><loc>{SITE_URL}/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{SITE_URL}/en/</loc><changefreq>weekly</changefreq><priority>1.0</priority></url>",
        f"  <url><loc>{SITE_URL}/blog/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{SITE_URL}/en/blog/</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        f"  <url><loc>{SITE_URL}/hakkimda/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
        f"  <url><loc>{SITE_URL}/en/about/</loc><changefreq>monthly</changefreq><priority>0.7</priority></url>",
        f"  <url><loc>{SITE_URL}/iletisim/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
        f"  <url><loc>{SITE_URL}/en/contact/</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
    ]
    for p in posts_tr:
        sitemap_urls.append(
            f"  <url><loc>{SITE_URL}/blog/{p['slug']}/</loc><lastmod>{p['date']}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>"
        )
    for p in posts_en:
        sitemap_urls.append(
            f"  <url><loc>{SITE_URL}/en/blog/{p['slug']}/</loc><lastmod>{p['date']}</lastmod><changefreq>monthly</changefreq><priority>0.8</priority></url>"
        )

    sitemap_xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(sitemap_urls)}
</urlset>"""
    (DIST_DIR / "sitemap.xml").write_text(sitemap_xml, encoding="utf-8")

    # 10. robots.txt
    robots_txt = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    (DIST_DIR / "robots.txt").write_text(robots_txt, encoding="utf-8")

    print(f"✨ Başarıyla tamamlandı: {len(posts_tr)} TR + {len(posts_en)} EN yazı derlendi -> dist/")

if __name__ == "__main__":
    build_site()
