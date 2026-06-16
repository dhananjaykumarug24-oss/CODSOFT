import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

DATA_FILE = "contacts.json"

# ── Data layer ──────────────────────────────────────────────────────────────

def load_contacts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    with open(DATA_FILE, "w") as f:
        json.dump(contacts, f, indent=2)

# ── App ──────────────────────────────────────────────────────────────────────

class ContactBookApp:
    # Colour palette – dark green accent, clean neutrals
    BG        = "#F7F8FA"
    SIDEBAR   = "#1B4332"
    ACCENT    = "#2D6A4F"
    ACCENT_LT = "#40916C"
    WHITE     = "#FFFFFF"
    TEXT      = "#1A1A2E"
    MUTED     = "#6B7280"
    DANGER    = "#DC2626"
    BORDER    = "#E5E7EB"

    def __init__(self, root):
        self.root = root
        self.root.title("Contact Book")
        self.root.geometry("860x580")
        self.root.minsize(760, 500)
        self.root.configure(bg=self.BG)

        self.contacts = load_contacts()
        self.selected_index = None          # index into self.filtered
        self.filtered = list(self.contacts) # currently displayed

        self._build_ui()
        self._refresh_list()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        # ── Left sidebar ─────────────────────────────────────────────────
        sidebar = tk.Frame(self.root, bg=self.SIDEBAR, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="📒", font=("Arial", 28),
                 bg=self.SIDEBAR, fg=self.WHITE).pack(pady=(30, 4))
        tk.Label(sidebar, text="Contact Book", font=("Arial", 13, "bold"),
                 bg=self.SIDEBAR, fg=self.WHITE).pack()
        tk.Label(sidebar, text="Keep everyone close",
                 font=("Arial", 8), bg=self.SIDEBAR, fg="#74C69D").pack(pady=(2, 28))

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", padx=16, pady=4)

        btn_cfg = dict(bg=self.ACCENT_LT, fg=self.WHITE, font=("Arial", 10, "bold"),
                       relief="flat", bd=0, cursor="hand2",
                       activebackground="#52B788", activeforeground=self.WHITE,
                       padx=12, pady=8, width=16)

        tk.Button(sidebar, text="＋  Add Contact",
                  command=self._open_add_dialog, **btn_cfg).pack(pady=(20, 6), padx=14)

        btn_cfg2 = dict(bg=self.SIDEBAR, fg="#74C69D", font=("Arial", 9),
                        relief="flat", bd=0, cursor="hand2",
                        activebackground=self.ACCENT, activeforeground=self.WHITE,
                        padx=12, pady=6, width=16)

        tk.Button(sidebar, text="✏️  Edit Selected",
                  command=self._open_edit_dialog, **btn_cfg2).pack(pady=2, padx=14)
        tk.Button(sidebar, text="🗑  Delete Selected",
                  command=self._delete_contact, **btn_cfg2).pack(pady=2, padx=14)

        self.count_var = tk.StringVar(value="0 contacts")
        tk.Label(sidebar, textvariable=self.count_var, font=("Arial", 8),
                 bg=self.SIDEBAR, fg="#74C69D").pack(side="bottom", pady=14)

        # ── Right content area ───────────────────────────────────────────
        right = tk.Frame(self.root, bg=self.BG)
        right.pack(side="left", fill="both", expand=True)

        # Search bar
        search_frame = tk.Frame(right, bg=self.BG)
        search_frame.pack(fill="x", padx=20, pady=(18, 10))

        tk.Label(search_frame, text="🔍", font=("Arial", 13),
                 bg=self.BG, fg=self.MUTED).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._do_search())

        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                font=("Arial", 11), relief="flat",
                                bg=self.WHITE, fg=self.TEXT,
                                insertbackground=self.TEXT)
        search_entry.pack(side="left", fill="x", expand=True, ipady=6, padx=8)
        search_entry.insert(0, "")
        search_entry.bind("<FocusIn>",  lambda e: search_entry.config(highlightthickness=2,
                                                                       highlightbackground=self.ACCENT_LT))
        search_entry.bind("<FocusOut>", lambda e: search_entry.config(highlightthickness=0))

        # Contact list (Treeview)
        list_frame = tk.Frame(right, bg=self.BG)
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 8))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("CB.Treeview",
                         background=self.WHITE,
                         fieldbackground=self.WHITE,
                         foreground=self.TEXT,
                         rowheight=36,
                         font=("Arial", 10),
                         borderwidth=0)
        style.configure("CB.Treeview.Heading",
                         background=self.ACCENT,
                         foreground=self.WHITE,
                         font=("Arial", 10, "bold"),
                         relief="flat")
        style.map("CB.Treeview",
                  background=[("selected", self.ACCENT_LT)],
                  foreground=[("selected", self.WHITE)])

        cols = ("name", "phone", "email", "address")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings",
                                  style="CB.Treeview", selectmode="browse")

        for col, heading, width in [
            ("name",    "Name",    180),
            ("phone",   "Phone",   130),
            ("email",   "Email",   200),
            ("address", "Address", 220),
        ]:
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>",         lambda e: self._open_edit_dialog())

        # Detail panel
        self.detail_frame = tk.Frame(right, bg=self.WHITE,
                                      highlightbackground=self.BORDER, highlightthickness=1)
        self.detail_frame.pack(fill="x", padx=20, pady=(0, 16))
        self._build_detail_panel()

    def _build_detail_panel(self):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        tk.Label(self.detail_frame, text="Select a contact to view details",
                 font=("Arial", 9), bg=self.WHITE, fg=self.MUTED,
                 pady=10).pack()

    def _show_detail(self, contact):
        for w in self.detail_frame.winfo_children():
            w.destroy()

        fields = [("👤 Name",    contact["name"]),
                  ("📞 Phone",   contact["phone"]),
                  ("✉️ Email",   contact["email"]),
                  ("🏠 Address", contact["address"])]

        row = tk.Frame(self.detail_frame, bg=self.WHITE)
        row.pack(fill="x", padx=16, pady=8)
        for label, value in fields:
            col = tk.Frame(row, bg=self.WHITE)
            col.pack(side="left", padx=12, anchor="w")
            tk.Label(col, text=label, font=("Arial", 8), bg=self.WHITE,
                     fg=self.MUTED).pack(anchor="w")
            tk.Label(col, text=value or "—", font=("Arial", 10, "bold"),
                     bg=self.WHITE, fg=self.TEXT, wraplength=180).pack(anchor="w")

    # ── Data / list helpers ───────────────────────────────────────────────

    def _refresh_list(self, query=""):
        q = query.strip().lower()
        self.filtered = [c for c in self.contacts
                         if q in c["name"].lower() or q in c["phone"].lower()]
        self.filtered.sort(key=lambda c: c["name"].lower())

        self.tree.delete(*self.tree.get_children())
        for c in self.filtered:
            self.tree.insert("", "end",
                             values=(c["name"], c["phone"], c["email"], c["address"]))

        total = len(self.contacts)
        self.count_var.set(f"{total} contact{'s' if total != 1 else ''}")
        self.selected_index = None
        self._build_detail_panel()

    def _do_search(self):
        self._refresh_list(self.search_var.get())

    def _on_select(self, _event=None):
        sel = self.tree.selection()
        if not sel:
            self.selected_index = None
            return
        idx = self.tree.index(sel[0])
        self.selected_index = idx
        self._show_detail(self.filtered[idx])

    def _get_selected_contact(self):
        if self.selected_index is None:
            messagebox.showwarning("No selection", "Please select a contact first.")
            return None, None
        contact = self.filtered[self.selected_index]
        real_idx = self.contacts.index(contact)
        return contact, real_idx

    # ── Dialogs ───────────────────────────────────────────────────────────

    def _open_add_dialog(self):
        self._contact_dialog(title="Add Contact")

    def _open_edit_dialog(self):
        contact, _ = self._get_selected_contact()
        if contact:
            self._contact_dialog(title="Edit Contact", contact=contact)

    def _contact_dialog(self, title, contact=None):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        dlg.geometry("420x320")
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

        fields = [("Full Name *", "name"), ("Phone Number *", "phone"),
                  ("Email Address", "email"), ("Address", "address")]
        entries = {}

        for i, (label, key) in enumerate(fields):
            tk.Label(body, text=label, font=("Arial", 9), bg=self.BG,
                     fg=self.MUTED).grid(row=i, column=0, sticky="w", pady=(6, 0))
            e = tk.Entry(body, font=("Arial", 10), relief="solid",
                         bg=self.WHITE, fg=self.TEXT, bd=1, width=32)
            e.grid(row=i, column=1, sticky="ew", padx=(10, 0), pady=(6, 0), ipady=4)
            if contact:
                e.insert(0, contact.get(key, ""))
            entries[key] = e
        body.columnconfigure(1, weight=1)

        # Buttons
        btn_row = tk.Frame(body, bg=self.BG)
        btn_row.grid(row=len(fields), column=0, columnspan=2, pady=(18, 0), sticky="e")

        def save():
            name  = entries["name"].get().strip()
            phone = entries["phone"].get().strip()
            if not name or not phone:
                messagebox.showerror("Required", "Name and Phone are required.", parent=dlg)
                return
            data = {k: entries[k].get().strip() for k in ("name","phone","email","address")}
            if contact:
                _, real_idx = self._get_selected_contact()
                self.contacts[real_idx] = data
            else:
                self.contacts.append(data)
            save_contacts(self.contacts)
            self._refresh_list(self.search_var.get())
            dlg.destroy()

        tk.Button(btn_row, text="Cancel", command=dlg.destroy,
                  bg=self.BORDER, fg=self.TEXT, relief="flat", font=("Arial", 9),
                  padx=14, pady=6, cursor="hand2").pack(side="left", padx=(0, 8))
        tk.Button(btn_row, text="Save Contact", command=save,
                  bg=self.ACCENT, fg=self.WHITE, relief="flat", font=("Arial", 9, "bold"),
                  padx=14, pady=6, cursor="hand2",
                  activebackground=self.ACCENT_LT, activeforeground=self.WHITE).pack(side="left")

        entries["name"].focus_set()
        dlg.bind("<Return>", lambda e: save())
        dlg.bind("<Escape>", lambda e: dlg.destroy())

    def _delete_contact(self):
        contact, real_idx = self._get_selected_contact()
        if contact is None:
            return
        if messagebox.askyesno("Delete Contact",
                               f"Delete '{contact['name']}'?\nThis cannot be undone.",
                               icon="warning"):
            self.contacts.pop(real_idx)
            save_contacts(self.contacts)
            self._refresh_list(self.search_var.get())


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = ContactBookApp(root)
    root.mainloop()
