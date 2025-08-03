import typing
from dataclasses import dataclass


class MealyMachine:
  """
  Means:
    Шаблон класса конечного автомата Мили для обработки двоичных чисел.
    Пример использования:
    ```python
      machine = MealyMachine(
        number="101",
        states_dict={
          "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
          "S_1": {0: ("S_0", 1), 1: ("S_1", 0)},
        },
        initial_state="S_0",
        add_zeros=True,
        zeros_amount=3,
        should_start=True,
      )

      print(machine.GetAnswer())
    ```
  """

  @dataclass
  class _State:
    BinaryDigit = typing.Literal[0, 1]
    NameType = str | int

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
    dict[_State.BinaryDigit, tuple[_State.NameType, _State.BinaryDigit]],
  ]

  _number: str = ""
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
        number (str): двоичное число, по которому будет проходиться конечный автомат.
        states_dict (MealyMachine.Dict): словарь состояний.
        initial_state (str | int): начальное состояние.
        add_zeros (bool, optional): факт необходимости незначащих доп. нулей.
          Defaults to True.
        zeros_amount (int, optional): кол-во незначащих доп. нулей. Defaults to 4.
        should_start (bool, optional): факт необходимости начала работы автомата.
          Defaults to True.
    """

    self._initial_state = initial_state

    self._states = {}
    self._InitStates(states_dict)

    self._number = number.zfill(len(number) + zeros_amount * add_zeros)
    self._answer: str = ""

    if should_start:
      self.Start()

  def GetAnswer(self) -> str:
    """
    Returns:
      str: вывод конечного автомата.
    """

    return self._answer

  def Start(self):
    """
    Does:
      Запускает алгоритм конечного автомата.
    """

    state_literal = self._initial_state

    while self._number:
      state = self._states[state_literal]

      last_digit = int(self._number[-1])
      self._number = self._number[:-1]

      # TODO: добавить логику с остановкой автомата в конкретном состоянии

      self._answer += str(state.DigitIf(last_digit))  # type: ignore
      state_literal = state.StateIf(last_digit)  # type: ignore

    self._answer = str(int("".join(reversed(self._answer))))

  def _InitStates(self, states_dict: Dict):
    """
    Does:
      Заполняет `self._states` и проверяет,
      что словарь `states_dict` соответствует структуре `MealyMachine.Dict`:
      ```python
        example: MealyMachine.Dict = {
          "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
          "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
          "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
        }
      ```

    Raises:
      ValueError: если не соответствует.
    """

    if self._initial_state not in states_dict.keys():
      raise KeyError(
        "MealyMachine (in states_dict):\n"
        f"Invalid initial state '{self._initial_state}' is not defined in states_dict. "
        f"Available states: {list(states_dict.keys())}"
      )

    for state_name, state_dict in states_dict.items():
      # MARK: Validation

      if not isinstance(state_name, MealyMachine._State.NameType):
        raise KeyError(
          "MealyMachine (in states_dict):\n"
          f"Invalid state name '{state_name}': "
          f"expected str or int, got {type(state_name)}"
        )

      if set(state_dict.keys()) != {0, 1}:
        raise KeyError(
          "MealyMachine (in states_dict):\n"
          f"Invalid transitions in state '{state_name}': "
          f"expected keys {{0, 1}}, but got {list(state_dict.keys())}"
        )

      for input_digit, (next_state, output_digit) in state_dict.items():
        if not isinstance(next_state, MealyMachine._State.NameType):
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            f"Invalid next state in transition {input_digit} -> {next_state}: "
            f"expected str or int, got {type(next_state)}"
          )

        if output_digit not in {1, 0}:
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            "Invalid output digit in transition "
            f"{state_name} --{input_digit}--> {next_state}: "
            f"expected 0 or 1, got {output_digit}"
          )

      # MARK: ~Validation

      self._states.setdefault(
        state_name,
        MealyMachine._State(
          state_dict[0][0],  # next_state if input=0
          state_dict[1][0],  # next_state if input=1
          state_dict[0][1],  # type: ignore; output if input=0
          state_dict[1][1],  # type: ignore; output if input=1
        ),
      )
