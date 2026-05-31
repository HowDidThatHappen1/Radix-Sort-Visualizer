import tkinter as tk
from tkinter import messagebox
from radix import radix_sort
from utils import parse_input
import random


BG_DARK   = "#0f172a"
BG_PANEL  = "#1e293b"
BG_CANVAS = "#0b1220"
BTN_RANDOM  = "#8b5cf6"
BTN_START   = "#22c55e"
BTN_STOP    = "#dc2626"
BTN_PREV    = "#f59e0b"
BTN_NEXT    = "#3b82f6"
BTN_CLEAR   = "#ef4444"
CLR_ORIG    = "#f97316"
CLR_OUT     = "#7c3aed"
CLR_COUNT   = "#1d4ed8"
CLR_HI      = "#22c55e"
CLR_TITLE   = "#38bdf8"
CLR_PHASE   = "#22c55e"
CLR_EXP     = "#facc15"
CLR_FG      = "white"
CLR_LOG     = "#e2e8f0"
CLR_DIM     = "#94a3b8"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_SUB    = ("Segoe UI", 14, "bold")
FONT_PHASE  = ("Segoe UI", 16, "bold")
FONT_BTN    = ("Segoe UI", 11, "bold")
FONT_BOX    = ("Segoe UI", 13, "bold")
FONT_LABEL  = ("Segoe UI", 10)
FONT_DIGIT  = ("Segoe UI", 9,  "bold")
FONT_IDX    = ("Segoe UI", 9)
FONT_LOG    = ("Consolas", 10)


