# Shiny-sortable

A Python library to add sortable widgets to Shiny UI.

# Install
```
pip install shiny-sortable
```

# Basic Usage

The easiest way to build a sortable shiny widget is to use the `@make()` decorator.

The `@make()` decorator has three optional arguments:

1.  `ID` (str): The keyword argument name to extract the input ID from, defaults to `'inputID'`, if not found, defaults to the first argument.
2.  `dataID` (str): The attribute used to store data-id on sortable items.
3.  `updatable` (bool): Whether the sortable items should be updatable.


Let's use an ordered list as an example:

```r
from shiny import *
import shiny_sortable as sortable

@sortable.make()
def sortable_list(inputID): # add `inputID` as the first argument
    list = ui.tags.ol(
        ui.tags.li("Item 1", **{'data-id': '1'}),
        ui.tags.li("Item 2", **{'data-id': '2'}),
        ui.tags.li("Item 3", **{'data-id': '3'}),
        id=inputID
    )
    return list
```

This allows a sortable list when it is added to the UI:

```r
app_ui = ui.page_fluid(
    sortable_list("list"),
)
app = App(app_ui, None)
```

The list will look like this:

![A sortable list](img/list.png)

Alternatively, you can use your own keyword arguments:

```r
@sortable.make(ID="SomeRandomID", dataID="SomeDataId")
def sortable_list(SomeRandomID): # use `SomeRandomID` as the first argument
    list = ui.tags.ol(
        ui.tags.li("Item 1", SomeDataId = '1'),
        ui.tags.li("Item 2", SomeDataId = '2'),
        ui.tags.li("Item 3", SomeDataId = '3'),
        id=SomeRandomID
    )
    return list
```

The order of the items can be retrieved as a Shiny input:
```r
from shiny import *
import shiny_sortable as sortable

@sortable.make()
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
    ui.output_text_verbatim(id = "text")
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

app = App(app_ui, server)
```

This mini-app runs like this:

![alt text](img/display.png)

Moreover, we can make the sortable widget *updatable* by passing `updatable=True` to the `@make()` decorator. This allows the order to be updated by using the `update()` function.

For example, we can add a "Reset" button to the UI which will reset the list order to the initial state of 123.

```r
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


app = App(app_ui, server)
```

This mini-app runs like this:

![alt text](img/button.png)

Not that for updating the sortable widget, `async` and `await` are required, since `session.send_custom_message()` is used behind the scenes.

# Custom Usage

There are also three internally used functions which can be used to create custom widgets.

- `dep()`: Creates and returns a SortableJS HTML dependency.
   Behind the scenes, it does:
   ```r
   sortable_dep = HTMLDependency(
        name="SortableJS",
        version="1.15.3",
        source={
            "href": "https://cdnjs.cloudflare.com/ajax/libs/Sortable/1.15.3"
        },
        script={"src": "Sortable.min.js"},
    )
    return sortable_dep
   ```
- `input()`: Returns a script tag for initializing a Sortable instance on an element. The tag looks like:
   ```r
   script = f"""
    var el_{inputID} = document.getElementById('{inputID}');
    if (el_{inputID}) {{
        var sortable_{inputID} = new Sortable(el_{inputID}, {{
            dataIdAttr: '{dataID}',
            animation: 150,
            ghostClass: 'sortable-ghost',
            chosenClass: 'sortable-chosen',
            onSort: function (evt) {{
                var order = sortable_{inputID}.toArray();
                Shiny.setInputValue("{inputID}", order);
            }}
        }});
    }} else {{
        console.error("Element with id '{inputID}' not found");
    }}
    """
    return tags.script(script)
   ```
- output(): Returns a script tag for handling updates to the Sortable instance order. The tag looks like:
   ```r
   script = f"""
    Shiny.addCustomMessageHandler("sortable_update_{outputID}", function(message) {{
        if (typeof sortable_{outputID} !== 'undefined') {{
            sortable_{outputID}.sort(message.order);
            Shiny.setInputValue("{outputID}", message.order);
        }} else {{
            console.error("sortable_{outputID} is not defined. Cannot update order.");
        }}
    }});
    """
    return tags.script(script)
    ```
