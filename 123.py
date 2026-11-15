
from auroraview import WebView
import inspect

view = WebView(
    html="<html><body>Test</body></html>",
    transparent=True,
    decorations=False,
    auto_show=False,
)

core = view._core

for name in (
    "enable_click_through",
    "disable_click_through",
    "is_click_through_enabled",
    "update_interactive_regions",
    "get_interactive_regions",
):
    method = getattr(core, name)
    print(f"\n=== {name} ===")

    try:
        print("Сигнатура:", inspect.signature(method))
    except Exception as e:
        print("Сигнатура недоступна:", e)

    print("Описание:", method.__doc__)
