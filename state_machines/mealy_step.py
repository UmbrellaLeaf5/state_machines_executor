from dataclasses import dataclass
from enum import Enum, auto


class MealyStepReason(Enum):
  SUCCESS = auto()  # успешный переход
  STOP_CONDITION = auto()  # останов по условию
  NO_TRANSITION = auto()  # нет доступных переходов


@dataclass
class MealyStepData[InputType, OutputType]:
  input: InputType | None = None
  output: OutputType | None = None

  def __iter__(self):
    return iter((self.input, self.output))

  @classmethod
  def from_tuple(cls, data: tuple[InputType | None, OutputType | None]):
    return cls(*data)


@dataclass
class MealyStepResult[InputType, OutputType]:
  reason: MealyStepReason
  data: MealyStepData[InputType, OutputType]

  def __init__(
    self,
    reason: MealyStepReason,
    data: tuple[InputType | None, OutputType | None]
    | MealyStepData[InputType, OutputType]
    | None = None,
  ):
    self.reason = reason

    if data is None:
      self.data = MealyStepData[InputType, OutputType]()

    elif isinstance(data, tuple):
      self.data = MealyStepData[InputType, OutputType].from_tuple(data)

    else:
      self.data = data
