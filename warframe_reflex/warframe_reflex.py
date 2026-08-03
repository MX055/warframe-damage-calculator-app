import reflex as rx

from .components import home_page, page
from .state import CalculatorState


app = rx.App(
    stylesheets=["/styles.css"],
)
app.add_page(
    home_page,
    route="/",
    title="Warframe Damage Calculator",
    description="Saved builds and calculator home.",
    on_load=CalculatorState.hub_on_load,
)
app.add_page(
    page,
    route="/calculator",
    title="Warframe Damage Calculator",
    description="A Reflex interface for warframe_damage_calculator.",
    on_load=CalculatorState.calculator_on_load,
)

# run localy: .\.venv\Scripts\python.exe -m reflex run
# deploy app: .\.venv\Scripts\python.exe -m reflex deploy --app-id b088ad07-e313-4948-a097-7a42b4f2844d --vmtype c4m8
