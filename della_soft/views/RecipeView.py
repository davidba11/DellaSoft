import reflex as rx

class RecipeView(rx.State):
    pass

def recipes() -> rx.Component:
    return rx.text("RECETAS")