from typing import Callable


class NumberPlusThree:
    """
    MEANS: 
      конечный автомат Мура, который выводит двоичное число, сложенное с тройкой (bin: 11)
    """

    _number: str
    _answer: str = ""

    def __init__(self, number: str) -> None:
        self._number = " " + "0"*(len(number)*2) + number

    def Start(self) -> None:
        self._State0()

    def GetAnswer(self) -> str:
        return str(int(self._answer))

    def _DoState(self, digit: str, FuncIf0: Callable[[], None], FuncIf1: Callable[[], None]):
        self._answer += digit
        self._number = self._number[0:-1]

        if self._number[-1] == "1":
            FuncIf1()

        elif self._number[-1] == "0":
            FuncIf0()

        else:
            self._answer = "".join(reversed(self._answer))

    def _State0(self) -> None:
        # первичное состояние немного отличается от всех переходных
        if self._number[-1] == "1":
            self._State2()

        elif self._number[-1] == "0":
            self._State1()

        else:
            self._answer = "".join(reversed(self._answer))

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
        print(bin(i)[2::])
        print(bin(i+3)[2::])
        print()

        machine = NumberPlusThree(bin(i)[2::])
        machine.Start()
        print(machine.GetAnswer())
        print()
        assert (bin(i+3)[2::] == machine.GetAnswer())
        print()
