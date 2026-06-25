import tkinter as tk
from tkinter import filedialog, messagebox
import os, shutil, random

# Palette
BG       = "#faf8f5"
SURFACE  = "#f0ece6"
BORDER   = "#ddd5c8"
ACCENT   = "#cc3d00"
ACCENTHO = "#a83200"
TEXT     = "#1e1610"
MUTED    = "#6e5f52"
SUCCESS  = "#2e7d32"

FONT    = ("Segoe UI", 10)
FONT_B  = ("Segoe UI", 10, "bold")
FONT_T  = ("Segoe UI", 20, "bold")
FONT_SM = ("Segoe UI", 9)

CLOTHING_CATS = ["Belt","Ear","Eye","Face","Hair","Hat","Legs","Neck","Shirt","Shoes","Shoulder","Wrist"]
PROP_CATS     = ["Decoration","Toys","Weapons"]
ITEM_TYPES    = ["Clothing Item", "Prop", "Map", "NPC"]

PATHS = {
    "Clothing Item": ("RecRoom-Avatar-Archive", "Items"),
    "Prop":          ("RecRoom-Avatar-Archive", "Props"),
    "Map":           ("RecRoom-World-Archive",  "Maps"),
    "NPC":           ("RecRoom-World-Archive",  "NPCs"),
}

# Widget helpers

def make_btn(parent, text, cmd, primary=False, fullwidth=False):
    bg = ACCENT if primary else SURFACE
    fg = "#ffffff" if primary else TEXT
    hv = ACCENTHO if primary else BORDER
    b  = tk.Button(
        parent, text=text, command=cmd,
        bg=bg, fg=fg, activebackground=hv, activeforeground="#fff" if primary else TEXT,
        font=FONT_B if primary else FONT,
        relief="flat", bd=0, cursor="hand2",
        padx=20, pady=10 if primary else 7,
    )
    if fullwidth:
        b.pack(fill="x")
    b.bind("<Enter>", lambda e: b.config(bg=hv))
    b.bind("<Leave>", lambda e: b.config(bg=bg))
    return b

def make_entry(parent, var, **kw):
    return tk.Entry(
        parent, textvariable=var,
        bg=SURFACE, fg=TEXT, insertbackground=TEXT,
        relief="flat", font=FONT, bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        **kw
    )

def section_label(parent, text):
    f = tk.Frame(parent, bg=BG)
    tk.Label(f, text=text, bg=BG, fg=ACCENT, font=FONT_B).pack(side="left")
    tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=(8,0), pady=5)
    return f

