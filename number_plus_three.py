from typing import Callable


class NumberPlusThree:
    """
    Means: 
      конечный автомат Мура, который выводит двоичное число, сложенное с тройкой (bin: 11)
    """

    _number: str
    _answer: str = ""

    def __init__(self, number: str,
                 add_zeros: bool = True, zeros_amount: int = 4) -> None:
        """
        Args:
          number (str): двоичное число, по которому будет проходиться конечный автомат
          add_zeros (bool, optional): факт необходимости незначащих доп. нулей (defaults to True)
          zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
        """

        self._number = "0"*(zeros_amount)*add_zeros + number

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

    def _DoState(self, digit: str, FuncIf0: Callable[[], None],
                 FuncIf1: Callable[[], None], make_shift: bool = True):
        """
        Means:
          вспомогательная функция, отвечающая за выполнение действий 
          в состояниях конечного автомата

        Args:
            digit (str): цифра, добавляемая к ответу
            FuncIf0 (Callable[[], None]): функция, выполняемая в случае "0 на входе"
            FuncIf1 (Callable[[], None]): функция, выполняемая в случае "1 на входе"
            make_shift (bool, optional): факт необходимости сдвига по входному числу
                                         (defaults to True)
        """

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
        self._DoState("", self._State1, self._State2, False)

    def _State1(self) -> None:
        self._DoState("1", self._State3, self._State4)

    def _State2(self) -> None:
        self._DoState("0", self._State5, self._State6)

    def _State3(self) -> None:
        self._DoState("1", self._State9, self._State10)

    def _State4(self) -> None:
        self._DoState("0", self._State7, self._State8)

    def _State5(self) -> None:
        self._DoState("0", self._State7, self._State8)

    def _State6(self) -> None:
        self._DoState("1", self._State7, self._State8)

    def _State7(self) -> None:
        self._DoState("1", self._State9, self._State10)

    def _State8(self) -> None:
        self._DoState("0", self._State7, self._State8)

    def _State9(self) -> None:
        self._DoState("0", self._State9, self._State10)

    def _State10(self) -> None:
        self._DoState("1", self._State9, self._State10)


# проверка работоспособности
if __name__ == "__main__":

    for i in range(0, 100):
        print(i)
        bin_number = bin(i)[2::]
        real_answer: str = bin(i+3)[2::]
        print("bin number: " + bin_number)
        print("real answer: " + real_answer)

        machine = NumberPlusThree(bin(i)[2::])
        machine.Start()
        print("machine ans: " + machine.GetAnswer())
        print()
        assert (bin(i+3)[2::] == machine.GetAnswer())
        print()