class RadixApp:



    def __init__(self, root):
        self.root = root
        self.root.title("Radix Sort Visualizer")
        self.root.geometry("1050x780")
        self.root.resizable(True, True)
        self.root.configure(bg=BG_DARK)

        self.steps      = []        # list of recorded step tuples
        self.step_index = 0         # next step to display
        self.auto_running = False
        self.after_id   = None

        self._build_ui()


    def _build_ui(self):

        tk.Label(
            self.root,
            text="RADIX SORT VISUALIZER",
            font=FONT_TITLE, fg=CLR_TITLE, bg=BG_DARK,
        ).pack(pady=(14, 4))


        inp_frame = tk.Frame(self.root, bg=BG_PANEL, padx=10, pady=10)
        inp_frame.pack(pady=6)
        tk.Label(
            inp_frame, text="Enter numbers separated by spaces",
            bg=BG_PANEL, fg=CLR_FG, font=FONT_LABEL,
        ).pack()
        self.entry = tk.Entry(
            inp_frame, width=50, font=("Segoe UI", 12), justify="center",
        )
        self.entry.pack(pady=5)


        btn_frame = tk.Frame(self.root, bg=BG_DARK)
        btn_frame.pack(pady=8)

        def _btn(text, color, cmd):
            return tk.Button(
                btn_frame, text=text, command=cmd,
                bg=color, fg=CLR_FG, font=FONT_BTN,
                width=12, relief="flat", cursor="hand2",
                activebackground=color, activeforeground=CLR_FG,
            )

        _btn("RANDOM",   BTN_RANDOM, self.generate_random).grid(row=0, column=0, padx=5)
        _btn("START",    BTN_START,  self.start_sort      ).grid(row=0, column=1, padx=5)

        self.stop_btn = _btn("STOP", BTN_STOP, self.toggle_stop_resume)
        self.stop_btn.grid(row=0, column=2, padx=5)

        self.prev_btn = _btn("◀ PREVIOUS", BTN_PREV, self.previous_step)
        self.prev_btn.grid(row=0, column=3, padx=5)

        self.next_btn = _btn("NEXT ▶", BTN_NEXT, self.next_step)
        self.next_btn.grid(row=0, column=4, padx=5)

        _btn("CLEAR", BTN_CLEAR, self.clear_output).grid(row=0, column=5, padx=5)

        # Start with PREVIOUS / NEXT disabled until sorting begins
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")


        canvas_wrap = tk.Frame(self.root, bg=BG_PANEL, padx=4, pady=4)
        canvas_wrap.pack(pady=6)
        self.canvas = tk.Canvas(
            canvas_wrap, width=990, height=490,
            bg=BG_CANVAS, highlightthickness=0,
        )
        self.canvas.pack()


        log_wrap = tk.Frame(self.root, bg=BG_PANEL, padx=4, pady=4)
        log_wrap.pack(pady=6, fill="x", padx=30)

        tk.Label(
            log_wrap, text="Step Log",
            bg=BG_PANEL, fg=CLR_TITLE, font=("Segoe UI", 11, "bold"),
        ).pack(anchor="w")

        scroll = tk.Scrollbar(log_wrap, orient="vertical")
        self.output = tk.Text(
            log_wrap, height=9, width=120,
            bg=BG_CANVAS, fg=CLR_LOG, font=FONT_LOG,
            relief="flat", yscrollcommand=scroll.set,
            state="normal",
        )
        scroll.config(command=self.output.yview)
        scroll.pack(side="right", fill="y")
        self.output.pack(side="left", fill="both", expand=True)


    def generate_random(self):
        popup = tk.Toplevel(self.root)
        popup.title("Generate Random Nu...")
        popup.geometry("300x190")
        popup.configure(bg=BG_PANEL)
        popup.resizable(False, False)
        popup.grab_set()

        tk.Label(
            popup, text="Choose number of elements (1-6)",
            bg=BG_PANEL, fg=CLR_FG, font=("Segoe UI", 11, "bold"),
        ).pack(pady=20)

        amount_var = tk.IntVar(value=6)
        tk.Spinbox(
            popup, from_=1, to=6, textvariable=amount_var,
            width=5, font=("Segoe UI", 14), justify="center",
        ).pack(pady=6)

        def _generate():
            n = max(1, min(6, amount_var.get()))
            nums = [random.randint(1, 999) for _ in range(n)]
            self.entry.delete(0, tk.END)
            self.entry.insert(0, " ".join(map(str, nums)))
            popup.destroy()

        tk.Button(
            popup, text="GENERATE", command=_generate,
            bg=BTN_START, fg=CLR_FG, font=FONT_BTN,
            width=15, relief="flat", cursor="hand2",
        ).pack(pady=16)


    def _cx(self):
        """Horizontal centre of the canvas."""
        return self.canvas.winfo_reqwidth() // 2

    def _draw_array(self, arr, y, title, base_color, exp=None, highlight=None):
        """Draw a labelled row of boxes for *arr* at vertical position *y*."""
        cx = self._cx()
        # Section title
        self.canvas.create_text(
            cx, y - 22, text=title, fill=CLR_TITLE, font=FONT_SUB,
        )

        box_w, gap = 68, 10
        n = len(arr)
        total = n * box_w + (n - 1) * gap
        sx = cx - total // 2

        for i, val in enumerate(arr):
            x0 = sx + i * (box_w + gap)
            x1 = x0 + box_w
            y1 = y + 58

            color = CLR_HI if (highlight is not None and i == highlight) else base_color

            self.canvas.create_rectangle(x0, y, x1, y1, fill=color, outline=CLR_FG, width=2)
            label = "" if val == -1 else str(val)
            self.canvas.create_text(x0 + 34, y + 29, text=label, fill=CLR_FG, font=FONT_BOX)

            if exp is not None and val != -1:
                digit = (val // exp) % 10
                self.canvas.create_text(
                    x0 + 34, y - 10,
                    text=f"d={digit}", fill=CLR_EXP, font=FONT_DIGIT,
                )

    def _draw_count(self, count, y):
        """Draw the ten-slot count array at vertical position *y*."""
        cx = self._cx()
        self.canvas.create_text(cx, y - 22, text="COUNT ARRAY", fill=CLR_TITLE, font=FONT_SUB)

        box_w, gap = 68, 8
        total = 10 * box_w + 9 * gap
        sx = cx - total // 2

        for i in range(10):
            x0 = sx + i * (box_w + gap)
            x1 = x0 + box_w
            y1 = y + 56
            self.canvas.create_rectangle(x0, y, x1, y1, fill=CLR_COUNT, outline=CLR_FG, width=2)
            self.canvas.create_text(x0 + 34, y + 28, text=str(count[i]), fill=CLR_FG, font=FONT_BOX)
            # index label below
            self.canvas.create_text(x0 + 34, y + 72, text=str(i), fill=CLR_DIM, font=FONT_IDX)

    def _draw_step(self, exp, original, output, count, phase, highlight):
        self.canvas.delete("all")
        cx = self._cx()

        # Phase label + exponent
        self.canvas.create_text(cx, 28, text=phase, fill=CLR_PHASE, font=FONT_PHASE)
        self.canvas.create_text(cx, 58, text=f"Current exp = {exp}", fill=CLR_EXP, font=FONT_SUB)

        # The three array rows
        self._draw_array(original, 105, "ORIGINAL ARRAY", CLR_ORIG, exp)
        self._draw_array(output,   235, "OUTPUT ARRAY",   CLR_OUT,  exp, highlight)
        self._draw_count(count,    375)


    def _log(self, msg):
        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)


    def start_sort(self):
        self._cancel_auto()
        self.output.delete(1.0, tk.END)
        self.steps = []
        self.step_index = 0

        raw = self.entry.get()
        data = parse_input(raw)

        if data is None:
            messagebox.showwarning("Warning", "Enter numbers.")
            return
        if data == "invalid":
            messagebox.showerror("Error", "Invalid input.")
            return
        if len(data) > 6:
            messagebox.showwarning("Warning", "Maximum of 6 elements only.")
            return

        self._log(f"Original Array: {data}")

        # Collect every step produced by radix_sort
        def _collect(exp, original, output, count, phase, highlight):
            self.steps.append((exp, original, output, count, phase, highlight))

        radix_sort(data[:], steps_callback=_collect)

        self.next_btn.config(state="normal")
        self.prev_btn.config(state="normal")
        self.stop_btn.config(text="STOP", bg=BTN_STOP)
        self._log("\n▶ Auto visualization started")
        self.auto_running = True
        self._auto_play()

    def _display_step(self, idx):

        exp, original, output, count, phase, highlight = self.steps[idx]
        self._draw_step(exp, original, output, count, phase, highlight)
        self._log("=" * 50)
        self._log(f"STEP {idx + 1}")
        self._log(f"Phase: {phase}")
        self._log(f"Output: {[v for v in output]}")
        self._log("=" * 50)

    def next_step(self):

        if self.step_index >= len(self.steps):
            self._log("\n✔ Sorting Complete!")
            self.next_btn.config(state="disabled")
            self.auto_running = False
            return

        self._display_step(self.step_index)
        self.step_index += 1

        # Re-enable PREVIOUS once past the first step
        if self.step_index > 1:
            self.prev_btn.config(state="normal")

    def previous_step(self):

        if self.step_index <= 1:
            self._log("\n⚠ Already at the first step.")
            return

        self.step_index -= 1          # un-consume the last displayed step
        self.step_index -= 1          # go one further back
        self._display_step(self.step_index)
        self.step_index += 1          # advance past it again

        self.next_btn.config(state="normal")
        if self.step_index <= 1:
            self.prev_btn.config(state="disabled")

    def toggle_stop_resume(self):

        if self.auto_running:
            # Pause
            self._cancel_auto()
            self._log("\n⏸ Animation paused.")
            self.stop_btn.config(text="RESUME", bg="#b45309")
        else:
            # Resume (only if there are more steps)
            if self.step_index < len(self.steps):
                self.auto_running = True
                self.stop_btn.config(text="STOP", bg=BTN_STOP)
                self._log("\n▶ Animation resumed.")
                self._auto_play()

    def _auto_play(self):

        if not self.auto_running:
            return
        if self.step_index >= len(self.steps):
            self._log("\n✔ Sorting Complete!")
            self.auto_running = False
            self.next_btn.config(state="disabled")
            self.stop_btn.config(text="STOP", bg=BTN_STOP)
            return

        self.next_step()
        self.after_id = self.root.after(1200, self._auto_play)

    def _cancel_auto(self):
        self.auto_running = False
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def clear_output(self):

        self._cancel_auto()
        self.entry.delete(0, tk.END)
        self.output.delete(1.0, tk.END)
        self.canvas.delete("all")
        self.steps = []
        self.step_index = 0
        self.stop_btn.config(text="STOP", bg=BTN_STOP)
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
