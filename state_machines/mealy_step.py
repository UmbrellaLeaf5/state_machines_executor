"""
Модуль для описания шагов выполнения автомата Мили.

Содержит перечисление причин остановки и классы для хранения результатов шагов.
"""

from dataclasses import dataclass
from enum import Enum, auto


class MealyStepReason(Enum):
  """Причина завершения шага выполнения."""

  SUCCESS = auto()  # успешный переход
  STOP_CONDITION = auto()  # останов по условию
  NO_TRANSITION = auto()  # нет доступных переходов
  EXCEPTION = auto()  # исключение при выполнении


@dataclass
class MealyStepData[InputType, OutputType]:
  """
  Данные успешного шага выполнения.

  Attributes:
      input: Входное значение после обработки процессором.
      output: Выходное значение, вычисленное функцией перехода.
  """

  input: InputType | None = None
  output: OutputType | None = None

  def __iter__(self):
    """Позволяет распаковывать объект как кортеж `(input, output)`."""
    return iter((self.input, self.output))

  @classmethod
  def from_tuple(
    cls, data: tuple[InputType | None, OutputType | None]
  ) -> "MealyStepData[InputType, OutputType]":
    """
    Создаёт объект из кортежа.

    Args:
        data: Кортеж `(input, output)`.

    Returns:
        Новый объект `MealyStepData`.
    """

    return cls(*data)


@dataclass
class MealyStepResult[InputType, OutputType]:
  """
  Результат выполнения одного шага автомата.

  Attributes:
      reason: Причина завершения шага.
      data: Данные шага (заполнены только при `SUCCESS`).
      exception: Исключение, если `reason == EXCEPTION`.
  """

  reason: MealyStepReason
  data: MealyStepData[InputType, OutputType]
  exception: Exception | None = None

  def __init__(
    self,
    reason: MealyStepReason,
    data: tuple[InputType | None, OutputType | None]
    | MealyStepData[InputType, OutputType]
    | None = None,
    exception: Exception | None = None,
  ):
    """
    Инициализирует результат шага.

    Args:
        reason: Причина завершения.
        data: Данные шага (кортеж, объект `MealyStepData` или `None`).
        exception: Исключение (только при `EXCEPTION`).
    """

    self.reason = reason
    self.exception = exception

    if data is None:
      self.data = MealyStepData[InputType, OutputType]()

    elif isinstance(data, tuple):
      self.data = MealyStepData[InputType, OutputType].from_tuple(data)

    else:
      self.data = data
