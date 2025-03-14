from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input, Label, Select
from rich.text import Text
import requests

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
    CSS_PATH = "css/request_widget.css"

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
        with Horizontal(id="request-container"):
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

                with Collapsible(id="response", title="Response"):
                    yield Label(id="response-status")
                    with Collapsible(title="Body", id="body-container"):
                        with VerticalScroll(id="scroller"):
                            yield Label(id="response-body")
            with Vertical(id="button-col"):
                yield Button("Delete", id="delete")
                yield Button("Send", id="send")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            # I have no idea why pyright doesn't fw this
            self.app.push_screen(DeleteConfirmation(), callback=self._delete_req)  # pyright: ignore
        elif event.button.id == "send":
            method = self.request_data.get("method", "GET")
            url = self.request_data.get("url", "URL")

            response = requests.request(method, url)
            response_block = self.query_one("#response", Collapsible)
            response_block.styles.display = "block"
            
            response_text = response.text

            response_block.query_one("#response-status", Label).update(f"Status: {response.status_code}")
            response_block.query_one("#response-body", Label).update(Text(response_text))



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
    DEFAULT_CSS = """
    RequestHolder {
        overflow-y: scroll;
    }
    """

    def __init__(self, requests: list | None = None) -> None:
        self.requests = requests or []

        super().__init__()

    def compose(self) -> ComposeResult:
        for i, request in enumerate(self.requests):
            yield RequestWidget(request, i)

    def update(self, requests: list) -> None:
        self.requests = requests
        self.remove_children()
        for i, request in enumerate(self.requests):
            self.mount(RequestWidget(request, i))

        self.refresh()

    def compile(self) -> list:
        return [child.compile() for child in self.children if isinstance(child, RequestWidget)]

