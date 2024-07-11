class MooreMachine:
    """
      Means: 
        шаблон класса конечного автомата Мура
    """
    _number: str
    _answer: str = ""
    _states_dict: dict[int, list[int | int | str]]

    def __init__(self, number: str, states_dict: dict[int, list[int | int | str]],
                 add_zeros: bool = True, zeros_amount: int = 4, should_start=True) -> None:
        """
        Args:
          number (str): двоичное число, по которому будет проходиться конечный автомат
          states_dict (dict[int, list[int | int | str]]): _description_
          add_zeros (bool, optional): факт необходимости незначащих доп. нулей (defaults to True)
          zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
          should_start (bool, optional): _description_. Defaults to True.
        """

        self._states_dict = states_dict
        self._Check_States_Dict()

        self._number = "0"*(zeros_amount)*add_zeros + number

        if (should_start):
            self.Start()

    def _Check_States_Dict(self) -> None:
        """
        Does:
          проверяет, что словарь `self._states_dict` соответствует структуре

        Raises:
          ValueError: если не соответствует
        """
        for key, value in self._states_dict.items():
            if not isinstance(key, int):
                raise ValueError("states_dict: Not all keys are ints")

            if not isinstance(value, list) or len(value) != 3:
                raise ValueError("states_dict: Not all states are lists of 3")

            for item in value:
                if not isinstance(item, (int, str)):
                    raise ValueError("states_dict: Extra value type in states")

                if isinstance(item, str) and not (item == "1" or item == "0"):
                    if key != 0 and item != "":
                        raise ValueError("states_dict: the value of state is not binary")

    def Start(self) -> None:
        """
        Does:
          запускает алгоритм конечного автомата
        """

        if self._states_dict.get(0) != None:
            self._DoState(self._states_dict.get(0)[0],
                          self._states_dict.get(0)[1],
                          self._states_dict.get(0)[2])

    def GetAnswer(self) -> str:
        """
        Returns:
          str: вывод конечного автомата
        """

        return str(int(self._answer))

    def _DoState(self, next_0_state: int, next_1_state: int, digit: str = ""):
        """
        Means:
          вспомогательная функция, отвечающая за выполнение действий
          в состояниях конечного автомата

        Args:
          next_0_state (int): ключ следующего состояния в словаре, если 0 на входе
          next_1_state (int): ключ следующего состояния в словаре, если 1 на входе
          digit (str, optional): цифра, которая добавляется к ответу (defaults to "")
        """
        make_shift: bool = True

        if digit == "":
            make_shift = False

        self._answer += digit
        if (make_shift):
            self._number = self._number[0:-1]

        try:
            if self._number[-1] == "0":
                # выполняем функцию, соотв. "0 на входе"
                self._DoState(self._states_dict.get(next_0_state)[0],
                              self._states_dict.get(next_0_state)[1],
                              self._states_dict.get(next_0_state)[2])

            elif self._number[-1] == "1":
                # выполняем функцию, соотв. "1 на входе"
                self._DoState(self._states_dict.get(next_1_state)[0],
                              self._states_dict.get(next_1_state)[1],
                              self._states_dict.get(next_1_state)[2])

        except IndexError:
            self._answer = "".join(reversed(self._answer))


# проверка работоспособности
if __name__ == "__main__":
    states_dict: dict[int, list[int | int | str]] = {0: [1, 2, ""],
                                                     1: [3, 4, "1"],
                                                     2: [4, 1, "0"],
                                                     3: [5, 3, "1"],
                                                     4: [3, 4, "0"],
                                                     5: [5, 3, "0"]}
    for i in range(0, 100):
        print(i)

        curr_number = bin(i)[2::]
        print(f"curr number: {curr_number}")

        real_answer: str = bin(i+3)[2::]
        print(f"real answer: {real_answer}")

        machine = MooreMachine(bin(i)[2::], states_dict)
        print(f"machine ans: {machine.GetAnswer()}")

        print()
        print()

    # bigger testing
    for i in range(0, 10000):
        machine = MooreMachine(bin(i)[2::], states_dict)
        assert (bin(i+3)[2::] == machine.GetAnswer())
