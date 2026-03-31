"""
Модуль для описания шагов выполнения автоматов Мили и Мура.

Содержит перечисление причин остановки и классы для хранения результатов шагов.
"""

from dataclasses import dataclass, field
from enum import Enum, auto


# MARK: StepReason
# --------------------------------------------------------------------------------------


class StepReason(Enum):
  """Причина завершения шага выполнения."""

  SUCCESS = auto()  # успешный переход
  STOP_CONDITION = auto()  # останов по условию
  NO_TRANSITION = auto()  # нет доступных переходов
  EXCEPTION = auto()  # исключение при выполнении


# MARK: StepData
# --------------------------------------------------------------------------------------


@dataclass
class StepData[InputType, OutputType]:
  """
  Данные успешного шага выполнения.

  Attributes:
    processed_input: Входное значение после обработки процессором.
    output: Выходное значение, вычисленное функцией перехода/состояния.
  """

  processed_input: InputType | None = None
  output: OutputType | None = None

  def __iter__(self):
    """Позволяет распаковывать объект как кортеж `(input, output)`."""

    return iter((self.processed_input, self.output))

  @classmethod
  def from_tuple(
    cls, data: tuple[InputType | None, OutputType | None]
  ) -> "StepData[InputType, OutputType]":
    """
    Создаёт объект из кортежа.

    Args:
      data: Кортеж `(input, output)`.

    Returns:
      Новый объект `StepData`.
    """

    return cls(*data)


# MARK: StepResult
# --------------------------------------------------------------------------------------


@dataclass
class StepResult[InputType, OutputType]:
  """
  Результат выполнения одного шага автомата.

  Attributes:
    reason: Причина завершения шага.
    data: Данные шага (заполнены только при `SUCCESS`).
    exception: Исключение, если `reason == EXCEPTION`.
  """

  reason: StepReason
  data: StepData[InputType, OutputType] = field(default_factory=StepData)
  exception: Exception | None = None

  @classmethod
  def error_step(cls, exception: Exception) -> "StepResult[InputType, OutputType]":
    """
    Создаёт результат шага для исключения.

    Args:
        exception: Исключение, вызвавшее остановку.

    Returns:
        Объект `StepResult` с `reason=EXCEPTION`.
    """

    return cls(
      reason=StepReason.EXCEPTION,
      exception=exception,
    )
