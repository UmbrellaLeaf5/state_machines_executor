from __future__ import annotations

from dataclasses import dataclass

from .._base import BaseTransition
from ..utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  TransConditionProtocol,
)
from ..utils.types import Kwargs


@dataclass
class MealyTransition[InputType, OutputType](BaseTransition[InputType]):
  """
  Описание перехода в автомате Мили.

  Связывает исходное и целевое состояние, условие, функцию вычисления выхода
  и процессор входа.

  Attributes:
    source_state: Имя исходного состояния.
    target_state: Имя целевого состояния.
    trans_condition: Функция-условие перехода.
    output_function: Функция вычисления выходного значения.
    input_processor: Функция обработки входа.
  """

  source_state: str
  target_state: str

  trans_condition: TransConditionProtocol[InputType]
  output_function: OutputFunctionProtocol[OutputType]
  input_processor: InputProcessorProtocol[InputType]

  # --------------------------------------------------------------------------------------

  def execute(
    self, previous_output: OutputType, function_kwargs: Kwargs | None = None
  ) -> OutputType:
    """
    Вычисляет выходное значение перехода.

    Args:
      previous_output: Выход предыдущего шага.
      function_kwargs: Дополнительные аргументы для функции выхода.

    Returns:
      Новое выходное значение.
    """

    if function_kwargs is None:
      function_kwargs = {}

    return self.output_function(previous_output, **function_kwargs)
