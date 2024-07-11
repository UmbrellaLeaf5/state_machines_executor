from uniclasses.moore_machine import MooreMachine


def NumberPlusThree() -> None:
    print("NumberPlusThree")

    print()

    # словарь конечного автомата, который прибавляет 3 (bin: 11) к исходному числу
    plus_three_states_dict: dict[int, list[int | str]] = {0: [1, 2, ""],
                                                          1: [3, 4, 1],
                                                          2: [4, 1, 0],
                                                          3: [5, 3, 1],
                                                          4: [3, 4, 0],
                                                          5: [5, 3, 0]}

    for i in range(0, 100):
        print(i)

        curr_number = bin(i)[2::]
        print(f"curr number: {curr_number}")

        real_answer: str = bin(i+3)[2::]
        print(f"real answer: {real_answer}")

        machine = MooreMachine(bin(i)[2::], plus_three_states_dict)
        print(f"machine ans: {machine.GetAnswer()}")
        print()

    # bigger testing
    for i in range(0, 10000):
        machine = MooreMachine(bin(i)[2::], plus_three_states_dict)
        assert (bin(i+3)[2::] == machine.GetAnswer())
