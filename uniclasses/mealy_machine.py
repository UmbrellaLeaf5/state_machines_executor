
from typing import Callable


class MealyMachine:
    """
    Means: 
      Шаблон класса конечного автомата Мили
    """

    _number: str
    _answer: str = ""
    _states_dict: dict[int, list[int | str]]

    def __init__(self, number: str, states_dict: dict[int, list[int | str]],
                 add_zeros: bool = True, zeros_amount: int = 4, should_start=True) -> None:
        """
        Args:
          number (str): двоичное число, по которому будет проходиться конечный автомат
          states_dict (dict[int, list[int | str]]): _description_
          add_zeros (bool, optional): факт необходимости незначащих доп. нулей (defaults to True)
          zeros_amount (int, optional): кол-во незначащих доп. нулей (defaults to 4)
          should_start (bool, optional): факт необходимости начала работы автомата (defaults to True)
        """

        self._states_dict = states_dict
        self._CheckStatesDict()

        self._number = number.zfill(len(number) + zeros_amount * add_zeros)

        if (should_start):
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

        try:
            if self._number[-1] == "0":
                self._answer += self._states_dict.get(state_id)[1]
                self._number = self._number[0:-1]

                # выполняем функцию, соотв. "0 на входе"
                self._DoState(self._states_dict.get(state_id)[0])

            elif self._number[-1] == "1":
                self._answer += self._states_dict.get(state_id)[3]
                self._number = self._number[0:-1]

                # выполняем функцию, соотв. "1 на входе"
                self._DoState(self._states_dict.get(state_id)[2])

        except IndexError:
            self._answer = "".join(reversed(self._answer))

    def _CheckStatesDict(self) -> None:
        """
        Does:
          проверяет, что словарь `self._states_dict` соответствует структуре

        Raises:
          ValueError: если не соответствует
        """
        for key, value in self._states_dict.items():
            if not isinstance(key, int):
                raise ValueError("states_dict: not all keys are ints")

            if not isinstance(value, list) or len(value) != 4:
                raise ValueError("states_dict: not all states are lists of 4")

            for item_index in range(len(value)):
                item = value[item_index]

                if not isinstance(item, (int, str)):
                    raise ValueError("states_dict: extra value type in states")

                if item_index % 2 == 0 and \
                   item not in self._states_dict.keys():  # то это номер состояния
                    raise ValueError(f"states_dict: extra key {item}")

                else:
                    if isinstance(item, str) and item not in ("1", "0", "") or \
                       isinstance(item, int) and item == value[-1] and item not in (1, 0):
                        raise ValueError("states_dict: the value of state is not binary")


# проверка работоспособности
def NumberMulThree() -> None:
    print("NumberMulThree")

    print()

    # словарь конечного автомата, который умножает на 3 (bin: 11) исходное число
    plus_mul_states_dict: dict[int, list[int | str]] = {0: [0, "0", 1, "1"],
                                                        1: [0, "1", 2, "0"],
                                                        2: [1, "0", 2, "1"]}

    for i in range(0, 100):
        print(i)

        curr_number = bin(i)[2::]
        print(f"curr number: {curr_number}")

        real_answer: str = bin(i*3)[2::]
        print(f"real answer: {real_answer}")

        machine = MealyMachine(bin(i)[2::], plus_mul_states_dict)
        print(f"machine ans: {machine.GetAnswer()}")

        print()

    # bigger testing
    for i in range(0, 10000):
        machine = MealyMachine(bin(i)[2::], plus_mul_states_dict)
        assert (bin(i*3)[2::] == machine.GetAnswer())


if __name__ == "__main__":
    NumberMulThree()
