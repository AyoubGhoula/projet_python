# GitHub Account Manager (Mini Project)

## Description

This mini project is a desktop app made with Python and Tkinter.
It lets you view your GitHub account and repositories, and run local Git commands from one interface.

## Features

- Load GitHub account data with username and optional token
- Show repositories with:
	- Repository name
	- Private/Public status
	- Last update time
	- Last push time
	- Update state (Recently updated / Stable)
- Local Git actions from buttons:
	- `status`
	- `add .`
	- `commit -m "message"`
	- `push`
	- `pull`
- Log panel for API and command output

## Project File

- Main script: `github_manager.py`

## Requirements

- Python 3.9 or newer
- Git installed and available in PATH
- Internet connection for GitHub API requests

Optional:
- GitHub Personal Access Token for private repo access and better API rate limits

## Run

From the project root:

```bash
python github_manager/github_manager.py
```

Or from this folder:

```bash
python github_manager.py
```

## How to Use

1. Start the app.
2. In the **GitHub Account** section:
	 - Enter a username, or
	 - Enter a token (username can be empty when token is used).
3. Click **Load Account + Repos**.
4. In **Local Git Actions**:
	 - Select your local repository path
	 - Use Status, Add All, Commit, Push, Pull buttons
5. Read results in the **Logs** area.

## Notes

- Without token: only public data is available.
- With token: private repositories can be listed if permissions allow it.
- Push/Pull depends on local Git remote and authentication setup.

## Future Improvements

- Add clone repository action
- Add branch management (create/switch/delete)
- Add secure token saving
- Add filtering/search for repositories

## Author

- GitHub: https://github.com/AyoubGhoula
