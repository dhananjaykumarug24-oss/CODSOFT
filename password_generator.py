import tkinter as tk
from tkinter import ttk, messagebox
import random
import string

# ── Colour palette (matches Contact Book / To-Do series) ─────────────────────
BG        = "#F7F8FA"
SIDEBAR   = "#1B4332"
ACCENT    = "#2D6A4F"
ACCENT_LT = "#40916C"
WHITE     = "#FFFFFF"
TEXT      = "#1A1A2E"
MUTED     = "#6B7280"
BORDER    = "#E5E7EB"
DANGER    = "#DC2626"
WARN      = "#F59E0B"
GOOD      = "#10B981"

# Strength colours: Weak / Fair / Strong / Very Strong
STRENGTH_COLORS = ["#DC2626", "#F59E0B", "#40916C", "#1B4332"]
STRENGTH_LABELS = ["Weak", "Fair", "Strong", "Very Strong"]

# ── Password logic ────────────────────────────────────────────────────────────

CHAR_SETS = {
    "uppercase": string.ascii_uppercase,
    "lowercase": string.ascii_lowercase,
    "digits":    string.digits,
    "symbols":   "!@#$%^&*()-_=+[]{}|;:,.<>?",
}

def generate_password(length, use_upper, use_lower, use_digits, use_symbols, exclude_ambiguous):
    pool = ""
    required = []

    if use_upper:
        chars = CHAR_SETS["uppercase"]
        if exclude_ambiguous:
            chars = chars.replace("I", "").replace("O", "")
        pool += chars
        required.append(random.choice(chars))
    if use_lower:
        chars = CHAR_SETS["lowercase"]
        if exclude_ambiguous:
            chars = chars.replace("l", "").replace("o", "")
        pool += chars
        required.append(random.choice(chars))
    if use_digits:
        chars = CHAR_SETS["digits"]
        if exclude_ambiguous:
            chars = chars.replace("0", "").replace("1", "")
        pool += chars
        required.append(random.choice(chars))
    if use_symbols:
        chars = CHAR_SETS["symbols"]
        pool += chars
        required.append(random.choice(chars))

    if not pool:
        return None

    remaining = [random.choice(pool) for _ in range(length - len(required))]
    pwd_list  = required + remaining
    random.shuffle(pwd_list)
    return "".join(pwd_list)

