from typing import Any

from .protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  TransConditionProtocol,
)


Kwargs = dict[str, Any]


class UNSET_TYPE:
  """Сентинель для обозначения 'значение не установлено'."""


UNSET_VAL = UNSET_TYPE()

# IMP: к сожалению, с такой функцией нету сужения типов
# def is_unset(obj: Any) -> bool:
#   return isinstance(obj, UNSET)

type ResultTuple[InputType, OutputType] = tuple[InputType | None, OutputType | None]

type MealyTransitionTuple[InputType, OutputType] = tuple[
  str,
  str,
  TransConditionProtocol[InputType],
  OutputFunctionProtocol[OutputType],
  InputProcessorProtocol[InputType],
]

type MooreTransitionTuple[InputType] = tuple[
  str,
  str,
  TransConditionProtocol[InputType],
  InputProcessorProtocol[InputType],
]

type MooreStateTuple[OutputType] = tuple[str, OutputFunctionProtocol[OutputType]]