# App

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("RR Archive Organizer")
        self.configure(bg=BG)
        self.minsize(520, 640)
        self.geometry("580x720")
        self.resizable(True, True)

        self.github_root = tk.StringVar()
        self.item_type   = tk.StringVar(value=ITEM_TYPES[0])
        self.sub_cat     = tk.StringVar(value=CLOTHING_CATS[0])
        self.item_name   = tk.StringVar()
        self.images      = []

        self._build()

    def _build(self):
        self._status = tk.Label(
            self, text="Ready.", bg=SURFACE, fg=MUTED,
            font=FONT_SM, anchor="w", padx=14, pady=7, relief="flat"
        )
        self._status.pack(fill="x", side="bottom")

        self._canvas = tk.Canvas(self, bg=BG, bd=0, highlightthickness=0)
        self._sb     = tk.Scrollbar(self, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._sb.set)
        self._sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas, bg=BG)
        self._win_id = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")

        self._inner.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        P = {"padx": 28}

        tk.Frame(self._inner, bg=ACCENT, height=6).pack(fill="x")
        tk.Frame(self._inner, bg=BG, height=20).pack()
        tk.Label(self._inner, text="RR Archive Organizer",
                 bg=BG, fg=ACCENT, font=FONT_T).pack(**P, anchor="w")
        tk.Label(self._inner, text="Organise assets into your local GitHub clone",
                 bg=BG, fg=MUTED, font=FONT_SM).pack(**P, anchor="w")
        tk.Frame(self._inner, bg=BG, height=10).pack()


        section_label(self._inner, "GitHub Folder").pack(fill="x", **P, pady=(10, 4))
        gh_frm = tk.Frame(self._inner, bg=BG)
        gh_frm.pack(fill="x", **P, pady=(0, 4))
        tk.Label(gh_frm, text="Parent folder that contains your repo folders",
                 bg=BG, fg=MUTED, font=FONT_SM).pack(anchor="w")
        tk.Label(gh_frm, text="e.g.  C:\\Users\\You\\Documents\\GitHub",
                 bg=BG, fg=MUTED, font=FONT_SM).pack(anchor="w")
        tk.Frame(gh_frm, bg=BG, height=6).pack()
        row = tk.Frame(gh_frm, bg=BG)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        make_entry(row, self.github_root).grid(row=0, column=0, sticky="ew", ipady=8)
        tk.Frame(row, bg=BG, width=8).grid(row=0, column=1)
        make_btn(row, "Browse…", self._browse_github).grid(row=0, column=2)


        section_label(self._inner, "Asset Type").pack(fill="x", **P, pady=(14, 6))
        type_frm = tk.Frame(self._inner, bg=BG)
        type_frm.pack(fill="x", **P)
        for t in ITEM_TYPES:
            tk.Radiobutton(
                type_frm, text=t, variable=self.item_type, value=t,
                command=self._update_cats,
                bg=BG, fg=TEXT, selectcolor=SURFACE,
                activebackground=BG, activeforeground=ACCENT,
                font=FONT, cursor="hand2", relief="flat"
            ).pack(side="left", padx=(0, 18))

        # Category
        section_label(self._inner, "Category").pack(fill="x", **P, pady=(14, 6))
        self._cat_block = tk.Frame(self._inner, bg=BG, height=96)
        self._cat_block.pack(fill="x", **P)
        self._cat_block.pack_propagate(False)
        self._cat_inner = tk.Frame(self._cat_block, bg=BG)
        self._cat_inner.pack(anchor="w")

        # Item name
        section_label(self._inner, "Item / Folder Name").pack(fill="x", **P, pady=(14, 6))
        name_frm = tk.Frame(self._inner, bg=BG)
        name_frm.pack(fill="x", **P)
        make_entry(name_frm, self.item_name).pack(fill="x", ipady=8)

        # Images
        section_label(self._inner, "Images (PNG)").pack(fill="x", **P, pady=(14, 6))
        img_frm = tk.Frame(self._inner, bg=BG)
        img_frm.pack(fill="x", **P)

        btn_row = tk.Frame(img_frm, bg=BG)
        btn_row.pack(fill="x", pady=(0, 6))
        make_btn(btn_row, "+ Add Images", self._pick_images).pack(side="left")
        make_btn(btn_row, "Clear", self._clear_images).pack(side="left", padx=(8, 0))
        self._img_count = tk.Label(btn_row, text="0 selected",
                                   bg=BG, fg=MUTED, font=FONT_SM)
        self._img_count.pack(side="right", anchor="e")

        list_wrap = tk.Frame(img_frm, bg=SURFACE,
                             highlightthickness=1, highlightbackground=BORDER)
        list_wrap.pack(fill="x")
        sb2 = tk.Scrollbar(list_wrap, relief="flat", bg=BORDER, troughcolor=SURFACE)
        sb2.pack(side="right", fill="y")
        self._listbox = tk.Listbox(
            list_wrap, bg=SURFACE, fg=TEXT, font=("Consolas", 9),
            selectbackground=ACCENT, selectforeground="#fff",
            relief="flat", bd=0, activestyle="none",
            yscrollcommand=sb2.set, height=7
        )
        self._listbox.pack(fill="both", expand=True)
        sb2.config(command=self._listbox.yview)


        tk.Frame(self._inner, bg=BG, height=18).pack()
        btn_wrap = tk.Frame(self._inner, bg=BG)
        btn_wrap.pack(fill="x", padx=28, pady=(0, 28))
        big = make_btn(btn_wrap, "▶   Organise Files", self._organise, primary=True, fullwidth=True)
        big.config(font=("Segoe UI", 12, "bold"), pady=14)

        self._update_cats()



    def _on_frame_configure(self, e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, e):
        self._canvas.itemconfig(self._win_id, width=e.width)

    def _on_mousewheel(self, e):
        self._canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")



    def _update_cats(self):
        for w in self._cat_inner.winfo_children():
            w.destroy()
        t    = self.item_type.get()
        cats = CLOTHING_CATS if t == "Clothing Item" else PROP_CATS if t == "Prop" else None
        if cats:
            self.sub_cat.set(cats[0])
            for i, c in enumerate(cats):
                tk.Radiobutton(
                    self._cat_inner, text=c, variable=self.sub_cat, value=c,
                    bg=BG, fg=TEXT, selectcolor=SURFACE,
                    activebackground=BG, activeforeground=ACCENT,
                    font=FONT, cursor="hand2", relief="flat"
                ).grid(row=i // 4, column=i % 4, sticky="w", padx=(0, 18), pady=2)
        else:
            tk.Label(self._cat_inner, text="No category for this asset type.",
                     bg=BG, fg=MUTED, font=FONT).grid(row=0, column=0, sticky="w")

    # Actions

    def _browse_github(self):
        d = filedialog.askdirectory(title="Select your GitHub folder")
        if d:
            self.github_root.set(d)
            self._set_status(f"GitHub root: {d}")

    def _pick_images(self):
        files = filedialog.askopenfilenames(
            title="Select PNG image(s)",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        for f in files:
            if f not in self.images:
                self.images.append(f)
        self._refresh_list()

    def _clear_images(self):
        self.images.clear()
        self._refresh_list()

    def _refresh_list(self):
        self._listbox.delete(0, "end")
        for p in self.images:
            self._listbox.insert("end", os.path.basename(p))
        n = len(self.images)
        self._img_count.config(text=f"{n} image{'s' if n != 1 else ''} selected")

    def _organise(self):
        gh   = self.github_root.get().strip()
        name = self.item_name.get().strip()
        t    = self.item_type.get()

        if not gh:
            messagebox.showwarning("Missing info", "Please set your GitHub folder path."); return
        if not name:
            messagebox.showwarning("Missing info", "Please enter a name for this item."); return
        if not self.images:
            messagebox.showwarning("Missing info", "Please add at least one image."); return

        repo_name, sub_dir = PATHS[t]
        dest = os.path.join(gh, repo_name, sub_dir,
                            *(([self.sub_cat.get()]) if t in ("Clothing Item","Prop") else []),
                            name)

        if not os.path.isdir(os.path.join(gh, repo_name)):
            if not messagebox.askyesno("Repo not found",
                f"Folder not found:\n  {os.path.join(gh, repo_name)}\n\nCreate it anyway?"):
                return

        if os.path.exists(dest):
            if not messagebox.askyesno("Folder exists",
                f'"{dest}" already exists.\n\nOverwrite / merge files?'):
                return

        try:
            os.makedirs(dest, exist_ok=True)
            if len(self.images) == 1:
                shutil.copy2(self.images[0], dest)
                summary = f"Copied 1 image into:\n  {dest}"
            else:
                for img_path in self.images:
                    stem = os.path.splitext(os.path.basename(img_path))[0]
                    os.makedirs(os.path.join(dest, stem), exist_ok=True)
                    shutil.copy2(img_path, os.path.join(dest, stem))
                cover = random.choice(self.images)
                shutil.copy2(cover, os.path.join(dest, os.path.basename(cover)))
                summary = (f"Organised {len(self.images)} images into:\n  {dest}\n\n"
                           f"Cover: {os.path.basename(cover)}")

            self._set_status(f"✓ Done — {len(self.images)} image(s) organised.", success=True)
            messagebox.showinfo("Done!", summary)
            self.images.clear()
            self.item_name.set("")
            self._refresh_list()

        except Exception as ex:
            messagebox.showerror("Error", str(ex))
            self._set_status(f"✗ Error: {ex}")

    def _set_status(self, msg, success=False):
        self._status.config(text=msg, fg=SUCCESS if success else MUTED)


if __name__ == "__main__":
    App().mainloop()
