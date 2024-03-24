from typing import Callable


class MooreMachine:

    _number: str
    _answer: str = ""
    _states_dict: dict
    _states_refs: list = []

    def __init__(self, number: str, states_dict: dict, should_start=True):
        self._number = number
        self._states_dict = states_dict

        self._InitStates()

        # if (should_start):
        self.Start()

    def Start(self):
        print(self._states_refs)
        self._states_refs[0]

    def GetAnswer(self) -> str:
        """
        Returns:
          str: вывод конечного автомата
        """

        return str(int(self._answer))

    def _InitStates(self):
        states_defs: list[str] = []
        for state_key, state_value in self._states_dict.items():
            state_dict: dict = state_value
            state_definition = f"def _State{state_key[-1]}(self):\n \
                   self._DoState( \
                            self._{state_dict['FuncIf0']}, \
                            self._{state_dict['FuncIf1']}, \
                            {state_dict['digit']})"

            states_defs.append(state_definition)

        for i in range(len(states_defs)):
            exec(states_defs[i])
            self._states_refs.append(eval(f"_State{i}"))

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


if __name__ == "__main__":
    state0_dict: dict = {'digit': "",
                         'FuncIf0': "State2",
                         'FuncIf1': "State1"}

    state1_dict: dict = {'digit': "0",
                         'FuncIf0': "State2",
                         'FuncIf1': "State1"}

    state2_dict: dict = {'digit': "1",
                         'FuncIf0': "State2",
                         'FuncIf1': "State1"}

    states_dict: dict = {'State0': state0_dict,
                         'State1': state1_dict,
                         'State2': state2_dict}

    machine = MooreMachine("100", states_dict)
    # print(machine.GetAnswer())
