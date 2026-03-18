import base64
import json
import os
import tkinter as tk
from dataclasses import dataclass
from tkinter import filedialog, messagebox, simpledialog

try:
    from cryptography.fernet import Fernet, InvalidToken
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except Exception:  
    Fernet = None
    InvalidToken = Exception
    PBKDF2HMAC = None
    hashes = None


APP_TITLE = "Simple Password Vault"
DEFAULT_VAULT_NAME = "vault.sec"
KDF_ITERATIONS = 200_000
SALT_BYTES = 16


@dataclass
class EntryItem:
    email: str
    password: str


def _require_crypto():
    if Fernet is None or PBKDF2HMAC is None:
        raise RuntimeError(
            "Missing dependency: install 'cryptography' (pip install cryptography)."
        )


def _derive_key(master_password: str, salt: bytes) -> bytes:
    _require_crypto()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=KDF_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))


def encrypt_entries(entries: list[EntryItem], master_password: str) -> dict:
    _require_crypto()
    salt = os.urandom(SALT_BYTES)
    key = _derive_key(master_password, salt)
    fernet = Fernet(key)
    payload = json.dumps(
        [entry.__dict__ for entry in entries], ensure_ascii=True
    ).encode("utf-8")
    token = fernet.encrypt(payload)
    return {
        "salt": base64.b64encode(salt).decode("ascii"),
        "data": token.decode("ascii"),
    }


def decrypt_entries(blob: dict, master_password: str) -> list[EntryItem]:
    _require_crypto()
    salt = base64.b64decode(blob["salt"].encode("ascii"))
    key = _derive_key(master_password, salt)
    fernet = Fernet(key)
    payload = fernet.decrypt(blob["data"].encode("ascii"))
    raw_entries = json.loads(payload.decode("utf-8"))
    return [EntryItem(**item) for item in raw_entries]


class VaultApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("700x420")
        self.entries: list[EntryItem] = []
        self.master_password: str | None = None
        self.current_path: str | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        menu = tk.Menu(self.root)
        file_menu = tk.Menu(menu, tearoff=False)
        file_menu.add_command(label="New Vault", command=self.new_vault)
        file_menu.add_command(label="Open Vault", command=self.open_vault)
        file_menu.add_command(label="Save Vault", command=self.save_vault)
        file_menu.add_separator()
        file_menu.add_command(label="Import TXT", command=self.import_txt)
        file_menu.add_command(label="Export TXT", command=self.export_txt)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu.add_cascade(label="File", menu=file_menu)
        self.root.config(menu=menu)

        main = tk.Frame(self.root, padx=10, pady=10)
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right = tk.Frame(main)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(left, height=18)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox.bind("<<ListboxSelect>>", self.on_select)

        scrollbar = tk.Scrollbar(left, command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        form = tk.LabelFrame(right, text="Details", padx=8, pady=8)
        form.pack(fill=tk.X)

        tk.Label(form, text="Email").grid(row=0, column=0, sticky="w")
        self.email_var = tk.StringVar()
        tk.Entry(form, textvariable=self.email_var, width=28).grid(
            row=1, column=0, padx=(0, 10), pady=(0, 8)
        )

        tk.Label(form, text="Password").grid(row=2, column=0, sticky="w")
        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            form, textvariable=self.password_var, width=28, show="*"
        )
        self.password_entry.grid(row=3, column=0, padx=(0, 10))

        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            form,
            text="Show",
            variable=self.show_var,
            command=self.toggle_show,
        ).grid(row=4, column=0, sticky="w", pady=(4, 8))

        buttons = tk.Frame(right)
        buttons.pack(fill=tk.X, pady=(12, 0))

        tk.Button(buttons, text="Add", width=14, command=self.add_entry).pack(
            pady=2
        )
        tk.Button(
            buttons, text="Update", width=14, command=self.update_entry
        ).pack(pady=2)
        tk.Button(
            buttons, text="Delete", width=14, command=self.delete_entry
        ).pack(pady=2)
        tk.Button(buttons, text="Clear", width=14, command=self.clear_form).pack(
            pady=2
        )

        self.status_var = tk.StringVar(value="Ready")
        status = tk.Label(self.root, textvariable=self.status_var, anchor="w")
        status.pack(fill=tk.X, side=tk.BOTTOM)

    def set_status(self, message: str) -> None:
        self.status_var.set(message)

    def toggle_show(self) -> None:
        self.password_entry.config(show="" if self.show_var.get() else "*")

    def refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for entry in self.entries:
            self.listbox.insert(tk.END, entry.email)

    def clear_form(self) -> None:
        self.email_var.set("")
        self.password_var.set("")
        self.listbox.selection_clear(0, tk.END)

    def on_select(self, _event: object) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        entry = self.entries[index]
        self.email_var.set(entry.email)
        self.password_var.set(entry.password)

    def add_entry(self) -> None:
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        if not email or not password:
            messagebox.showwarning(APP_TITLE, "Email and password are required.")
            return
        self.entries.append(EntryItem(email=email, password=password))
        self.refresh_list()
        self.clear_form()
        self.set_status("Entry added.")

    def update_entry(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning(APP_TITLE, "Select an entry to update.")
            return
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()
        if not email or not password:
            messagebox.showwarning(APP_TITLE, "Email and password are required.")
            return
        index = selection[0]
        self.entries[index] = EntryItem(email=email, password=password)
        self.refresh_list()
        self.set_status("Entry updated.")

    def delete_entry(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning(APP_TITLE, "Select an entry to delete.")
            return
        index = selection[0]
        del self.entries[index]
        self.refresh_list()
        self.clear_form()
        self.set_status("Entry deleted.")

    def prompt_master_password(self, prompt: str) -> str | None:
        return simpledialog.askstring(APP_TITLE, prompt, show="*")
    
    def new_vault(self) -> None:
        try:
            _require_crypto()
        except RuntimeError as exc:
            messagebox.showerror(APP_TITLE, str(exc))
            return
        master = self.prompt_master_password("Set a master password:")
        if not master:
            return
        confirm = self.prompt_master_password("Confirm master password:")
        if master != confirm:
            messagebox.showerror(APP_TITLE, "Passwords do not match.")
            return
        self.master_password = master
        self.entries = []
        self.current_path = None
        self.refresh_list()
        self.clear_form()
        self.set_status("New vault created. Remember to save.")

    def open_vault(self) -> None:
        path = filedialog.askopenfilename(
            title="Open Vault",
            filetypes=[("Secure vault", "*.sec"), ("All files", "*.*")],
        )
        if not path:
            return
        master = self.prompt_master_password("Enter master password:")
        if not master:
            return
        try:
            with open(path, "r", encoding="utf-8") as handle:
                blob = json.load(handle)
            self.entries = decrypt_entries(blob, master)
        except InvalidToken:
            messagebox.showerror(APP_TITLE, "Wrong master password.")
            return
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Failed to open vault: {exc}")
            return
        self.master_password = master
        self.current_path = path
        self.refresh_list()
        self.clear_form()
        self.set_status(f"Vault opened: {os.path.basename(path)}")

    def save_vault(self) -> None:
        if self.master_password is None:
            messagebox.showwarning(APP_TITLE, "Create or open a vault first.")
            return
        path = self.current_path
        if not path:
            path = filedialog.asksaveasfilename(
                title="Save Vault",
                defaultextension=".sec",
                initialfile=DEFAULT_VAULT_NAME,
                filetypes=[("Secure vault", "*.sec"), ("All files", "*.*")],
            )
        if not path:
            return
        try:
            blob = encrypt_entries(self.entries, self.master_password)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(blob, handle, ensure_ascii=True, indent=2)
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Failed to save vault: {exc}")
            return
        self.current_path = path
        self.set_status(f"Vault saved: {os.path.basename(path)}")

    def import_txt(self) -> None:
        path = filedialog.askopenfilename(
            title="Import TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            imported: list[EntryItem] = []
            with open(path, "r", encoding="utf-8") as handle:
                for line in handle:
                    clean = line.strip()
                    if not clean or clean.startswith("#"):
                        continue
                    if ":" not in clean:
                        raise ValueError("Each line must be: email:password")
                    email, password = clean.split(":", 1)
                    imported.append(
                        EntryItem(email=email.strip(), password=password.strip())
                    )
            if not imported:
                messagebox.showinfo(APP_TITLE, "No entries found.")
                return
            self.entries.extend(imported)
            self.refresh_list()
            self.set_status(f"Imported {len(imported)} entries.")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Import failed: {exc}")

    def export_txt(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Export TXT",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as handle:
                for entry in self.entries:
                    handle.write(f"{entry.email}:{entry.password}\n")
            self.set_status(f"Exported {len(self.entries)} entries.")
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"Export failed: {exc}")


def main() -> None:
    root = tk.Tk()
    app = VaultApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()