from __future__ import unicode_literals
from prompt_toolkit.application import Application
from prompt_toolkit.key_binding.defaults import load_key_bindings
from prompt_toolkit.key_binding.key_bindings import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.keys import Keys
from prompt_toolkit.widgets import RadioList, Label
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import HSplit


def radiolist_dialog(title="", values=None, style=None, async_=False):
    # Add exit key binding.
    bindings = KeyBindings()

    @bindings.add(Keys.ControlC)
    def exit_(event):
        """
        Pressing Ctrl+c will exit the user interface.
        """
        event.app.exit()

    @bindings.add(Keys.Tab)
    def exit_with_value(event):
        """
        Pressing Ctrl-a will exit the user interface returning the selected value.
        """
        event.app.exit(result=radio_list.current_value)

    radio_list = RadioList(values)
    application = Application(
        layout=Layout(HSplit([Label(title), radio_list])),
        key_bindings=merge_key_bindings([load_key_bindings(), bindings]),
        mouse_support=True,
        style=style,
        full_screen=False,
    )

    if async_:
        return application.run_async()
    else:
        return application.run()
