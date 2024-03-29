from typing import Callable


class NumberPlusThree:
    """
    Means: 
      конечный автомат Мура, который выводит двоичное число, сложенное с тройкой (bin: 11)
    """

    _number: str
    _answer: str = ""

    def __init__(self, number: str,
                 add_zeros: bool = True, zeros_amount: int = 4, should_start=True) -> None:
        """
        Args:
          number (str): двоичное число, по которому будет проходиться конечный автомат
          add_zeros (bool, optional): факт необходимости незначащих доп. нулей (defaults to True)
          zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
        """

        self._number = "0"*(zeros_amount)*add_zeros + number

        if (should_start):
            self.Start()

    def Start(self) -> None:
        """
        Does:
          запускает алгоритм конечного автомата
        """

        self._State0()

    def GetAnswer(self) -> str:
        """
        Returns:
          str: вывод конечного автомата
        """

        return str(int(self._answer))

    def _DoState(self, FuncIf0: Callable[[], None],
                 FuncIf1: Callable[[], None], digit: str = ""):
        """
        Means:
          вспомогательная функция, отвечающая за выполнение действий 
          в состояниях конечного автомата

        Args:
            FuncIf0 (Callable[[], None]): функция, выполняемая в случае "0 на входе"
            FuncIf1 (Callable[[], None]): функция, выполняемая в случае "1 на входе"
            digit (str, optional): цифра, добавляемая к ответу (defaults to "")
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
                FuncIf0()

            elif self._number[-1] == "1":
                # выполняем функцию, соотв. "1 на входе"
                FuncIf1()

        except IndexError:
            self._answer = "".join(reversed(self._answer))

    # состояния:

    def _State0(self) -> None:
        self._DoState(self._State1, self._State2)

    def _State1(self) -> None:
        self._DoState(self._State3, self._State4, "1")

    def _State2(self) -> None:
        self._DoState(self._State4, self._State1, "0")

    def _State3(self) -> None:
        self._DoState(self._State5, self._State3, "1")

    def _State4(self) -> None:
        self._DoState(self._State3, self._State4, "0")

    def _State5(self) -> None:
        self._DoState(self._State5, self._State3, "0")


# проверка работоспособности
if __name__ == "__main__":
    for i in range(0, 100):
        print(i)

        curr_number = bin(i)[2::]
        print("curr number: " + curr_number)

        real_answer: str = bin(i+3)[2::]
        print("real answer: " + real_answer)

        machine = NumberPlusThree(bin(i)[2::])
        print("machine ans: " + machine.GetAnswer())

        print()
        print()

    # bigger testing
    for i in range(0, 10000):
        machine = NumberPlusThree(bin(i)[2::])
        assert (bin(i+3)[2::] == machine.GetAnswer())
