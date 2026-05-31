import tkinter as tk
from tkinter import messagebox
from radix import radix_sort
from utils import parse_input
import random


class RadixApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Radix Sort Visualizer")
        self.root.geometry("1050x1100")
        self.root.resizable(True, True)
        self.root.configure(bg="#0f172a")
        self.steps = []
        self.step_index = 0
        self.auto_running = False
        self.after_id = None
        self.build_ui()

    def build_ui(self):

        tk.Label(self.root,text="RADIX SORT VISUALIZER",font=("Segoe UI", 22, "bold"),fg="#38bdf8",bg="#0f172a").pack(pady=10)

        input_frame = tk.Frame(self.root,bg="#1e293b",padx=10,pady=10)
        input_frame.pack(pady=10)
        tk.Label(input_frame,text="Enter numbers separated by spaces",bg="#1e293b",fg="white",font=("Segoe UI", 10)).pack()
        self.entry = tk.Entry(input_frame,width=45,font=("Segoe UI", 12),justify="center")
        self.entry.pack(pady=5)
        btn_frame = tk.Frame(self.root, bg="#0f172a")
        btn_frame.pack(pady=10)

        def btn(text, color, command):
            return tk.Button(btn_frame,text=text,command=command,bg=color,fg="white",font=("Segoe UI", 11, "bold"),width=12,relief="flat",cursor="hand2")

        btn("RANDOM","#8b5cf6",self.generate_random).grid(row=0, column=0, padx=5)
        btn("START","#22c55e",self.start_sort).grid(row=0, column=1, padx=5)

        self.stop_btn = btn("STOP","#dc2626",self.stop_animation)
        self.stop_btn.grid(row=0, column=2, padx=5)
        self.prev_btn = btn("◀ PREVIOUS","#f59e0b",self.previous_step)
        self.prev_btn.grid(row=0, column=3, padx=5)
        self.next_btn = btn("NEXT ▶","#3b82f6",self.next_step)
        self.next_btn.grid(row=0, column=4, padx=5)
        btn("CLEAR","#ef4444",self.clear_output).grid(row=0, column=5, padx=5)
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")

        canvas_frame = tk.Frame(self.root,bg="#1e293b")
        canvas_frame.pack(pady=10)

        self.canvas = tk.Canvas(canvas_frame,width=940,height=500,bg="#0b1220",highlightthickness=0)
        self.canvas.pack()

        log_frame = tk.Frame(self.root,bg="#1e293b")
        log_frame.pack(pady=10)

        self.output = tk.Text(log_frame,height=15,width=120,bg="#0b1220",fg="#e2e8f0",font=("Consolas", 10),relief="flat")
        self.output.pack()

    def generate_random(self):

        popup = tk.Toplevel(self.root)
        popup.title("Generate Random Numbers")
        popup.geometry("300x180")
        popup.configure(bg="#1e293b")
        popup.resizable(False, False)

        tk.Label(popup,text="Choose number of elements (1-6)",bg="#1e293b",fg="white",font=("Segoe UI", 11, "bold")).pack(pady=15)

        amount_var = tk.IntVar(value=6)

        spinbox = tk.Spinbox(popup,from_=1,to=6,textvariable=amount_var,width=5,font=("Segoe UI", 14),justify="center")
        spinbox.pack(pady=10)

        def generate():
            amount = amount_var.get()
            nums = []

            for _ in range(amount):
                nums.append(random.randint(1, 999))

            self.entry.delete(0, tk.END)
            self.entry.insert(0," ".join(map(str, nums)))
            popup.destroy()

        tk.Button(popup,text="GENERATE",command=generate,bg="#22c55e",fg="white",font=("Segoe UI", 11, "bold"),width=15,relief="flat",cursor="hand2").pack(pady=15)

    def draw_boxes(self,arr,y,title,color,exp=None,highlight_index=None):

        self.canvas.create_text(475,y - 40,text=title,fill="white",font=("Segoe UI", 14, "bold"))
        box_width = 60
        spacing = 10
        total_width = len(arr) * (box_width + spacing)
        start_x = (950 - total_width) / 2

        for i, num in enumerate(arr):
            x = start_x + i * (box_width + spacing)
            fill_color = color

            if highlight_index == i:
                fill_color = "#22c55e"

            self.canvas.create_rectangle(x,y,x + box_width,y + 60,fill=fill_color,outline="white",width=2)
            display = "" if num == -1 else str(num)
            self.canvas.create_text(x + 30,y + 30,text=display,fill="white",font=("Segoe UI", 13, "bold"))

            if exp and num != -1:
                digit = (num // exp) % 10
                self.canvas.create_text(x + 30,y - 15,text=f"d={digit}",fill="#facc15",font=("Segoe UI", 9, "bold"))

    def draw_count(self, count):
        y = 390
        self.canvas.create_text(475,350,text="COUNT ARRAY",fill="#38bdf8",font=("Segoe UI", 14, "bold"))

        for i in range(10):
            x = 90 + i * 75
            self.canvas.create_rectangle(x,y,x + 55,y + 55,fill="#1d4ed8",outline="white",width=2)
            self.canvas.create_text(x + 27,y + 27,text=str(count[i]),fill="white",font=("Segoe UI", 12, "bold"))
            self.canvas.create_text(x + 27,y + 68,text=str(i),fill="#94a3b8",font=("Segoe UI", 9))

    def draw_visual(self,original,output,count,exp,phase,highlight_index=None):
        self.canvas.delete("all")
        self.canvas.create_text(475,25,text=phase,fill="#22c55e",font=("Segoe UI", 18, "bold"))
        self.canvas.create_text(475,60,text=f"Current exp = {exp}",fill="#facc15",font=("Segoe UI", 14, "bold"))
        self.draw_boxes(original,130,"ORIGINAL ARRAY","#f97316", exp)
        self.draw_boxes(output,260,"OUTPUT ARRAY","#7c3aed", exp, highlight_index)
        self.draw_count(count)

    def log(self, msg):

        self.output.insert(tk.END, msg + "\n")
        self.output.see(tk.END)

    def start_sort(self):

        self.stop_animation()
        self.output.delete(1.0, tk.END)
        self.steps = []
        self.step_index = 0
        data = parse_input(self.entry.get())

        if data is None:
            messagebox.showwarning("Warning","Enter numbers.")
            return

        if data == "invalid":
            messagebox.showerror("Error","Invalid input.")
            return

        if len(data) > 6:
            messagebox.showwarning("Warning","Maximum of 6 elements only.")
            return

        self.log(f"Original Array: {data}")

        def collect(exp, original, output, count, phase, highlight):
            self.steps.append((exp, original.copy(), output.copy(), count.copy(), phase, highlight))

        radix_sort(data, steps_callback=collect)
        self.next_btn.config(state="normal")
        self.prev_btn.config(state="normal")
        self.auto_running = True
        self.stop_btn.config(text="STOP")
        self.log("\n▶ Auto visualization started")
        self.auto_play()

    def next_step(self):

        if self.step_index >= len(self.steps):
            self.log("\n✔ Sorting Complete!")
            self.next_btn.config(state="disabled")
            self.auto_running = False
            return

        (exp, original, output, count, phase, highlight) = self.steps[self.step_index]
        self.draw_visual(original, output, count, exp, phase, highlight)
        self.log("=" * 50)
        self.log(f"STEP {self.step_index + 1}")
        self.log(f"Phase: {phase}")
        self.log(f"Output: {output}")
        self.log("=" * 50)
        self.step_index += 1

    def auto_play(self):

        if not self.auto_running:
            return

        if self.step_index >= len(self.steps):
            self.log("\n✔ Sorting Complete!")
            self.auto_running = False
            return

        self.next_step()
        self.after_id = self.root.after(1200, self.auto_play)

    def stop_animation(self):

        if self.auto_running:
            self.auto_running = False
            if self.after_id:
                self.root.after_cancel(self.after_id)
                self.after_id = None
            self.log("\n⏸ Animation paused.")
            self.stop_btn.config(text="RESUME")
        else:

            if self.step_index < len(self.steps):
                self.auto_running = True
                self.log("\n▶ Animation resumed.")
                self.stop_btn.config(text="STOP")
                self.auto_play()

    def previous_step(self):

        if self.step_index <= 1:
            self.log("\n⚠ Already at first step.")
            return

        self.step_index -= 1
        (exp, original, output, count, phase, highlight) = self.steps[self.step_index - 1]
        self.draw_visual(original, output, count, exp , phase, highlight)

        self.log("=" * 50)
        self.log(f"STEP {self.step_index}")
        self.log(f"Phase: {phase}")
        self.log(f"Output: {output}")
        self.log("=" * 50)
        self.next_btn.config(state="normal")

    def clear_output(self):

        self.stop_animation()
        self.entry.delete(0, tk.END)
        self.output.delete(1.0, tk.END)
        self.canvas.delete("all")
        self.steps = []
        self.step_index = 0
        self.next_btn.config(state="disabled")
        self.prev_btn.config(state="disabled")
