# 🌿 gizemuzer.xyz — Kişisel Blog & Dijital Bahçe

Gizem Uzer için özel olarak tasarlanmış; modern, editoryal tipografiye sahip, sıfır bağımlılıkla çalışan ve **tamamen yapay zeka (Antigravity) aracılığıyla yönetilebilen** kişisel düşünce alanı.

---

## 🤖 Yapay Zeka (Antigravity) ile Yönetim Rehberi

Bu blogun tüm altyapısı, doğrudan Antigravity sohbeti üzerinden kontrol edilmek üzere inşa edilmiştir. Terminal veya kodlarla uğraşmanıza gerek yoktur. Sadece bana söylemeniz yeterli:

### 1. Yeni Yazı Yazma & Taslak Çıkarma
> **Örnek Talepler:**
> - *"Gizem: Bugün okuduğum şu kitap hakkında bir yazı yazalım..."*
> - *"Şu notlarımı derleyip 'Dijital Sadeleşme' başlıklı bir blog yazısına dönüştür."*
> - *"Yapay zeka ve sanat üzerine 3 maddelik bir düşünce yazısı hazırla."*

Ben yazıyı hazırlar, `content/blog/` altına ekler ve yerel önizlemede incelemeniz için hazır hale getiririm.

### 2. Düzeltme & Güncelleme
> **Örnek Talepler:**
> - *"'Yapay Zeka ve İnsan Yaratıcılığı' yazısındaki ikinci paragrafı biraz daha samimi bir dille yeniden yaz."*
> - *"Son yazıma #Teknoloji etiketini de ekle."*
> - *"Hakkımda sayfasındaki biyografimi şu şekilde güncelle..."*

### 3. Yayına Alma & Arşivleme
> **Örnek Talepler:**
> - *"Taslağı onaylıyorum, yazıyı yayına al ve siteyi güncelle."*
> - *"Mevcut tüm yazılarımı listele."*

---

## 🌐 gizemuzer.xyz Alan Adını Bağlama Rehberi

### Vercel ile Canlıya Alma (Önerilen & En Hızlı Yol):
1. [vercel.com](https://vercel.com) üzerinde ücretsiz bir hesap açın ve GitHub reponuzu bağlayın.
2. Proje ayarlarından **Domains** sekmesine gidin.
3. `gizemuzer.xyz` ve `www.gizemuzer.xyz` adreslerini ekleyin.
4. Namecheap DNS paneline şu iki kaydı girin:
   - **Type A:** `76.76.21.21` (Host: `@`)
   - **Type CNAME:** `cname.vercel-dns.com` (Host: `www`)
5. 5-10 dakika içinde SSL sertifikanız otomatik tanımlanacak ve siteniz dünya çapında yayına girecektir.

---

## 💻 Yerel Geliştirme & Yönetim (Terminal Komutları)

Eğer kendiniz çalıştırmak isterseniz:

```bash
# Mevcut yazıları listele
python3 manage.py list

# Yeni taslak yazı oluştur
python3 manage.py new "Yazı Başlığı" --tags "Teknoloji,Felsefe"

# Taslak yazıyı yayına al
python3 manage.py publish yazi-basligi

# Tüm siteyi derle (dist/ klasörüne)
python3 manage.py build

# Yerel önizleme sunucusunu başlat (http://localhost:8080)
python3 manage.py serve
```

---

## 📂 Dosya Yapısı

```
gizemuzer-blog/
├── content/
│   ├── blog/          # Markdown formatındaki blog yazıları
│   └── pages/         # Hakkımda ve İletişim sayfaları
├── static/
│   ├── css/style.css  # Modern, responsive, karanlık mod destekli CSS
│   ├── js/main.js     # Arama, filtreleme, karanlık mod ve okuma çubuğu
│   └── images/        # Görseller ve avatarlar
├── dist/              # Yayına hazır derlenmiş statik web sitesi
├── builder.py         # Yüksek hızlı statik site derleme motoru
├── manage.py          # AI ve kullanıcı yönetim CLI aracı
├── vercel.json        # Vercel yayınlama ayarları
└── .github/workflows/ # GitHub Pages otomatik yayınlama
```
