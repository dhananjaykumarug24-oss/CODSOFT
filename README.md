# 🐍 Python GUI Projects — CodSoft Internship

A collection of Python desktop GUI applications built with `tkinter` as part of the **CodSoft Python Programming Internship**. All apps share a consistent dark-green design system and require **no external dependencies**.

---

## 📁 Projects

### Task 1 — To-Do List
> `todo_list.py`

A task management app to create, update, and track your to-do list.

**Features:**
- Add tasks with title, priority (High / Medium / Low), due date, and notes
- Quick-add bar at the bottom for fast entry
- Toggle tasks as done / undone (click button or press `Space`)
- Live search by task title
- Filter view: All / Active / Done
- Progress bar showing completion percentage
- Bulk-clear all completed tasks
- Data persisted to `todos.json`

---

### Task 3 — Password Generator
> `password_generator.py`

A secure random password generator with full control over length and complexity.

**Features:**
- Adjustable length slider (4–64 characters)
- Toggle character sets: Uppercase, Lowercase, Numbers, Symbols
- Option to exclude ambiguous characters (`0`, `O`, `l`, `1`, `I`)
- Real-time strength meter (Weak / Fair / Strong / Very Strong)
- One-click copy to clipboard
- History of last 10 generated passwords (double-click to reload)
- Auto-regenerates on any option change

---

### Task 5 — Contact Book
> `contact_book.py`

A full-featured contact manager to store and organise personal contacts.

**Features:**
- Store name, phone number, email, and address per contact
- Add, edit (double-click), and delete contacts
- Live search by name or phone number
- Detail panel shows full contact info on selection
- Data persisted to `contacts.json`

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x (tkinter is included in the standard library)
- No `pip install` required

### Run any app
```bash
python todo_list.py
python password_generator.py
python contact_book.py
```

### Data storage
The To-Do List and Contact Book apps automatically save data locally:
- `todos.json` — task data
- `contacts.json` — contact data

These files are created in the same directory as the script on first run.

---

## 🗂 Project Structure

```
.
├── todo_list.py          # Task 1 — To-Do List
├── password_generator.py # Task 3 — Password Generator
├── contact_book.py       # Task 5 — Contact Book
├── todos.json            # Auto-generated (To-Do data)
├── contacts.json         # Auto-generated (Contact data)
└── README.md
```

---

## 🎨 Design System

All three apps share a unified visual style:

| Token        | Value     | Usage                        |
|--------------|-----------|------------------------------|
| Sidebar      | `#1B4332` | Dark green sidebar           |
| Accent       | `#2D6A4F` | Buttons, headers             |
| Accent Light | `#40916C` | Hover states, highlights     |
| Background   | `#F7F8FA` | Main content area            |
| Text         | `#1A1A2E` | Primary text                 |
| Muted        | `#6B7280` | Labels, secondary text       |

---

## 🛠 Tech Stack

- **Language:** Python 3
- **GUI Framework:** tkinter (stdlib)
- **Data Storage:** JSON (local files)
- **No third-party libraries required**
