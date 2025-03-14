from textual import on
from textual.app import ComposeResult, RenderResult
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input

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
        padding: 0 1;
        border: $secondary tall;
        height: 10;
    }

    #delete {
        background: $error;
    }
    """

    def __init__(self, request_data, id) -> None:
        super().__init__()
        self.request_data = request_data
        self.req_id = id

    def _set_unsaved_edit(self):
        if isinstance(self.parent, RequestHolder):
            setattr(self.parent.parent, "unsaved_edit", True)

    def compose(self) -> ComposeResult:
        with Collapsible(title=self.request_data.get("name", "Name"), id="collapsible"):
            yield Input(self.request_data.get("name", "Name"), id="name")
            yield Button("Delete", id="delete")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            if isinstance(self.parent, RequestHolder):
                self.parent.requests.pop(self.req_id)
                self.parent.update(self.parent.requests)

                # doing self.parent.parent.unsaved_edit made pyright complain
                # "waa waa its not a known attribute :(" yeah shut up
                self._set_unsaved_edit()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "name":
            self.request_data["name"] = event.input.value
            self.update()
            self._set_unsaved_edit()

    def update(self) -> None:
        collapsible = self.query_one("#collapsible", Collapsible)
        if collapsible:
            collapsible.title = self.request_data.get("name", "Name")

        self.refresh()

    def compile(self) -> dict:
        return {
            "name": self.query_one(Input).value
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

