import typing
from dataclasses import dataclass


class MealyMachine:
  """
  Means:
    Шаблон класса конечного автомата Мили
  """

  @dataclass
  class _State:
    BinaryDigit = typing.Literal[0, 1]
    NameType = str | int

    name: NameType

    state_if_0: NameType
    state_if_1: NameType

    digit_if_0: BinaryDigit
    digit_if_1: BinaryDigit

    def DigitIf(self, digit: BinaryDigit) -> BinaryDigit:
      return self.digit_if_0 if digit == 0 else self.digit_if_1

    def StateIf(self, digit: BinaryDigit) -> NameType:
      return self.state_if_0 if digit == 0 else self.state_if_1

  Dict = dict[
    _State.NameType,
    dict[_State.BinaryDigit, list[_State.NameType | _State.BinaryDigit]],
  ]

  _number: str
  _answer: str = ""
  _states: dict[_State.NameType, _State] = {}
  _initial_state: _State.NameType

  def __init__(
    self,
    number: str,
    states_dict: Dict,
    initial_state: _State.NameType,
    add_zeros: bool = True,
    zeros_amount: int = 4,
    should_start: bool = True,
  ) -> None:
    """
    Args:
      number (str): двоичное число, по которому будет проходиться конечный автомат
      states_dict (MealyMachineDict): словарь состояний
      initial_state (str | int): начальное состояние
      add_zeros (bool, optional):
        факт необходимости незначащих доп. нулей (defaults to True)
      zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
      should_start (bool, optional):
        факт необходимости начала работы автомата (defaults to True)
    """

    self._initial_state = initial_state
    self._InitStates(states_dict)

    self._number = number.zfill(len(number) + zeros_amount * add_zeros)

    if should_start:
      self.Start()

  def Start(self) -> None:
    """
    Does:
      запускает алгоритм конечного автомата
    """

    self._DoState(self._initial_state)

  def GetAnswer(self) -> str:
    """
    Returns:
      str: вывод конечного автомата
    """

    return str(int(self._answer))

  def _DoState(self, state_literal: _State.NameType):
    """
    Means:
      Вспомогательная функция, отвечающая за выполнение действий
      в состояниях конечного автомата

    Args:
      state_literal (str | int): номер (название) состояния
    """

    while self._number:
      state = self._states[state_literal]

      last_digit = int(self._number[-1])
      self._number = self._number[:-1]

      self._answer += str(state.DigitIf(last_digit))  # type: ignore
      state_literal = state.StateIf(last_digit)  # type: ignore

    self._answer = str(int("".join(reversed(self._answer))))

  def _InitStates(self, states_dict: Dict):
    """
    Does:
      Заполняет `self._states` и проверяет,
      что словарь `self._states_dict` соответствует структуре `MealyMachineDict`:
      ```python
        example: MealyMachineDict = {
          "S_0": {0: ["S_0", 1], 1: ["S_1", 1]},
          "S_1": {0: ["S_1", 1], 1: ["S_1", 1]},
          "S_2": {0: ["S_1", 1], 1: ["S_1", 1]},
        }
      ```

    Raises:
      ValueError: если не соответствует
    """

    for state_name, state_dict in states_dict.items():
      if not isinstance(state_name, MealyMachine._State.NameType):
        raise ValueError(f"states_dict: state_name '{state_name}' is not str or int")

      if len(state_dict.keys()) != len([0, 1]):
        raise ValueError(
          "stated_dict: there should be only two keys: [0, 1], no more, no less, "
          f"your variant is wrong: {list(state_dict.keys())}"
        )

      for digit, state_digit_info in state_dict.items():
        if digit not in {1, 0}:
          raise ValueError(f"states_dict: digit '{digit}' is not binary digit")

        if len(state_digit_info) != len(
          [MealyMachine._State.NameType, MealyMachine._State.BinaryDigit]
        ):
          raise ValueError(
            "stated_dict: first element in state_digit_info should be str or int, "
            "second should be binary digit, no more, no less, "
            f"your variant is wrong: {state_digit_info}"
          )

        state_if = state_digit_info[0]
        digit_if = state_digit_info[1]

        if not isinstance(state_if, MealyMachine._State.NameType):
          raise ValueError(
            f"states_dict: state_if_{digit} '{state_if}' is not str or int"
          )

        if digit_if not in {1, 0}:
          raise ValueError(
            f"states_dict: digit_if_{digit} '{digit_if}' is not str or int"
          )

      state_if_0 = state_dict[0][0]
      state_if_1 = state_dict[1][0]

      digit_if_0 = state_dict[0][1]
      digit_if_1 = state_dict[1][1]

      self._states.setdefault(
        state_name,
        MealyMachine._State(
          state_name,
          state_if_0,
          state_if_1,
          digit_if_0,  # type: ignore
          digit_if_1,  # type: ignore
        ),
      )
