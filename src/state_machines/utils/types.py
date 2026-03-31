from typing import Any


Kwargs = dict[str, Any]


class UNSET:
  """Сентинель для обозначения 'значение не установлено'."""


UNSET_VAL = UNSET()

# IMP: к сожалению, с такой функцией нету сужения типов
# def is_unset(obj: Any) -> bool:
#   return isinstance(obj, UNSET)
