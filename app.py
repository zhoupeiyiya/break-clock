import tkinter as tk
from PIL import Image, ImageTk
import Quartz

TEXT_COLOR = "#9B7FA6"
DARK_TEXT = "#7B4F7A"

WORK_SECONDS = 45 * 60
IDLE_RESET = 5 * 60

BASE = "/Users/yiyachou/Desktop/my_python/"

class BreakClock:
    def __init__(self, window):
        self.window = window
        self.window.title("Break Clock")
        self.window.resizable(False, False)
        self.window.attributes("-topmost", True)

        self.active_seconds = 0
        self.seconds_left = WORK_SECONDS
        self.is_resting = False

        def load(name, size):
            img = Image.open(BASE + name).convert("RGBA")
            img = img.resize(size, Image.LANCZOS)
            return ImageTk.PhotoImage(img)

        bg_img = Image.open(BASE + "background2.jpg").convert("RGBA")
        bg_img = bg_img.resize((280, 300), Image.LANCZOS)
        self.bg_image = ImageTk.PhotoImage(bg_img)

        self.img_apple = load("icon4.png", (60, 60))
        self.img_name = load("name.png", (40, 17))

        screen_w = self.window.winfo_screenwidth()
        screen_h = self.window.winfo_screenheight()
        x = screen_w - 280 - 20
        y = screen_h - 300 - 150
        self.window.geometry(f"280x300+{x}+{y}")

        self._build_ui()
        self.tick()

    def _build_ui(self):
        self.canvas = tk.Canvas(
            self.window,
            width=280, height=300,
            highlightthickness=0
        )
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image)
        self.canvas.create_image(140, 55, anchor="center", image=self.img_apple)

        self.canvas.create_text(
            140, 100,
            text="✿ Break Clock ✿",
            font=("Courier", 13, "bold"),
            fill=TEXT_COLOR
        )

        self.timer_id = self.canvas.create_text(
            140, 140,
            text=self.format_time(),
            font=("Courier", 38, "bold"),
            fill=TEXT_COLOR
        )

        self.status_id = self.canvas.create_text(
            140, 180,
            text="˚₊· working ·₊˚",
            font=("Courier", 10),
            fill=TEXT_COLOR
        )

        self.canvas.create_rectangle(
            64, 200, 216, 220,
            fill=TEXT_COLOR, outline=""
        )
        self.progress_bar = self.canvas.create_rectangle(
            64, 200, 64, 220,
            fill="#FFF5B9", outline=""
        )

        self.canvas.create_image(140, 245, anchor="center", image=self.img_name)

        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._drag)

    def _start_drag(self, event):
        self._drag_x = event.x
        self._drag_y = event.y

    def _drag(self, event):
        x = self.window.winfo_x() + event.x - self._drag_x
        y = self.window.winfo_y() + event.y - self._drag_y
        self.window.geometry(f"+{x}+{y}")

    def format_time(self):
        mins = self.seconds_left // 60
        secs = self.seconds_left % 60
        return f"{mins:02d}:{secs:02d}"

    def reset(self):
        self.active_seconds = 0
        self.seconds_left = WORK_SECONDS
        self.is_resting = False
        self.canvas.itemconfig(self.timer_id, text=self.format_time(), fill=TEXT_COLOR)
        self.canvas.itemconfig(self.status_id, text="˚₊· working ·₊˚", fill=TEXT_COLOR)
        self.canvas.coords(self.progress_bar, 64, 200, 64, 220)

    def get_idle_seconds(self):
        return Quartz.CGEventSourceSecondsSinceLastEventType(
            Quartz.kCGEventSourceStateHIDSystemState,
            Quartz.kCGAnyInputEventType
        )

    def tick(self):
        idle = self.get_idle_seconds()

        if idle > IDLE_RESET:
            if not self.is_resting:
                self.is_resting = True
                self.canvas.itemconfig(self.status_id, text="✿ resting... ✿")
            if self.active_seconds > 0:
                self.reset()
        else:
            self.is_resting = False
            self.active_seconds += 1
            self.seconds_left = max(0, WORK_SECONDS - self.active_seconds)
            self.canvas.itemconfig(self.timer_id, text=self.format_time())
            progress_width = int((self.active_seconds / WORK_SECONDS) * 152)
            self.canvas.coords(self.progress_bar, 64, 200, 64 + progress_width, 220)

            if self.active_seconds >= WORK_SECONDS:
                self.alert()

        self.window.after(1000, self.tick)

    def alert(self):
        self.canvas.itemconfig(self.timer_id, fill=DARK_TEXT)
        self.canvas.itemconfig(self.status_id, text="! 站起來伸展 !", fill=DARK_TEXT)
        self.window.after(100, self._show_dialog)

    def _show_dialog(self):
        import subprocess
        subprocess.call([
            'osascript', '-e',
            'display dialog "站起來！\\n\\n你已持續使用電腦超過60分鐘。\\n做個胸椎伸展再回來 ✿" '
            'with title "Break Clock" buttons {"我站起來了"} '
            'default button 1 with icon caution'
        ])
        self.reset()

window = tk.Tk()
app = BreakClock(window)
window.mainloop()