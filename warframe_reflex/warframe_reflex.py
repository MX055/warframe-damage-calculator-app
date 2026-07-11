import reflex as rx

from .components import page
from .state import CalculatorState


app = rx.App(
    stylesheets=["/styles.css"],
)

app.add_page(
    page,
    route="/",
    title="Warframe Damage Calculator",
    description="A Reflex interface for warframe_damage_calculator.",
    on_load=CalculatorState.initialize,
)

# run localy: .\.venv\Scripts\python.exe -m reflex run
# deploy app: .\.venv\Scripts\python.exe -m reflex deploy --app-id b088ad07-e313-4948-a097-7a42b4f2844d