from textual import on
from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input, Label, OptionList, Select

from postperson.modals import DeleteConfirmation

class ErrorWidget(Widget):
    DEFAULT_CSS = """
    ErrorWidget {
        border: $secondary tall;
        height: 3;
        padding: 0 2;
        display: none;
    }
    """

    def __init__(self, error: str = ""):
        super().__init__()

        self.error = error

    def render(self) -> RenderResult:
        if self.error:
            return f"[red]Error:[/red] {self.error}"
        return ""

    def update(self, error: str) -> None:
        self.error = error
        self.styles.display = "block" if error else "none"
        self.refresh()


class RequestWidget(Widget):
    DEFAULT_CSS = """
    RequestWidget {
        border: $secondary tall;
    }

    #collapsible > * {
        padding: 0;
        margin: 0;
    }

    #delete {
        background: $error;
    }

    #send {
        background: $success;
    }

    #request-row {
        height: auto;
    }

    #request-row Select {
        width: 15;
        dock: left;
    }

    #request > Button {
        dock: right;
    }

    #button-col {
        width: auto;
    }

    #button-col Button {
        color: white;
    }

    Label {
        margin: 1 0 0 0;
    }
    """

    def __init__(self, request_data, id) -> None:
        super().__init__()
        self.request_data = request_data
        self.req_id = id

    def _set_unsaved_edit(self):
        if isinstance(self.parent, RequestHolder):
            setattr(self.parent.parent, "unsaved_edit", True)

    def _delete_req(self, result: int) -> None:
        if result:
            if isinstance(self.parent, RequestHolder):
                self.parent.requests.pop(self.req_id)
                self.parent.update(self.parent.requests)

                # doing self.parent.parent.unsaved_edit made pyright complain
                # "waa waa its not a known attribute :(" yeah shut up
                self._set_unsaved_edit()


    def compose(self) -> ComposeResult:
        with Horizontal(id="request"):
            with Collapsible(title=self.request_data.get("name", "Name"), id="collapsible"):
                yield Input(self.request_data.get("name", "Name"), id="name")
                yield Label("Request", id="request")
                with Horizontal(id="request-row"):
                    yield Select(
                        [(method, method) for method in ["GET", "POST", "PUT", "DELETE"]],
                        id="method",
                        value=self.request_data.get("method", "GET")
                    )
                    yield Input(self.request_data.get("url", "URL"), id="url")
            with Vertical(id="button-col"):
                yield Button("Delete", id="delete")
                yield Button("Send", id="send")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            # I have no idea why pyright doesn't fw this
            self.app.push_screen(DeleteConfirmation(), callback=self._delete_req)  # pyright: ignore

    def on_input_changed(self, event: Input.Changed) -> None:
         self.request_data[event.input.id] = event.input.value
         self.update()
         self._set_unsaved_edit()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "method":
            self.request_data["method"] = event.select.value
            self.update()
            self._set_unsaved_edit()

    def update(self) -> None:
        collapsible = self.query_one("#collapsible", Collapsible)
        if collapsible:
            collapsible.title = self.request_data.get("name", "Name")

        self.refresh()

    def compile(self) -> dict:
        return {
            "name": self.query_one("#name", Input).value,
            "method": self.query_one("#method", Select).value,
            "url": self.query_one("#url", Input).value,
        }


class RequestHolder(Widget):
    def __init__(self, requests: list | None = None) -> None:
        self.requests = requests or []

        super().__init__()

    def compose(self) -> ComposeResult:
        yield from [RequestWidget(request, i) for i, request in enumerate(self.requests)]

    def update(self, requests: list) -> None:
        self.requests = requests
        self.remove_children()
        for i, request in enumerate(self.requests):
            self.mount(RequestWidget(request, i))

        self.refresh()

    def compile(self) -> list:
        return [child.compile() for child in self.children if isinstance(child, RequestWidget)]

