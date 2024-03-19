from typing import Callable


class NumberMulThree:
    """
    MEANS: 
      конечный автомат Мили, который выводит двоичное число, умноженное на три (bin: 11)
    """

    _number: str
    _answer: str = ""

    def __init__(self, number: str) -> None:
        self._number = " " + "0"*(len(number)*2) + number

    def Start(self) -> None:
        self._State0()

    def GetAnswer(self) -> str:
        return str(int(self._answer))

    def _DoState(self,  FuncIf0: Callable[[], None], digit_if_0: str,
                 FuncIf1: Callable[[], None], digit_if_1: str):

        if self._number[-1] == "1":
            self._answer += digit_if_1
            self._number = self._number[0:-1]
            FuncIf1()

        elif self._number[-1] == "0":
            self._answer += digit_if_0
            self._number = self._number[0:-1]
            FuncIf0()

        else:
            self._answer = "".join(reversed(self._answer))

    def _State0(self) -> None:
        self._DoState(self._State0, "0", self._State1, "1")

    def _State1(self) -> None:
        self._DoState(self._State0, "1", self._State2, "0")

    def _State2(self) -> None:
        self._DoState(self._State1, "0", self._State2, "1")


# проверка работоспособности
if __name__ == "__main__":

    for i in range(0, 100):
        print(i)
        print(bin(i)[2::])
        print(bin(i*3)[2::])
        print()

        machine = NumberMulThree(bin(i)[2::])
        machine.Start()
        print()
        assert (bin(i*3)[2::] == machine.GetAnswer())
        print()
