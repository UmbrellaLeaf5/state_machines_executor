from dataclasses import dataclass

import dearpygui.dearpygui as dpg

# from gui.colors_tuples import *


@dataclass
class State:
  id: int
  name: str
  x: float
  y: float
  label: str  # Для Мура: выход внутри состояния


@dataclass
class Transition:
  start: int  # id начального состояния
  end: int  # id конечного состояния
  label: str  # Для Мили: вход/выход на переходе


class AutomatonEditor:
  def __init__(self):
    self.states: dict[int, State] = {}
    self.transitions: list[Transition] = []
    self.selected_state = None
    self.drag_start_pos = (0, 0)

  def draw_automaton(self):
    dpg.delete_item("drawing_node", children_only=True)  # Очистка перед перерисовкой

    # Рисуем переходы (стрелки)
    for trans in self.transitions:
      start = self.states[trans.start]
      end = self.states[trans.end]

      self.draw_arrow(start.x, start.y, end.x, end.y, trans.label)

    # Рисуем состояния (круги с метками)
    for state in self.states.values():
      self.draw_state(state.x, state.y, state.label, state.name)

  def draw_state(self, x, y, label, name):
    # Круг состояния
    dpg.draw_circle((x, y), 30, fill=(100, 100, 200, 255), parent="drawing_node")
    # Название состояния
    dpg.draw_text((x - 10, y - 10), name, color=(80, 80, 80, 255), parent="drawing_node")
    # Метка (для Мура)
    dpg.draw_text((x - 10, y + 10), label, color=(80, 80, 80, 255), parent="drawing_node")

  def draw_arrow(self, x1, y1, x2, y2, label):
    # Линия перехода
    dpg.draw_arrow(
      (x1, y1),
      (x2, y2),
      thickness=4,
      color=(80, 80, 80, 255),  # dark gray
      parent="drawing_node",
    )
    # Метка перехода (для Мили)
    dpg.draw_text(
      ((x1 + x2) / 2, (y1 + y2) / 2),
      label,
      color=(80, 80, 80, 255),
      parent="drawing_node",
    )

  def handle_drag(self, sender, app_data, user_data):
    if self.selected_state:
      mouse_x = dpg.get_mouse_pos()[0]
      mouse_y = dpg.get_mouse_pos()[1]

      self.states[self.selected_state].x = mouse_x
      self.states[self.selected_state].y = mouse_y

      self.draw_automaton()  # Обновляем отрисовку

  def handle_click(self, sender, app_data, user_data):
    mouse_x = dpg.get_mouse_pos()[0]
    mouse_y = dpg.get_mouse_pos()[1]

    for state_id, state in self.states.items():
      if (state.x - mouse_x) ** 2 + (
        state.y - mouse_y
      ) ** 2 <= 30**2:  # Проверка клика внутри круга
        self.selected_state = state_id
        self.drag_start_pos = (mouse_x, mouse_y)
        break


# Инициализация DearPyGui
dpg.create_context()
editor = AutomatonEditor()

# Добавляем тестовые данные
editor.states[1] = State(1, "S_1", 100, 100, "A")
editor.states[2] = State(2, "S_2", 300, 200, "B")
editor.transitions.append(Transition(1, 2, "x/y"))

with dpg.window(label="State Machine Executor", tag="main_window"):
  with dpg.drawlist(width=800, height=600, tag="drawing_node"):
    editor.draw_automaton()

  # Обработчики событий мыши
  with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=editor.handle_drag)
    dpg.add_mouse_click_handler(
      button=dpg.mvMouseButton_Left, callback=editor.handle_click
    )

dpg.create_viewport(title="State Machine Executor", width=1000, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
