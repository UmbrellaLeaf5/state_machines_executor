"""
Пример автомата Мура: прибавление 3 к двоичному числу.

Автомат читает двоичное число (строку из '0' и '1') от младшего бита к старшему
и выдаёт результат прибавления 3 в двоичном виде (также от младшего бита).

Схема автомата:
    S_0 — начальное состояние (выход не определён)
    S_1 — остаток 1, выход 1
    S_2 — остаток 0, выход 0
    S_3 — остаток 0, выход 1
    S_4 — остаток 1, выход 0
    S_5 — остаток 0, выход 0

На вход подаётся двоичное число, каждый такт считывается очередной бит.
Выход определяется текущим состоянием (классика Мура).
"""

from src.state_machines import MooreMachine, MooreTransition


def add_nothing(previous_output: str) -> str:
  """Возвращает выход без изменений (для начального состояния)."""
  return previous_output


def add_zero(previous_output: str) -> str:
  """Добавляет '0' в начало выходной строки."""
  return "0" + previous_output


def add_one(previous_output: str) -> str:
  """Добавляет '1' в начало выходной строки."""
  return "1" + previous_output


def shift(input: str) -> str:
  """Удаляет последний (прочитанный) бит из входной строки."""
  return input[:-1]


def shift_add_zero(input: str) -> str:
  """Добавляет '0' в начало и удаляет последний бит."""
  return "0" + input[:-1]


def zero_condition(input: str) -> bool:
  """Условие: последний бит входной строки равен '0'."""
  return input[-1] == "0"


def one_condition(input: str) -> bool:
  """Условие: последний бит входной строки равен '1'."""
  return input[-1] == "1"


def create_plus_three_machine() -> MooreMachine[str, str]:
  """Создаёт и возвращает автомат Мура для прибавления 3."""

  return MooreMachine[str, str](
    states=[
      # (имя_состояния, функция_выхода)
      ("S_0", add_nothing),  # начальное состояние
      ("S_1", add_one),  # выход 1
      ("S_2", add_zero),  # выход 0
      ("S_3", add_one),  # выход 1
      ("S_4", add_zero),  # выход 0
      ("S_5", add_zero),  # выход 0
    ],
    transitions=[
      # Из S_0 (начальное состояние) — используется shift_add_zero
      ("S_0", "S_1", zero_condition, shift_add_zero),  # вход 0 → S_1
      MooreTransition("S_0", "S_2", one_condition, shift_add_zero),  # вход 1 → S_2
      # Из S_1
      ("S_1", "S_3", zero_condition, shift),  # вход 0 → S_3
      ("S_1", "S_4", one_condition, shift),  # вход 1 → S_4
      # Из S_2
      ("S_2", "S_4", zero_condition, shift),  # вход 0 → S_4
      ("S_2", "S_1", one_condition, shift),  # вход 1 → S_1
      # Из S_3
      ("S_3", "S_5", zero_condition, shift),  # вход 0 → S_5
      ("S_3", "S_3", one_condition, shift),  # вход 1 → S_3
      # Из S_4
      ("S_4", "S_3", zero_condition, shift),  # вход 0 → S_3
      ("S_4", "S_4", one_condition, shift),  # вход 1 → S_4
      # Из S_5
      ("S_5", "S_5", zero_condition, shift),  # вход 0 → S_5
      ("S_5", "S_3", one_condition, shift),  # вход 1 → S_3
    ],
    initial_state="S_0",
    initial_output="",
    stop_condition=lambda input: len(input) == 0,
  )


def run_example(number: int) -> None:
  """Запускает пример для заданного числа."""

  input_str = bin(number)[2:]  # двоичное представление без префикса '0b'
  # Добавляем ведущие нули для корректной работы автомата
  input_str = "0" * 8 + input_str

  machine = create_plus_three_machine()
  machine.update_current_data(input=input_str)
  machine.run_all(raise_on_error=False)

  result = machine.get_final_result()
  assert result is not None
  result = result.lstrip("0") or "0"

  print(f"Число: {number} ({bin(number)[2:]})")
  print(f"Результат: {result} (ожидалось: {bin(number + 3)[2:]})")
  print(f"Шагов выполнено: {len(machine.get_results())}")
  print()


if __name__ == "__main__":
  print("Автомат Мура: прибавление 3")
  print()

  for n in [0, 1, 2, 5, 10, 42]:
    run_example(n)

  # Подробный вывод с историей выполнения
  print("Детальный разбор для числа 5 (101 в двоичной)")
  print()

  machine = create_plus_three_machine()
  machine.update_current_data(input="00000000101")  # 5 с ведущими нулями
  machine.run_all(raise_on_error=False)

  print("История шагов (вход после обработки, выход):")
  for i, step in enumerate(machine.get_results()):
    print(
      f"  Шаг {i + 1}: "
      f"вход = '{step.data.processed_input}', "
      f"выход = '{step.data.output}', "
      f"состояние = '{step.reason}'"
    )

  result = machine.get_final_result()
  assert result is not None
  result = result.lstrip("0") or "0"

  print()
  print(f"Финальный результат: {result}")
  print(f"Ожидалось: {bin(5 + 3)[2:]}")
