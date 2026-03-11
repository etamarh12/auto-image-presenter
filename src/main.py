import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os
from datetime import datetime
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout), # שולח טקסט ל-Console למטה
        logging.FileHandler("app_debug.log") # שומר עותק בקובץ
    ]
)
logger = logging.getLogger(__name__)

logger.info("--- Image Presenter System Started ---")

class ImagePresenter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Presenter")
        self.root.geometry("480x380")
        self.root.configure(bg="#f0f6ff")
        self.root.resizable(False, False)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self.image_list = []
        self.current_idx = 0
        self.delay = 3000
        self.running = False
        self.fullscreen_win = None
        self.after_id = None

        self.create_style()
        self.build_ui()

        self.root.bind('<Escape>', lambda event: self.stop_slideshow())

    # ================= STYLE =================
    def create_style(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Blue.TButton",
                        font=("Segoe UI", 12, "bold"),
                        padding=10,
                        foreground="white",
                        background="#1f6feb",
                        borderwidth=0)

        style.map("Blue.TButton",
                  background=[("active", "#1554c0")])

        style.configure("White.TButton",
                        font=("Segoe UI", 11),
                        padding=8,
                        foreground="#1f6feb",
                        background="white",
                        borderwidth=1)

        style.map("White.TButton",
                  background=[("active", "#e6f0ff")])

    # ================= UI =================
    def build_ui(self):

        main_frame = tk.Frame(self.root, bg="#f0f6ff")
        main_frame.grid(row=0, column=0, sticky="nsew")

        self.title_label = tk.Label(
            main_frame,
            text="📽 Image Presenter",
            font=("Segoe UI", 22, "bold"),
            fg="#0b3d91",
            bg="#f0f6ff"
        )
        self.title_label.pack(pady=20)

        self.details = tk.Label(
            main_frame,
            text="Controls : Left | Right | Esc",
            font=("Segoe UI", 8),
            fg="#0b3d91",
            bg="#f0f6ff"
        )
        self.details.pack(pady=(0))

        self.btn_select = ttk.Button(
            main_frame,
            text="בחר תיקיית תמונות",
            style="Blue.TButton",
            command=self.load_images
        )
        self.btn_select.pack(pady=10, ipadx=15)

        self.time_label = tk.Label(
            main_frame,
            text="זמן החלפה (בשניות)",
            font=("Segoe UI", 12),
            fg="#0b3d91",
            bg="#f0f6ff"
        )
        self.time_label.pack(pady=(20, 5))

        self.entry_time = tk.Entry(
            main_frame,
            font=("Segoe UI", 14),
            justify="center",
            width=6,
            bd=2,
            relief="groove"
        )
        self.entry_time.insert(0, "3")
        self.entry_time.pack()

        self.btn_start = ttk.Button(
            main_frame,
            text="▶ הפעלת מצגת",
            style="Blue.TButton",
            command=self.start_slideshow
        )
        self.btn_start.pack(pady=25, ipadx=20)

        # ===== COPYRIGHT =====
        current_year = datetime.now().year
        footer = tk.Label(
            self.root,
            text=f"© {current_year} Itamar Chen. All Rights Reserved.",
            font=("Segoe UI", 8),
            fg="#6c757d",
            bg="#f0f6ff"
        )
        footer.grid(row=1, column=0, pady=8)

    # ================= LOGIC =================
    def load_images(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_list = [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))
            ]
            messagebox.showinfo("Success",f"נטענו {len(self.image_list)} תמונות")

    def start_slideshow(self):
        if not self.image_list:
            return

        try:
            self.delay = int(self.entry_time.get()) * 1000
        except:
            self.delay = 3000

        self.running = True
        self.current_idx = 0
        self.show_fullscreen()

    def show_fullscreen(self):
        if not self.running:
            return

        if self.fullscreen_win is None:
            self.fullscreen_win = tk.Toplevel(self.root)
            self.fullscreen_win.attributes("-fullscreen", True)
            self.fullscreen_win.configure(bg="black")

            self.fullscreen_win.bind('<Escape>', lambda e: self.stop_slideshow())
            self.fullscreen_win.bind('<Left>', lambda e: self.next_image())
            self.fullscreen_win.bind('<Right>', lambda e: self.prev_image())

            self.fullscreen_win.focus_set()
            self.fullscreen_win.grab_set()

            self.label = tk.Label(self.fullscreen_win, bg='black')
            self.label.pack(expand=True, fill='both')

        self.display_image()

    def display_image(self):
        if not self.running:
            return

        img_path = self.image_list[self.current_idx]
        img = Image.open(img_path)

        screen_w = self.fullscreen_win.winfo_screenwidth()
        screen_h = self.fullscreen_win.winfo_screenheight()
        img.thumbnail((screen_w, screen_h))

        self.photo = ImageTk.PhotoImage(img)
        self.label.config(image=self.photo)

        if self.after_id:
            self.root.after_cancel(self.after_id)

        self.after_id = self.root.after(self.delay, self.auto_next)

    def auto_next(self):
        if not self.running:
            return

        self.current_idx = (self.current_idx + 1) % len(self.image_list)
        self.display_image()

    def next_image(self):
        if not self.running:
            return

        self.current_idx = (self.current_idx + 1) % len(self.image_list)
        self.display_image()

    def prev_image(self):
        if not self.running:
            return

        self.current_idx = (self.current_idx - 1) % len(self.image_list)
        self.display_image()

    def stop_slideshow(self):
        self.running = False

        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

        if self.fullscreen_win:
            self.fullscreen_win.destroy()
            self.fullscreen_win = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePresenter(root)
    root.mainloop()