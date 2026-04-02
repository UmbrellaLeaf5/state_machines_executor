from src.state_machines import MealyMachine, MooreMachine


def make_condition(bit: str):
  def condition(input: str) -> bool:
    return input[-1] == bit

  return condition


def shift_processor(input: str) -> str:
  return input[:-1]


def shift_add_zero_processor(input: str) -> str:
  return "0" + input[:-1]


def make_output(bit: str):
  def add(previous_output: str) -> str:
    return bit + previous_output

  return add


def add_nothing(previous_output: str) -> str:
  return previous_output


def make_mealy_from_dict(
  states_dict: dict, initial_state: str, input_str: str
) -> MealyMachine[str, str]:
  transitions = []

  for src, trans in states_dict.items():
    for bit, (dst, out_bit) in trans.items():
      cond = make_condition(str(bit))
      func = make_output(str(out_bit))
      transitions.append((src, dst, cond, func, shift_processor))

  return MealyMachine(
    transitions=transitions,
    initial_state=initial_state,
    initial_output="",
    initial_input=input_str,
    stop_condition=lambda input: len(input) == 0,
  )


def make_moore_from_dict(
  states_dict: dict[str, tuple[dict[int, str], int | None]],
  initial_state: str,
  input_str: str,
) -> MooreMachine[str, str]:
  states = []

  for state_name, (_, output_bit) in states_dict.items():
    if output_bit is not None:
      states.append((state_name, make_output(str(output_bit))))

    else:
      states.append((state_name, add_nothing))

  transitions = []

  for src, (trans_dict, _) in states_dict.items():
    for bit, dst in trans_dict.items():
      cond = make_condition(str(bit))

      if src == initial_state:
        processor = shift_add_zero_processor

      else:
        processor = shift_processor

      transitions.append((src, dst, cond, processor))

  return MooreMachine(
    states=states,
    transitions=transitions,
    initial_state=initial_state,
    initial_output="",
    initial_input=input_str,
    stop_condition=lambda input: len(input) == 0,
  )
