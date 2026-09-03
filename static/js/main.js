// gizemuzer.com - Client Enhancements

(function () {
  // 1. Theme Management (Dark / Light)
  const root = document.documentElement;
  const storageKey = 'gizemuzer-theme';

  function getPreferredTheme() {
    const saved = localStorage.getItem(storageKey);
    if (saved) return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    if (theme === 'dark') {
      root.setAttribute('data-theme', 'dark');
    } else {
      root.removeAttribute('data-theme');
    }
    updateThemeIcon(theme);
  }

  function updateThemeIcon(theme) {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;
    if (theme === 'dark') {
      btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>`;
      btn.setAttribute('aria-label', 'Aydınlık moda geç');
      btn.setAttribute('title', 'Aydınlık moda geç');
    } else {
      btn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>`;
      btn.setAttribute('aria-label', 'Karanlık moda geç');
      btn.setAttribute('title', 'Karanlık moda geç');
    }
  }

  // Initial theme setup
  const currentTheme = getPreferredTheme();
  applyTheme(currentTheme);

  document.addEventListener('DOMContentLoaded', () => {
    updateThemeIcon(root.getAttribute('data-theme') === 'dark' ? 'dark' : 'light');

    const toggleBtn = document.getElementById('theme-toggle');
    if (toggleBtn) {
      toggleBtn.addEventListener('click', () => {
        const isDark = root.getAttribute('data-theme') === 'dark';
        const nextTheme = isDark ? 'light' : 'dark';
        localStorage.setItem(storageKey, nextTheme);
        applyTheme(nextTheme);
      });
    }

    // 2. Reading Progress Bar
    const progressBar = document.getElementById('reading-progress');
    if (progressBar) {
      window.addEventListener('scroll', () => {
        const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (totalHeight > 0) {
          const progress = (window.pageYOffset / totalHeight) * 100;
          progressBar.style.width = Math.min(progress, 100) + '%';
        }
      }, { passive: true });
    }

    // 3. Client-Side Search & Tag Filter on /blog/
    const searchInput = document.getElementById('blog-search');
    const filterChips = document.querySelectorAll('.filter-chip');
    const postCards = document.querySelectorAll('.post-card');

    if (searchInput || filterChips.length > 0) {
      let activeTag = 'all';

      function filterPosts() {
        const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

        postCards.forEach(card => {
          const title = card.getAttribute('data-title') || '';
          const excerpt = card.getAttribute('data-excerpt') || '';
          const tags = (card.getAttribute('data-tags') || '').split(',');

          const matchesQuery = !query || title.includes(query) || excerpt.includes(query);
          const matchesTag = activeTag === 'all' || tags.includes(activeTag);

          if (matchesQuery && matchesTag) {
            card.style.display = 'block';
          } else {
            card.style.display = 'none';
          }
        });
      }

      if (searchInput) {
        searchInput.addEventListener('input', filterPosts);
      }

      filterChips.forEach(chip => {
        chip.addEventListener('click', () => {
          filterChips.forEach(c => c.classList.remove('active'));
          chip.classList.add('active');
          activeTag = chip.getAttribute('data-tag');
          filterPosts();
        });
      });
    }

    // 4. Code Block Copy Buttons
    document.querySelectorAll('pre').forEach(pre => {
      const code = pre.querySelector('code');
      if (!code) return;

      const copyBtn = document.createElement('button');
      copyBtn.className = 'copy-code-btn';
      copyBtn.innerText = 'Kopyala';
      copyBtn.style.cssText = 'position: absolute; top: 8px; right: 8px; font-size: 11px; padding: 3px 8px; border-radius: 4px; border: 1px solid var(--border); background: var(--bg-card); color: var(--text-muted); cursor: pointer;';
      
      pre.style.position = 'relative';
      pre.appendChild(copyBtn);

      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(code.innerText).then(() => {
          copyBtn.innerText = 'Kopyalandı!';
          setTimeout(() => { copyBtn.innerText = 'Kopyala'; }, 2000);
        });
      });
    });
  });
})();
