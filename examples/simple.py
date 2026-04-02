from src.state_machines import MealyMachine, MooreMachine


def zero_condition(input: str) -> bool:
  return input[-1] == "0"


def add_nothing(previous_output: str) -> str:
  return previous_output


def add_one(previous_output: str) -> str:
  return "1" + previous_output


def shift(input: str) -> str:
  return input[:-1]


machine = MealyMachine(
  transitions=[
    ("S0", "S0", zero_condition, add_one, shift),
  ],
  initial_state="S0",
  initial_output="",
  initial_input="100",
  stop_condition=lambda input: len(input) == 0,
)

machine.run_all()
result = machine.get_final_result()

machine = MooreMachine(
  states=[
    ("S0", add_nothing),
    ("S1", add_one),
  ],
  transitions=[
    ("S0", "S1", zero_condition, shift),
  ],
  initial_state="S0",
  initial_output="",
  initial_input="100",
  stop_condition=lambda input: len(input) == 0,
)

machine.run_all()
result = machine.get_final_result()
