from typing import Callable


class NumberMulThree:
    """
    Means: 
      конечный автомат Мили, который выводит двоичное число, 
      умноженное на три, сложенное с двойкой (bin: (*11) + 2)
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

    def _DoState(self,  FuncIf0: Callable[[], None], digit_if_0: str,
                 FuncIf1: Callable[[], None], digit_if_1: str,
                 make_shift: bool = True):
        """
        Means:
          вспомогательная функция, отвечающая за выполнение действий 
          в состояниях конечного автомата

        Args:
          FuncIf0 (Callable[[], None]): функция, выполняемая в случае "0 на входе"
          digit_if_0 (str): цифра, добавляемая к ответу в случае "0 на входе"
          FuncIf1 (Callable[[], None]): функция, выполняемая в случае "1 на входе"
          digit_if_1 (str): цифра, добавляемая к ответу в случае "1 на входе"
        """

        try:
            if self._number[-1] == "0":
                self._answer += digit_if_0
                if (make_shift):
                    self._number = self._number[0:-1]

                # выполняем функцию, соотв. "0 на входе"
                FuncIf0()

            elif self._number[-1] == "1":
                self._answer += digit_if_1
                if (make_shift):
                    self._number = self._number[0:-1]

                # выполняем функцию, соотв. "1 на входе"
                FuncIf1()

        except IndexError:
            self._answer = "".join(reversed(self._answer))

    # состояния:

    def _State0(self) -> None:
        self._DoState(self._State1, "0", self._State2, "1")

    def _State1(self) -> None:
        self._DoState(self._State3, "1", self._State6, "0")

    def _State2(self) -> None:
        self._DoState(self._StateEnd, "", self._StateEnd, "")

    def _State3(self) -> None:
        self._DoState(self._State3, "0", self._State4, "1")

    def _State4(self) -> None:
        self._DoState(self._State3, "1", self._State5, "0")

    def _State5(self) -> None:
        self._DoState(self._State4, "0", self._State5, "1")

    def _State6(self) -> None:
        self._DoState(self._State8, "0", self._State7, "1")

    def _State7(self) -> None:
        self._DoState(self._State4, "0", self._State7, "1")

    def _State8(self) -> None:
        self._DoState(self._State3, "1", self._State6, "0")

    def _StateEnd(self) -> None:
        self._answer += "2"
        self._answer = "".join(reversed(self._answer))


# проверка работоспособности
if __name__ == "__main__":
    for i in range(0, 100):
        print(i)
        print(bin(i)[2::])
        print("real answer: " + bin(i*3+2)[2::])

        machine = NumberMulThree(bin(i)[2::])
        machine.Start()
        print("machine ans: " + machine.GetAnswer())

        print()
        print()

    for i in range(0, 10000, 2):
        machine = NumberMulThree(bin(i)[2::], add_zeros=True, zeros_amount=8)
        machine.Start()
        assert (bin(i*3+2)[2::] == machine.GetAnswer())
