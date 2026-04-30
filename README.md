# 🚀 FyHook - Discord Webhook Manager

FyHook is a modern, sleek, and user-friendly desktop application developed to manage Discord webhooks, send customized embed messages, and instantly preview messages.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

## ✨ Features

- **🖼️ Live Discord Preview**: See exactly how your message will appear on Discord in real-time.
- **🤖 Dynamic Bot Information**: When you enter a webhook URL, the bot's name and profile picture are automatically fetched from Discord.
- **📚 Webhook Manager**: Save, delete, and use your frequently used webhooks with a single click, giving them custom names.
- **🎨 Advanced Embed Editor**:
  - Author, Title, Description
  - Fields - Support for unlimited fields
  - Images & Thumbnails
  - Footer & Timestamp
  - Color Picker (Hex code support)
- **⚡ JSON Editor**: Edit message data directly as JSON or import from an external source.
- **🔄 Update Checker**: Get instant notifications within the application when a new version is released.
- **🔗 Message Loader**: Provide a link to a sent message to load it back for editing.

---


## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/furkanyasarr0/FyHook.git
   cd FyHook
   ```

2. **Install required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python main.py
   ```

---

## 📦 Convert to EXE

If you want to convert the application into a single `.exe` file, you can use the following command:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --add-data "webhooks.json;." main.py
```

---

## 🤝 Contributing

1. Fork this repository.
2. Create a new feature branch (`git checkout -b feature/newFeature`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to your branch (`git push origin feature/newFeature`).
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the **MIT** license. See the `LICENSE` file for more details.

---

## 👤 Developer

**Furkan Yaşar**  
- GitHub: [@furkanyasarr0](https://github.com/furkanyasarr0)

---
*Manage your Discord server more professionally with FyHook!*
