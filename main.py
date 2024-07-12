from examples.number_plus_three import NumberPlusThree
from examples.number_mul_three_plus_one import NumberMulThreePlusOne
from examples.number_mul_three_plus_two import NumberMulThreePlusTwo
from examples.number_mul_three import NumberMulThree

if __name__ == "__main__":
    # NumberPlusThree()
    # NumberMulThreePlusOne()
    # NumberMulThreePlusTwo()
    # NumberMulThree()
    pass


import dearpygui.dearpygui as dpg


def button1_callback():
    dpg.set_value("output_text", "Button 1 was clicked!")


def button2_callback():
    dpg.set_value("output_text", "Button 2 was clicked!")


dpg.create_context()
dpg.create_viewport(title='DearPyGui Demo', width=800, height=600)

with dpg.window(label="Main Window", tag="main_window", width=800, height=600):
    with dpg.child_window(tag="child_window", width=-1, height=-1):
        dpg.add_button(label="Button 1", callback=button1_callback)
        dpg.add_button(label="Button 2", callback=button2_callback)
        dpg.add_text("", tag="output_text")

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
