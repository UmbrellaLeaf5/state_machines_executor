from state_machines.moore_machine import MooreMachine


def NumberPlusThree() -> None:
  print("NumberPlusThree")

  print()

  # словарь конечного автомата, который прибавляет 3 (bin: 11) к исходному числу
  plus_three_states_dict: MooreMachine.Dict = {
    "S_0": ({0: "S_1", 1: "S_2"}, None),
    "S_1": ({0: "S_3", 1: "S_4"}, 1),
    "S_2": ({0: "S_4", 1: "S_1"}, 0),
    "S_3": ({0: "S_5", 1: "S_3"}, 1),
    "S_4": ({0: "S_3", 1: "S_4"}, 0),
    "S_5": ({0: "S_5", 1: "S_3"}, 0),
  }

  for i in range(0, 100):
    print(i)

    curr_number = bin(i)[2::]
    print(f"curr number: {curr_number}")

    real_answer: str = bin(i + 3)[2::]
    print(f"real answer: {real_answer}")

    machine = MooreMachine(bin(i)[2::], plus_three_states_dict, "S_0")
    print(f"machine ans: {machine.GetAnswer()}")
    print()

  # bigger testing
  for i in range(0, 10000):
    machine = MooreMachine(bin(i)[2::], plus_three_states_dict, "S_0")
    assert bin(i + 3)[2::] == machine.GetAnswer()


if __name__ == "__main__":
  NumberPlusThree()
