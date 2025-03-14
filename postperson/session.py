from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Static

from pathlib import Path
import json

from postperson import Binding
from postperson.widgets import RequestHolder


class Session(Screen):
    BINDINGS = [
        Binding("escape", "return", "Back"),
        Binding("s", "save", "Save"),
        Binding("q", "quit", "Back"),
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

        self.unsaved_edit = False

        super().__init__()

    def on_mount(self) -> None:
        self.sub_title = self.source_file

    def compose(self) -> ComposeResult:
        self.request_holder = RequestHolder(self.data)

        yield Header()
        yield Button("Add Request", id="add-request", action="add_request")
        yield self.request_holder
        yield Footer()

    def action_save(self) -> None:
        self.data = self.request_holder.compile()
        with open(self.source_file, "w") as f:
            f.write(json.dumps(self.data, indent=4))

        self.notify("Saved")
        self.unsaved_edit = False
        self.refresh()

    def action_return(self) -> None:
        if self.unsaved_edit:
            self.app.push_screen(UnsavedExitConfirmation(action="back"))
        else:
            self.app.pop_screen()

    async def action_quit(self) -> None:
        if self.unsaved_edit:
            self.app.push_screen(UnsavedExitConfirmation())
        else:
            await self.app.action_quit()

    def action_add_request(self) -> None:
        self.data.append({})
        self.request_holder.update(self.data)
        self.unsaved_edit = True


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

    #button-row Button {
        color: white;
    }

    #yes {
        background: $success;
    }

    #no {
        background: $error;
    }
    """

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def __init__(self, action: str = "quit") -> None:
        self.action = action

        super().__init__()

    def compose(self) -> ComposeResult:
        with Static(classes="confirmation-box"):
            with Center():
                yield Label(
                    "You have unsaved changes. Are you sure you want to exit?", 
                    id="confirmation"
                )
            with Center():
                with Horizontal(id="button-row"):
                    yield Button("No", id="no")
                    yield Button("Yes", id="yes")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "yes":
            self.app.pop_screen()
            if self.action == "quit":
                await self.app.action_quit()
            else:
                self.app.pop_screen()
        else:
            self.app.pop_screen()

