
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import sys
import shutil
from datetime import date, timedelta

# ==================================================
# TASK 4J - MADE BY RAKSHIT
# Offline productivity and gamification application
# ==================================================

root = tk.Tk()
root.title("Task forge - Smart Productivity Workspace")
root.geometry("1050x850")
root.minsize(800, 650)
root.configure(bg="#f2f5fa")

BG = "#f2f5fa"
NAVY = "#243b67"
BLUE = "#2878d0"
GREEN = "#28a745"
RED = "#dc4c4c"

# ---------------- DATABASE ----------------

db = sqlite3.connect("taskforge.db")
db.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    day TEXT NOT NULL,
    priority TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    xp_awarded INTEGER DEFAULT 0
)
""")

# Support databases created by the earlier TaskForge versions.
task_columns = {
    row[1] for row in db.execute("PRAGMA table_info(tasks)")
}
if "xp_awarded" not in task_columns:
    db.execute(
        "ALTER TABLE tasks ADD COLUMN xp_awarded INTEGER DEFAULT 0"
    )

db.execute("""
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    xp INTEGER DEFAULT 0,
    streak INTEGER DEFAULT 0,
    last_completion_day TEXT DEFAULT ''
)
""")

db.execute("""
INSERT OR IGNORE INTO profile
(id, xp, streak, last_completion_day)
VALUES (1, 0, 0, '')
""")
db.commit()

# ---------------- HEADER ----------------

header = tk.Frame(root, bg=NAVY, padx=22, pady=12)
header.pack(fill="x")

tk.Label(
    header, text="Task 4J",
    font=("Arial", 27, "bold"),
    fg="white", bg=NAVY
).pack(anchor="w")

tk.Label(
    header, text="made by Rakshit",
    font=("Arial", 10),
    fg="#dce6ff", bg=NAVY
).pack(anchor="w")

tk.Label(
    header, text="Your Smart Productivity Workspace",
    font=("Arial", 12),
    fg="white", bg=NAVY
).pack(anchor="w", pady=(5, 0))

# ---------------- WORKSPACE ----------------

workspace = tk.LabelFrame(
    root, text=" Workspace ",
    font=("Arial", 11, "bold"),
    bg=BG, padx=10, pady=8
)
workspace.pack(fill="x", padx=15, pady=8)


def open_app(app_name, display_name):
    try:
        if sys.platform == "win32":
            path = shutil.which(app_name)

            if path:
                subprocess.Popen([path])
            else:
                subprocess.Popen(
                    ["cmd", "/c", "start", "", app_name],
                    shell=False
                )
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-a", app_name])
        else:
            messagebox.showinfo(
                "Workspace",
                "These shortcuts are designed for Windows."
            )
    except OSError:
        messagebox.showerror(
            "Cannot open application",
            f"Could not open {display_name}.\n"
            "Check that it is installed on this computer."
        )


tk.Button(
    workspace, text="Open MS Word",
    command=lambda: open_app("winword", "Microsoft Word"),
    bg=BLUE, fg="white", width=16
).pack(side="left", padx=5)

tk.Button(
    workspace, text="Open PowerPoint",
    command=lambda: open_app("powerpnt", "PowerPoint"),
    bg="#c65332", fg="white", width=16
).pack(side="left", padx=5)

tk.Button(
    workspace, text="Open Notepad",
    command=lambda: open_app("notepad", "Notepad"),
    bg="#52627a", fg="white", width=16
).pack(side="left", padx=5)

# ---------------- ACHIEVEMENTS ----------------

achievements = tk.LabelFrame(
    root, text=" Achievement Dashboard ",
    font=("Arial", 11, "bold"),
    bg=BG, padx=12, pady=8
)
achievements.pack(fill="x", padx=15, pady=5)

xp_label = tk.Label(
    achievements, text="", font=("Arial", 12, "bold"),
    bg=BG, fg=NAVY
)
xp_label.pack(anchor="w")

level_label = tk.Label(
    achievements, text="", font=("Arial", 11),
    bg=BG
)
level_label.pack(anchor="w", pady=2)

rank_label = tk.Label(
    achievements, text="", font=("Arial", 11, "bold"),
    bg=BG, fg="#a66a20"
)
rank_label.pack(anchor="w", pady=2)

streak_label = tk.Label(
    achievements, text="", font=("Arial", 11, "bold"),
    bg=BG, fg="#d35400"
)
streak_label.pack(anchor="w", pady=2)

level_bar = ttk.Progressbar(
    achievements, orient="horizontal",
    mode="determinate", maximum=100
)
level_bar.pack(fill="x", pady=5)

level_progress_label = tk.Label(
    achievements, text="", bg=BG, fg="#52627a"
)
level_progress_label.pack(anchor="w")


def get_profile():
    return db.execute(
        "SELECT xp, streak, last_completion_day "
        "FROM profile WHERE id = 1"
    ).fetchone()


def rank_for_level(level):
    if level >= 20:
        return "Diamond"
    if level >= 15:
        return "Platinum"
    if level >= 10:
        return "Gold"
    if level >= 5:
        return "Silver"
    return "Bronze"


def update_dashboard():
    xp, streak, last_day = get_profile()
    level = xp // 100 + 1
    level_xp = xp % 100

    # Show a missed-day streak as zero immediately.
    if last_day:
        days_since = (
            date.today() - date.fromisoformat(last_day)
        ).days
        if days_since > 1:
            streak = 0

    xp_label.config(text=f"⭐ Total XP: {xp}")
    level_label.config(
        text=f"🎮 Level {level} | {level_xp}/100 XP to next level"
    )
    rank_label.config(text=f"🏆 Rank: {rank_for_level(level)}")
    streak_label.config(text=f"🔥 Daily streak: {streak} day(s)")

    level_bar["value"] = level_xp
    level_progress_label.config(
        text=f"{100 - level_xp} XP remaining for the next level"
    )

# ---------------- TASK ENTRY ----------------

form = tk.Frame(root, bg=BG, padx=15, pady=8)
form.pack(fill="x")

task_entry = tk.Entry(form, font=("Arial", 11), width=25)
task_entry.grid(row=0, column=0, padx=4, pady=4)

day_entry = tk.Entry(form, font=("Arial", 10), width=12)
day_entry.insert(0, date.today().isoformat())
day_entry.grid(row=0, column=1, padx=4)

priority = ttk.Combobox(
    form, values=["High", "Medium", "Low"],
    state="readonly", width=9
)
priority.set("Medium")
priority.grid(row=0, column=2, padx=4)

# ---------------- TASK TABLE ----------------

stats = tk.Label(
    root, text="", bg=BG,
    font=("Arial", 11, "bold")
)
stats.pack(pady=3)

table = ttk.Treeview(
    root,
    columns=("id", "task", "day", "priority", "status"),
    show="headings",
    height=8
)

for col, heading in [
    ("id", "ID"),
    ("task", "Task"),
    ("day", "Due Date"),
    ("priority", "Priority"),
    ("status", "Status")
]:
    table.heading(col, text=heading)

table.column("id", width=40, anchor="center")
table.column("task", width=330)
table.column("day", width=110, anchor="center")
table.column("priority", width=90, anchor="center")
table.column("status", width=100, anchor="center")

table.pack(fill="both", expand=True, padx=15, pady=5)

# ---------------- STATISTICS GRAPH ----------------

graph_box = tk.LabelFrame(
    root, text=" Task Statistics ",
    font=("Arial", 11, "bold"),
    bg=BG, padx=10, pady=5
)
graph_box.pack(fill="x", padx=15, pady=5)

graph = tk.Canvas(
    graph_box, height=105,
    bg=BG, highlightthickness=0
)
graph.pack(fill="x", expand=True)


def draw_statistics():
    graph.delete("all")

    rows = db.execute(
        "SELECT done FROM tasks"
    ).fetchall()

    total = len(rows)
    completed = sum(row[0] for row in rows)
    pending = total - completed

    completed_pct = completed / total * 100 if total else 0
    pending_pct = pending / total * 100 if total else 0

    width = max(graph.winfo_width(), 300)
    x = 15
    bar_width = width - 30
    bar_y = 43
    bar_height = 22

    graph.create_text(
        x, 12,
        text=f"Completed: {completed} ({completed_pct:.1f}%)",
        anchor="w", fill=GREEN,
        font=("Arial", 10, "bold")
    )
    graph.create_text(
        x, 29,
        text=f"Pending: {pending} ({pending_pct:.1f}%)",
        anchor="w", fill=RED,
        font=("Arial", 10, "bold")
    )

    graph.create_rectangle(
        x, bar_y, x + bar_width, bar_y + bar_height,
        fill="#e1e6ef", outline=""
    )

    if total:
        green_width = bar_width * completed / total
        if green_width > 0:
            graph.create_rectangle(
                x, bar_y, x + green_width, bar_y + bar_height,
                fill=GREEN, outline=""
            )

    graph.create_text(
        width / 2, 83,
        text=f"Overall task completion: {completed_pct:.1f}%",
        font=("Arial", 11, "bold"),
        fill=NAVY
    )

# ---------------- REFRESH TASKS ----------------

def refresh():
    for item in table.get_children():
        table.delete(item)

    rows = db.execute("""
        SELECT id, title, day, priority, done
        FROM tasks ORDER BY done, day
    """).fetchall()

    completed = sum(row[4] for row in rows)
    total = len(rows)

    stats.config(
        text=f"📊 Completed: {completed}/{total} tasks"
    )

    for task_id, title, day, level, done in rows:
        table.insert(
            "", "end",
            values=(
                task_id, title, day, level,
                "Completed" if done else "Pending"
            )
        )

    update_dashboard()
    draw_statistics()


def add_task():
    title = task_entry.get().strip()
    due_day = day_entry.get().strip()

    if not title:
        messagebox.showwarning("Missing task", "Enter a task first.")
        return

    try:
        date.fromisoformat(due_day)
    except ValueError:
        messagebox.showwarning(
            "Invalid date", "Use YYYY-MM-DD."
        )
        return

    db.execute(
        "INSERT INTO tasks (title, day, priority) VALUES (?, ?, ?)",
        (title, due_day, priority.get())
    )
    db.commit()
    task_entry.delete(0, tk.END)
    refresh()


tk.Button(
    form, text="Add Task", command=add_task,
    bg=BLUE, fg="white",
    font=("Arial", 10, "bold")
).grid(row=0, column=3, padx=4)

# ---------------- COMPLETE TASK / XP ----------------

def complete_task():
    selection = table.selection()

    if not selection:
        messagebox.showinfo("Select task", "Select a task first.")
        return

    task_id = table.item(selection[0], "values")[0]

    row = db.execute(
        "SELECT done FROM tasks WHERE id = ?",
        (task_id,)
    ).fetchone()

    if not row or row[0]:
        messagebox.showinfo(
            "Already completed",
            "This task has already been completed."
        )
        return

    today = date.today()
    xp, streak, last_day = get_profile()

    if last_day != today.isoformat():
        if last_day:
            previous = date.fromisoformat(last_day)
            if previous == today - timedelta(days=1):
                streak += 1
            else:
                streak = 1
        else:
            streak = 1

    xp += 10

    db.execute(
        "UPDATE tasks SET done = 1, xp_awarded = 1 WHERE id = ?",
        (task_id,)
    )
    db.execute("""
        UPDATE profile
        SET xp = ?, streak = ?, last_completion_day = ?
        WHERE id = 1
    """, (xp, streak, today.isoformat()))

    db.commit()
    refresh()

    level = xp // 100 + 1

    messagebox.showinfo(
        "Task completed!",
        f"Great work!\n\n"
        f"+10 XP earned!\n"
        f"Total XP: {xp}\n"
        f"Level: {level}\n"
        f"Rank: {rank_for_level(level)}\n"
        f"Daily streak: {streak} day(s)"
    )

# ---------------- DELETE TASK ----------------

def delete_task():
    selection = table.selection()

    if not selection:
        messagebox.showinfo("Select task", "Select a task first.")
        return

    task_id = table.item(selection[0], "values")[0]

    if messagebox.askyesno("Confirm", "Delete this task?"):
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()
        refresh()

# ---------------- BUTTONS ----------------

buttons = tk.Frame(root, bg=BG, pady=7)
buttons.pack()

tk.Button(
    buttons, text="Mark Completed (+10 XP)",
    command=complete_task, width=23
).pack(side="left", padx=5)

tk.Button(
    buttons, text="Delete Task",
    command=delete_task, width=15
).pack(side="left", padx=5)

# ---------------- REMINDERS EVERY 11 MINUTES ----------------

REMINDER_MS = 11 * 60 * 1000


def remind():
    pending = db.execute(
        "SELECT title FROM tasks WHERE done = 0"
    ).fetchall()

    if pending:
        messagebox.showinfo(
            "Task 4J Reminder",
            "Time to review your pending tasks!\n\n"
            + "\n".join("- " + row[0] for row in pending)
        )

    root.after(REMINDER_MS, remind)

# ---------------- FOOTER & STARTUP ----------------

tk.Label(
    root,
    text="Task 4J | made by Rakshit | Offline mode",
    bg=BG, fg="#65738a"
).pack(pady=5)

refresh()

# Redraw the graph if the window is resized.
graph.bind("<Configure>", lambda event: draw_statistics())

root.after(REMINDER_MS, remind)


def close_app():
    db.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()
