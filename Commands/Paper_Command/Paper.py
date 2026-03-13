import os
from .viewer import ProjectStreamViewer
from . import utils

class PaperCommand:
    def __init__(self, terminal=None, newpage=None, papers_root=None, window=(1024,768)):
        self.terminal = terminal
        self.newpage = newpage or (lambda: None)
        self.papers_root = papers_root or os.path.join(os.path.dirname(__file__), "papers")
        self.window = window

        # default: papers directory inside this command package
        self.papers_root = papers_root or os.path.join(os.path.dirname(__file__), "papers")
        self.filter_text = ""

    def run(self):
        while True:
            projects = utils.scan_projects(self.papers_root, self.filter_text)

            self._clear()
            print("=== Papers Hub ===")
            if self.filter_text:
                print(f"Filter: '{self.filter_text}'")
            print()

            if not os.path.isdir(self.papers_root):
                print("[paper] No papers directory found.")
                print(f"Create: {self.papers_root}")
                input("\nPress Enter...")
                return

            if not projects:
                print("[paper] No projects found.")
                print("Commands: r refresh | / filter | 'exit' to quit")
                c = input("> ").strip().lower()
                if c == "exit":
                    return
                if c == "/":
                    self.filter_text = input("filter> ").strip()
                continue

            for i, p in enumerate(projects, 1):
                print(f"{i:2d}. {p['title']}")

            print("\nEnter number to open | / filter | r refresh | 'exit' to quit")
            print()  # <-- extra blank line before prompt
            raw = input("> ").strip().lower()

            if raw == "exit":
                return
            if raw == "r":
                continue
            if raw == "/":
                self.filter_text = input("filter> ").strip()
                continue
            if raw.isdigit():
                idx = int(raw) - 1
                if 0 <= idx < len(projects):
                    self._open_project(projects[idx])

    def _open_project(self, proj):
        items, open_docs, title = utils.build_stream_items(proj)
        if not items:
            self._clear()
            print("[paper] No viewable files in this project folder.")
            input("Press Enter...")
            return

        try:
            ProjectStreamViewer(items, window=self.window, title=title).run()
        finally:
            utils.close_open_docs(open_docs)

    def _clear(self):
        os.system("cls" if os.name == "nt" else "clear")
