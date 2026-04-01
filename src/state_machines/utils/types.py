from typing import Any


Kwargs = dict[str, Any]


class UNSET_TYPE:
  """Сентинель для обозначения 'значение не установлено'."""


UNSET_VAL = UNSET_TYPE()

# IMP: к сожалению, с такой функцией нету сужения типов
# def is_unset(obj: Any) -> bool:
#   return isinstance(obj, UNSET)

type ResultTuple[InputType, OutputType] = tuple[InputType | None, OutputType | None]
