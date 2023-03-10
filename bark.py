import os
import commands


def format_bookmark(bookmark):
    return "\t".join(str(field) if field else "" for field in bookmark)


class Option:
    def __init__(
        self, name, command, prep_cal=None, success_message="{result}"
    ) -> None:
        self.name = name
        self.command = command
        self.prep_call = prep_cal
        self.success_message = success_message

    def choose(self):
        data = self.prep_call() if self.prep_call else None
        success, result = self.command.execute(data)

        formatted_result = ""

        if isinstance(result, list):
            for bookmark in result:
                formatted_result += format_bookmark(bookmark)
            else:
                formatted_result = result

        if success:
            print(self.success_message.format(result=result))

    def __str__(self) -> str:
        return self.name


def print_options(options):
    for shortcut, option in options.items():
        print(f"({shortcut}) {option}")
    print()


def option_choice_is_valid(choice: str, options):
    return choice in options or choice.upper() in options


def get_option_choice(options):
    choice = input("Choose an option: ")
    while not option_choice_is_valid(choice, options):
        print("Invalid choice")
        choice = input("Choose an option: ")
    return options[choice.upper()]


def get_user_input(label, required=True):
    value = input(f"{label}: ") or None
    while required and value is None:
        value = input(f"{label}: ") or None
    return value


def get_new_bookmark_data():
    return {
        "title": get_user_input("Title"),
        "url": get_user_input("URL"),
        "notes": get_user_input("Notes", required=False),
    }


def get_book_id_for_deletion():
    return get_user_input("Enter a bookmark ID to delete")


def clear_screen():
    clear = "cls" if os.name == "nt" else "clear"
    os.system(clear)


def get_github_import_options():
    return {
        "github_username": get_user_input("GitHub username"),
        "preserve_timestamps": get_user_input(
            "Preserve timestamps [Y/n]", required=None
        )
        in ["Y", "y", None],
    }


def loop():
    options = {
        "A": Option(
            "Add a bookmark",
            commands.AddBookmarkCommand(),
            prep_cal=get_new_bookmark_data,
            success_message="Bookmark Added",
        ),
        "B": Option("List bookmarks by date", commands.ListBookmarksCommand()),
        "T": Option(
            "List bookmarks by title", commands.ListBookmarksCommand(order_by="title")
        ),
        "D": Option(
            "Delete a bookmark",
            commands.DeleteBookmarkCommand(),
            prep_cal=get_book_id_for_deletion,
            success_message="Bookmark deleted!"
        ),
        "G": Option(
            "Import GitHub stars",
            commands.ImportGitHubStarsCommand(),
            prep_cal=get_github_import_options,
            success_message="Imported {result} bookmarks from starred repos"
        ),
        "Q": Option("Quit", commands.QuitCommand()),
    }

    clear_screen()
    print_options(options)
    chosen_option = get_option_choice(options)
    clear_screen()
    chosen_option.choose()

    _ = input("Press Enter to return to menu")


if __name__ == "__main__":

    while True:
        loop()
