from abc import ABC

from ..utils.protocols import InputProcessorProtocol, TransConditionProtocol
from ..utils.types import Kwargs


class BaseTransition[InputType](ABC):
  """
  Базовый класс перехода.

  Определяет минимальный интерфейс и общую реализацию для перехода в автомате.
  """

  source_state: str
  target_state: str

  trans_condition: TransConditionProtocol[InputType]
  input_processor: InputProcessorProtocol[InputType]

  def is_transferable(
    self, input: InputType, condition_kwargs: Kwargs | None = None
  ) -> bool:
    """
    Проверяет, можно ли выполнить переход для заданного входа.

    Args:
      input: Входное значение.
      condition_kwargs: Дополнительные аргументы для функции условия.

    Returns:
      `True` если условие выполнено, иначе `False`.
    """

    if condition_kwargs is None:
      condition_kwargs = {}

    return self.trans_condition(input, **condition_kwargs)

  def process_input(
    self, input: InputType, processor_kwargs: Kwargs | None = None
  ) -> InputType:
    """
    Обрабатывает входное значение.

    Args:
      input: Входное значение.
      processor_kwargs: Дополнительные аргументы для процессора входа.

    Returns:
      Обработанное входное значение.
    """

    if processor_kwargs is None:
      processor_kwargs = {}

    return self.input_processor(input, **processor_kwargs)