def password_strength(pwd, use_upper, use_lower, use_digits, use_symbols):
    score = 0
    if len(pwd) >= 8:  score += 1
    if len(pwd) >= 14: score += 1
    if use_upper and use_lower: score += 1
    if use_digits:              score += 1
    if use_symbols:             score += 1
    # map 0-5 → 0-3
    idx = min(3, score // 2 + (1 if score >= 3 else 0))
    idx = min(3, max(0, score - 1))
    return min(3, idx)

# ── App ───────────────────────────────────────────────────────────────────────

class PasswordGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Generator")
        self.root.geometry("720x520")
        self.root.minsize(660, 460)
        self.root.configure(bg=BG)
        self.history = []
        self._build_ui()

    def _build_ui(self):
        # ── Sidebar ───────────────────────────────────────────────────────
        sb = tk.Frame(self.root, bg=SIDEBAR, width=210)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        tk.Label(sb, text="🔐", font=("Arial", 30), bg=SIDEBAR, fg=WHITE).pack(pady=(30, 4))
        tk.Label(sb, text="Password Generator", font=("Arial", 11, "bold"),
                 bg=SIDEBAR, fg=WHITE).pack()
        tk.Label(sb, text="Strong. Random. Yours.",
                 font=("Arial", 8), bg=SIDEBAR, fg="#74C69D").pack(pady=(2, 22))

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16, pady=4)

        # ── Options ───────────────────────────────────────────────────────
        tk.Label(sb, text="LENGTH", font=("Arial", 7, "bold"),
                 bg=SIDEBAR, fg="#74C69D").pack(anchor="w", padx=20, pady=(14, 2))

        len_frame = tk.Frame(sb, bg=SIDEBAR)
        len_frame.pack(fill="x", padx=16, pady=(0, 8))

        self.len_var = tk.IntVar(value=16)
        self.len_label = tk.Label(len_frame, text="16", font=("Arial", 12, "bold"),
                                   bg=SIDEBAR, fg=WHITE, width=3)
        self.len_label.pack(side="right")

        slider = ttk.Scale(len_frame, from_=4, to=64, orient="horizontal",
                            variable=self.len_var,
                            command=lambda v: self.len_label.config(text=str(int(float(v)))))
        slider.pack(side="left", fill="x", expand=True)

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16, pady=8)

        tk.Label(sb, text="CHARACTER TYPES", font=("Arial", 7, "bold"),
                 bg=SIDEBAR, fg="#74C69D").pack(anchor="w", padx=20, pady=(4, 4))

        self.use_upper   = tk.BooleanVar(value=True)
        self.use_lower   = tk.BooleanVar(value=True)
        self.use_digits  = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=False)
        self.excl_ambig  = tk.BooleanVar(value=False)

        chk_cfg = dict(bg=SIDEBAR, fg=WHITE, activebackground=SIDEBAR,
                       activeforeground=WHITE, selectcolor=ACCENT_LT,
                       font=("Arial", 9), cursor="hand2")

        tk.Checkbutton(sb, text="Uppercase  (A–Z)", variable=self.use_upper,
                       command=self._auto_generate, **chk_cfg).pack(anchor="w", padx=20, pady=2)
        tk.Checkbutton(sb, text="Lowercase  (a–z)", variable=self.use_lower,
                       command=self._auto_generate, **chk_cfg).pack(anchor="w", padx=20, pady=2)
        tk.Checkbutton(sb, text="Numbers  (0–9)", variable=self.use_digits,
                       command=self._auto_generate, **chk_cfg).pack(anchor="w", padx=20, pady=2)
        tk.Checkbutton(sb, text="Symbols  (!@#…)", variable=self.use_symbols,
                       command=self._auto_generate, **chk_cfg).pack(anchor="w", padx=20, pady=2)

        ttk.Separator(sb, orient="horizontal").pack(fill="x", padx=16, pady=8)
        tk.Checkbutton(sb, text="Exclude ambiguous\n(0, O, l, 1, I…)", variable=self.excl_ambig,
                       command=self._auto_generate, **chk_cfg).pack(anchor="w", padx=20, pady=2)

        # Generate button
        tk.Button(sb, text="⚡  Generate", command=self._generate,
                  bg=ACCENT_LT, fg=WHITE, font=("Arial", 10, "bold"),
                  relief="flat", bd=0, cursor="hand2",
                  activebackground="#52B788", activeforeground=WHITE,
                  padx=12, pady=8, width=16).pack(side="bottom", pady=(0, 20), padx=14)

        # ── Right panel ───────────────────────────────────────────────────
        right = tk.Frame(self.root, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Title
        title_f = tk.Frame(right, bg=BG)
        title_f.pack(fill="x", padx=24, pady=(22, 4))
        tk.Label(title_f, text="Generated Password", font=("Arial", 11, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")

        # Password display box
        pwd_outer = tk.Frame(right, bg=SIDEBAR, padx=2, pady=2)
        pwd_outer.pack(fill="x", padx=24, pady=(4, 0))

        pwd_inner = tk.Frame(pwd_outer, bg=WHITE)
        pwd_inner.pack(fill="x")

        self.pwd_var = tk.StringVar()
        self.pwd_entry = tk.Entry(pwd_inner, textvariable=self.pwd_var,
                                   font=("Courier", 15, "bold"), relief="flat",
                                   bg=WHITE, fg=ACCENT, readonlybackground=WHITE,
                                   state="readonly", justify="center")
        self.pwd_entry.pack(fill="x", ipady=16, padx=12)

        # Copy button
        tk.Button(right, text="📋  Copy to Clipboard", command=self._copy,
                  bg=ACCENT, fg=WHITE, font=("Arial", 10, "bold"),
                  relief="flat", cursor="hand2", padx=16, pady=8,
                  activebackground=ACCENT_LT, activeforeground=WHITE).pack(pady=(10, 4))

        self.copy_label = tk.Label(right, text="", font=("Arial", 8),
                                    bg=BG, fg=GOOD)
        self.copy_label.pack()

        # Strength meter
        str_frame = tk.Frame(right, bg=BG)
        str_frame.pack(fill="x", padx=24, pady=(12, 4))
        tk.Label(str_frame, text="Strength", font=("Arial", 9, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        self.str_label = tk.Label(str_frame, text="—", font=("Arial", 9),
                                   bg=BG, fg=MUTED)
        self.str_label.pack(side="right")

        bar_f = tk.Frame(right, bg=BG)
        bar_f.pack(fill="x", padx=24, pady=(0, 12))
        self.str_bars = []
        for i in range(4):
            b = tk.Frame(bar_f, bg=BORDER, height=8, width=80)
            b.pack(side="left", padx=3)
            b.pack_propagate(False)
            self.str_bars.append(b)

        # History section
        ttk.Separator(right, orient="horizontal").pack(fill="x", padx=24, pady=4)
        hist_hdr = tk.Frame(right, bg=BG)
        hist_hdr.pack(fill="x", padx=24, pady=(4, 4))
        tk.Label(hist_hdr, text="History", font=("Arial", 10, "bold"),
                 bg=BG, fg=TEXT).pack(side="left")
        tk.Button(hist_hdr, text="Clear", command=self._clear_history,
                  bg=BG, fg=MUTED, font=("Arial", 8), relief="flat",
                  cursor="hand2").pack(side="right")

        hist_f = tk.Frame(right, bg=WHITE,
                           highlightbackground=BORDER, highlightthickness=1)
        hist_f.pack(fill="both", expand=True, padx=24, pady=(0, 18))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Hist.Treeview",
                         background=WHITE, fieldbackground=WHITE,
                         foreground=TEXT, rowheight=28,
                         font=("Courier", 9), borderwidth=0)
        style.configure("Hist.Treeview.Heading",
                         background=ACCENT, foreground=WHITE,
                         font=("Arial", 9, "bold"), relief="flat")
        style.map("Hist.Treeview",
                  background=[("selected", ACCENT_LT)],
                  foreground=[("selected", WHITE)])

        self.hist_tree = ttk.Treeview(hist_f, columns=("pwd", "len", "strength"),
                                       show="headings", style="Hist.Treeview",
                                       selectmode="browse", height=5)
        self.hist_tree.heading("pwd",      text="Password")
        self.hist_tree.heading("len",      text="Len")
        self.hist_tree.heading("strength", text="Strength")
        self.hist_tree.column("pwd",      width=320, anchor="w")
        self.hist_tree.column("len",      width=40,  anchor="center")
        self.hist_tree.column("strength", width=90,  anchor="center")
        self.hist_tree.pack(fill="both", expand=True)
        self.hist_tree.bind("<Double-1>", self._load_from_history)

        # Bind slider release to auto-generate
        slider.bind("<ButtonRelease-1>", lambda e: self._auto_generate())

        # Generate initial password
        self._generate()

    # ── Actions ───────────────────────────────────────────────────────────

    def _generate(self):
        length = int(self.len_var.get())
        pwd = generate_password(
            length,
            self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get(),
            self.excl_ambig.get()
        )
        if pwd is None:
            messagebox.showwarning("No character types",
                                   "Please select at least one character type.")
            return

        self.pwd_var.set(pwd)
        self._update_strength(pwd)

        # Add to history
        idx  = min(3, max(0, password_strength(
            pwd, self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get()) ))
        slbl = STRENGTH_LABELS[idx]
        self.history.insert(0, (pwd, str(len(pwd)), slbl))
        if len(self.history) > 10:
            self.history.pop()
        self._refresh_history()
        self.copy_label.config(text="")

    def _auto_generate(self, *_):
        if self.pwd_var.get():
            self._generate()

    def _update_strength(self, pwd):
        idx = password_strength(
            pwd, self.use_upper.get(), self.use_lower.get(),
            self.use_digits.get(), self.use_symbols.get()
        )
        colour = STRENGTH_COLORS[idx]
        label  = STRENGTH_LABELS[idx]
        self.str_label.config(text=label, fg=colour)
        for i, bar in enumerate(self.str_bars):
            bar.config(bg=colour if i <= idx else BORDER)

    def _copy(self):
        pwd = self.pwd_var.get()
        if not pwd:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(pwd)
        self.root.update()
        self.copy_label.config(text="✔ Copied!", fg=GOOD)
        self.root.after(2000, lambda: self.copy_label.config(text=""))

    def _refresh_history(self):
        self.hist_tree.delete(*self.hist_tree.get_children())
        for item in self.history:
            self.hist_tree.insert("", "end", values=item)

    def _clear_history(self):
        self.history.clear()
        self._refresh_history()

    def _load_from_history(self, _=None):
        sel = self.hist_tree.selection()
        if not sel:
            return
        vals = self.hist_tree.item(sel[0])["values"]
        self.pwd_var.set(vals[0])
        self._update_strength(str(vals[0]))
        self.copy_label.config(text="")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordGeneratorApp(root)
    root.mainloop()
