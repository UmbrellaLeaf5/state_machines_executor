from state_machines.state import BinaryDigit, MooreState, StateNameType


class MooreMachine:
  """
  Means:
    Шаблон класса конечного автомата Мура для обработки двоичных чисел.
    Пример использования:
    ```python
      machine = MooreMachine(
        number="101",
        states_dict={
          "S_0": ({0: "S_1", 1: "S_2"}, None),
          "S_1": ({0: "S_1", 1: "S_2"}, 1),
          "S_2": ({0: "S_1", 1: "S_2"}, 0),
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
    tuple[dict[BinaryDigit, StateNameType], BinaryDigit | None],
  ]

  _number: str
  _answer: str = ""
  _states: dict[StateNameType, MooreState] = {}
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
        states_dict (MooreMachine.Dict): словарь состояний.
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

  def Start(self) -> None:
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

      if state.Digit() is not None:
        self._answer += str(state.Digit())

      state_name = state.StateIf(last_digit)  # type: ignore

    self._answer = str(int("".join(reversed(self._answer))))

  def _InitStates(self, states_dict: Dict):
    """
    Does:
      Заполняет `self._states` и проверяет,
      что словарь `states_dict` соответствует структуре `MooreMachine.Dict`:
      ```python
        example: MooreMachine.Dict = {
          "S_0": ({0: "S_1", 1: "S_2"}, None),
          "S_1": ({0: "S_3", 1: "S_4"}, 1),
          "S_2": ({0: "S_4", 1: "S_1"}, 0),
          "S_3": ({0: "S_5", 1: "S_3"}, 1),
          "S_4": ({0: "S_3", 1: "S_4"}, 0),
          "S_5": ({0: "S_5", 1: "S_3"}, 0),
        }
      ```

    Raises:
      ValueError | KeyError: если не соответствует.
    """

    if not isinstance(states_dict, dict):
      raise ValueError(
        "MooreMachine (in states_dict):\n"
        "Invalid states_dict type: "
        f"expected MooreMachine.Dict, but got {type(states_dict)}"
      )

    if not states_dict:  # empty
      raise ValueError(
        "MooreMachine (in states_dict):\nInvalid states_dict: expected non-empty dict"
      )

    if self._initial_state not in states_dict.keys():
      raise KeyError(
        "MooreMachine (in states_dict):\n"
        f"Invalid initial state '{self._initial_state}' is not defined in states_dict. "
        f"Available states: {list(states_dict.keys())}"
      )

    for state_name, state_tuple in states_dict.items():
      if not isinstance(state_name, StateNameType):
        raise KeyError(
          "MooreMachine (in states_dict):\n"
          f"Invalid state name '{state_name}': "
          f"expected str or int, but got {type(state_name)}"
        )

      if not isinstance(state_tuple, tuple):
        raise ValueError(
          "MooreMachine (in states_dict):\n"
          f"Invalid state_dict type in state '{state_name}': "
          f"expected tuple, but got {type(state_tuple)}"
        )

      if not state_tuple:  # empty
        raise ValueError(
          "MooreMachine (in states_dict):\n"
          f"Invalid state_dict in state '{state_name}': expected non-empty dict"
        )

      if len(state_tuple) != 2:  # noqa: PLR2004
        raise ValueError(
          "MooreMachine (in states_dict):\n"
          f"Invalid state_tuple length in state '{state_name}': "
          f"expected (dict, 0 or 1), but got {state_tuple}"
        )

      output_dict, output_digit = state_tuple

      if not isinstance(output_dict, dict):
        raise ValueError(
          "MooreMachine (in states_dict):\n"
          f"Invalid transitions type in state '{state_name}': "
          f"expected dict, but got {type(output_dict)}"
        )

      if set(output_dict.keys()) != {0, 1}:
        raise KeyError(
          "MooreMachine (in states_dict):\n"
          f"Invalid transitions in state '{state_name}': "
          f"expected keys 0 and 1, but got {list(output_dict.keys())}"
        )

      for next_digit, next_state in output_dict.items():
        if not isinstance(next_state, StateNameType):
          raise ValueError(
            "MooreMachine (in states_dict):\n"
            f"Invalid next_state name in state '{state_name}' in transition "
            f"'{state_name}' --({next_digit})--> '{next_state}', ...: "
            f"expected tuple, but got {type(next_state)}"
          )

      if output_digit not in {0, 1, None}:
        raise ValueError(
          "MooreMachine (in states_dict):\n"
          f"Invalid transition in state '{state_name}': "
          f"'{state_name}' --(...)--> ..., {output_digit}: "
          f"expected 0, 1 or None, but got {output_digit}"
        )

      self._states.setdefault(
        state_name,
        MooreState(
          state_tuple[0][0],  # next_state if input=0
          state_tuple[0][1],  # next_state if input=1
          output_digit,  # == state_tuple[1]
        ),
      )
