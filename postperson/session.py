from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Static

from pathlib import Path
import json

from postperson import Binding
from postperson.widgets import RequestWidget

class Session(Screen):
    BINDINGS = [
        Binding("escape", "return", "Back"),
        Binding("s", "save", "Save"),
    ]

    def __init__(self, source_file: str) -> None:
        self.source_file = source_file
        if not Path(source_file).exists():
            with open(source_file, "w") as f:
                f.write("[]")

        with open(source_file, "r") as f:
            data = f.read()
            self.data = json.loads(data)

            if not isinstance(self.data, list):
                raise ValueError("Data must be a list")

        self.unsaved_edit = True 

        super().__init__()

    def on_mount(self) -> None:
        self.sub_title = self.source_file

    def compose(self) -> ComposeResult:
        yield Header()
        yield from [RequestWidget(request_data) for request_data in self.data]
        yield Footer()

    def action_save(self) -> None:
        with open(self.source_file, "w") as f:
            f.write(json.dumps(self.data, indent=4))

        self.refresh()

    def action_return(self) -> None:
        if self.unsaved_edit:
            self.app.push_screen(UnsavedExitConfirmation())
        else:
            self.app.pop_screen()


class UnsavedExitConfirmation(ModalScreen):
    DEFAULT_CSS = """
    UnsavedExitConfirmation {
        align: center middle;
    }

    .confirmation-box {
        padding: 1;
        height: 7;
    }

    #confirmation {
        width: auto;
    }

    #button-row {
        padding: 1;
        width: auto;
    }

    #yes {
        background: green;
    }

    #no {
        background: red;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Static(classes="confirmation-box"):
            with Center():
                yield Label("You have unsaved changes. Are you sure you want to exit?", id="confirmation")
            with Center():
                with Horizontal(id="button-row"):
                    yield Button("No", id="no")
                    yield Button("Yes", id="yes")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.app.pop_screen()
            self.app.pop_screen()
        else:
            self.app.pop_screen()
