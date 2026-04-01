from __future__ import annotations

from dataclasses import dataclass

from ..base import BaseState
from ..utils import (
  OutputFunctionProtocol,
)
from ..utils.types import Kwargs
from .transition import MooreTransition


@dataclass
class MooreState[InputType, OutputType](BaseState[InputType, MooreTransition]):
  """
  Состояние автомата Мура.

  Содержит имя состояния, функцию выхода и словарь переходов в другие состояния.

  Attributes:
    name: Имя состояния.
    output_function: Функция, вычисляющая выходное значение состояния.
    transitions: Словарь переходов, где ключ - имя целевого состояния,
      значение - объект MooreTransition.
  """

  name: str
  output_function: OutputFunctionProtocol[OutputType]
  transitions: dict[str, MooreTransition[InputType]]

  # --------------------------------------------------------------------------------------

  def execute(
    self, previous_output: OutputType, function_kwargs: Kwargs | None = None
  ) -> OutputType:
    """
    Вычисляет выходное значение состояния.

    Args:
      previous_output: Выход предыдущего шага.
      function_kwargs: Дополнительные аргументы для функции выхода.

    Returns:
      Новое выходное значение.
    """

    if function_kwargs is None:
      function_kwargs = {}

    return self.output_function(previous_output, **function_kwargs)
