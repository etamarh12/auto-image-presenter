import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import os
import json
from datetime import datetime
import logging
import sys

# הגדרת ה-Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app_debug.log")
    ]
)
logger = logging.getLogger(__name__)


class ImagePresenter:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Presenter")
        self.root.geometry("480x420")
        self.root.configure(bg="#f0f6ff")
        self.root.resizable(False, False)

        # טעינת הגדרות מקובץ חיצוני (Platform Step)
        self.config = self.load_config()
        self.delay = self.config.get("slideshow_delay", 3)  # ברירת מחדל 3 שניות

        logger.info(f"--- Image Presenter System Started with delay: {self.delay}s ---")

        self.image_list = []
        self.current_idx = 0
        self.running = False
        self.fullscreen_win = None
        self.after_id = None

        self.create_style()
        self.build_ui()

        self.root.bind('<Escape>', lambda event: self.stop_slideshow())

    def load_config(self):
        """טעינת הגדרות מקובץ config.json"""
        if os.path.exists("config.json"):
            try:
                with open("config.json", "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        return {"slideshow_delay": 3}

    def save_config(self, new_delay):
        """שמירת הגדרות לקובץ"""
        try:
            with open("config.json", "w") as f:
                json.dump({"slideshow_delay": new_delay}, f)
            logger.info(f"Saved new delay to config: {new_delay}s")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    # ================= STYLE =================
    def create_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Blue.TButton", font=("Segoe UI", 12, "bold"), padding=10, foreground="white",
                        background="#1f6feb", borderwidth=0)
        style.map("Blue.TButton", background=[("active", "#1554c0")])

    # ================= UI =================
    def build_ui(self):
        main_frame = tk.Frame(self.root, bg="#f0f6ff")
        main_frame.pack(expand=True, fill="both")

        self.title_label = tk.Label(main_frame, text="📽 Image Presenter", font=("Segoe UI", 22, "bold"), fg="#0b3d91",
                                    bg="#f0f6ff")
        self.title_label.pack(pady=20)

        self.btn_select = ttk.Button(main_frame, text="בחר תיקיית תמונות", style="Blue.TButton",
                                     command=self.load_images)
        self.btn_select.pack(pady=10, ipadx=15)

        self.time_label = tk.Label(main_frame, text="זמן החלפה (בשניות)", font=("Segoe UI", 12), fg="#0b3d91",
                                   bg="#f0f6ff")
        self.time_label.pack(pady=(20, 5))

        self.entry_time = tk.Entry(main_frame, font=("Segoe UI", 14), justify="center", width=6, bd=2, relief="groove")
        self.entry_time.insert(0, str(self.delay))
        self.entry_time.pack()

        self.btn_start = ttk.Button(main_frame, text="▶ הפעלת מצגת", style="Blue.TButton", command=self.start_slideshow)
        self.btn_start.pack(pady=25, ipadx=20)

        footer = tk.Label(self.root, text=f"© {datetime.now().year} Itamar Chen. All Rights Reserved.",
                          font=("Segoe UI", 8), fg="#6c757d", bg="#f0f6ff")
        footer.pack(pady=10)

    # ================= LOGIC =================
    def load_images(self):
        folder = filedialog.askdirectory()
        if folder:
            self.image_list = [os.path.join(folder, f) for f in os.listdir(folder) if
                               f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
            logger.info(f"Loaded {len(self.image_list)} images from {folder}")
            messagebox.showinfo("Success", f"נטענו {len(self.image_list)} תמונות")

    def start_slideshow(self):
        if not self.image_list:
            messagebox.showwarning("Warning", "נא לבחור תיקייה קודם")
            return

        try:
            val = int(self.entry_time.get())
            self.delay = val * 1000
            self.save_config(val)  # שומר את הבחירה של המשתמש לקובץ ה-Config
        except:
            self.delay = 3000

        self.running = True
        self.current_idx = 0
        self.show_fullscreen()

    def show_fullscreen(self):
        if not self.running: return
        if self.fullscreen_win is None:
            self.fullscreen_win = tk.Toplevel(self.root)
            self.fullscreen_win.attributes("-fullscreen", True)
            self.fullscreen_win.configure(bg="black")
            self.fullscreen_win.bind('<Escape>', lambda e: self.stop_slideshow())
            self.fullscreen_win.bind('<Right>', lambda e: self.next_image())
            self.fullscreen_win.bind('<Left>', lambda e: self.prev_image())
            self.label = tk.Label(self.fullscreen_win, bg='black')
            self.label.pack(expand=True, fill='both')
        self.display_image()

    def display_image(self):
        if not self.running: return
        try:
            img_path = self.image_list[self.current_idx]
            img = Image.open(img_path)
            sw, sh = self.fullscreen_win.winfo_screenwidth(), self.fullscreen_win.winfo_screenheight()
            img.thumbnail((sw, sh))
            self.photo = ImageTk.PhotoImage(img)
            self.label.config(image=self.photo)
            if self.after_id: self.root.after_cancel(self.after_id)
            self.after_id = self.root.after(self.delay, self.auto_next)
        except Exception as e:
            logger.error(f"Error displaying image: {e}")
            self.stop_slideshow()

    def auto_next(self):
        if self.running:
            self.current_idx = (self.current_idx + 1) % len(self.image_list)
            self.display_image()

    def next_image(self):
        self.current_idx = (self.current_idx + 1) % len(self.image_list)
        self.display_image()

    def prev_image(self):
        self.current_idx = (self.current_idx - 1) % len(self.image_list)
        self.display_image()

    def stop_slideshow(self):
        self.running = False
        if self.after_id: self.root.after_cancel(self.after_id)
        if self.fullscreen_win:
            self.fullscreen_win.destroy()
            self.fullscreen_win = None


if __name__ == "__main__":
    root = tk.Tk()
    app = ImagePresenter(root)
    root.mainloop()