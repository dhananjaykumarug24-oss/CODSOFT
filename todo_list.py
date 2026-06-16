import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "todos.json"

# ── Data layer ───────────────────────────────────────────────────────────────

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

# ── App ──────────────────────────────────────────────────────────────────────

class ToDoApp:
    BG        = "#F7F8FA"
    SIDEBAR   = "#1B4332"
    ACCENT    = "#2D6A4F"
    ACCENT_LT = "#40916C"
    WHITE     = "#FFFFFF"
    TEXT      = "#1A1A2E"
    MUTED     = "#6B7280"
    BORDER    = "#E5E7EB"
    DANGER    = "#DC2626"
    DONE_CLR  = "#9CA3AF"

    PRIORITIES = {"High": "#DC2626", "Medium": "#F59E0B", "Low": "#10B981"}

    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List")
        self.root.geometry("860x580")
        self.root.minsize(760, 500)
        self.root.configure(bg=self.BG)

        self.tasks = load_tasks()
        self.filter_mode = "All"   # All / Active / Done
        self.selected_iid = None

        self._build_ui()
        self._refresh()

    # ── UI ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Sidebar
        sb = tk.Frame(self.root, bg=self.SIDEBAR, width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="✅", font=("Arial", 28), bg=self.SIDEBAR,
                 fg=self.WHITE).pack(pady=(30, 4))
        tk.Label(sb, text="To-Do List", font=("Arial", 13, "bold"),
                 bg=self.SIDEBAR, fg=self.WHITE).pack()
        tk.Label(sb, text="Stay on top of things",
                 font=("Arial", 8), bg=self.SIDEBAR, fg="#74C69D").pack(pady=(2, 24))

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16, pady=4)

        # Add task button
        tk.Button(sb, text="＋  Add Task", command=self._open_add_dialog,
                  bg=self.ACCENT_LT, fg=self.WHITE, font=("Arial", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="#52B788", activeforeground=self.WHITE,
                  padx=12, pady=8, width=16).pack(pady=(20, 6), padx=14)

        ghost = dict(bg=self.SIDEBAR, fg="#74C69D", font=("Arial", 9),
                     relief="flat", bd=0, cursor="hand2",
                     activebackground=self.ACCENT, activeforeground=self.WHITE,
                     padx=12, pady=6, width=16)

        tk.Button(sb, text="✏️  Edit Selected",
                  command=self._open_edit_dialog, **ghost).pack(pady=2, padx=14)
        tk.Button(sb, text="☑  Toggle Done",
                  command=self._toggle_done, **ghost).pack(pady=2, padx=14)
        tk.Button(sb, text="🗑  Delete Selected",
                  command=self._delete_task, **ghost).pack(pady=2, padx=14)
        tk.Button(sb, text="🧹  Clear Completed",
                  command=self._clear_done, **ghost).pack(pady=(12, 2), padx=14)

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16, pady=12)

        # Filter buttons
        tk.Label(sb, text="FILTER", font=("Arial", 7, "bold"),
                 bg=self.SIDEBAR, fg="#74C69D").pack(anchor="w", padx=20)
        self.filter_btns = {}
        for label in ("All", "Active", "Done"):
            b = tk.Button(sb, text=label, command=lambda l=label: self._set_filter(l),
                          bg=self.SIDEBAR, fg=self.WHITE, font=("Arial", 9),
                          relief="flat", bd=0, cursor="hand2", width=16,
                          activebackground=self.ACCENT, activeforeground=self.WHITE,
                          padx=12, pady=5)
            b.pack(pady=2, padx=14)
            self.filter_btns[label] = b
        self._highlight_filter()

        self.stats_var = tk.StringVar()
        tk.Label(sb, textvariable=self.stats_var, font=("Arial", 8),
                 bg=self.SIDEBAR, fg="#74C69D").pack(side="bottom", pady=14)

        # Right panel
        right = tk.Frame(self.root, bg=self.BG)
        right.pack(side="left", fill="both", expand=True)

        # Search
        sf = tk.Frame(right, bg=self.BG)
        sf.pack(fill="x", padx=20, pady=(18, 10))
        tk.Label(sf, text="🔍", font=("Arial", 13), bg=self.BG, fg=self.MUTED).pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._refresh())
        e = tk.Entry(sf, textvariable=self.search_var, font=("Arial", 11),
                     relief="flat", bg=self.WHITE, fg=self.TEXT,
                     insertbackground=self.TEXT)
        e.pack(side="left", fill="x", expand=True, ipady=6, padx=8)

        # Progress bar area
        prog_frame = tk.Frame(right, bg=self.BG)
        prog_frame.pack(fill="x", padx=20, pady=(0, 8))
        self.prog_label = tk.Label(prog_frame, text="", font=("Arial", 9),
                                    bg=self.BG, fg=self.MUTED)
        self.prog_label.pack(side="left")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("green.Horizontal.TProgressbar",
                         troughcolor=self.BORDER,
                         background=self.ACCENT_LT,
                         borderwidth=0)
        self.progress = ttk.Progressbar(prog_frame, style="green.Horizontal.TProgressbar",
                                         orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side="right", pady=4)

        # Task list (Treeview)
        lf = tk.Frame(right, bg=self.BG)
        lf.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        style.configure("CB.Treeview",
                         background=self.WHITE, fieldbackground=self.WHITE,
                         foreground=self.TEXT, rowheight=38,
                         font=("Arial", 10), borderwidth=0)
        style.configure("CB.Treeview.Heading",
                         background=self.ACCENT, foreground=self.WHITE,
                         font=("Arial", 10, "bold"), relief="flat")
        style.map("CB.Treeview",
                  background=[("selected", self.ACCENT_LT)],
                  foreground=[("selected", self.WHITE)])

        cols = ("status", "task", "priority", "due", "created")
        self.tree = ttk.Treeview(lf, columns=cols, show="headings",
                                  style="CB.Treeview", selectmode="browse")

        for col, heading, width, anchor in [
            ("status",   "✔",        38,  "center"),
            ("task",     "Task",     260, "w"),
            ("priority", "Priority",  80, "center"),
            ("due",      "Due Date", 100, "center"),
            ("created",  "Added",    110, "center"),
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=anchor, minwidth=width)

        # Tag colours
        self.tree.tag_configure("done",   foreground=self.DONE_CLR)
        self.tree.tag_configure("high",   foreground="#DC2626")
        self.tree.tag_configure("medium", foreground="#B45309")
        self.tree.tag_configure("low",    foreground="#065F46")

        sb2 = ttk.Scrollbar(lf, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb2.set)
        sb2.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>", lambda e: self._open_edit_dialog())
        self.tree.bind("<space>",    lambda e: self._toggle_done())

        # Input quick-add bar at bottom
        qa = tk.Frame(right, bg=self.WHITE,
                      highlightbackground=self.BORDER, highlightthickness=1)
        qa.pack(fill="x", padx=20, pady=(0, 16))

        self.quick_var = tk.StringVar()
        qe = tk.Entry(qa, textvariable=self.quick_var, font=("Arial", 10),
                      relief="flat", bg=self.WHITE, fg=self.TEXT,
                      insertbackground=self.TEXT)
        qe.pack(side="left", fill="x", expand=True, ipady=8, padx=(12, 0))
        qe.insert(0, "")
        qe.bind("<Return>", lambda e: self._quick_add())

        # Priority selector for quick-add
        self.quick_pri = tk.StringVar(value="Medium")
        pri_menu = ttk.Combobox(qa, textvariable=self.quick_pri,
                                 values=list(self.PRIORITIES.keys()),
                                 state="readonly", width=8, font=("Arial", 9))
        pri_menu.pack(side="left", padx=6, ipady=4)

        tk.Button(qa, text="Quick Add ↵", command=self._quick_add,
                  bg=self.ACCENT, fg=self.WHITE, relief="flat",
                  font=("Arial", 9, "bold"), padx=12, pady=8, cursor="hand2",
                  activebackground=self.ACCENT_LT, activeforeground=self.WHITE).pack(side="right")

    # ── Refresh / filter ─────────────────────────────────────────────────

    def _visible_tasks(self):
        q    = self.search_var.get().strip().lower()
        mode = self.filter_mode
        out  = []
        for t in self.tasks:
            if mode == "Active" and t.get("done"):
                continue
            if mode == "Done"   and not t.get("done"):
                continue
            if q and q not in t["title"].lower():
                continue
            out.append(t)
        return out

    def _refresh(self):
        visible = self._visible_tasks()
        self.tree.delete(*self.tree.get_children())

        for t in visible:
            status = "✔" if t.get("done") else "○"
            pri    = t.get("priority", "Medium")
            due    = t.get("due", "")
            added  = t.get("created", "")[:10]
            tag    = "done" if t.get("done") else pri.lower()
            iid    = str(id(t))
            self.tree.insert("", "end", iid=iid,
                             values=(status, t["title"], pri, due, added),
                             tags=(tag,))

        # Stats
        total = len(self.tasks)
        done  = sum(1 for t in self.tasks if t.get("done"))
        pct   = int(done / total * 100) if total else 0
        self.stats_var.set(f"{done}/{total} done")
        self.progress["value"] = pct
        self.prog_label.config(text=f"{done} of {total} tasks complete  ({pct}%)")
        self._highlight_filter()

    def _set_filter(self, mode):
        self.filter_mode = mode
        self._refresh()

    def _highlight_filter(self):
        for label, btn in self.filter_btns.items():
            if label == self.filter_mode:
                btn.config(bg=self.ACCENT_LT, fg=self.WHITE)
            else:
                btn.config(bg=self.SIDEBAR, fg=self.WHITE)

    def _on_select(self, _=None):
        sel = self.tree.selection()
        self.selected_iid = sel[0] if sel else None

    def _task_from_iid(self, iid):
        """Return the task dict whose id() matches iid."""
        for t in self.tasks:
            if str(id(t)) == iid:
                return t
        return None

    # ── Actions ───────────────────────────────────────────────────────────

    def _quick_add(self):
        title = self.quick_var.get().strip()
        if not title:
            return
        self.tasks.append({
            "title":    title,
            "priority": self.quick_pri.get(),
            "due":      "",
            "note":     "",
            "done":     False,
            "created":  datetime.now().isoformat(),
        })
        save_tasks(self.tasks)
        self.quick_var.set("")
        self._refresh()

    def _toggle_done(self):
        if not self.selected_iid:
            messagebox.showwarning("No selection", "Select a task first.")
            return
        t = self._task_from_iid(self.selected_iid)
        if t:
            t["done"] = not t.get("done", False)
            save_tasks(self.tasks)
            self._refresh()

    def _delete_task(self):
        if not self.selected_iid:
            messagebox.showwarning("No selection", "Select a task first.")
            return
        t = self._task_from_iid(self.selected_iid)
        if t and messagebox.askyesno("Delete", f"Delete '{t['title']}'?", icon="warning"):
            self.tasks.remove(t)
            save_tasks(self.tasks)
            self.selected_iid = None
            self._refresh()

    def _clear_done(self):
        done_count = sum(1 for t in self.tasks if t.get("done"))
        if done_count == 0:
            messagebox.showinfo("Nothing to clear", "No completed tasks.")
            return
        if messagebox.askyesno("Clear Completed",
                                f"Remove {done_count} completed task(s)?"):
            self.tasks = [t for t in self.tasks if not t.get("done")]
            save_tasks(self.tasks)
            self._refresh()

    # ── Dialogs ───────────────────────────────────────────────────────────

    def _open_add_dialog(self):
        self._task_dialog("Add Task")

    def _open_edit_dialog(self):
        if not self.selected_iid:
            messagebox.showwarning("No selection", "Select a task first.")
            return
        t = self._task_from_iid(self.selected_iid)
        if t:
            self._task_dialog("Edit Task", task=t)

    def _task_dialog(self, title, task=None):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("440x340")
        dlg.resizable(False, False)
        dlg.configure(bg=self.BG)
        dlg.grab_set()
        dlg.transient(self.root)

        # Header
        hdr = tk.Frame(dlg, bg=self.SIDEBAR, height=52)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, font=("Arial", 12, "bold"),
                 bg=self.SIDEBAR, fg=self.WHITE).pack(side="left", padx=16, pady=14)

        body = tk.Frame(dlg, bg=self.BG, padx=24, pady=16)
        body.pack(fill="both", expand=True)

        def row(label, widget_fn, r):
            tk.Label(body, text=label, font=("Arial", 9),
                     bg=self.BG, fg=self.MUTED).grid(row=r, column=0, sticky="w", pady=(8,0))
            w = widget_fn()
            w.grid(row=r, column=1, sticky="ew", padx=(10, 0), pady=(8,0), ipady=4)
            return w

        body.columnconfigure(1, weight=1)

        # Title
        title_var = tk.StringVar(value=task["title"] if task else "")
        title_e = row("Task *", lambda: tk.Entry(body, textvariable=title_var,
                       font=("Arial", 10), relief="solid", bg=self.WHITE,
                       fg=self.TEXT, bd=1), 0)

        # Priority
        pri_var = tk.StringVar(value=task.get("priority","Medium") if task else "Medium")
        pri_cb  = row("Priority", lambda: ttk.Combobox(body, textvariable=pri_var,
                       values=list(self.PRIORITIES.keys()), state="readonly",
                       font=("Arial", 10)), 1)

        # Due date
        due_var = tk.StringVar(value=task.get("due","") if task else "")
        row("Due Date (YYYY-MM-DD)", lambda: tk.Entry(body, textvariable=due_var,
             font=("Arial", 10), relief="solid", bg=self.WHITE,
             fg=self.TEXT, bd=1), 2)

        # Note
        tk.Label(body, text="Note", font=("Arial", 9),
                 bg=self.BG, fg=self.MUTED).grid(row=3, column=0, sticky="nw", pady=(10,0))
        note_txt = tk.Text(body, font=("Arial", 10), relief="solid", bd=1,
                           bg=self.WHITE, fg=self.TEXT, height=3, width=28)
        note_txt.grid(row=3, column=1, sticky="ew", padx=(10,0), pady=(10,0))
        if task and task.get("note"):
            note_txt.insert("1.0", task["note"])

        # Done checkbox (edit only)
        done_var = tk.BooleanVar(value=task.get("done", False) if task else False)
        if task:
            tk.Checkbutton(body, text="Mark as done", variable=done_var,
                           bg=self.BG, fg=self.TEXT, font=("Arial", 9),
                           activebackground=self.BG, cursor="hand2").grid(
                           row=4, column=1, sticky="w", padx=(10,0), pady=(8,0))

        # Buttons
        btn_row = tk.Frame(body, bg=self.BG)
        btn_row.grid(row=5, column=0, columnspan=2, pady=(16,0), sticky="e")

        def save():
            t_title = title_var.get().strip()
            if not t_title:
                messagebox.showerror("Required", "Task title is required.", parent=dlg)
                return
            data = {
                "title":    t_title,
                "priority": pri_var.get(),
                "due":      due_var.get().strip(),
                "note":     note_txt.get("1.0", "end").strip(),
                "done":     done_var.get(),
                "created":  task["created"] if task else datetime.now().isoformat(),
            }
            if task:
                idx = self.tasks.index(task)
                self.tasks[idx] = data
            else:
                self.tasks.append(data)
            save_tasks(self.tasks)
            self._refresh()
            dlg.destroy()

        tk.Button(btn_row, text="Cancel", command=dlg.destroy,
                  bg=self.BORDER, fg=self.TEXT, relief="flat",
                  font=("Arial", 9), padx=14, pady=6, cursor="hand2").pack(side="left", padx=(0,8))
        tk.Button(btn_row, text="Save Task", command=save,
                  bg=self.ACCENT, fg=self.WHITE, relief="flat",
                  font=("Arial", 9, "bold"), padx=14, pady=6, cursor="hand2",
                  activebackground=self.ACCENT_LT, activeforeground=self.WHITE).pack(side="left")

        title_e.focus_set()
        dlg.bind("<Return>", lambda e: save())
        dlg.bind("<Escape>", lambda e: dlg.destroy())


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
