from textual.app import ComposeResult, RenderResult
from textual.widget import Widget

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
    """

    def __init__(self, *args) -> None:
        super().__init__()
        self.args = args

    def render(self) -> str:
        return f"{self.args}"


class RequestHolder(Widget):
    def __init__(self, requests: list | None = None) -> None:
        self.requests = requests or []

        super().__init__()

    def compose(self) -> ComposeResult:
        yield from [RequestWidget(request) for request in self.requests]

    def update(self, requests: list) -> None:
        self.requests = requests
        self.remove_children()
        for request in self.requests:
            self.mount(RequestWidget(request))

        self.refresh()

