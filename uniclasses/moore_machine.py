class MooreMachine:
  """
  Means:
    Шаблон класса конечного автомата Мура
  """

  _number: str
  _answer: str = ""
  _states_dict: dict[int, list[int | str]]

  def __init__(
    self,
    number: str,
    states_dict: dict[int, list[int | str]],
    add_zeros: bool = True,
    zeros_amount: int = 4,
    should_start=True,
  ) -> None:
    """
    Args:
      number (str): двоичное число, по которому будет проходиться конечный автомат
      states_dict (dict[int, list[int | str]]): словарь состояний
      add_zeros (bool, optional):
        факт необходимости незначащих доп. нулей (defaults to True)
      zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
      should_start (bool, optional):
        факт необходимости начала работы автомата (defaults to True)
    """

    self._states_dict = states_dict
    self._CheckStatesDict()

    self._number = number.zfill(len(number) + zeros_amount * add_zeros)

    if should_start:
      self.Start()

  def Start(self) -> None:
    """
    Does:
      запускает алгоритм конечного автомата
    """

    self._DoState(0)

  def GetAnswer(self) -> str:
    """
    Returns:
      str: вывод конечного автомата
    """

    return str(int(self._answer))

  def _DoState(self, state_id: int):
    """
    Means:
      Вспомогательная функция, отвечающая за выполнение действий
      в состояниях конечного автомата

    Args:
      state_id (int): номер состояния
    """
    make_shift: bool = True

    digit = str(self._states_dict.get(state_id)[-1])  # type: ignore

    if digit == "":
      make_shift = False

    self._answer += digit
    if make_shift:
      self._number = self._number[:-1]

    try:
      next: int = int(
        self._number[-1]
      )  # следующее число на вход (последнее в изначальном)
      self._DoState(self._states_dict.get(state_id)[next])  # type: ignore

    except IndexError:
      self._answer = "".join(reversed(self._answer))

  def _CheckStatesDict(self) -> None:
    """
    Does:
      Проверяет, что словарь `self._states_dict` соответствует структуре

    Raises:
      ValueError: если не соответствует
    """
    for key, value in self._states_dict.items():
      if not isinstance(key, int):
        raise ValueError("states_dict: not all keys are ints")

      if not isinstance(value, list) or len(value) != 3:  # noqa: PLR2004
        raise ValueError("states_dict: not all states are lists of 3")

      for item in value:
        if not isinstance(item, int | str):
          raise ValueError("states_dict: extra value type in states")

        if (
          isinstance(item, int)
          and item in value[:-1]
          and item not in self._states_dict.keys()
        ):
          raise ValueError(f"states_dict: extra key {item}")

        if (isinstance(item, str) and item not in ("1", "0", "")) or (
          isinstance(item, int) and item == value[-1] and item not in (1, 0)
        ):
          raise ValueError("states_dict: the value of state is not binary")
