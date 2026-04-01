from dataclasses import dataclass

from ..base import BaseTransition
from ..utils import (
  InputProcessorProtocol,
  TransConditionProtocol,
)


@dataclass
class MooreTransition[InputType](BaseTransition[InputType]):
  """
  Описание перехода в автомате Мура.

  Связывает исходное и целевое состояние, условие и процессор входа.

  Attributes:
    source_state: Имя исходного состояния.
    target_state: Имя целевого состояния.
    trans_condition: Функция-условие перехода.
    input_processor: Функция обработки входа.
  """

  source_state: str
  target_state: str

  trans_condition: TransConditionProtocol[InputType]
  input_processor: InputProcessorProtocol[InputType]
