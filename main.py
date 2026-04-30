import tkinter as tk
import customtkinter as ctk
import requests
import json
from datetime import datetime, timezone

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class FyHookApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FyHook - Discord Webhook Manager")
        self.geometry("1400x900")
        
        # Colors - Discohook Pro Palette
        self.bg_dark = "#1E1F22"
        self.bg_medium = "#2B2D31"
        self.bg_light = "#313338"
        self.accent_blurple = "#5865F2"
        self.text_gray = "#B5BAC1"
        self.border_gray = "#3F4147"
        
        self.saved_webhooks = self.load_webhooks_from_file()
        
        self.configure(fg_color=self.bg_dark)
        self.version = "1.0.0"
        self.github_repo = "furkanyasarr0/FyHook" # Değiştirmeyi unutmayın
        self.embeds_list = []
        self.is_json_mode = False
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=self.bg_dark, border_width=1, border_color=self.border_gray)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="FyHook", font=ctk.CTkFont(size=28, weight="bold"), text_color="white").pack(pady=40)
        
        ctk.CTkButton(self.sidebar, text="Send Webhook", height=45, corner_radius=8, font=ctk.CTkFont(weight="bold"), fg_color=self.accent_blurple, hover_color="#4752C4", command=self.send_webhook).pack(pady=10, padx=25, fill="x")
        
        self.webhooks_mgr_btn = ctk.CTkButton(self.sidebar, text="Webhooks", height=45, corner_radius=8, fg_color="transparent", border_width=1, border_color=self.border_gray, hover_color=self.bg_light, command=self.open_webhook_manager)
        self.webhooks_mgr_btn.pack(pady=10, padx=25, fill="x")
        
        self.json_editor_btn = ctk.CTkButton(self.sidebar, text="JSON Data Editor", height=45, corner_radius=8, fg_color="transparent", border_width=1, border_color=self.border_gray, hover_color=self.bg_light, command=self.toggle_json_editor)
        self.json_editor_btn.pack(pady=10, padx=25, fill="x")
        ctk.CTkButton(self.sidebar, text="Clear All", height=45, corner_radius=8, fg_color="transparent", border_width=1, border_color="#ED4245", text_color="#ED4245", hover_color="#2A191B", command=self.clear_all).pack(pady=10, padx=25, fill="x")

        # Bottom Sidebar
        self.sidebar_bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.sidebar_bottom.pack(side="bottom", fill="x", pady=20)
        
        self.about_btn = ctk.CTkButton(self.sidebar_bottom, text="About & Updates", height=35, corner_radius=8, fg_color="transparent", border_width=1, border_color=self.border_gray, hover_color=self.bg_light, command=self.open_about_window)
        self.about_btn.pack(pady=5, padx=25, fill="x")
        
        self.version_label = ctk.CTkLabel(self.sidebar_bottom, text=f"v{self.version}", font=ctk.CTkFont(size=10), text_color=self.text_gray)
        self.version_label.pack()

        # --- Editor ---
        self.editor = ctk.CTkScrollableFrame(self, label_text="WEBHOOK EDITOR", fg_color=self.bg_medium, label_text_color=self.text_gray, label_font=ctk.CTkFont(size=11, weight="bold"))
        self.editor.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.editor.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=15)
        
        ctk.CTkLabel(self.header_frame, text="Webhook URL", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_gray).pack(anchor="w", padx=5, pady=(15,0))
        self.url_entry = ctk.CTkEntry(self.header_frame, placeholder_text="Paste Discord Webhook URL here...", height=42, fg_color=self.bg_dark, border_color=self.border_gray)
        self.url_entry.pack(pady=(5, 10), padx=5, fill="x")
        self.url_entry.bind("<KeyRelease>", lambda e: self.fetch_webhook_info())
        self.url_entry.bind("<FocusOut>", lambda e: self.fetch_webhook_info())
        self.url_entry.bind("<<Paste>>", lambda e: self.after(100, self.fetch_webhook_info))

        # Message Link Section
        ctk.CTkLabel(self.header_frame, text="Message Link", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_gray).pack(anchor="w", padx=5, pady=(5,0))
        msg_link_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        msg_link_frame.pack(fill="x", pady=(5, 0))
        
        self.msg_link_entry = ctk.CTkEntry(msg_link_frame, placeholder_text="https://discord.com/channels/...", height=42, fg_color=self.bg_dark, border_color=self.border_gray)
        self.msg_link_entry.pack(side="left", fill="x", expand=True, padx=(5, 10))
        
        self.load_msg_btn = ctk.CTkButton(msg_link_frame, text="Load", width=80, height=42, corner_radius=6, fg_color="transparent", border_width=1, border_color=self.border_gray, hover_color=self.bg_light, command=self.load_message_link)
        self.load_msg_btn.pack(side="right", padx=5)
        
        info_text = "When a message link is set, pressing submit or edit will edit the message sent inside of Discord. To load a message sent in Discord, use the 'Load' button or the bot's 'restore' command found in the apps section of the right click menu on any message."
        ctk.CTkLabel(self.header_frame, text=info_text, font=ctk.CTkFont(size=11, slant="italic"), text_color="#8E9297", wraplength=700, justify="left").pack(anchor="w", padx=5, pady=(5, 15))
        
        ctk.CTkLabel(self.header_frame, text="Message Content", font=ctk.CTkFont(size=12, weight="bold"), text_color=self.text_gray).pack(anchor="w", padx=5, pady=(5,0))
        self.content_text = ctk.CTkTextbox(self.header_frame, height=120, fg_color=self.bg_dark, border_color=self.border_gray, border_width=1)
        self.content_text.pack(pady=(5, 15), padx=5, fill="x")
        self.content_text.bind("<KeyRelease>", lambda e: self.update_preview())

        self.embeds_container = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.embeds_container.pack(fill="x")
        
        self.add_embed_btn = ctk.CTkButton(self.editor, text="+ Add New Embed", height=45, corner_radius=8, fg_color="#248046", hover_color="#1A6334", font=ctk.CTkFont(weight="bold"), command=self.add_embed)
        self.add_embed_btn.pack(pady=40)

        # JSON Editor (Hidden by default)
        self.json_editor_frame = ctk.CTkFrame(self.editor, fg_color="transparent")
        self.json_text = ctk.CTkTextbox(self.json_editor_frame, height=500, font=ctk.CTkFont(family="Courier", size=13))
        self.json_text.pack(fill="both", expand=True, padx=20, pady=10)
        ctk.CTkButton(self.json_editor_frame, text="Import JSON to Visual Editor", fg_color="#5865F2", height=40, command=self.import_json_data).pack(pady=10)

        # --- Preview ---
        self.preview_panel = ctk.CTkFrame(self, width=450, fg_color="#36393f")
        self.preview_panel.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        self.preview_panel.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self.preview_panel, text="Discord Preview", font=ctk.CTkFont(weight="bold")).pack(pady=15)
        
        self.preview_scroll = ctk.CTkScrollableFrame(self.preview_panel, fg_color="transparent")
        self.preview_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.msg_frame = ctk.CTkFrame(self.preview_scroll, fg_color="transparent")
        self.msg_frame.pack(fill="x", pady=10)

        # User Info Header (Image + Name + Tag + Time)
        self.user_info_frame = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        self.user_info_frame.pack(fill="x", padx=10, pady=(0, 5))

        # Avatar placeholder (rounded circle simulation)
        self.avatar_canvas = tk.Canvas(self.user_info_frame, width=40, height=40, bg=self.bg_dark, highlightthickness=0)
        self.avatar_canvas.pack(side="left", padx=(0, 10))
        
        # Default avatar circle
        self.avatar_circle = self.avatar_canvas.create_oval(2, 2, 38, 38, fill=self.accent_blurple, outline="")
        self.avatar_text = self.avatar_canvas.create_text(20, 20, text="FH", fill="white", font=ctk.CTkFont(size=12, weight="bold"))

        self.name_info_frame = ctk.CTkFrame(self.user_info_frame, fg_color="transparent")
        self.name_info_frame.pack(side="left", fill="y")

        self.bot_name_label = ctk.CTkLabel(self.name_info_frame, text="FyHook", font=ctk.CTkFont(size=14, weight="bold"), text_color="white")
        self.bot_name_label.pack(side="left")

        self.bot_tag = ctk.CTkFrame(self.name_info_frame, fg_color=self.accent_blurple, corner_radius=3)
        self.bot_tag.pack(side="left", padx=5)
        ctk.CTkLabel(self.bot_tag, text="BOT", font=ctk.CTkFont(size=10, weight="bold"), text_color="white", height=15).pack(padx=3)

        self.timestamp_label = ctk.CTkLabel(self.name_info_frame, text="Today at 11:49 PM", font=ctk.CTkFont(size=12), text_color=self.text_gray)
        self.timestamp_label.pack(side="left", padx=5)
        
        self.preview_content = ctk.CTkLabel(self.msg_frame, text="", text_color="#dcddde", wraplength=350, justify="left", font=ctk.CTkFont(size=14))
        self.preview_content.pack(anchor="w", padx=50)
        self.preview_embeds_area = ctk.CTkFrame(self.msg_frame, fg_color="transparent")
        self.preview_embeds_area.pack(fill="x", padx=50)
        self.status_label = ctk.CTkLabel(self.preview_panel, text="Status: Ready", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=15)

    # --- Methods ---
    def fetch_webhook_info(self, event=None):
        url = self.url_entry.get().strip()
        print(f"DEBUG: Webhook URL check: {url}")
        if not url or "discord.com/api/webhooks" not in url:
            self.bot_name_label.configure(text="FyHook")
            self.avatar_canvas.delete("all")
            self.avatar_circle = self.avatar_canvas.create_oval(2, 2, 38, 38, fill=self.accent_blurple, outline="")
            self.avatar_text = self.avatar_canvas.create_text(20, 20, text="FH", fill="white", font=ctk.CTkFont(size=12, weight="bold"))
            return

        def update_info():
            try:
                print(f"DEBUG: Fetching from Discord API...")
                res = requests.get(url, timeout=5)
                print(f"DEBUG: API Response Code: {res.status_code}")
                if res.status_code == 200:
                    data = res.json()
                    name = data.get("name", "FyHook")
                    avatar_id = data.get("avatar")
                    webhook_id = data.get("id")
                    print(f"DEBUG: Webhook Name: {name}, Avatar ID: {avatar_id}")
                    
                    def apply_to_ui(n=name, a_id=avatar_id, w_id=webhook_id):
                        self.bot_name_label.configure(text=n)
                        
                        if a_id and w_id:
                            img_url = f"https://cdn.discordapp.com/avatars/{w_id}/{a_id}.png?size=40"
                            print(f"DEBUG: Avatar URL: {img_url}")
                            def download_avatar():
                                try:
                                    img_res = requests.get(img_url, timeout=5)
                                    if img_res.status_code == 200:
                                        from PIL import Image, ImageTk
                                        import io
                                        img_data = img_res.content
                                        img = Image.open(io.BytesIO(img_data)).resize((40, 40), Image.Resampling.LANCZOS)
                                        
                                        mask = Image.new("L", (40, 40), 0)
                                        from PIL import ImageDraw
                                        draw = ImageDraw.Draw(mask)
                                        draw.ellipse((0, 0, 40, 40), fill=255)
                                        
                                        output = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
                                        output.paste(img, (0, 0), mask=mask)
                                        
                                        self.avatar_img = ImageTk.PhotoImage(output)
                                        
                                        def update_canvas():
                                            self.avatar_canvas.delete("all")
                                            self.avatar_canvas.create_image(0, 0, anchor="nw", image=self.avatar_img)
                                        self.after(0, update_canvas)
                                        print(f"DEBUG: Avatar updated successfully")
                                    else:
                                        print(f"DEBUG: Avatar download failed code {img_res.status_code}")
                                except Exception as e:
                                    print(f"DEBUG: Avatar download error: {e}")
                            
                            import threading
                            threading.Thread(target=download_avatar, daemon=True).start()
                        else:
                            print(f"DEBUG: No avatar found, using default")
                            self.avatar_canvas.delete("all")
                            self.avatar_circle = self.avatar_canvas.create_oval(2, 2, 38, 38, fill=self.accent_blurple, outline="")
                            self.avatar_text = self.avatar_canvas.create_text(20, 20, text="FH", fill="white", font=ctk.CTkFont(size=12, weight="bold"))

                    self.after(0, apply_to_ui)
                else:
                    print(f"DEBUG: Webhook API error: {res.status_code}")
                    self.bot_name_label.configure(text="FyHook")
            except Exception as e:
                print(f"DEBUG: General Fetch Error: {e}")

        import threading
        threading.Thread(target=update_info, daemon=True).start()

    def load_webhooks_from_file(self):
        import os
        if os.path.exists("webhooks.json"):
            try:
                with open("webhooks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except: return []
        return []

    def save_webhooks_to_file(self):
        with open("webhooks.json", "w", encoding="utf-8") as f:
            json.dump(self.saved_webhooks, f, indent=4)

    def open_about_window(self):
        about = ctk.CTkToplevel(self)
        about.title("About & Updates")
        about.geometry("450x400")
        about.configure(fg_color=self.bg_dark)
        about.transient(self)
        about.grab_set()

        ctk.CTkLabel(about, text="FyHook", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=(30, 5))
        ctk.CTkLabel(about, text=f"Version {self.version}", text_color=self.text_gray).pack()

        info_frame = ctk.CTkFrame(about, fg_color=self.bg_medium, corner_radius=10)
        info_frame.pack(fill="both", expand=True, padx=30, pady=20)

        desc = "A modern Discord Webhook Manager\nbuilt with Python & CustomTkinter.\n\nDeveloped by FyHook Team"
        ctk.CTkLabel(info_frame, text=desc, justify="center").pack(pady=20)

        status_frame = ctk.CTkFrame(info_frame, fg_color=self.bg_dark, height=50)
        status_frame.pack(fill="x", padx=15, pady=10)
        
        self.update_status = ctk.CTkLabel(status_frame, text="Checking for updates...", font=ctk.CTkFont(size=12))
        self.update_status.pack(pady=10)

        def check_updates():
            try:
                # GitHub API üzerinden son sürümü kontrol et
                # Not: Gerçek repo isminizi self.github_repo'ya yazmalısınız
                api_url = f"https://api.github.com/repos/{self.github_repo}/releases/latest"
                res = requests.get(api_url, timeout=5)
                if res.status_code == 200:
                    latest_version = res.json()["tag_name"].replace("v", "")
                    if latest_version > self.version:
                        self.update_status.configure(text=f"New version available: v{latest_version}", text_color=self.accent_blurple)
                        ctk.CTkButton(info_frame, text="Download Update", fg_color=self.accent_blurple, 
                                     command=lambda: import_webbrowser().open(res.json()["html_url"])).pack(pady=10)
                    else:
                        self.update_status.configure(text="You are using the latest version", text_color="#43B581")
                else:
                    self.update_status.configure(text="Could not check updates", text_color="#ED4245")
            except:
                self.update_status.configure(text="Update check failed", text_color="#ED4245")

        def import_webbrowser():
            import webbrowser
            return webbrowser

        import threading
        threading.Thread(target=check_updates, daemon=True).start()

    def open_webhook_manager(self):
        manager = ctk.CTkToplevel(self)
        manager.title("Webhook Manager")
        manager.geometry("600x500")
        manager.configure(fg_color=self.bg_dark)
        manager.transient(self)
        manager.grab_set()

        # Input Frame
        input_frame = ctk.CTkFrame(manager, fg_color=self.bg_medium, corner_radius=10)
        input_frame.pack(fill="x", padx=20, pady=20)

        name_entry = ctk.CTkEntry(input_frame, placeholder_text="Webhook Name (e.g. Logs)", height=40, fg_color=self.bg_dark)
        name_entry.pack(fill="x", padx=15, pady=(15, 5))

        url_entry = ctk.CTkEntry(input_frame, placeholder_text="Discord Webhook URL", height=40, fg_color=self.bg_dark)
        url_entry.pack(fill="x", padx=15, pady=5)

        def add_webhook():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            if name and url:
                self.saved_webhooks.append({"name": name, "url": url})
                self.save_webhooks_to_file()
                refresh_list()
                name_entry.delete(0, "end")
                url_entry.delete(0, "end")

        ctk.CTkButton(input_frame, text="Add Webhook", fg_color=self.accent_blurple, command=add_webhook).pack(pady=15)

        # List Frame
        list_scroll = ctk.CTkScrollableFrame(manager, fg_color="transparent")
        list_scroll.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def refresh_list():
            for w in list_scroll.winfo_children(): w.destroy()
            for i, hook in enumerate(self.saved_webhooks):
                h_frame = ctk.CTkFrame(list_scroll, fg_color=self.bg_medium, height=60)
                h_frame.pack(fill="x", pady=5)
                
                info_frame = ctk.CTkFrame(h_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="both", expand=True, padx=15)
                
                ctk.CTkLabel(info_frame, text=hook["name"], font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=(5, 0))
                url_short = (hook["url"][:40] + "...") if len(hook["url"]) > 40 else hook["url"]
                ctk.CTkLabel(info_frame, text=url_short, font=ctk.CTkFont(size=10), text_color=self.text_gray).pack(anchor="w")

                def use_webhook(u=hook["url"]):
                    self.url_entry.delete(0, "end")
                    self.url_entry.insert(0, u)
                    manager.destroy()

                def delete_webhook(idx=i):
                    self.saved_webhooks.pop(idx)
                    self.save_webhooks_to_file()
                    refresh_list()

                ctk.CTkButton(h_frame, text="Use", width=60, height=30, fg_color="#248046", command=use_webhook).pack(side="left", padx=5)
                ctk.CTkButton(h_frame, text="Delete", width=60, height=30, fg_color="#ED4245", command=delete_webhook).pack(side="left", padx=15)

        refresh_list()

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
            self.header_frame.pack_forget()
            self.embeds_container.pack_forget()
            self.add_embed_btn.pack_forget()
            self.json_editor_frame.pack(fill="both", expand=True)
            self.json_editor_btn.configure(text="Visual Editor")
            self.json_text.delete("1.0", "end")
            self.json_text.insert("1.0", json.dumps(self.get_payload(), indent=4))
            self.is_json_mode = True
        else:
            self.json_editor_frame.pack_forget()
            self.header_frame.pack(fill="x")
            self.embeds_container.pack(fill="x")
            self.add_embed_btn.pack(pady=30)
            self.json_editor_btn.configure(text="JSON Data Editor")
            self.is_json_mode = False

    def add_embed(self):
        if len(self.embeds_list) >= 10: return
        
        e_frame = ctk.CTkFrame(self.embeds_container, fg_color=self.bg_medium, border_width=1, border_color=self.border_gray, corner_radius=10)
        e_frame.pack(fill="x", padx=15, pady=15)
        
        header = ctk.CTkFrame(e_frame, fg_color=self.bg_light, height=50, corner_radius=10)
        header.pack(fill="x", padx=2, pady=2)
        ctk.CTkLabel(header, text=f"EMBED #{len(self.embeds_list)+1}", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(side="left", padx=20)
        ctk.CTkButton(header, text="REMOVE", width=80, height=30, corner_radius=6, fg_color="#ED4245", hover_color="#C03537", font=ctk.CTkFont(size=11, weight="bold"), command=lambda f=e_frame: self.remove_embed(f)).pack(side="right", padx=15)

        embed_data = {"frame": e_frame, "fields": []}

        def create_section(name, parent, open_by_default=False):
            sec_frame = ctk.CTkFrame(parent, fg_color="transparent")
            sec_frame.pack(fill="x", padx=10, pady=(5, 0))
            
            btn = ctk.CTkButton(sec_frame, text=f"▶  {name.upper()}", fg_color="transparent", text_color=self.text_gray, anchor="w", font=ctk.CTkFont(size=11, weight="bold"), hover_color=self.bg_light, height=35)
            btn.pack(fill="x")
            
            content = ctk.CTkFrame(sec_frame, fg_color="transparent")
            if open_by_default: 
                content.pack(fill="x", padx=15, pady=10)
                btn.configure(text=f"▼  {name.upper()}")
                
            btn.configure(command=lambda c=content, b=btn, n=name: self.toggle_design_section(c, b, n))
            return content

        # Author Section
        auth_c = create_section("Author", e_frame)
        self.add_label_entry(auth_c, "Author Name", embed_data, "author_name")
        
        auth_urls = ctk.CTkFrame(auth_c, fg_color="transparent"); auth_urls.pack(fill="x"); auth_urls.grid_columnconfigure((0,1), weight=1)
        self.add_grid_entry(auth_urls, "Author URL", embed_data, "author_url", 0, 0)
        self.add_grid_entry(auth_urls, "Author Icon URL", embed_data, "author_icon", 0, 1)

        # Body Section
        body_c = create_section("Body", e_frame, True)
        self.add_label_entry(body_c, "Title", embed_data, "title")
        
        ctk.CTkLabel(body_c, text="Description", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_gray).pack(anchor="w", pady=(5,0))
        embed_data["desc"] = ctk.CTkTextbox(body_c, height=100, fg_color=self.bg_dark, border_color=self.border_gray, border_width=1)
        embed_data["desc"].pack(fill="x", pady=(2, 10))
        
        body_meta = ctk.CTkFrame(body_c, fg_color="transparent"); body_meta.pack(fill="x"); body_meta.grid_columnconfigure((0,1), weight=1)
        self.add_grid_entry(body_meta, "URL", embed_data, "url", 0, 0)
        self.add_grid_entry(body_meta, "Color", embed_data, "color", 0, 1, placeholder="#58b9ff")

        # Fields Section
        fld_c = create_section("Fields", e_frame)
        
        # Buton listenin üstünde olmalı ve boşluk az olmalı
        add_field_btn = ctk.CTkButton(fld_c, text="+ ADD FIELD", fg_color=self.accent_blurple, width=120, height=32, corner_radius=6, font=ctk.CTkFont(size=11, weight="bold"), command=lambda c=None, d=embed_data["fields"]: self.add_field(self.get_f_list(fld_c), d))
        add_field_btn.pack(anchor="w", pady=(2, 5), padx=5)
        
        f_list = ctk.CTkFrame(fld_c, fg_color="transparent")
        f_list.pack(fill="x")
        embed_data["f_list_widget"] = f_list # Referansı saklayalım

        # Images Section
        img_c = create_section("Images", e_frame)
        self.add_label_entry(img_c, "Image URL", embed_data, "image_url")
        self.add_label_entry(img_c, "Thumbnail URL", embed_data, "thumb_url")

        # Footer Section
        foot_c = create_section("Footer", e_frame)
        self.add_label_entry(foot_c, "Footer Text", embed_data, "footer_text")
        
        foot_meta = ctk.CTkFrame(foot_c, fg_color="transparent"); foot_meta.pack(fill="x"); foot_meta.grid_columnconfigure((0,1), weight=1)
        
        ctk.CTkLabel(foot_meta, text="Timestamp", font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_gray).grid(row=0, column=0, sticky="w")
        ts_frame = ctk.CTkFrame(foot_meta, fg_color=self.bg_dark, height=42, corner_radius=6, border_width=1, border_color=self.border_gray)
        ts_frame.grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=5)
        embed_data["timestamp"] = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(ts_frame, text="Add Timestamp", variable=embed_data["timestamp"], command=self.update_preview, font=ctk.CTkFont(size=12), fg_color=self.accent_blurple).pack(side="left", padx=15, pady=10)
        
        self.add_grid_entry(foot_meta, "Footer Icon URL", embed_data, "footer_icon", 0, 1)

        # Binds
        for k in ["author_name", "author_url", "author_icon", "title", "url", "color", "image_url", "thumb_url", "footer_text", "footer_icon"]:
            embed_data[k].bind("<KeyRelease>", lambda e: self.update_preview())
        embed_data["desc"].bind("<KeyRelease>", lambda e: self.update_preview())

        self.embeds_list.append(embed_data)
        self.update_preview()

    def add_label_entry(self, parent, label, data_dict, key, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_gray).pack(anchor="w", pady=(5,0))
        data_dict[key] = ctk.CTkEntry(parent, height=42, fg_color=self.bg_dark, border_color=self.border_gray, placeholder_text=placeholder)
        data_dict[key].pack(fill="x", pady=(2, 10))

    def add_grid_entry(self, parent, label, data_dict, key, row, col, placeholder=""):
        ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=11, weight="bold"), text_color=self.text_gray).grid(row=row*2, column=col, sticky="w", pady=(5,0))
        data_dict[key] = ctk.CTkEntry(parent, height=42, fg_color=self.bg_dark, border_color=self.border_gray, placeholder_text=placeholder)
        data_dict[key].grid(row=row*2+1, column=col, sticky="ew", padx=(5 if col==1 else 0, 5 if col==0 else 0), pady=(2, 10))

    def toggle_design_section(self, frame, btn, name):
        if frame.winfo_viewable():
            frame.pack_forget()
            btn.configure(text=f"▶  {name.upper()}")
        else:
            frame.pack(fill="x", padx=20, pady=10)
            btn.configure(text=f"▼  {name.upper()}")

    def toggle_section(self, frame, btn, name):
        if frame.winfo_viewable():
            frame.pack_forget()
            btn.configure(text=f"> {name}")
        else:
            frame.pack(fill="x", padx=20, pady=5)
            btn.configure(text=f"v {name}")

    def get_f_list(self, parent):
        # f_list widget'ını bulmak için yardımcı
        for child in parent.winfo_children():
            if isinstance(child, ctk.CTkFrame) and child.cget("fg_color") == "transparent":
                return child
        return parent

    def add_field(self, container, data):
        f = ctk.CTkFrame(container, fg_color="#2f3136", corner_radius=5)
        f.pack(fill="x", pady=2)
        
        # Grid layout for field fields to save space
        f.grid_columnconfigure((0, 1), weight=1)
        
        ctk.CTkLabel(f, text="Field Name", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray).grid(row=0, column=0, sticky="w", padx=10, pady=(5, 0))
        n_entry = ctk.CTkEntry(f, height=28, fg_color=self.bg_dark, border_color=self.border_gray)
        n_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))
        
        ctk.CTkLabel(f, text="Field Value", font=ctk.CTkFont(size=10, weight="bold"), text_color=self.text_gray).grid(row=0, column=1, sticky="w", padx=10, pady=(5, 0))
        v_entry = ctk.CTkEntry(f, height=28, fg_color=self.bg_dark, border_color=self.border_gray)
        v_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 5))
        
        ctrl = ctk.CTkFrame(f, fg_color="transparent")
        ctrl.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 5))
        
        inline_v = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(ctrl, text="Inline", variable=inline_v, command=self.update_preview, font=ctk.CTkFont(size=11), fg_color=self.accent_blurple, checkbox_width=18, checkbox_height=18).pack(side="left")
        ctk.CTkButton(ctrl, text="Remove", width=60, height=22, fg_color="transparent", text_color="#ED4245", hover_color="#2A191B", font=ctk.CTkFont(size=10, weight="bold"), command=lambda: self.remove_field(f, data)).pack(side="right")
        
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
            f = ctk.CTkFrame(self.preview_embeds_area, fg_color="#2f3136", border_width=1, border_color="#202225")
            f.pack(fill="x", pady=5)
            col = f"#{emb.get('color', 2109733):06x}"
            ctk.CTkFrame(f, width=4, fg_color=col).pack(side="left", fill="y")
            c = ctk.CTkFrame(f, fg_color="transparent")
            c.pack(side="left", fill="both", expand=True, padx=12, pady=10)
            if "author" in emb: ctk.CTkLabel(c, text=emb["author"]["name"], font=ctk.CTkFont(weight="bold", size=13)).pack(anchor="w")
            if "title" in emb: ctk.CTkLabel(c, text=emb["title"], font=ctk.CTkFont(weight="bold", size=15), text_color="#00b0f4").pack(anchor="w")
            if "description" in emb: ctk.CTkLabel(c, text=emb["description"], text_color="#dcddde", wraplength=300, justify="left").pack(anchor="w")
            if "fields" in emb:
                fg = ctk.CTkFrame(c, fg_color="transparent"); fg.pack(fill="x", pady=5)
                for fld in emb["fields"]:
                    ctk.CTkLabel(fg, text=fld["name"], font=ctk.CTkFont(weight="bold", size=12)).pack(anchor="w")
                    ctk.CTkLabel(fg, text=fld["value"], text_color="#dcddde").pack(anchor="w")
            if "footer" in emb: ctk.CTkLabel(c, text=emb["footer"]["text"], font=ctk.CTkFont(size=11), text_color="#72767d").pack(anchor="w", pady=(5,0))
            
            # Images in Preview
            if "image" in emb:
                self.load_preview_image(c, emb["image"]["url"], "image")
            if "thumbnail" in emb:
                self.load_preview_image(c, emb["thumbnail"]["url"], "thumbnail")

    def load_preview_image(self, parent, url, type):
        def download():
            try:
                res = requests.get(url, timeout=5)
                if res.status_code == 200:
                    from PIL import Image, ImageTk
                    import io
                    img_data = res.content
                    img = Image.open(io.BytesIO(img_data))
                    
                    if type == "image":
                        w, h = img.size
                        new_w = 300
                        new_h = int((h / w) * new_w)
                        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    else:
                        img = img.resize((80, 80), Image.Resampling.LANCZOS)
                    
                    tk_img = ImageTk.PhotoImage(img)
                    
                    def update_ui(ti=tk_img):
                        if not hasattr(self, 'preview_imgs'): self.preview_imgs = []
                        self.preview_imgs.append(ti)
                        lbl = ctk.CTkLabel(parent, image=ti, text="")
                        if type == "image":
                            lbl.pack(anchor="w", pady=10)
                        else:
                            lbl.pack(anchor="ne", pady=5)
                            
                    self.after(0, update_ui)
            except: pass

        import threading
        threading.Thread(target=download, daemon=True).start()

    def load_message_link(self):
        url = self.url_entry.get().strip()
        msg_link = self.msg_link_entry.get().strip()
        
        if not url:
            self.status_label.configure(text="Error: Webhook URL required to load", text_color="#ED4245")
            return
        if not msg_link:
            self.status_label.configure(text="Error: Message Link required", text_color="#ED4245")
            return

        try:
            # Mesaj ID'sini linkten ayıkla
            msg_id = msg_link.split("/")[-1]
            if "?" in msg_id: msg_id = msg_id.split("?")[0]
            
            # Mesaj verilerini çek
            load_url = f"{url}/messages/{msg_id}"
            res = requests.get(load_url)
            
            if res.status_code == 200:
                data = res.json()
                
                # Mevcut editörü temizle
                self.clear_all_internal()
                
                # İçeriği yükle
                if "content" in data and data["content"]:
                    self.content_text.insert("1.0", data["content"])
                
                # Embed'leri yükle
                if "embeds" in data:
                    for emb in data["embeds"]:
                        self.add_embed()
                        e = self.embeds_list[-1]
                        
                        # Author
                        if "author" in emb:
                            e["author_name"].insert(0, emb["author"].get("name", ""))
                            e["author_url"].insert(0, emb["author"].get("url", ""))
                            e["author_icon"].insert(0, emb["author"].get("icon_url", ""))
                        
                        # Body
                        if "title" in emb: e["title"].insert(0, emb["title"])
                        if "url" in emb: e["url"].insert(0, emb["url"])
                        if "description" in emb: e["desc"].insert("1.0", emb["description"])
                        if "color" in emb: e["color"].insert(0, f"#{emb['color']:06x}")
                        
                        # Images
                        if "image" in emb: e["image_url"].insert(0, emb["image"].get("url", ""))
                        if "thumbnail" in emb: e["thumb_url"].insert(0, emb["thumbnail"].get("url", ""))
                        
                        # Footer
                        if "footer" in emb:
                            e["footer_text"].insert(0, emb["footer"].get("text", ""))
                            e["footer_icon"].insert(0, emb["footer"].get("icon_url", ""))
                        
                        # Fields
                        if "fields" in emb:
                            # add_field metodunu f_list_widget ile çağıralım
                            for fld in emb["fields"]:
                                self.add_field(e["f_list_widget"], e["fields"])
                                f_item = e["fields"][-1]
                                f_item["name"].insert(0, fld.get("name", ""))
                                f_item["value"].insert(0, fld.get("value", ""))
                                f_item["inline"].set(fld.get("inline", False))

                self.update_preview()
                self.status_label.configure(text="Status: Message Loaded Successfully!", text_color="#43B581")
            else:
                self.status_label.configure(text=f"Failed to load: {res.status_code}", text_color="#ED4245")
        except Exception as e:
            self.status_label.configure(text="Error processing link", text_color="#ED4245")
            print(f"Load Error: {e}")

    def clear_all_internal(self):
        # Sadece içeriği ve embed listesini temizle (URL kalsın diye)
        self.content_text.delete("1.0", "end")
        for e in self.embeds_list: e["frame"].destroy()
        self.embeds_list = []

    def send_webhook(self):
        url = self.url_entry.get().strip()
        msg_link = self.msg_link_entry.get().strip()
        
        if url:
            try:
                payload = self.get_payload()
                
                # Eğer Message Link varsa, URL'ye mesaj ID'sini ekle ve PATCH kullan
                if msg_link:
                    # Linkten mesaj ID'sini ayıkla (genelde son kısımdır)
                    msg_id = msg_link.split("/")[-1]
                    if "?" in msg_id: msg_id = msg_id.split("?")[0]
                    
                    edit_url = f"{url}/messages/{msg_id}"
                    res = requests.patch(edit_url, json=payload)
                    mode = "Edited"
                else:
                    res = requests.post(url, json=payload)
                    mode = "Sent"
                
                if res.status_code in [200, 204]:
                    self.status_label.configure(text=f"Success: {mode}!", text_color="#43B581")
                else:
                    self.status_label.configure(text=f"Error: {res.status_code}", text_color="#ED4245")
            except Exception as e:
                self.status_label.configure(text=f"Connection Error", text_color="#ED4245")
                print(f"Error: {e}")

    def clear_all(self):
        self.url_entry.delete(0, "end")
        self.content_text.delete("1.0", "end")
        for e in self.embeds_list: e["frame"].destroy()
        self.embeds_list = []
        self.update_preview()

if __name__ == "__main__":
    app = FyHookApp()
    app.mainloop()
