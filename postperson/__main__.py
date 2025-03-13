from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

from collections import namedtuple

Binding = namedtuple("Binding", ["key", "action", "description"])

class PostPerson(App):
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("^p", "palette", "Change palette"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

if __name__ == "__main__":
    PostPerson().run()

