from __future__ import annotations

from dataclasses import dataclass

from .._base import BaseState
from .transition import MealyTransition


@dataclass
class MealyState[InputType, OutputType](BaseState[InputType, MealyTransition]):
  """
  Состояние автомата Мили.

  Содержит имя состояния и словарь переходов в другие состояния.

  Attributes:
    name: Имя состояния.
    transitions: Словарь переходов, где ключ - имя целевого состояния,
                  значение - объект MealyTransition.
  """

  name: str

  transitions: dict[str, MealyTransition[InputType, OutputType]]
