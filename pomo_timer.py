# coding: utf-8
"""
@author: naubull2
@email: naubull2@gmail.com

Pomodoro Timer
"""
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os


CONFIG_FILE = "pomodoro_config.json"
DEFAULT_CONFIG = {
    "work_duration": 25,     # minutes
    "short_break": 5,        # minutes
    "long_break": 15,        # minutes
    "long_break_every": 4    # after how many work sessions a long break happens
}

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.load_config()
        self.current_iteration = 0
        self.total_iterations = 0
        self.state = "idle"  # possible states: idle, work, short_break, long_break
        self.timer_seconds = 0
        self.timer_id = None
        self.paused = False

        self.create_widgets()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    self.config = json.load(f)
            except Exception as e:
                messagebox.showwarning("Warning", f"Error loading config: {e}\nUsing defaults.")
                self.config = DEFAULT_CONFIG.copy()
        else:
            self.config = DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving config: {e}")

    def auto_save_config(self, event=None):
        try:
            self.config["work_duration"] = int(self.work_entry.get())
            self.config["short_break"] = int(self.short_break_entry.get())
            self.config["long_break"] = int(self.long_break_entry.get())
            self.config["long_break_every"] = int(self.long_break_every_entry.get())
            self.save_config()
        except Exception as e:
            messagebox.showerror("Error", f"Invalid configuration input: {e}")

    def create_widgets(self):
        # Configuration frame
        config_frame = ttk.LabelFrame(self.root, text="Configuration")
        config_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(config_frame, text="Work (min):").grid(row=0, column=0, sticky="w")
        self.work_entry = ttk.Entry(config_frame, width=5)
        self.work_entry.insert(0, str(self.config["work_duration"]))
        self.work_entry.grid(row=0, column=1, padx=5)
        self.work_entry.bind("<FocusOut>", self.auto_save_config)

        ttk.Label(config_frame, text="Short Break (min):").grid(row=0, column=2, sticky="w")
        self.short_break_entry = ttk.Entry(config_frame, width=5)
        self.short_break_entry.insert(0, str(self.config["short_break"]))
        self.short_break_entry.grid(row=0, column=3, padx=5)
        self.short_break_entry.bind("<FocusOut>", self.auto_save_config)

        ttk.Label(config_frame, text="Long Break (min):").grid(row=1, column=0, sticky="w")
        self.long_break_entry = ttk.Entry(config_frame, width=5)
        self.long_break_entry.insert(0, str(self.config["long_break"]))
        self.long_break_entry.grid(row=1, column=1, padx=5)
        self.long_break_entry.bind("<FocusOut>", self.auto_save_config)

        ttk.Label(config_frame, text="Long Break Every:").grid(row=1, column=2, sticky="w")
        self.long_break_every_entry = ttk.Entry(config_frame, width=5)
        self.long_break_every_entry.insert(0, str(self.config["long_break_every"]))
        self.long_break_every_entry.grid(row=1, column=3, padx=5)
        self.long_break_every_entry.bind("<FocusOut>", self.auto_save_config)

        # Task setup frame
        task_frame = ttk.LabelFrame(self.root, text="Task Setup")
        task_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(task_frame, text="Task Name:").grid(row=0, column=0, sticky="w")
        self.task_entry = ttk.Entry(task_frame, width=30)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(task_frame, text="Total Iterations:").grid(row=1, column=0, sticky="w")
        self.iterations_entry = ttk.Entry(task_frame, width=5)
        self.iterations_entry.insert(0, "4")
        self.iterations_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Timer display and controls frame
        timer_frame = ttk.LabelFrame(self.root, text="Timer")
        timer_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.state_label = ttk.Label(timer_frame, text="State: Idle", font=("Helvetica", 14))
        self.state_label.grid(row=0, column=0, columnspan=4, pady=5)

        self.iteration_label = ttk.Label(timer_frame, text="Iteration: 0/0", font=("Helvetica", 12))
        self.iteration_label.grid(row=1, column=0, columnspan=4, pady=5)

        self.timer_label = ttk.Label(timer_frame, text="00:00", font=("Helvetica", 36))
        self.timer_label.grid(row=2, column=0, columnspan=4, pady=10)

        # Control buttons: Start, Pause/Resume, Skip, Reset.
        self.start_button = ttk.Button(timer_frame, text="Start Work", command=self.start_work)
        self.start_button.grid(row=3, column=0, padx=5, pady=5)

        self.pause_button = ttk.Button(timer_frame, text="Pause", command=self.toggle_pause, state="disabled")
        self.pause_button.grid(row=3, column=1, padx=5, pady=5)

        self.skip_button = ttk.Button(timer_frame, text="Skip", command=self.skip_timer, state="disabled")
        self.skip_button.grid(row=3, column=2, padx=5, pady=5)
        
        self.reset_button = ttk.Button(timer_frame, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=3, column=3, padx=5, pady=5)

    def update_iteration_label(self):
        self.iteration_label.config(text=f"Iteration: {self.current_iteration}/{self.total_iterations}")

    def change_state(self, new_state):
        self.state = new_state
        if new_state == "work":
            self.state_label.config(text="State: Work", foreground="green")
        elif new_state == "short_break":
            self.state_label.config(text="State: Short Break", foreground="orange")
        elif new_state == "long_break":
            self.state_label.config(text="State: Long Break", foreground="blue")
        else:
            self.state_label.config(text="State: Idle", foreground="black")

    def start_work(self):
        self.root.focus()  # Remove focus from entries
        if not self.task_entry.get().strip():
            messagebox.showerror("Error", "Please enter a task name.")
            return
        try:
            self.total_iterations = int(self.iterations_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Total iterations must be an integer.")
            return

        # Reset iteration if needed.
        if self.state == "idle" and self.current_iteration >= self.total_iterations:
            self.current_iteration = 0

        if self.current_iteration < self.total_iterations:
            self.current_iteration += 1
            self.update_iteration_label()
            self.change_state("work")
            self.timer_seconds = self.config["work_duration"] * 60
            self.start_button.config(state="disabled")
            self.skip_button.config(state="normal")
            self.pause_button.config(state="normal", text="Pause")
            self.paused = False
            self.update_timer()
        else:
            messagebox.showinfo("Info", "All work sessions completed. Great job!")

    def start_break(self, break_type):
        self.change_state(break_type)
        if break_type == "short_break":
            self.timer_seconds = self.config["short_break"] * 60
        else:
            self.timer_seconds = self.config["long_break"] * 60
        self.skip_button.config(state="normal")
        self.pause_button.config(state="normal", text="Pause")
        self.paused = False
        self.update_timer()

    def update_timer(self):
        mins, secs = divmod(self.timer_seconds, 60)
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        if self.timer_seconds > 0 and not self.paused:
            self.timer_seconds -= 1
            self.timer_id = self.root.after(1000, self.update_timer)
        else:
            # If timer_seconds is 0, finish the phase.
            if self.timer_seconds == 0:
                self.timer_id = None
                self.skip_button.config(state="disabled")
                self.pause_button.config(state="disabled")
                self.handle_phase_completion()

    def toggle_pause(self):
        self.root.focus()  # Ensure focus isn't interfering with button clicks.
        if self.paused:
            # Resume timer
            self.paused = False
            self.pause_button.config(text="Pause")
            self.update_timer()
        else:
            # Pause timer
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None
            self.paused = True
            self.pause_button.config(text="Resume")

    def skip_timer(self):
        self.root.focus()
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.skip_button.config(state="disabled")
        self.pause_button.config(state="disabled")
        self.handle_phase_completion(skipped=True)

    def handle_phase_completion(self, skipped=False):
        if self.state == "work":
            # For work sessions, skipping starts the break automatically.
            if self.current_iteration < self.total_iterations:
                if self.current_iteration % self.config["long_break_every"] == 0:
                    self.start_break("long_break")
                else:
                    self.start_break("short_break")
            else:
                self.change_state("idle")
                messagebox.showinfo("Done", "All work sessions completed. Great job!")
                self.start_button.config(state="normal")
                self.pause_button.config(state="disabled")
        elif self.state in ["short_break", "long_break"]:
            # When skipping during a break, update the timer to the upcoming work session's initial value.
            self.change_state("idle")
            self.start_button.config(state="normal")
            self.pause_button.config(state="disabled")
            if skipped:
                self.timer_seconds = self.config["work_duration"] * 60
                mins, secs = divmod(self.timer_seconds, 60)
                self.timer_label.config(text=f"{mins:02d}:{secs:02d}")

    def reset_timer(self):
        self.root.focus()  # Remove focus from entries.
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.current_iteration = 0
        self.timer_seconds = 0
        self.change_state("idle")
        self.update_iteration_label()
        self.timer_label.config(text="00:00")
        self.start_button.config(state="normal")
        self.skip_button.config(state="disabled")
        self.pause_button.config(state="disabled", text="Pause")
        self.paused = False
        messagebox.showinfo("Reset", "Timer has been reset.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()

