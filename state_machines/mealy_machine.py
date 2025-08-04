from state_machines.state import BinaryDigit, MealyState, StateNameType


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

  Dict = dict[
    StateNameType,
    dict[BinaryDigit, tuple[StateNameType, BinaryDigit]],
  ]

  _number: str = ""
  _answer: str = ""
  _states: dict[StateNameType, MealyState] = {}
  _initial_state: StateNameType

  def __init__(
    self,
    number: str,
    states_dict: Dict,
    initial_state: StateNameType,
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

    Raises:
      ValueError: если формат исходного числа некорректен
    """

    if set(number) > {"0", "1"}:
      raise ValueError(
        "MealyMachine (in states_dict):\n"
        f"Invalid number format: "
        f"expected binary number, but got '{number}'"
      )

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

    state_name = self._initial_state

    while self._number:
      state = self._states[state_name]

      last_digit = int(self._number[-1])
      self._number = self._number[:-1]

      # TODO: добавить логику с остановкой автомата в конкретном состоянии

      self._answer += str(state.DigitIf(last_digit))  # type: ignore
      state_name = state.StateIf(last_digit)  # type: ignore

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
      ValueError | KeyError: если не соответствует.
    """

    if not isinstance(states_dict, dict):
      raise ValueError(
        "MealyMachine (in states_dict):\n"
        "Invalid states_dict type: "
        f"expected MealyMachine.Dict, but got {type(states_dict)}"
      )

    if not states_dict:  # empty
      raise ValueError(
        "MealyMachine (in states_dict):\nInvalid states_dict: expected non-empty dict"
      )

    if self._initial_state not in states_dict.keys():
      raise KeyError(
        "MealyMachine (in states_dict):\n"
        f"Invalid initial state '{self._initial_state}' is not defined in states_dict. "
        f"Available states: {list(states_dict.keys())}"
      )

    for state_name, state_dict in states_dict.items():
      if not isinstance(state_name, StateNameType):
        raise KeyError(
          "MealyMachine (in states_dict):\n"
          f"Invalid state name '{state_name}': "
          f"expected str or int, but got {type(state_name)}"
        )

      if not isinstance(state_dict, dict):
        raise ValueError(
          "MealyMachine (in states_dict):\n"
          f"Invalid transitions type in state '{state_name}': "
          f"expected dict, but got {type(state_dict)}"
        )

      if set(state_dict.keys()) != {0, 1}:
        raise KeyError(
          "MealyMachine (in states_dict):\n"
          f"Invalid transitions in state '{state_name}': "
          f"expected keys 0 and 1, but got {list(state_dict.keys())}"
        )

      for input_digit, output_tuple in state_dict.items():
        if not isinstance(output_tuple, tuple):
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            f"Invalid output_tuple type in state '{state_name}' in transition "
            f"'{state_name}' --({input_digit}, ...)--> ...: "
            f"expected tuple, but got {type(output_tuple)}"
          )

        if len(output_tuple) != 2:  # noqa: PLR2004
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            f"Invalid output_tuple length in state '{state_name}' in transition: "
            f"'{state_name}' --({input_digit}, ...)--> ...: "
            f"expected (next_state, output_digit), but got {output_tuple}"
          )

        next_state, output_digit = output_tuple

        if not isinstance(next_state, StateNameType):
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            f"Invalid next_state name in transition "
            f"'{state_name}' --({input_digit}, ...)--> '{next_state}': "
            f"expected str or int, but got {type(next_state)}"
          )

        if next_state not in states_dict.keys():
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            f"Invalid next_state in transition "
            f"'{state_name}' --({input_digit}, ...)--> '{next_state}': "
            f"state '{next_state}' is not defined states_dict. "
            f"Available states: {list(states_dict.keys())}"
          )

        if output_digit not in {0, 1}:
          raise ValueError(
            "MealyMachine (in states_dict):\n"
            "Invalid output digit in transition "
            f"'{state_name}' --({input_digit}, {output_digit})--> '{next_state}': "
            f"expected 0 or 1, but got {output_digit}"
          )

      self._states.setdefault(
        state_name,
        MealyState(
          state_dict[0][0],  # next_state if input=0
          state_dict[1][0],  # next_state if input=1
          state_dict[0][1],  # output if input=0
          state_dict[1][1],  # output if input=1
        ),
      )
