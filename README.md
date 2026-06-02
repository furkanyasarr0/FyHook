# 🚀 FyHook - Discord Webhook Manager

FyHook is a modern, sleek, and user-friendly desktop application developed to manage Discord webhooks, send customized embed messages, and instantly preview messages.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-blueviolet?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

---

# ⌛ Changelog

- **🖼️ Theme and GUI Update.**
- **☀️ Light mode added.**

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
## 📸 Screenshots

### Visual Editor
<img width="1208" height="852" alt="Visual Editor" src="https://github.com/user-attachments/assets/54bf3328-f67e-4e8c-923f-1bc04bdef8d1" />

<img width="1338" height="736" alt="Visual Editor Preview" src="https://github.com/user-attachments/assets/adf01820-0552-44b6-aba1-133c333c6360" />

### JSON Data Editor
Import or export using the JSON editor

<img width="1208" height="852" alt="JSON Data Editor" src="https://github.com/user-attachments/assets/cab6ab97-b0f1-46bc-90d8-0815dbb5477e" />

### Webhooks
Effortlessly manage your webhooks with JSON-based local storage, eliminating the need to re-enter URLs every time

<img width="602" height="532" alt="Webhooks" src="https://github.com/user-attachments/assets/bc1f7660-887e-478c-8cec-7676a9355ea1" />

### About and Check for Updates
Stay up to date with new features and bug fixes

<img width="452" height="432" alt="main_IXtZIhMCge" src="https://github.com/user-attachments/assets/55207724-386a-40d5-b0a8-761fcc0940dd" />

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
