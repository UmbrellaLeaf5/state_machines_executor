from uniclasses.mealy_machine import MealyMachine


def NumberMulThree() -> None:
  print("NumberMulThree")

  print()

  # словарь конечного автомата, который умножает на 3 (bin: 11) исходное число
  plus_mul_states_dict: MealyMachine.Dict = {
    "S_0": {0: ["S_0", 0], 1: ["S_1", 1]},
    "S_1": {0: ["S_0", 1], 1: ["S_2", 0]},
    "S_2": {0: ["S_1", 0], 1: ["S_2", 1]},
  }

  for i in range(0, 100):
    print(i)

    curr_number = bin(i)[2::]
    print(f"curr number: {curr_number}")

    real_answer: str = bin(i * 3)[2::]
    print(f"real answer: {real_answer}")

    machine = MealyMachine(bin(i)[2::], plus_mul_states_dict, "S_0")
    print(f"machine ans: {machine.GetAnswer()}")

    print()

  # bigger testing
  for i in range(0, 10000):
    machine = MealyMachine(bin(i)[2::], plus_mul_states_dict, "S_0")
    assert bin(i * 3)[2::] == machine.GetAnswer()


if __name__ == "__main__":
  NumberMulThree()
