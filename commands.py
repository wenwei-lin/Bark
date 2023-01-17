from abc import ABC, abstractmethod
from persistence import BookmarkDatabase
from datetime import datetime
import sys
import requests

bookmark_database = BookmarkDatabase()


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        pass

class AddBookmarkCommand(Command):
    def execute(self, data):
        data["date_added"] = data.get("date_added", datetime.utcnow().isoformat())
        bookmark_database.create(data)
        return True, None


class ListBookmarksCommand(Command):
    def __init__(self, order_by="date_added"):
        self.order_by = order_by

    def execute(self, data=None):
        return True, bookmark_database.list(self.order_by)


class DeleteBookmarkCommand(Command):
    def execute(self, bookmark_id):
        bookmark_database.delete(bookmark_id)
        return True, None


class QuitCommand(Command):
    def execute(self, data=None):
        sys.exit()
        return True, None


class ImportGitHubStarsCommand(Command):
    def _extract_bookmark_info(self, repo):
        return {
            "title": repo["name"],
            "url": repo["html_url"],
            "notes": repo["description"],
        }

    def execute(self, data):
        bookmark_imported = 0

        github_username = data["github_username"]
        next_page_of_results = f"https://api.github.com/users/{github_username}/starred"

        while next_page_of_results:
            stars_response = requests.get(
                next_page_of_results,
                headers={"Accept": "application/vnd.github.v3.star+json"},
            )
            next_page_of_results = stars_response.links.get("next", {}).get("url")

            for repo_info in stars_response.json():
                repo = repo_info["repo"]

                if data["preserve_timestamps"]:
                    timestamp = datetime.strptime(
                        repo_info["starred_at"], "%Y-%m-%dT%H:%M:%SZ"
                    )
                else:
                    timestamp = None

                bookmark_imported += 1

                bookmark_data = self._extract_bookmark_info(repo)
                if timestamp:
                    bookmark_data["date_added"] = timestamp

                AddBookmarkCommand().execute(data=bookmark_data)

        return True, bookmark_imported
