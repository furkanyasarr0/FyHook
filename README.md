# 🚀 FyHook - Discord Webhook Manager

FyHook, Discord webhook'larını yönetmek, özelleştirilmiş embed mesajları göndermek ve mesajları anlık olarak önizlemek için geliştirilmiş modern, şık ve kullanıcı dostu bir masaüstü uygulamasıdır.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Özellikler

- **🖼️ Canlı Discord Önizlemesi**: Mesajınızın Discord'da tam olarak nasıl görüneceğini anlık olarak görün.
- **🤖 Dinamik Bot Bilgisi**: Webhook URL'sini girdiğinizde botun ismi ve profil fotoğrafı otomatik olarak Discord'dan çekilir.
- **📚 Webhook Yöneticisi**: Sık kullandığınız webhook'ları isim vererek kaydedin, silin ve tek tıkla kullanın.
- **🎨 Gelişmiş Embed Editörü**: 
  - Author (Yazar), Title (Başlık), Description (Açıklama)
  - Fields (Alanlar) - Sınırsız alan ekleme desteği
  - Images & Thumbnails (Resimler)
  - Footer & Timestamp (Alt bilgi ve Zaman damgası)
  - Renk Seçici (Hex kod desteği)
- **⚡ JSON Düzenleyici**: Mesaj verilerini doğrudan JSON olarak düzenleyin veya dışarıdan içe aktarın.
- **🔄 Güncelleme Denetleyicisi**: Yeni bir sürüm yayınlandığında uygulama içinden anında haberdar olun.
- **🔗 Mesaj Yükleme**: Gönderilmiş bir mesajın linkini vererek o mesajı düzenlemek üzere geri yükleyin.

---

## 📸 Ekran Görüntüleri

> *Uygulama arayüzünden görselleri buraya ekleyebilirsiniz.*

---

## 🛠️ Kurulum

1. **Depoyu bilgisayarınıza indirin:**
   ```bash
   git clone https://github.com/furkanyasarr0/FyHook.git
   cd FyHook
   ```

2. **Gerekli kütüphaneleri yükleyin:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Uygulamayı çalıştırın:**
   ```bash
   python main.py
   ```

---

## 📦 EXE Haline Getirme

Uygulamayı tek bir `.exe` dosyası yapmak isterseniz şu komutu kullanabilirsiniz:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "webhooks.json;." main.py
```

---

## 🤝 Katkıda Bulunma

1. Bu depoyu fork'layın.
2. Yeni bir özellik dalı (branch) oluşturun (`git checkout -b feature/yeniOzellik`).
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni özellik eklendi'`).
4. Dalınıza push yapın (`git push origin feature/yeniOzellik`).
5. Bir Pull Request açın.

---

## 📄 Lisans

Bu proje **MIT** lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasına bakabilirsiniz.

---

## 👤 Geliştirici

**Furkan Yaşar**  
- GitHub: [@furkanyasarr0](https://github.com/furkanyasarr0)

---
*FyHook ile Discord sunucunuzu daha profesyonel yönetin!*
