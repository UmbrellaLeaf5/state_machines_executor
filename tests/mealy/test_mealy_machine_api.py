import pytest

from src.state_machines import MealyMachine, MealyState, MealyStepReason


class TestMealyMachineAPI:
  def test_add_duplicate_state(self, empty_machine):
    empty_machine.add_state(MealyState("A", {}))
    with pytest.raises(ValueError, match="State 'A' already exists"):
      empty_machine.add_state(MealyState("A", {}))

  def test_remove_state(self, empty_machine):
    empty_machine.add_state(MealyState("A", {}))
    empty_machine.remove_state("A")
    assert "A" not in empty_machine.get_state_names()

  def test_remove_current_state_warns(self, empty_machine):
    empty_machine.add_state(MealyState("A", {}))
    empty_machine.update_current_data("A", 0, 0)
    with pytest.warns(UserWarning, match="Removing current state 'A'"):
      empty_machine.remove_state("A")
    assert empty_machine.get_current_state_name() is None

  def test_update_states_with_duplicate(self, empty_machine):
    with pytest.raises(ValueError, match="Duplicate state name in input: A"):
      empty_machine.update_states(["A", "A"])

  def test_add_transition_duplicate_no_replace(self, empty_machine):
    def cond(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_machine.add_transition("A", "B", cond, func, proc)
    with pytest.raises(ValueError, match="already exists"):
      empty_machine.add_transition("A", "B", cond, func, proc, replace=False)

  def test_add_transition_replace(self, empty_machine):
    def cond1(input):
      return True

    def cond2(input):
      return False

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_machine.add_transition("A", "B", cond1, func, proc)
    empty_machine.add_transition("A", "B", cond2, func, proc, replace=True)

    transitions = empty_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][1] is cond2

  def test_run_once_not_ready(self, empty_machine):
    with pytest.raises(RuntimeError, match="Current state not set"):
      empty_machine.run_once()

  def test_run_once_no_transition(self, empty_machine):
    empty_machine.add_state(MealyState("A", {}))
    empty_machine.update_current_data("A", 0, 0)

    with pytest.warns(UserWarning, match="No transitions in state 'A'"):
      result = empty_machine.run_once()

    assert result.reason == MealyStepReason.NO_TRANSITION

  def test_run_once_ambiguous(self, empty_machine):
    def cond_true(input):
      return True

    def func(previous_output):
      return previous_output

    def proc(input):
      return input

    empty_machine.add_transition("A", "B", cond_true, func, proc)
    empty_machine.add_transition("A", "C", cond_true, func, proc)
    empty_machine.update_current_data("A", 0, 0)

    with pytest.raises(RuntimeError) as exc:
      empty_machine.run_once()

    msg = str(exc.value)
    assert "Ambiguous transition: 2 transitions available" in msg
    assert "Current state: 'A'" in msg
    assert "to 'B' with:" in msg
    assert "to 'C' with:" in msg

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
    assert results[0].reason == MealyStepReason.EXCEPTION
    assert isinstance(results[0].exception, RuntimeError)
    assert results[0].exception.args[0] == "boom"

  def test_run_all_stop_condition(self, machine_with_two_states):
    machine = MealyMachine[str, str](stop_condition=lambda input: len(input) == 0)

    machine.add_state(MealyState("A", {}))
    machine.add_transition(
      "A",
      "B",
      trans_condition=lambda input: True,
      output_function=lambda previous_output: previous_output,
      input_processor=lambda input: input,
    )
    machine.add_transition(
      "B",
      "A",
      trans_condition=lambda input: True,
      output_function=lambda previous_output: previous_output,
      input_processor=lambda input: input,
    )
    machine.update_current_data("A", "", "0")

    result = machine.run_all()[-1]
    assert result.reason == MealyStepReason.STOP_CONDITION

  def test_results_methods(self, simple_machine):
    simple_machine.update_current_data("A", 0, 0)
    simple_machine.run_once()

    results = simple_machine.get_results()
    assert len(results) == 1

    data = simple_machine.get_results_data()
    assert len(data) == 1
    assert data[0].output == 1

    tuples = simple_machine.get_results_tuple()
    assert tuples[0] == (1, 1)

    outputs = simple_machine.get_only_results()
    assert outputs[0] == 1

    final = simple_machine.get_final_result()
    assert final == 1

  def test_clear_results(self, simple_machine):
    simple_machine.update_current_data("A", 0, 0)
    simple_machine.run_once()
    simple_machine.clear_results()
    assert simple_machine.get_results() == []
