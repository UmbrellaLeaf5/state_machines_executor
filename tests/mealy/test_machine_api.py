import pytest

from src.state_machines import MealyMachine, MealyState, MealyTransition, StepReason


class TestMealyMachineAPI:
  def test_add_duplicate_state(self, empty_mealy_machine: MealyMachine):
    empty_mealy_machine.add_state(MealyState("A", {}))
    with pytest.raises(ValueError, match="State 'A' already exists"):
      empty_mealy_machine.add_state(MealyState("A", {}))

  def test_remove_state(self, empty_mealy_machine: MealyMachine):
    empty_mealy_machine.add_state(MealyState("A", {}))
    empty_mealy_machine.remove_state("A")
    assert "A" not in empty_mealy_machine.get_state_names()

  def test_remove_current_state_warns(self, empty_mealy_machine: MealyMachine):
    empty_mealy_machine.add_state(MealyState("A", {}))
    empty_mealy_machine.update_current_data("A", 0, 0)
    with pytest.warns(UserWarning, match="Removing current state 'A'"):
      empty_mealy_machine.remove_state("A")
    assert empty_mealy_machine.get_current_state_name() is None

  def test_update_states_with_duplicate(self, empty_mealy_machine: MealyMachine):
    with pytest.raises(ValueError, match="Duplicate state name in input: A"):
      empty_mealy_machine.update_states(["A", "A"])

  def test_add_transition_duplicate_no_replace(self, empty_mealy_machine: MealyMachine):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_mealy_machine.add_transition("A", "B", cond, func, proc)
    with pytest.raises(ValueError, match="already exists"):
      empty_mealy_machine.add_transition("A", "B", cond, func, proc, replace=False)

  def test_add_transition_replace(self, empty_mealy_machine: MealyMachine):
    def cond1(input):
      return True

    def cond2(input):
      return False

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_mealy_machine.add_transition("A", "B", cond1, func, proc)
    empty_mealy_machine.add_transition("A", "B", cond2, func, proc, replace=True)

    transitions = empty_mealy_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  # ----- Новые тесты на add_transition_entity -----

  def test_add_transition_entity_from_object(self, empty_mealy_machine: MealyMachine):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition = MealyTransition("A", "B", cond, func, proc)
    empty_mealy_machine.add_transition_entity(transition)

    assert empty_mealy_machine.get_state_transitions_amount("A") == 1
    assert "A" in empty_mealy_machine.get_state_names()
    assert "B" in empty_mealy_machine.get_state_names()

  def test_add_transition_entity_from_tuple(self, empty_mealy_machine: MealyMachine):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition = ("A", "B", cond, func, proc)
    empty_mealy_machine.add_transition_entity(transition)

    assert empty_mealy_machine.get_state_transitions_amount("A") == 1

  def test_add_transition_entity_duplicate_no_replace(
    self, empty_mealy_machine: MealyMachine
  ):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition = MealyTransition("A", "B", cond, func, proc)
    empty_mealy_machine.add_transition_entity(transition)

    with pytest.raises(ValueError, match="already exists"):
      empty_mealy_machine.add_transition_entity(transition, replace=False)

  def test_add_transition_entity_replace(self, empty_mealy_machine: MealyMachine):
    def cond1(input):
      return True

    def cond2(input):
      return False

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition1 = MealyTransition("A", "B", cond1, func, proc)
    transition2 = MealyTransition("A", "B", cond2, func, proc)

    empty_mealy_machine.add_transition_entity(transition1)
    empty_mealy_machine.add_transition_entity(transition2, replace=True)

    transitions = empty_mealy_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  def test_add_transition_entity_invalid_type(self, empty_mealy_machine: MealyMachine):
    with pytest.raises(TypeError, match=r"Expected .* or tuple"):
      empty_mealy_machine.add_transition_entity("not a transition")  # type: ignore

  # ----- Новые тесты на update_transitions со смешанными типами -----

  def test_update_transitions_mixed_types(self, empty_mealy_machine: MealyMachine):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition_tuple = ("A", "B", cond, func, proc)
    transition_obj = MealyTransition("B", "C", cond, func, proc)

    empty_mealy_machine.update_transitions([transition_tuple, transition_obj])

    assert empty_mealy_machine.get_state_transitions_amount("A") == 1
    assert empty_mealy_machine.get_state_transitions_amount("B") == 1
    assert "C" in empty_mealy_machine.get_state_names()

  def test_update_transitions_with_replace_flag(self, empty_mealy_machine: MealyMachine):
    def cond1(input):
      return True

    def cond2(input):
      return False

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition1 = ("A", "B", cond1, func, proc)
    transition2 = MealyTransition("A", "B", cond2, func, proc)

    empty_mealy_machine.update_transitions([transition1])
    empty_mealy_machine.update_transitions([transition2], replace=True)

    transitions = empty_mealy_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  def test_update_transitions_creates_states_automatically(
    self, empty_mealy_machine: MealyMachine
  ):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_mealy_machine.update_transitions([("A", "B", cond, func, proc)])

    assert "A" in empty_mealy_machine.get_state_names()
    assert "B" in empty_mealy_machine.get_state_names()

  # ----- Тесты на конструктор со смешанными типами -----

  def test_constructor_with_mixed_transitions(self):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transition_tuple = ("A", "B", cond, func, proc)
    transition_obj = MealyTransition("B", "C", cond, func, proc)

    machine = MealyMachine(
      transitions=[transition_tuple, transition_obj],
      initial_state="A",
      initial_output=0,
      initial_input=0,
    )

    assert machine.get_state_transitions_amount("A") == 1
    assert machine.get_state_transitions_amount("B") == 1

  def test_constructor_with_only_objects(self):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    transitions = [
      MealyTransition[str, str]("A", "B", cond, func, proc),
      MealyTransition("B", "A", cond, func, proc),
    ]

    machine = MealyMachine(
      transitions=transitions,
      initial_state="A",
      initial_output=0,
      initial_input=0,
    )

    assert machine.get_state_transitions_amount("A") == 1
    assert machine.get_state_transitions_amount("B") == 1

  # ----- Остальные старые тесты -----

  def test_run_once_not_ready(self, empty_mealy_machine: MealyMachine):
    with pytest.raises(RuntimeError, match="Current state not set"):
      empty_mealy_machine.run_once()

  def test_run_once_no_transition(self, empty_mealy_machine: MealyMachine):
    empty_mealy_machine.add_state(MealyState("A", {}))
    empty_mealy_machine.update_current_data("A", 0, 0)

    with pytest.warns(UserWarning, match="No transitions in state 'A'"):
      result = empty_mealy_machine.run_once()

    assert result.reason == StepReason.NO_TRANSITION

  def test_run_once_ambiguous(self, empty_mealy_machine: MealyMachine):
    def cond_true(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_mealy_machine.add_transition("A", "B", cond_true, func, proc)
    empty_mealy_machine.add_transition("A", "C", cond_true, func, proc)
    empty_mealy_machine.update_current_data("A", 0, 0)

    with pytest.raises(RuntimeError) as exc:
      empty_mealy_machine.run_once()

    msg = str(exc.value)
    assert "Ambiguous transition: 2 transitions available" in msg
    assert "Current state: 'A'" in msg
    assert "target_state: 'B'" in msg
    assert "target_state: 'C'" in msg

  def test_run_once_exception_in_condition(self):
    machine = MealyMachine[str, str]()

    def bad_cond(input):
      raise RuntimeError("boom")

    machine.add_transition(
      "A", "B", bad_cond, lambda previous_output: previous_output, lambda input: input
    )
    machine.update_current_data("A", "", "0")

    with pytest.raises(RuntimeError, match="boom"):
      machine.run_once()

  def test_run_all_catches_exception(self):
    machine = MealyMachine[str, str]()

    def bad_cond(input):
      raise RuntimeError("boom")

    machine.add_transition(
      "A", "B", bad_cond, lambda previous_output: previous_output, lambda input: input
    )
    machine.update_current_data("A", "", "0")

    results = machine.run_all(raise_on_error=False)

    assert len(results) == 1
    assert results[0].reason == StepReason.EXCEPTION
    assert isinstance(results[0].exception, RuntimeError)
    assert results[0].exception.args[0] == "boom"

  def test_run_all_stop_condition(self):
    machine = MealyMachine[str, str](stop_condition=lambda input: len(input) == 0)

    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    machine.add_transition("A", "A", cond, func, proc)
    machine.update_current_data("A", "", "0")

    result = machine.run_all()[-1]
    assert result.reason == StepReason.STOP_CONDITION

  def test_results_methods(self, simple_mealy_machine: MealyMachine):
    simple_mealy_machine.update_current_data("A", 0, 0)
    simple_mealy_machine.run_once()

    results = simple_mealy_machine.get_results()
    assert len(results) == 1

    data = simple_mealy_machine.get_results_data()
    assert len(data) == 1
    assert data[0].output == 1

    tuples = simple_mealy_machine.get_results_tuple()
    assert tuples[0] == (1, 1)

    outputs = simple_mealy_machine.get_only_results()
    assert outputs[0] == 1

    final = simple_mealy_machine.get_final_result()
    assert final == 1

  def test_clear_results(self, simple_mealy_machine: MealyMachine):
    simple_mealy_machine.update_current_data("A", 0, 0)
    simple_mealy_machine.run_once()
    simple_mealy_machine.clear_results()
    assert simple_mealy_machine.get_results() == []

  def test_common_kwargs(self):
    machine = MealyMachine[int, int]()

    def cond(input, threshold=0):
      return input > threshold

    def func(previous_output, multiplier=1):
      return previous_output * multiplier

    def proc(input, offset=0):
      return input + offset

    machine.add_transition("A", "A", cond, func, proc)
    machine.update_common_kwargs(
      condition_kwargs={"threshold": 5},
      function_kwargs={"multiplier": 2},
      processor_kwargs={"offset": 1},
    )
    machine.update_current_data("A", 10, 1)

    result = machine.run_once()
    assert result.reason == StepReason.SUCCESS
    assert result.data.processed_input == 11  # 10 + offset=1  # noqa: PLR2004
    assert result.data.output == 2  # 1 * multiplier=2  # noqa: PLR2004
