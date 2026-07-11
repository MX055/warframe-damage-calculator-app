import reflex as rx

from .components import page
from .state import CalculatorState

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="tomato",
        gray_color="slate",
        radius="medium",
        scaling="100%",
    ),
    stylesheets=["/styles.css"],
)
app.add_page(
    page,
    route="/",
    title="Warframe Damage Calculator",
    description="A Reflex interface for warframe_damage_calculator.",
    on_load=CalculatorState.initialize,
)
