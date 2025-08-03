from dataclasses import dataclass
from typing import Literal

import dearpygui.dearpygui as dpg

from gui.colors_tuples import *


@dataclass
class State:
  id: int
  name: str
  x: float
  y: float
  label: str  # Для Мура: выход внутри состояния
  SIZE: Literal[30] = 30


@dataclass
class Transition:
  start: int  # id начального состояния
  end: int  # id конечного состояния
  label: str  # Для Мили: вход/выход на переходе
  THICKNESS: Literal[4] = 4


class StateMachineEditor:
  DRAG_INIT_POS: tuple[int, int] = (0, 0)
  SME_EDITOR_NODE: str = "sme_editor_node"

  def __init__(self):
    self.states: dict[int, State] = {}
    self.transitions: list[Transition] = []
    self.selected_state = None
    self.drag_start_pos = StateMachineEditor.DRAG_INIT_POS

  def DrawStateMachine(self):
    # Очистка перед перерисовкой
    dpg.delete_item(StateMachineEditor.SME_EDITOR_NODE, children_only=True)

    # Рисуем переходы (стрелки)
    for trans in self.transitions:
      start = self.states[trans.start]
      end = self.states[trans.end]

      self.DrawArrow(start.x, start.y, end.x, end.y, trans.label)

    # Рисуем состояния (круги с метками)
    for state in self.states.values():
      self.DrawState(state.x, state.y, state.label, state.name)

  def DrawState(self, x: float, y, label: str, name: str):
    dpg.draw_circle(  # Круг состояния
      (x, y),
      State.SIZE,
      fill=BLUE_GRAY,
      parent=StateMachineEditor.SME_EDITOR_NODE,
    )

    dpg.draw_text(  # Название состояния
      (x - 10, y - 10),
      name,
      color=DARK_GRAY,
      parent=StateMachineEditor.SME_EDITOR_NODE,
    )

    dpg.draw_text(  # Метка (для Мура)
      (x - 10, y + 10),
      label,
      color=DARK_GRAY,
      parent=StateMachineEditor.SME_EDITOR_NODE,
    )

  def DrawArrow(self, x1, y1, x2, y2, label):
    dpg.draw_arrow(  # Линия перехода
      (x1, y1),
      (x2, y2),
      thickness=Transition.THICKNESS,
      color=GRAY,
      parent=StateMachineEditor.SME_EDITOR_NODE,
    )

    dpg.draw_text(  # Метка перехода (для Мили)
      ((x1 + x2) / 2, (y1 + y2) / 2),
      label,
      color=LIGHT_GRAY,
      parent=StateMachineEditor.SME_EDITOR_NODE,
    )

  def HandleDrag(self, sender, app_data, user_data):
    if self.selected_state:
      mouse_x = dpg.get_mouse_pos()[0]
      mouse_y = dpg.get_mouse_pos()[1]

      self.states[self.selected_state].x = mouse_x
      self.states[self.selected_state].y = mouse_y

      self.DrawStateMachine()  # Обновляем отрисовку

  def HandleClick(self, sender, app_data, user_data):
    mouse_x = dpg.get_mouse_pos()[0]
    mouse_y = dpg.get_mouse_pos()[1]

    for state_id, state in self.states.items():
      # Проверка клика внутри круга
      if (state.x - mouse_x) ** 2 + (state.y - mouse_y) ** 2 <= State.SIZE**2:
        self.selected_state = state_id
        self.drag_start_pos = (mouse_x, mouse_y)
        break

      else:
        self.selected_state = None
        self.drag_start_pos = StateMachineEditor.DRAG_INIT_POS


# Инициализация DearPyGui
dpg.create_context()
editor = StateMachineEditor()

# Добавляем тестовые данные
editor.states[1] = State(1, "S_1", 100, 100, "A")
editor.states[2] = State(2, "S_2", 300, 200, "B")
editor.transitions.append(Transition(1, 2, "x/y"))

with dpg.window(label="State Machine Executor", tag="main_window"):
  with dpg.drawlist(width=800, height=600, tag=StateMachineEditor.SME_EDITOR_NODE):
    editor.DrawStateMachine()

  # Обработчики событий мыши
  with dpg.handler_registry():
    dpg.add_mouse_drag_handler(button=dpg.mvMouseButton_Left, callback=editor.HandleDrag)
    dpg.add_mouse_click_handler(
      button=dpg.mvMouseButton_Left, callback=editor.HandleClick
    )

dpg.create_viewport(title="State Machine Executor", width=1000, height=800)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main_window", True)
dpg.start_dearpygui()
dpg.destroy_context()
