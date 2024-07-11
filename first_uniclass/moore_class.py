class MooreMachine:
    """
      Means: 
        шаблон класса конечного автомата Мура
    """
    _number: str
    _answer: str = ""
    _states_dict: dict[str, list[str]]

    def __init__(self, number: str, states_dict: dict[str, list[str]],
                 add_zeros: bool = True, zeros_amount: int = 4, should_start=True) -> None:
        """
        Args:
          number (str): двоичное число, по которому будет проходиться конечный автомат
          add_zeros (bool, optional): факт необходимости незначащих доп. нулей (defaults to True)
          zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
        """

        self._states_dict = states_dict

        self._number = "0"*(zeros_amount)*add_zeros + number

        if (should_start):
            self.Start()

    def Start(self) -> None:
        """
        Does:
          запускает алгоритм конечного автомата
        """

        if self._states_dict.get("0") != None:
            self._DoState(self._states_dict.get("0")[0],
                          self._states_dict.get("0")[1],
                          self._states_dict.get("0")[2])

    def GetAnswer(self) -> str:
        """
        Returns:
          str: вывод конечного автомата
        """

        return str(int(self._answer))

    def _DoState(self, next_0_state: str, next_1_state: str, digit: str = ""):
        make_shift: bool = True

        if digit == "":
            make_shift = False

        self._answer += digit
        if (make_shift):
            self._number = self._number[0:-1]

        try:
            if self._number[-1] == "0" and self._states_dict.get(next_0_state) != None:
                if self._states_dict.get(next_0_state)[0] == None or \
                   self._states_dict.get(next_0_state)[1] == None or \
                   self._states_dict.get(next_0_state)[2] == None:
                    raise ValueError("Extra value type in states_dict")

                # выполняем функцию, соотв. "0 на входе"
                self._DoState(self._states_dict.get(next_0_state)[0],
                              self._states_dict.get(next_0_state)[1],
                              self._states_dict.get(next_0_state)[2])

            elif self._number[-1] == "1" and self._states_dict.get(next_1_state) != None:
                if self._states_dict.get(next_1_state)[0] == None or \
                   self._states_dict.get(next_1_state)[1] == None or \
                   self._states_dict.get(next_1_state)[2] == None:
                    raise ValueError("Extra value type in states_dict")
                # выполняем функцию, соотв. "1 на входе"
                self._DoState(self._states_dict.get(next_1_state)[0],
                              self._states_dict.get(next_1_state)[1],
                              self._states_dict.get(next_1_state)[2])

        except IndexError:
            self._answer = "".join(reversed(self._answer))


# проверка работоспособности
if __name__ == "__main__":
    states_dict: dict[str, list[str]] = {"0": ["1", "2", ""],
                                         "1": ["3", "4", "1"],
                                         "2": ["4", "1", "0"],
                                         "3": ["5", "3", "1"],
                                         "4": ["3", "4", "0"],
                                         "5": ["5", "3", "0"]}
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
