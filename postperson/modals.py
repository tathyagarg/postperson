from textual.app import ComposeResult
from textual.containers import Center, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Static

from postperson import Binding


class UnsavedExitConfirmation(ModalScreen):
    CSS_PATH = "css/unsaved_exit_confirmation.css"

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


class DeleteConfirmation(ModalScreen):
    CSS_PATH = "css/delete_confirmation.css"

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Static(classes="confirmation-box"):
            with Center():
                yield Label(
                    "Are you sure you want to delete this request?", 
                    id="confirmation"
                )
            with Center():
                with Horizontal(id="button-row"):
                    yield Button("No", id="no")
                    yield Button("Yes", id="yes")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")

