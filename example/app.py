from shiny import *
import shiny_sortable as sortable

@sortable.make(updatable=True)
def sortable_list(inputID):
    list = ui.tags.ol(
        ui.tags.li("Item 1", **{'data-id': '1'}),
        ui.tags.li("Item 2", **{'data-id': '2'}),
        ui.tags.li("Item 3", **{'data-id': '3'}),
        id=inputID
    )
    return list

app_ui = ui.page_fluid(
    sortable_list("list"),
    ui.output_text_verbatim(id = "text"),
    ui.input_action_button("reset", "Reset")
)

def server(input, output, session):
    list_order = reactive.value("")
    @output
    @render.text
    def text():
        return list_order()

    @reactive.effect
    @reactive.event(input.list)
    def _():
        list_order.set(input.list())

    @reactive.effect
    @reactive.event(input.reset)
    async def _():
        await sortable.update(session, "list", ["1", "2", "3"])


app = App(app_ui, server, debug=True)