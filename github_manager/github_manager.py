import json
import subprocess
import threading
import tkinter as tk
from datetime import datetime, timedelta, timezone
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText
from urllib import error, parse, request


API_BASE = "https://api.github.com"


class GitHubManagerApp(tk.Tk):
	def __init__(self):
		super().__init__()
		self.title("GitHub Account Manager")
		self.geometry("1100x760")
		self.minsize(920, 620)

		self.username_var = tk.StringVar()
		self.token_var = tk.StringVar()
		self.repo_path_var = tk.StringVar()
		self.commit_message_var = tk.StringVar()
		self.account_state_var = tk.StringVar(value="Account state: not loaded")

		self._build_ui()

	def _build_ui(self):
		main = ttk.Frame(self, padding=12)
		main.pack(fill=tk.BOTH, expand=True)

		github_frame = ttk.LabelFrame(main, text="GitHub Account", padding=10)
		github_frame.pack(fill=tk.X)

		ttk.Label(github_frame, text="Username:").grid(row=0, column=0, sticky="w")
		ttk.Entry(github_frame, textvariable=self.username_var, width=28).grid(
			row=0, column=1, padx=6, sticky="w"
		)

		ttk.Label(github_frame, text="Token (optional):").grid(
			row=0, column=2, sticky="w", padx=(14, 0)
		)
		ttk.Entry(github_frame, textvariable=self.token_var, show="*", width=40).grid(
			row=0, column=3, padx=6, sticky="we"
		)

		ttk.Button(github_frame, text="Load Account + Repos", command=self.on_load_account).grid(
			row=0, column=4, padx=(8, 0), sticky="e"
		)

		github_frame.columnconfigure(3, weight=1)

		ttk.Label(main, textvariable=self.account_state_var).pack(fill=tk.X, pady=(8, 6))

		repos_frame = ttk.LabelFrame(main, text="Repositories", padding=8)
		repos_frame.pack(fill=tk.BOTH, expand=True)

		columns = ("name", "private", "updated", "pushed", "activity")
		self.repos_tree = ttk.Treeview(
			repos_frame,
			columns=columns,
			show="headings",
			height=14,
		)
		self.repos_tree.heading("name", text="Repository")
		self.repos_tree.heading("private", text="Private")
		self.repos_tree.heading("updated", text="Updated At")
		self.repos_tree.heading("pushed", text="Last Push")
		self.repos_tree.heading("activity", text="Update State")

		self.repos_tree.column("name", width=280, anchor="w")
		self.repos_tree.column("private", width=80, anchor="center")
		self.repos_tree.column("updated", width=180, anchor="center")
		self.repos_tree.column("pushed", width=180, anchor="center")
		self.repos_tree.column("activity", width=160, anchor="center")

		yscroll = ttk.Scrollbar(repos_frame, orient=tk.VERTICAL, command=self.repos_tree.yview)
		self.repos_tree.configure(yscrollcommand=yscroll.set)
		self.repos_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		yscroll.pack(side=tk.RIGHT, fill=tk.Y)

		local_git_frame = ttk.LabelFrame(main, text="Local Git Actions", padding=10)
		local_git_frame.pack(fill=tk.X, pady=(10, 0))

		ttk.Label(local_git_frame, text="Local repository path:").grid(
			row=0, column=0, sticky="w"
		)
		ttk.Entry(local_git_frame, textvariable=self.repo_path_var).grid(
			row=0, column=1, sticky="we", padx=6
		)
		ttk.Button(local_git_frame, text="Browse", command=self.on_browse_repo).grid(
			row=0, column=2, padx=(0, 8)
		)

		ttk.Button(local_git_frame, text="Status", command=self.on_git_status).grid(row=0, column=3)
		ttk.Button(local_git_frame, text="Add All", command=self.on_git_add).grid(
			row=0, column=4, padx=6
		)
		ttk.Button(local_git_frame, text="Push", command=self.on_git_push).grid(
			row=0, column=5, padx=6
		)
		ttk.Button(local_git_frame, text="Pull", command=self.on_git_pull).grid(row=0, column=6)

		ttk.Label(local_git_frame, text="Commit message:").grid(
			row=1, column=0, sticky="w", pady=(8, 0)
		)
		ttk.Entry(local_git_frame, textvariable=self.commit_message_var).grid(
			row=1, column=1, sticky="we", padx=6, pady=(8, 0)
		)
		ttk.Button(local_git_frame, text="Commit", command=self.on_git_commit).grid(
			row=1, column=2, pady=(8, 0)
		)

		local_git_frame.columnconfigure(1, weight=1)

		log_frame = ttk.LabelFrame(main, text="Logs", padding=8)
		log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

		self.log_text = ScrolledText(log_frame, height=12, wrap=tk.WORD)
		self.log_text.pack(fill=tk.BOTH, expand=True)
		self.log("Application started.")

	def log(self, message: str):
		stamp = datetime.now().strftime("%H:%M:%S")
		self.log_text.insert(tk.END, f"[{stamp}] {message}\n")
		self.log_text.see(tk.END)

	def on_browse_repo(self):
		path = filedialog.askdirectory(title="Select local git repository")
		if path:
			self.repo_path_var.set(path)

	def on_load_account(self):
		username = self.username_var.get().strip()
		token = self.token_var.get().strip()

		if not username and not token:
			messagebox.showerror("Missing info", "Enter a username or a token.")
			return

		self.log("Loading account and repositories from GitHub...")
		self._run_in_thread(self._load_account_worker, username, token)

	def _run_in_thread(self, func, *args):
		threading.Thread(target=func, args=args, daemon=True).start()

	def _headers(self, token: str):
		headers = {
			"Accept": "application/vnd.github+json",
			"User-Agent": "github-manager-app",
		}
		if token:
			headers["Authorization"] = f"Bearer {token}"
		return headers

	def _fetch_json(self, url: str, token: str):
		req = request.Request(url, headers=self._headers(token))
		with request.urlopen(req, timeout=20) as response:
			return json.loads(response.read().decode("utf-8"))

	def _load_account_worker(self, username: str, token: str):
		try:
			effective_username = username

			if token and not username:
				me = self._fetch_json(f"{API_BASE}/user", token)
				effective_username = me.get("login", "")
				account = me
				repos_url = (
					f"{API_BASE}/user/repos?per_page=100&sort=updated&direction=desc"
				)
				repos = self._fetch_json(repos_url, token)
			else:
				account = self._fetch_json(f"{API_BASE}/users/{parse.quote(username)}", token)
				repos_url = (
					f"{API_BASE}/users/{parse.quote(username)}/repos"
					"?per_page=100&sort=updated&direction=desc"
				)
				repos = self._fetch_json(repos_url, token)

			self.after(0, lambda: self._update_account_ui(account, repos, effective_username))
		except error.HTTPError as exc:
			msg = f"GitHub API error: HTTP {exc.code}."
			if exc.code == 401:
				msg += " Token is invalid or expired."
			elif exc.code == 404:
				msg += " User not found."
			self.after(0, lambda: self.log(msg))
			self.after(0, lambda: messagebox.showerror("GitHub error", msg))
		except Exception as exc:  # broad catch to keep UI responsive
			msg = f"Unexpected error while loading GitHub data: {exc}"
			self.after(0, lambda: self.log(msg))
			self.after(0, lambda: messagebox.showerror("Error", msg))

	def _update_account_ui(self, account, repos, effective_username: str):
		name = account.get("name") or effective_username
		public_repos = account.get("public_repos", "?")
		followers = account.get("followers", "?")
		following = account.get("following", "?")
		self.account_state_var.set(
			f"Account: {name} (@{effective_username}) | Public repos: {public_repos}"
			f" | Followers: {followers} | Following: {following}"
		)

		for item in self.repos_tree.get_children():
			self.repos_tree.delete(item)

		recent_threshold = datetime.now(timezone.utc) - timedelta(days=7)

		for repo in repos:
			updated_raw = repo.get("updated_at")
			pushed_raw = repo.get("pushed_at")
			updated_display = self._format_github_datetime(updated_raw)
			pushed_display = self._format_github_datetime(pushed_raw)
			updated_dt = self._parse_github_datetime(updated_raw)

			state = "Recently updated" if updated_dt and updated_dt >= recent_threshold else "Stable"
			self.repos_tree.insert(
				"",
				tk.END,
				values=(
					repo.get("name", "-"),
					"Yes" if repo.get("private") else "No",
					updated_display,
					pushed_display,
					state,
				),
			)

		self.log(f"Loaded {len(repos)} repositories for @{effective_username}.")

	@staticmethod
	def _parse_github_datetime(value):
		if not value:
			return None
		try:
			return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
		except ValueError:
			return None

	def _format_github_datetime(self, value):
		dt = self._parse_github_datetime(value)
		if not dt:
			return "-"
		local_dt = dt.astimezone()
		return local_dt.strftime("%Y-%m-%d %H:%M")

	def _validate_repo_path(self):
		repo_path = self.repo_path_var.get().strip()
		if not repo_path:
			messagebox.showerror("Missing path", "Choose a local repository path.")
			return None

		result = subprocess.run(
			["git", "-C", repo_path, "rev-parse", "--is-inside-work-tree"],
			capture_output=True,
			text=True,
		)
		if result.returncode != 0:
			messagebox.showerror(
				"Invalid repository",
				"Selected folder is not a git repository.",
			)
			return None
		return repo_path

	def _run_git(self, git_args, success_label):
		repo_path = self._validate_repo_path()
		if not repo_path:
			return

		self.log(f"Running: git {' '.join(git_args)}")

		def worker():
			try:
				result = subprocess.run(
					["git", "-C", repo_path, *git_args],
					capture_output=True,
					text=True,
				)
				output = (result.stdout or "") + (result.stderr or "")

				if result.returncode == 0:
					self.after(0, lambda: self.log(f"{success_label} succeeded."))
				else:
					self.after(0, lambda: self.log(f"{success_label} failed (code {result.returncode})."))

				if output.strip():
					self.after(0, lambda: self.log(output.strip()))
			except Exception as exc:  # broad catch to keep UI responsive
				self.after(0, lambda: self.log(f"Git action failed: {exc}"))

		self._run_in_thread(worker)

	def on_git_status(self):
		self._run_git(["status", "-sb"], "Git status")

	def on_git_add(self):
		self._run_git(["add", "."], "Git add")

	def on_git_commit(self):
		message = self.commit_message_var.get().strip()
		if not message:
			messagebox.showerror("Missing commit message", "Enter a commit message.")
			return
		self._run_git(["commit", "-m", message], "Git commit")

	def on_git_push(self):
		self._run_git(["push"], "Git push")

	def on_git_pull(self):
		self._run_git(["pull"], "Git pull")


if __name__ == "__main__":
	app = GitHubManagerApp()
	app.mainloop()
