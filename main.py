import tkinter as tk
import customtkinter as ctk
import requests
import json
import os
import threading
import webbrowser
import io
import re
from datetime import datetime, timezone
from tkinter import colorchooser

try:
    from PIL import Image, ImageTk, ImageDraw
except ImportError:
    print("Uyarı: Pillow(PIL) kütüphanesi eksik. Profil fotoğrafları ve ikonlar yüklenemeyebilir.")

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue") 

class FyHookApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FyHook - Discord Webhook Manager")
        
        window_width = 1400
        window_height = 900
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (window_width / 2))
        y_coordinate = int((screen_height / 2) - (window_height / 2))
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")
        
        # Tuple Format: ("Light Mode Color", "Dark Mode Color")
        self.c_bg_sidebar = ("#F2F3F5", "#2B2D31")
        self.c_bg_main = ("#FFFFFF", "#313338")
        self.c_bg_card = ("#EAECEE", "#1E1F22")
        self.c_bg_hover = ("#D4D7DC", "#3F4147")
        self.c_text_primary = ("#000000", "white")
        self.c_text_gray = ("#4E5058", "#B5BAC1")
        self.c_border_gray = ("#C8C8C8", "#3F4147")
        self.accent_blurple = "#5865F2"
        
        self.c_hover_red = ("#FEE8E9", "#3A2024")
        self.c_blue_link = ("#006CE7", "#00A8FC")
        
        # Mutlak yol ile uygulamanın her yerden ikonları hatasız bulması garantilendi
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_ico_path = os.path.join(base_dir, "icon", "icon.ico")
        self.icon_png_path = os.path.join(base_dir, "icon", "icon.png")
        self.has_icon = False
        self.logo_img = None
        self.avatar_fallback_img = None
        self.icon_photo = None 
        
        # Windows Titlebar ve Görev Çubuğu (Taskbar) Kesin İkon Çözümü
        if os.name == 'nt':
            try:
                # Windows'a Python app'i olmadığını bildiren Native ID ayarı
                import ctypes
                myappid = 'furkanyasarr0.fyhook.manager.1.6'
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            except Exception: pass
            
            if os.path.exists(self.icon_ico_path):
                try:
                    # 'default=' keyword hatası (1. Problem) giderildi
                    self.iconbitmap(self.icon_ico_path)
                except Exception: pass
            
        # UI (Sidebar & Avatar) Logo
        ui_img_path = self.icon_png_path if os.path.exists(self.icon_png_path) else (self.icon_ico_path if os.path.exists(self.icon_ico_path) else None)
        
        if ui_img_path:
            try:
                pil_img = Image.open(ui_img_path)
                self.logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(36, 36))
                self.avatar_fallback_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(40, 40))
                self.has_icon = True
                
                if os.name != 'nt':
                    self.icon_photo = ImageTk.PhotoImage(pil_img)
                    self.wm_iconphoto(True, self.icon_photo)
            except Exception as e:
                print(f"Ikon yükleme hatası: {e}")

        self.saved_webhooks = self.load_webhooks_from_file()
        self.configure(fg_color=self.c_bg_main)
        self.version = "1.1 - Theme & GUI"
        self.github_repo = "furkanyasarr0/FyHook"
        self.embeds_list = []
        self.is_json_mode = False
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color=self.c_bg_sidebar)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.pack(pady=(40, 30))
        
        if self.has_icon:
            ctk.CTkLabel(self.brand_frame, image=self.logo_img, text=" FyHook", compound="left", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.c_text_primary).pack()
        else:
            ctk.CTkLabel(self.brand_frame, text="FyHook", font=ctk.CTkFont(size=28, weight="bold"), text_color=self.c_text_primary).pack()
        
        ctk.CTkButton(self.sidebar, text="Send Webhook", height=45, corner_radius=8, font=ctk.CTkFont(size=14, weight="bold"), fg_color=self.accent_blurple, hover_color="#4752C4", text_color="white", command=self.send_webhook).pack(pady=(0, 20), padx=25, fill="x")
        
        nav_kwargs = {"height": 40, "corner_radius": 6, "fg_color": "transparent", "text_color": self.c_text_gray, "hover_color": self.c_bg_hover, "anchor": "w"}
        
        self.webhooks_mgr_btn = ctk.CTkButton(self.sidebar, text=" 📌  Saved Webhooks", command=self.open_webhook_manager, **nav_kwargs)
        self.webhooks_mgr_btn.pack(pady=5, padx=25, fill="x")
        
        self.json_editor_btn = ctk.CTkButton(self.sidebar, text=" 🛠️  JSON Editor", command=self.toggle_json_editor, **nav_kwargs)
        self.json_editor_btn.pack(pady=5, padx=25, fill="x")
        
        ctk.CTkButton(self.sidebar, text=" 🗑️  Clear All Fields", height=40, corner_radius=6, fg_color="transparent", text_color="#ED4245", hover_color=self.c_hover_red, anchor="w", command=self.clear_all).pack(pady=5, padx=25, fill="x")

        self.sidebar_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_bottom.pack(side="bottom", fill="x", pady=20)
        
        self.about_btn = ctk.CTkButton(self.sidebar_bottom, text="ℹ️  About & Settings", height=35, corner_radius=6, fg_color="transparent", text_color=self.c_text_gray, hover_color=self.c_bg_hover, command=self.open_about_window)
        self.about_btn.pack(pady=5, padx=25, fill="x")
        
        self.version_label = ctk.CTkLabel(self.sidebar_bottom, text=f"v{self.version}", font=ctk.CTkFont(size=11), text_color=self.c_text_gray)
        self.version_label.pack()

        self.editor = ctk.CTkScrollableFrame(self, fg_color=self.c_bg_main)
        self.editor.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.editor.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(self.editor, text="MESSAGE EDITOR", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.c_text_gray).pack(anchor="w", padx=10, pady=(0, 10))

        self.config_card = ctk.CTkFrame(self.editor, fg_color=self.c_bg_sidebar, corner_radius=12, border_width=1, border_color=self.c_border_gray)
        self.config_card.pack(fill="x", padx=10, pady=(0, 20))
        
        ctk.CTkLabel(self.config_card, text="Webhook URL", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.c_text_primary).pack(anchor="w", padx=20, pady=(20,5))
        self.url_entry = ctk.CTkEntry(self.config_card, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, placeholder_text="Paste Discord Webhook URL here...", height=42, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, border_width=1)
        self.url_entry.pack(padx=20, pady=(0, 15), fill="x")
        self.url_entry.bind("<KeyRelease>", lambda e: self.fetch_webhook_info())
        self.url_entry.bind("<FocusOut>", lambda e: self.fetch_webhook_info())
        self.url_entry.bind("<<Paste>>", lambda e: self.after(100, self.fetch_webhook_info))

        ctk.CTkLabel(self.config_card, text="Message Link (For Editing)", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.c_text_primary).pack(anchor="w", padx=20, pady=(5,5))
        msg_link_frame = ctk.CTkFrame(self.config_card, fg_color="transparent")
        msg_link_frame.pack(fill="x", padx=20, pady=(0, 5))
        
        self.msg_link_entry = ctk.CTkEntry(msg_link_frame, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, placeholder_text="https://discord.com/channels/...", height=42, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, border_width=1)
        self.msg_link_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.load_msg_btn = ctk.CTkButton(msg_link_frame, text="Load Data", width=100, height=42, corner_radius=8, fg_color=self.c_bg_hover, hover_color=self.c_border_gray, text_color=self.c_text_primary, command=self.load_message_link)
        self.load_msg_btn.pack(side="right")
        
        info_text = "Pro Tip: Provide a message link to edit an existing webhook message."
        ctk.CTkLabel(self.config_card, text=info_text, font=ctk.CTkFont(size=11, slant="italic"), text_color=self.c_text_gray).pack(anchor="w", padx=20, pady=(0, 20))
        
        self.content_card = ctk.CTkFrame(self.editor, fg_color=self.c_bg_sidebar, corner_radius=12, border_width=1, border_color=self.c_border_gray)
        self.content_card.pack(fill="x", padx=10, pady=(0, 20))

        ctk.CTkLabel(self.content_card, text="Message Content", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.c_text_primary).pack(anchor="w", padx=20, pady=(20,5))
        self.content_text = ctk.CTkTextbox(self.content_card, text_color=self.c_text_primary, height=120, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, border_width=1)
        self.content_text.pack(padx=20, pady=(0, 20), fill="x")
        self.content_text.bind("<KeyRelease>", lambda e: self.update_preview())

        self.embeds_container = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.embeds_container.pack(fill="x")
        
        self.add_embed_btn = ctk.CTkButton(self.editor, text="+ Add New Embed", height=45, corner_radius=8, fg_color="#248046", hover_color="#1A6334", text_color="white", font=ctk.CTkFont(weight="bold", size=13), command=self.add_embed)
        self.add_embed_btn.pack(pady=(20, 40))

        self.json_editor_frame = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.json_text = ctk.CTkTextbox(self.json_editor_frame, text_color=self.c_text_primary, height=600, corner_radius=8, font=ctk.CTkFont(family="Courier", size=13), fg_color=self.c_bg_sidebar, border_color=self.c_border_gray, border_width=1)
        self.json_text.pack(fill="both", expand=True, padx=10, pady=(0, 15))
        ctk.CTkButton(self.json_editor_frame, text="Apply JSON to Visual Editor", fg_color=self.accent_blurple, text_color="white", height=45, corner_radius=8, font=ctk.CTkFont(weight="bold"), command=self.import_json_data).pack()

        self.preview_panel = ctk.CTkFrame(self, width=450, corner_radius=0, fg_color=self.c_bg_main, border_width=1, border_color=self.c_border_gray)
        self.preview_panel.grid(row=0, column=2, sticky="nsew")
        self.preview_panel.grid_columnconfigure(0, weight=1)
        
        self.preview_header = ctk.CTkFrame(self.preview_panel, height=60, corner_radius=0, fg_color=self.c_bg_sidebar, border_width=1, border_color=self.c_border_gray)
        self.preview_header.pack(fill="x")
        self.preview_header.pack_propagate(False)
        
        ctk.CTkLabel(self.preview_header, text="Live Preview", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.c_text_primary).pack(side="left", padx=20)
        self.status_label = ctk.CTkLabel(self.preview_header, text="Ready", font=ctk.CTkFont(size=12, weight="bold"), text_color="#43B581")
        self.status_label.pack(side="right", padx=20)
        
        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_panel, fg_color=self.c_bg_main)
        self.preview_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.msg_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        self.msg_frame.pack(fill="x", pady=10)

        self.user_info_frame = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        self.user_info_frame.pack(fill="x", padx=10, pady=(0, 5))

        self.avatar_label = ctk.CTkLabel(self.user_info_frame, text="", width=40, height=40)
        self.avatar_label.pack(side="left", padx=(0, 15))
        self.reset_default_avatar()

        self.name_info_frame = ctk.CTkFrame(self.user_info_frame, fg_color="transparent")
        self.name_info_frame.pack(side="left", fill="y", pady=(2,0))

        bot_name_wrap = ctk.CTkFrame(self.name_info_frame, fg_color="transparent")
        bot_name_wrap.pack(anchor="w")
        self.bot_name_label = ctk.CTkLabel(bot_name_wrap, text="FyHook", font=ctk.CTkFont(size=15, weight="bold"), text_color=self.c_text_primary)
        self.bot_name_label.pack(side="left")

        self.bot_tag = ctk.CTkFrame(bot_name_wrap, fg_color=self.accent_blurple, corner_radius=4)
        self.bot_tag.pack(side="left", padx=5)
        ctk.CTkLabel(self.bot_tag, text="BOT", font=ctk.CTkFont(size=10, weight="bold"), text_color="white", height=16).pack(padx=4, pady=1)

        self.timestamp_label = ctk.CTkLabel(bot_name_wrap, text="Today at 11:49 PM", font=ctk.CTkFont(size=12), text_color=self.c_text_gray)
        self.timestamp_label.pack(side="left", padx=5)
        
        self.preview_content = ctk.CTkLabel(self.msg_frame, text="", text_color=self.c_text_primary, wraplength=380, justify="left", font=ctk.CTkFont(size=14))
        self.preview_content.pack(anchor="w", padx=65)
        self.preview_embeds_area = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        self.preview_embeds_area.pack(fill="x", padx=65, pady=(5, 0))

    def reset_default_avatar(self):
        if self.has_icon and self.avatar_fallback_img:
            self.avatar_label.configure(image=self.avatar_fallback_img, text="")
        else:
            self.avatar_label.configure(image="", text="🤖", font=ctk.CTkFont(size=25), fg_color=self.accent_blurple, text_color="white", corner_radius=20)

    def fetch_webhook_info(self, event=None):
        url = self.url_entry.get().strip()
        if not url or "discord.com/api/webhooks" not in url:
            self.bot_name_label.configure(text="FyHook")
            self.reset_default_avatar()
            return

        def update_info():
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    data = res.json()
                    name = data.get("name", "FyHook")
                    avatar_id = data.get("avatar")
                    webhook_id = data.get("id")
                    
                    self.after(0, lambda n=name: self.bot_name_label.configure(text=n))
                    
                    if avatar_id and webhook_id:
                        img_url = f"https://cdn.discordapp.com/avatars/{webhook_id}/{avatar_id}.png?size=80"
                        self.download_and_set_avatar(img_url)
                    else:
                        self.after(0, self.reset_default_avatar)
                else:
                    self.after(0, lambda: self.bot_name_label.configure(text="FyHook"))
            except requests.exceptions.Timeout:
                pass
            except Exception:
                pass

        threading.Thread(target=update_info, daemon=True).start()

    def download_and_set_avatar(self, img_url):
        try:
            img_res = requests.get(img_url, timeout=5)
            if img_res.status_code == 200:
                img_data = img_res.content
                img = Image.open(io.BytesIO(img_data)).resize((40, 40), Image.Resampling.LANCZOS).convert("RGBA")
                
                mask = Image.new("L", (40, 40), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, 40, 40), fill=255)
                
                output = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
                output.paste(img, (0, 0), mask=mask)
                
                self.after(0, lambda o=output: self._apply_avatar_ui(o))
        except Exception as e:
            print(f"Avatar download error: {e}")

    def _apply_avatar_ui(self, pil_img):
        self.fetched_avatar_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(40, 40))
        self.avatar_label.configure(image=self.fetched_avatar_img, text="")

    def load_webhooks_from_file(self):
        if os.path.exists("webhooks.json"):
            try:
                with open("webhooks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception: return []
        return []

    def save_webhooks_to_file(self):
        try:
            with open("webhooks.json", "w", encoding="utf-8") as f:
                json.dump(self.saved_webhooks, f, indent=4)
        except Exception: pass

    def open_about_window(self):
        if hasattr(self, 'about_window') and self.about_window is not None:
            if self.about_window.winfo_exists():
                self.about_window.deiconify()
                self.about_window.lift()
                self.about_window.focus_force()
                return
            else:
                self.about_window = None
                
        about = ctk.CTkToplevel(self)
        self.about_window = about
        
        def on_closing():
            about.destroy()
            self.about_window = None
            
        about.protocol("WM_DELETE_WINDOW", on_closing)
        
        about.title("About & Settings")
        
        window_width = 450
        window_height = 480
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        about.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        about.configure(fg_color=self.c_bg_main)
        
        def apply_about_icon():
            if os.name == 'nt' and os.path.exists(self.icon_ico_path):
                try: about.iconbitmap(self.icon_ico_path)
                except: pass
            elif hasattr(self, 'icon_photo') and self.icon_photo:
                try: about.wm_iconphoto(False, self.icon_photo)
                except: pass
                
        about.after(250, apply_about_icon)

        if self.has_icon:
            ctk.CTkLabel(about, image=self.logo_img, text="").pack(pady=(20, 5))
        ctk.CTkLabel(about, text="FyHook", font=ctk.CTkFont(size=26, weight="bold"), text_color=self.c_text_primary).pack()
        ctk.CTkLabel(about, text=f"Version {self.version}", text_color=self.c_text_gray).pack(pady=(0, 15))

        info_frame = ctk.CTkFrame(about, fg_color=self.c_bg_sidebar, corner_radius=12)
        info_frame.pack(fill="both", expand=True, padx=30, pady=(10, 10))

        desc = "A modern Discord Webhook Manager.\nRedesigned for efficiency and style.\n\nDeveloped by furkanyasarr0"
        ctk.CTkLabel(info_frame, text=desc, justify="center", font=ctk.CTkFont(size=13), text_color=self.c_text_primary).pack(pady=15)

        status_frame = ctk.CTkFrame(info_frame, fg_color=self.c_bg_card, corner_radius=8, height=50)
        status_frame.pack(fill="x", padx=20, pady=10)
        
        self.update_status = ctk.CTkLabel(status_frame, text="Checking for updates...", font=ctk.CTkFont(size=12), text_color=self.c_text_gray)
        self.update_status.pack(pady=10)

        theme_frame = ctk.CTkFrame(info_frame, fg_color=self.c_bg_card, corner_radius=8, height=50)
        theme_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        ctk.CTkLabel(theme_frame, text="🎨 Appearance", font=ctk.CTkFont(weight="bold", size=12), text_color=self.c_text_primary).pack(side="left", padx=15)
        
        self.theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        
        def switch_event():
            value = self.theme_var.get()
            def apply_theme():
                ctk.set_appearance_mode(value)
                self.configure(fg_color=self.c_bg_main)
                if hasattr(self, 'about_window') and self.about_window and self.about_window.winfo_exists():
                    self.about_window.configure(fg_color=self.c_bg_main)
                
                self.content_text.configure(text_color=self.c_text_primary)
                self.json_text.configure(text_color=self.c_text_primary)
                for e in self.embeds_list:
                    if e["frame"].winfo_exists():
                        e["desc"].configure(text_color=self.c_text_primary)
                
                self.update_preview()
                
            self.after(50, apply_theme)
            
        theme_switch = ctk.CTkSwitch(theme_frame, text="Dark Mode", command=switch_event,
                                     variable=self.theme_var, onvalue="Dark", offvalue="Light",
                                     progress_color=self.accent_blurple, font=ctk.CTkFont(size=12, weight="bold"))
        theme_switch.pack(side="right", padx=15, pady=10)
        
        if ctk.get_appearance_mode() == "Dark":
            theme_switch.select()
        else:
            theme_switch.deselect()

        def check_updates():
            try:
                api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
                res = requests.get(api_url, timeout=5)
                
                if res.status_code == 200:
                    data = res.json()
                    latest_version = data["tag_name"].replace("v", "")
                    
                    def update_ui():
                        if latest_version > self.version:
                            self.update_status.configure(text=f"New version available: v{latest_version}", text_color=self.accent_blurple)
                            download_btn = ctk.CTkButton(info_frame, text="Download Update", fg_color=self.accent_blurple, text_color="white", corner_radius=8,
                                                         command=lambda: webbrowser.open(data["html_url"]))
                            download_btn.pack(pady=10)
                        else:
                            self.update_status.configure(text="You are using the latest version", text_color="#43B581")
                    self.after(0, update_ui)
                elif res.status_code == 404:
                    self.after(0, lambda: self.update_status.configure(text="No releases found on GitHub", text_color="#ED4245"))
                else:
                    self.after(0, lambda: self.update_status.configure(text=f"Update check error: {res.status_code}", text_color="#ED4245"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.update_status.configure(text="Error: Update check timed out", text_color="#ED4245"))
            except Exception:
                self.after(0, lambda: self.update_status.configure(text="Connection failed", text_color="#ED4245"))

        threading.Thread(target=check_updates, daemon=True).start()
        
        about.attributes("-topmost", True)
        about.after(200, lambda: about.attributes("-topmost", False))
        about.after(50, about.focus_force)

    def open_webhook_manager(self):
        if hasattr(self, 'manager_window') and self.manager_window is not None:
            if self.manager_window.winfo_exists():
                self.manager_window.deiconify()
                self.manager_window.lift()
                self.manager_window.focus_force()
                return
            else:
                self.manager_window = None
                
        manager = ctk.CTkToplevel(self)
        self.manager_window = manager
        
        def on_closing_mgr():
            manager.destroy()
            self.manager_window = None
            
        manager.protocol("WM_DELETE_WINDOW", on_closing_mgr)
        
        manager.title("Webhook Manager")
        
        window_width = 600
        window_height = 550
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        manager.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        manager.configure(fg_color=self.c_bg_main)
        
        def apply_manager_icon():
            if os.name == 'nt' and os.path.exists(self.icon_ico_path):
                try: manager.iconbitmap(self.icon_ico_path)
                except: pass
            elif hasattr(self, 'icon_photo') and self.icon_photo:
                try: manager.wm_iconphoto(False, self.icon_photo)
                except: pass
                
        manager.after(250, apply_manager_icon)

        ctk.CTkLabel(manager, text="Saved Webhooks", font=ctk.CTkFont(size=20, weight="bold"), text_color=self.c_text_primary).pack(pady=(20, 0))

        input_frame = ctk.CTkFrame(manager, fg_color=self.c_bg_sidebar, corner_radius=12)
        input_frame.pack(fill="x", padx=20, pady=20)

        name_entry = ctk.CTkEntry(input_frame, placeholder_text="Webhook Name (e.g. Logs Server)", text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=40, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray)
        name_entry.pack(fill="x", padx=20, pady=(20, 10))

        url_entry = ctk.CTkEntry(input_frame, placeholder_text="Discord Webhook URL", text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=40, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray)
        url_entry.pack(fill="x", padx=20, pady=(0, 15))

        def add_webhook():
            if len(self.saved_webhooks) >= 5: 
                return
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            if name and url:
                self.saved_webhooks.append({"name": name, "url": url})
                self.save_webhooks_to_file()
                refresh_list()
                name_entry.delete(0, "end")
                url_entry.delete(0, "end")

        ctk.CTkButton(input_frame, text="Save Webhook", fg_color=self.accent_blurple, text_color="white", height=40, corner_radius=8, font=ctk.CTkFont(weight="bold"), command=add_webhook).pack(pady=(0, 20))

        list_scroll = ctk.CTkScrollableFrame(manager, fg_color="transparent")
        list_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 20))

        def refresh_list():
            for w in list_scroll.winfo_children(): w.destroy()
            for i, hook in enumerate(self.saved_webhooks):
                h_frame = ctk.CTkFrame(list_scroll, fg_color=self.c_bg_sidebar, height=70, corner_radius=10)
                h_frame.pack(fill="x", pady=5)
                h_frame.pack_propagate(False)
                
                info_frame = ctk.CTkFrame(h_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)
                
                ctk.CTkLabel(info_frame, text=hook["name"], font=ctk.CTkFont(weight="bold", size=14), text_color=self.c_text_primary).pack(anchor="w")
                url_short = (hook["url"][:45] + "...") if len(hook["url"]) > 45 else hook["url"]
                ctk.CTkLabel(info_frame, text=url_short, font=ctk.CTkFont(size=11), text_color=self.c_text_gray).pack(anchor="w")

                def use_webhook(u=hook["url"]):
                    self.url_entry.delete(0, "end")
                    self.url_entry.insert(0, u)
                    self.fetch_webhook_info()
                    manager.destroy()

                def delete_webhook(idx=i):
                    self.saved_webhooks.pop(idx)
                    self.save_webhooks_to_file()
                    refresh_list()

                btns = ctk.CTkFrame(h_frame, fg_color="transparent")
                btns.pack(side="right", padx=15)
                
                ctk.CTkButton(btns, text="Use", width=70, height=32, corner_radius=6, fg_color="#248046", text_color="white", font=ctk.CTkFont(weight="bold"), command=use_webhook).pack(side="left", padx=5)
                ctk.CTkButton(btns, text="Delete", width=70, height=32, corner_radius=6, fg_color="transparent", border_width=1, border_color="#ED4245", text_color="#ED4245", hover_color=self.c_hover_red, command=delete_webhook).pack(side="left")

        refresh_list()
        
        manager.attributes("-topmost", True)
        manager.after(200, lambda: manager.attributes("-topmost", False))
        manager.after(50, manager.focus_force)

    def load_json_file(self):
        from tkinter import filedialog
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.json_text.delete("1.0", "end")
                    self.json_text.insert("1.0", f.read())
            except Exception as e:
                print(f"Error loading file: {e}")

    def import_json_data(self):
        try:
            raw_json = self.json_text.get("1.0", "end").strip()
            data = json.loads(raw_json)
            self.clear_all()
            if "content" in data: 
                self.content_text.insert("1.0", data["content"])
            if "embeds" in data:
                for emb in data["embeds"]:
                    self.add_embed()
                    e = self.embeds_list[-1]
                    if "author" in emb: e["author_name"].insert(0, emb["author"].get("name", ""))
                    if "title" in emb: e["title"].insert(0, emb["title"])
                    if "description" in emb: e["desc"].insert("1.0", emb["description"])
                    if "footer" in emb: e["footer_text"].insert(0, emb["footer"].get("text", ""))
                    if "color" in emb: e["color"].insert(0, f"#{emb['color']:06x}")
            self.toggle_json_editor()
            self.update_preview()
        except Exception as e:
            print(f"Import Error: {e}")

    def toggle_json_editor(self):
        if not self.is_json_mode:
            self.config_card.pack_forget()
            self.content_card.pack_forget()
            self.embeds_container.pack_forget()
            self.add_embed_btn.pack_forget()
            self.json_editor_frame.pack(fill="both", expand=True)
            self.json_editor_btn.configure(text=" 🎨  Visual Editor")
            self.json_text.delete("1.0", "end")
            self.json_text.insert("1.0", json.dumps(self.get_payload(), indent=4))
            self.is_json_mode = True
        else:
            self.json_editor_frame.pack_forget()
            self.config_card.pack(fill="x", padx=10, pady=(0, 20))
            self.content_card.pack(fill="x", padx=10, pady=(0, 20))
            self.embeds_container.pack(fill="x")
            self.add_embed_btn.pack(pady=(20, 40))
            self.json_editor_btn.configure(text=" 🛠️  JSON Editor")
            self.is_json_mode = False

    def add_embed(self):
        if len(self.embeds_list) >= 10: return
        
        e_frame = ctk.CTkFrame(self.embeds_container, fg_color=self.c_bg_sidebar, border_width=1, border_color=self.c_border_gray, corner_radius=12)
        e_frame.pack(fill="x", padx=10, pady=10)
        
        header = ctk.CTkFrame(e_frame, fg_color="transparent", height=50)
        header.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(header, text=f"EMBED #{len(self.embeds_list)+1}", font=ctk.CTkFont(size=14, weight="bold"), text_color=self.c_text_primary).pack(side="left")
        ctk.CTkButton(header, text="REMOVE", width=80, height=32, corner_radius=6, fg_color="transparent", border_width=1, border_color="#ED4245", text_color="#ED4245", hover_color=self.c_hover_red, font=ctk.CTkFont(size=11, weight="bold"), command=lambda f=e_frame: self.remove_embed(f)).pack(side="right")

        embed_data = {"frame": e_frame, "fields": []}

        def create_section(name, parent, open_by_default=False):
            sec_frame = ctk.CTkFrame(parent, fg_color="transparent")
            sec_frame.pack(fill="x", padx=15, pady=(0, 5))
            
            btn = ctk.CTkButton(sec_frame, text=f"▶  {name}", fg_color=self.c_bg_card, text_color=self.c_text_gray, anchor="w", font=ctk.CTkFont(size=12, weight="bold"), hover_color=self.c_bg_hover, corner_radius=6, height=38)
            btn.pack(fill="x")
            
            content = ctk.CTkFrame(sec_frame, fg_color="transparent")
            if open_by_default: 
                content.pack(fill="x", pady=10)
                btn.configure(text=f"▼  {name}")
                
            btn.configure(command=lambda c=content, b=btn, n=name: self.toggle_design_section(c, b, n))
            return content

        auth_c = create_section("Author Settings", e_frame)
        self.add_label_entry(auth_c, "Author Name", embed_data, "author_name")
        auth_urls = ctk.CTkFrame(auth_c, fg_color="transparent"); auth_urls.pack(fill="x"); auth_urls.grid_columnconfigure((0,1), weight=1)
        self.add_grid_entry(auth_urls, "Author URL", embed_data, "author_url", 0, 0)
        self.add_grid_entry(auth_urls, "Author Icon URL", embed_data, "author_icon", 0, 1)

        body_c = create_section("Body Settings", e_frame, True)
        self.add_label_entry(body_c, "Title", embed_data, "title")
        ctk.CTkLabel(body_c, text="Description", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).pack(anchor="w", pady=(5,0))
        embed_data["desc"] = ctk.CTkTextbox(body_c, height=100, text_color=self.c_text_primary, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, border_width=1)
        embed_data["desc"].pack(fill="x", pady=(2, 10))
        
        body_meta = ctk.CTkFrame(body_c, fg_color="transparent"); body_meta.pack(fill="x"); body_meta.grid_columnconfigure((0,1), weight=1)
        self.add_grid_entry(body_meta, "URL", embed_data, "url", 0, 0)
        self.add_color_entry(body_meta, "Color", embed_data, "color", 0, 1, placeholder="#58b9ff")

        fld_c = create_section("Fields", e_frame)
        add_field_btn = ctk.CTkButton(fld_c, text="+ Add Field", fg_color=self.c_bg_card, text_color=self.c_text_primary, hover_color=self.c_bg_hover, border_width=1, border_color=self.c_border_gray, width=120, height=35, corner_radius=6, font=ctk.CTkFont(size=12, weight="bold"), command=lambda c=None, d=embed_data["fields"]: self.add_field(self.get_f_list(fld_c), d))
        add_field_btn.pack(anchor="w", pady=(5, 10))
        f_list = ctk.CTkFrame(fld_c, fg_color="transparent")
        f_list.pack(fill="x")
        embed_data["f_list_widget"] = f_list

        img_c = create_section("Images", e_frame)
        self.add_label_entry(img_c, "Image URL", embed_data, "image_url")
        self.add_label_entry(img_c, "Thumbnail URL", embed_data, "thumb_url")

        foot_c = create_section("Footer Settings", e_frame)
        self.add_label_entry(foot_c, "Footer Text", embed_data, "footer_text")
        foot_meta = ctk.CTkFrame(foot_c, fg_color="transparent"); foot_meta.pack(fill="x"); foot_meta.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkLabel(foot_meta, text="Timestamp", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).grid(row=0, column=0, sticky="w")
        ts_frame = ctk.CTkFrame(foot_meta, fg_color=self.c_bg_card, height=42, corner_radius=8, border_width=1, border_color=self.c_border_gray)
        ts_frame.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=5)
        embed_data["timestamp"] = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(ts_frame, text="Add Timestamp", text_color=self.c_text_primary, variable=embed_data["timestamp"], command=self.update_preview, font=ctk.CTkFont(size=12), fg_color=self.accent_blurple).pack(side="left", padx=15, pady=10)
        
        self.add_grid_entry(foot_meta, "Footer Icon URL", embed_data, "footer_icon", 0, 1)

        ctk.CTkFrame(e_frame, fg_color="transparent", height=10).pack()

        for k in ["author_name", "author_url", "author_icon", "title", "url", "color", "image_url", "thumb_url", "footer_text", "footer_icon"]:
            embed_data[k].bind("<KeyRelease>", lambda e: self.update_preview())
        embed_data["desc"].bind("<KeyRelease>", lambda e: self.update_preview())

        self.embeds_list.append(embed_data)
        self.update_preview()

    def add_label_entry(self, parent, label, data_dict, key, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).pack(anchor="w", pady=(5,0))
        data_dict[key] = ctk.CTkEntry(parent, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=42, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, placeholder_text=placeholder)
        data_dict[key].pack(fill="x", pady=(2, 10))

    def add_grid_entry(self, parent, label, data_dict, key, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).grid(row=row*2, column=col, sticky="w", pady=(5,0))
        data_dict[key] = ctk.CTkEntry(parent, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=42, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, placeholder_text=placeholder)
        data_dict[key].grid(row=row*2+1, column=col, sticky="ew", padx=(5 if col==1 else 0, 5 if col==0 else 0), pady=(2, 10))

    def add_color_entry(self, parent, label, data_dict, key, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).grid(row=row*2, column=col, sticky="w", pady=(5,0))
        
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row*2+1, column=col, sticky="ew", padx=(5 if col==1 else 0, 5 if col==0 else 0), pady=(2, 10))
        f.grid_columnconfigure(0, weight=1)
        
        data_dict[key] = ctk.CTkEntry(f, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=42, corner_radius=8, fg_color=self.c_bg_card, border_color=self.c_border_gray, placeholder_text=placeholder)
        data_dict[key].grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        def pick_color():
            color_code = colorchooser.askcolor(title="Choose Embed Color")[1]
            if color_code:
                data_dict[key].delete(0, "end")
                data_dict[key].insert(0, color_code)
                self.update_preview()
                
        btn = ctk.CTkButton(f, text="🎨", text_color=self.c_text_primary, width=42, height=42, corner_radius=8, fg_color=self.c_bg_card, hover_color=self.c_bg_hover, border_width=1, border_color=self.c_border_gray, command=pick_color)
        btn.grid(row=0, column=1)

    def toggle_design_section(self, frame, btn, name):
        if frame.winfo_viewable():
            frame.pack_forget()
            btn.configure(text=f"▶  {name}")
        else:
            frame.pack(fill="x", pady=10)
            btn.configure(text=f"▼  {name}")

    def get_f_list(self, parent):
        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") == "transparent":
                return child
        return parent

    def add_field(self, container, data):
        f = ctk.CTkFrame(container, fg_color=self.c_bg_card, corner_radius=8, border_width=1, border_color=self.c_border_gray)
        f.pack(fill="x", pady=5)
        f.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(f, text="Field Name", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))
        n_entry = ctk.CTkEntry(f, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=35, corner_radius=6, fg_color=self.c_bg_sidebar, border_color=self.c_border_gray)
        n_entry.grid(row=1, column=0, sticky="ew", padx=(15, 5), pady=(5, 5))
        
        ctk.CTkLabel(f, text="Field Value", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.c_text_gray).grid(row=0, column=1, sticky="w", padx=5, pady=(10, 0))
        v_entry = ctk.CTkEntry(f, text_color=self.c_text_primary, placeholder_text_color=self.c_text_gray, height=35, corner_radius=6, fg_color=self.c_bg_sidebar, border_color=self.c_border_gray)
        v_entry.grid(row=1, column=1, sticky="ew", padx=(5, 15), pady=(5, 5))
        
        ctrl = ctk.CTkFrame(f, fg_color="transparent")
        ctrl.grid(row=2, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 10))
        
        inline_v = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(ctrl, text="Inline", text_color=self.c_text_primary, variable=inline_v, command=self.update_preview, font=ctk.CTkFont(size=12), fg_color=self.accent_blurple, checkbox_width=18, checkbox_height=18).pack(side="left")
        ctk.CTkButton(ctrl, text="Remove", width=70, height=26, corner_radius=6, fg_color="transparent", text_color="#ED4245", hover_color=self.c_hover_red, font=ctk.CTkFont(size=11, weight="bold"), command=lambda: self.remove_field(f, data)).pack(side="right")
        
        n_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        v_entry.bind("<KeyRelease>", lambda e: self.update_preview())
        data.append({"frame": f, "name": n_entry, "value": v_entry, "inline": inline_v})
        self.update_preview()

    def remove_field(self, frame, data):
        frame.destroy()
        self.update_preview()

    def remove_embed(self, frame):
        frame.destroy()
        self.embeds_list = [e for e in self.embeds_list if e["frame"].winfo_exists()]
        self.update_preview()

    def get_payload(self):
        content = self.content_text.get("1.0", "end").strip()
        payload = {}
        if content: payload["content"] = content
        embeds = []
        for e in self.embeds_list:
            if not e["frame"].winfo_exists(): continue
            emb = {}
            if e["author_name"].get().strip():
                emb["author"] = {"name": e["author_name"].get().strip()}
                if e["author_url"].get().strip(): emb["author"]["url"] = e["author_url"].get().strip()
                if e["author_icon"].get().strip(): emb["author"]["icon_url"] = e["author_icon"].get().strip()
            if e["title"].get().strip(): 
                emb["title"] = e["title"].get().strip()
                if e["url"].get().strip(): emb["url"] = e["url"].get().strip()
            if e["desc"].get("1.0", "end").strip(): emb["description"] = e["desc"].get("1.0", "end").strip()
            if e["image_url"].get().strip(): emb["image"] = {"url": e["image_url"].get().strip()}
            if e["thumb_url"].get().strip(): emb["thumbnail"] = {"url": e["thumb_url"].get().strip()}
            if e["footer_text"].get().strip():
                emb["footer"] = {"text": e["footer_text"].get().strip()}
                if e["footer_icon"].get().strip(): emb["footer"]["icon_url"] = e["footer_icon"].get().strip()
            if e["timestamp"].get(): emb["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            color = e["color"].get().replace("#", "").strip()
            if color:
                if re.match(r'^(?:[0-9a-fA-F]{3}){1,2}$', color):
                    try: emb["color"] = int(color, 16)
                    except: pass
                    
            f_list = []
            for f in e["fields"]:
                if f["frame"].winfo_exists() and f["name"].get().strip() and f["value"].get().strip():
                    f_list.append({"name": f["name"].get().strip(), "value": f["value"].get().strip(), "inline": f["inline"].get()})
            if f_list: emb["fields"] = f_list
            if emb: embeds.append(emb)
        if embeds: payload["embeds"] = embeds
        return payload

    def update_preview(self, event=None):
        payload = self.get_payload()
        self.preview_content.configure(text=payload.get("content", ""))
        for w in self.preview_embeds_area.winfo_children(): w.destroy()
        
        for emb in payload.get("embeds", []):
            f = ctk.CTkFrame(self.preview_embeds_area, fg_color=self.c_bg_sidebar, corner_radius=4)
            f.pack(fill="x", pady=5)
            
            col = f"#{emb.get('color', 2109733):06x}"
            side = ctk.CTkFrame(f, width=4, corner_radius=0, fg_color=col)
            side.pack(side="left", fill="y")
            
            c = ctk.CTkFrame(f, fg_color="transparent")
            c.pack(side="left", fill="both", expand=True, padx=15, pady=12)
            
            if "author" in emb: 
                auth_f = ctk.CTkFrame(c, fg_color="transparent")
                auth_f.pack(anchor="w", pady=(0, 5))
                ctk.CTkLabel(auth_f, text=emb["author"]["name"], font=ctk.CTkFont(weight="bold", size=13), text_color=self.c_text_primary).pack(side="left")
            
            if "title" in emb: 
                ctk.CTkLabel(c, text=emb["title"], font=ctk.CTkFont(weight="bold", size=15), text_color=self.c_blue_link).pack(anchor="w", pady=(0, 5))
                
            if "description" in emb: 
                ctk.CTkLabel(c, text=emb["description"], text_color=self.c_text_gray, wraplength=330, justify="left").pack(anchor="w", pady=(0, 5))
                
            if "fields" in emb:
                fg = ctk.CTkFrame(c, fg_color="transparent")
                fg.pack(fill="x", pady=5)
                for fld in emb["fields"]:
                    fld_f = ctk.CTkFrame(fg, fg_color="transparent")
                    fld_f.pack(anchor="w", pady=2)
                    ctk.CTkLabel(fld_f, text=fld["name"], font=ctk.CTkFont(weight="bold", size=13), text_color=self.c_text_primary).pack(anchor="w")
                    ctk.CTkLabel(fld_f, text=fld["value"], text_color=self.c_text_gray).pack(anchor="w")
                    
            if "image" in emb:
                self.load_preview_image(c, emb["image"]["url"], "image")
            if "thumbnail" in emb:
                self.load_preview_image(c, emb["thumbnail"]["url"], "thumbnail")
                
            if "footer" in emb: 
                foot_f = ctk.CTkFrame(c, fg_color="transparent")
                foot_f.pack(anchor="w", pady=(10,0))
                ctk.CTkLabel(foot_f, text=emb["footer"]["text"], font=ctk.CTkFont(size=11), text_color=self.c_text_gray).pack(side="left")

    def load_preview_image(self, parent, url, type):
        def download():
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    img_data = res.content
                    img = Image.open(io.BytesIO(img_data)).convert("RGBA")
                    
                    if type == "image":
                        w, h = img.size
                        new_w = 300
                        new_h = int((h / w) * new_w) if w > 0 else 300
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                        size = (new_w, new_h)
                    else:
                        img = img.resize((80, 80), Image.Resampling.LANCZOS)
                        size = (80, 80)
                    
                    self.after(0, lambda i=img, s=size: update_ui(i, s))
            except Exception: pass

        def update_ui(pil_img, size):
            if not hasattr(self, 'preview_imgs'): self.preview_imgs = []
            tk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=size)
            self.preview_imgs.append(tk_img)
            lbl = ctk.CTkLabel(parent, image=tk_img, text="")
            if type == "image":
                lbl.pack(anchor="w", pady=(10, 0))
            else:
                lbl.pack(anchor="ne", pady=(5, 0))

        threading.Thread(target=download, daemon=True).start()

    def load_message_link(self):
        url = self.url_entry.get().strip()
        msg_link = self.msg_link_entry.get().strip()
        
        if not url:
            self.status_label.configure(text="URL Required!", text_color="#ED4245")
            return
        if not msg_link:
            self.status_label.configure(text="Message Link Required!", text_color="#ED4245")
            return

        self.status_label.configure(text="Loading...", text_color=self.accent_blurple)

        def fetch_task():
            try:
                msg_id = msg_link.split("/")[-1]
                if "?" in msg_id: msg_id = msg_id.split("?")[0]
                
                load_url = f"{url}/messages/{msg_id}"
                res = requests.get(load_url, timeout=10)
                
                if res.status_code == 200:
                    data = res.json()
                    self.after(0, lambda d=data: self.apply_loaded_message(d))
                else:
                    self.after(0, lambda: self.status_label.configure(text=f"Failed: {res.status_code}", text_color="#ED4245"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.status_label.configure(text="Timed Out!", text_color="#ED4245"))
            except Exception:
                self.after(0, lambda: self.status_label.configure(text="Error", text_color="#ED4245"))

        threading.Thread(target=fetch_task, daemon=True).start()

    def apply_loaded_message(self, data):
        self.clear_all_internal()
        
        if "content" in data and data["content"]:
            self.content_text.insert("1.0", data["content"])
        
        if "embeds" in data:
            for emb in data["embeds"]:
                self.add_embed()
                e = self.embeds_list[-1]
                
                if "author" in emb:
                    e["author_name"].insert(0, emb["author"].get("name", ""))
                    e["author_url"].insert(0, emb["author"].get("url", ""))
                    e["author_icon"].insert(0, emb["author"].get("icon_url", ""))
                
                if "title" in emb: e["title"].insert(0, emb["title"])
                if "url" in emb: e["url"].insert(0, emb["url"])
                if "description" in emb: e["desc"].insert("1.0", emb["description"])
                if "color" in emb: e["color"].insert(0, f"#{emb['color']:06x}")
                
                if "image" in emb: e["image_url"].insert(0, emb["image"].get("url", ""))
                if "thumbnail" in emb: e["thumb_url"].insert(0, emb["thumbnail"].get("url", ""))
                
                if "footer" in emb:
                    e["footer_text"].insert(0, emb["footer"].get("text", ""))
                    e["footer_icon"].insert(0, emb["footer"].get("icon_url", ""))
                
                if "fields" in emb:
                    for fld in emb["fields"]:
                        self.add_field(e["f_list_widget"], e["fields"])
                        f_item = e["fields"][-1]
                        f_item["name"].insert(0, fld.get("name", ""))
                        f_item["value"].insert(0, fld.get("value", ""))
                        f_item["inline"].set(fld.get("inline", False))

        self.update_preview()
        self.status_label.configure(text="Loaded!", text_color="#43B581")

    def clear_all_internal(self):
        self.content_text.delete("1.0", "end")
        for e in self.embeds_list: e["frame"].destroy()
        self.embeds_list = []

    def send_webhook(self):
        url = self.url_entry.get().strip()
        msg_link = self.msg_link_entry.get().strip()
        
        if not url:
            self.status_label.configure(text="URL Required", text_color="#ED4245")
            return

        self.status_label.configure(text="Sending...", text_color=self.c_text_gray)
        payload = self.get_payload()

        def send_task():
            try:
                if msg_link:
                    msg_id = msg_link.split("/")[-1]
                    if "?" in msg_id: msg_id = msg_id.split("?")[0]
                    edit_url = f"{url}/messages/{msg_id}"
                    res = requests.patch(edit_url, json=payload, timeout=10)
                    mode = "Edited"
                else:
                    res = requests.post(url, json=payload, timeout=10)
                    mode = "Sent"
                
                if res.status_code in [200, 204]:
                    self.after(0, lambda: self.status_label.configure(text=f"Success: {mode}!", text_color="#43B581"))
                else:
                    self.after(0, lambda: self.status_label.configure(text=f"Error: {res.status_code}", text_color="#ED4245"))
            except requests.exceptions.Timeout:
                self.after(0, lambda: self.status_label.configure(text="Timed Out!", text_color="#ED4245"))
            except Exception:
                self.after(0, lambda: self.status_label.configure(text="Connection Error", text_color="#ED4245"))

        threading.Thread(target=send_task, daemon=True).start()

    def clear_all(self):
        self.url_entry.delete(0, "end")
        self.msg_link_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        for e in self.embeds_list: e["frame"].destroy()
        self.embeds_list = []
        self.update_preview()
        self.reset_default_avatar()
        self.bot_name_label.configure(text="FyHook")
        self.status_label.configure(text="Cleared", text_color="#43B581")

if __name__ == "__main__":
    app = FyHookApp()
    app.mainloop()