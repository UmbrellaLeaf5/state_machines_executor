import pytest

from src.state_machines import MooreMachine, MooreState, MooreTransition, StepReason


@pytest.fixture
def empty_moore_machine():
  """Возвращает пустой автомат Мура."""
  return MooreMachine()


@pytest.fixture
def simple_moore_machine():
  """Возвращает простой автомат Мура с одним состоянием."""
  machine = MooreMachine()

  def cond(input):
    return True

  def output_func(previous_output):
    return previous_output + 1 if isinstance(previous_output, int) else 1

  def proc(input):
    return input + 1 if isinstance(input, int) else 1

  machine.add_state(MooreState("A", output_func, {}))
  machine.add_transition("A", "A", cond, proc)

  return machine


@pytest.fixture
def moore_machine_with_two_states():
  """Возвращает автомат Мура с двумя состояниями."""
  machine = MooreMachine()

  def cond(input):
    return True

  def output_func(previous_output):
    return previous_output

  def proc(input):
    return input

  machine.add_state(MooreState("A", output_func, {}))
  machine.add_state(MooreState("B", output_func, {}))
  machine.add_transition("A", "B", cond, proc)
  machine.add_transition("B", "A", cond, proc)

  return machine


class TestMooreMachineAPI:
  # ----- Тесты состояний -----

  def test_add_state(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    state = MooreState("A", output_func, {})
    empty_moore_machine.add_state(state)
    assert "A" in empty_moore_machine.get_state_names()

  def test_add_duplicate_state(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    with pytest.raises(ValueError, match="State 'A' already exists"):
      empty_moore_machine.add_state(MooreState("A", output_func, {}))

  def test_remove_state(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.remove_state("A")
    assert "A" not in empty_moore_machine.get_state_names()

  def test_remove_current_state_warns(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.update_current_data("A", 0, 0)
    with pytest.warns(UserWarning, match="Removing current state 'A'"):
      empty_moore_machine.remove_state("A")
    assert empty_moore_machine.get_current_state_name() is None

  def test_set_states_with_strings(self, empty_moore_machine):
    def output_func1(previous_output):
      return previous_output

    def output_func2(previous_output):
      return previous_output

    empty_moore_machine.set_states(
      [
        ("A", output_func1),
        ("B", output_func2),
      ]
    )
    assert set(empty_moore_machine.get_state_names()) == {"A", "B"}

  def test_set_states_with_objects(self, empty_moore_machine):
    def output_func1(previous_output):
      return previous_output

    def output_func2(previous_output):
      return previous_output

    state1 = MooreState("A", output_func1, {})
    state2 = MooreState("B", output_func2, {})
    empty_moore_machine.set_states([state1, state2])
    assert set(empty_moore_machine.get_state_names()) == {"A", "B"}

  def test_set_states_mixed(self, empty_moore_machine):
    def output_func1(previous_output):
      return previous_output

    def output_func2(previous_output):
      return previous_output

    state1 = MooreState("A", output_func1, {})
    empty_moore_machine.set_states([state1, ("B", output_func2)])
    assert set(empty_moore_machine.get_state_names()) == {"A", "B"}

  def test_update_states_mixed(self, empty_moore_machine):
    def output_func1(previous_output):
      return previous_output

    def output_func2(previous_output):
      return previous_output

    state1 = MooreState("A", output_func1, {})
    empty_moore_machine.update_states([state1, ("B", output_func2)])
    assert set(empty_moore_machine.get_state_names()) == {"A", "B"}

  # ----- Тесты переходов -----

  def test_add_transition(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))
    empty_moore_machine.add_transition("A", "B", cond, proc)

    assert empty_moore_machine.get_state_transitions_amount("A") == 1

  def test_add_transition_missing_state_raises(self, empty_moore_machine):
    def cond(input):
      return True

    def proc(input):
      return input

    with pytest.raises(KeyError, match="not found"):
      empty_moore_machine.add_transition("A", "B", cond, proc)

  def test_add_transition_duplicate_no_replace(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))
    empty_moore_machine.add_transition("A", "B", cond, proc)

    with pytest.raises(ValueError, match="already exists"):
      empty_moore_machine.add_transition("A", "B", cond, proc, replace=False)

  def test_add_transition_replace(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond1(input):
      return True

    def cond2(input):
      return False

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))
    empty_moore_machine.add_transition("A", "B", cond1, proc)
    empty_moore_machine.add_transition("A", "B", cond2, proc, replace=True)

    transitions = empty_moore_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  # ----- Тесты add_transition_entity -----

  def test_add_transition_entity_from_object(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))

    transition = MooreTransition("A", "B", cond, proc)
    empty_moore_machine.add_transition_entity(transition)

    assert empty_moore_machine.get_state_transitions_amount("A") == 1

  def test_add_transition_entity_from_tuple(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))

    transition = ("A", "B", cond, proc)
    empty_moore_machine.add_transition_entity(transition)

    assert empty_moore_machine.get_state_transitions_amount("A") == 1

  def test_add_transition_entity_duplicate_no_replace(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))

    transition = MooreTransition("A", "B", cond, proc)
    empty_moore_machine.add_transition_entity(transition)

    with pytest.raises(ValueError, match="already exists"):
      empty_moore_machine.add_transition_entity(transition, replace=False)

  def test_add_transition_entity_replace(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond1(input):
      return True

    def cond2(input):
      return False

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))

    transition1 = MooreTransition("A", "B", cond1, proc)
    transition2 = MooreTransition("A", "B", cond2, proc)

    empty_moore_machine.add_transition_entity(transition1)
    empty_moore_machine.add_transition_entity(transition2, replace=True)

    transitions = empty_moore_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  def test_add_transition_entity_invalid_type(self, empty_moore_machine):
    with pytest.raises(TypeError, match=r"Expected .* or tuple"):
      empty_moore_machine.add_transition_entity("not a transition")

  # ----- Тесты update_transitions -----

  def test_update_transitions_mixed_types(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))
    empty_moore_machine.add_state(MooreState("C", output_func, {}))

    transition_tuple = ("A", "B", cond, proc)
    transition_obj = MooreTransition("B", "C", cond, proc)

    empty_moore_machine.update_transitions([transition_tuple, transition_obj])

    assert empty_moore_machine.get_state_transitions_amount("A") == 1
    assert empty_moore_machine.get_state_transitions_amount("B") == 1

  def test_update_transitions_with_replace_flag(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond1(input):
      return True

    def cond2(input):
      return False

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))

    transition1 = ("A", "B", cond1, proc)
    transition2 = MooreTransition("A", "B", cond2, proc)

    empty_moore_machine.update_transitions([transition1])
    empty_moore_machine.update_transitions([transition2], replace=True)

    transitions = empty_moore_machine.get_state_transitions("A")
    assert len(transitions) == 1
    assert transitions[0][2] is cond2

  # ----- Тесты конструктора -----

  def test_constructor_with_mixed_states(self):
    def output_func1(previous_output):
      return previous_output

    def output_func2(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    state1 = MooreState("A", output_func1, {})
    machine = MooreMachine(
      states=[state1, ("B", output_func2)],
      transitions=[("A", "B", cond, proc)],
      initial_state="A",
      initial_output=0,
      initial_input=0,
    )

    assert set(machine.get_state_names()) == {"A", "B"}

  def test_constructor_with_mixed_transitions(self):
    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    transition_tuple = ("A", "B", cond, proc)
    transition_obj = MooreTransition("B", "C", cond, proc)

    machine = MooreMachine(
      states=[
        ("A", output_func),
        ("B", output_func),
        ("C", output_func),
      ],
      transitions=[transition_tuple, transition_obj],
      initial_state="A",
      initial_output=0,
      initial_input=0,
    )

    assert machine.get_state_transitions_amount("A") == 1
    assert machine.get_state_transitions_amount("B") == 1

  # ----- Тесты выполнения -----

  def test_validate_missing_output_function(self, empty_moore_machine):
    empty_moore_machine.add_state(MooreState("A", None, {}))  # type: ignore
    with pytest.raises(ValueError, match="States without output function"):
      empty_moore_machine.validate()

  def test_run_once_not_ready(self, empty_moore_machine):
    with pytest.raises(RuntimeError, match="Current state not set"):
      empty_moore_machine.run_once()

  def test_run_once_no_transition(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.update_current_data("A", 0, 0)

    with pytest.warns(UserWarning, match="No transitions in state 'A'"):
      result = empty_moore_machine.run_once()

    assert result.reason == StepReason.NO_TRANSITION

  def test_run_once_ambiguous(self, empty_moore_machine):
    def output_func(previous_output):
      return previous_output

    def cond_true(input):
      return True

    def proc(input):
      return input

    empty_moore_machine.add_state(MooreState("A", output_func, {}))
    empty_moore_machine.add_state(MooreState("B", output_func, {}))
    empty_moore_machine.add_state(MooreState("C", output_func, {}))
    empty_moore_machine.add_transition("A", "B", cond_true, proc)
    empty_moore_machine.add_transition("A", "C", cond_true, proc)
    empty_moore_machine.update_current_data("A", 0, 0)

    with pytest.raises(RuntimeError) as exc:
      empty_moore_machine.run_once()

    msg = str(exc.value)
    assert "Ambiguous transition: 2 transitions available" in msg
    assert "Current state: 'A'" in msg

  def test_run_once_exception_in_condition(self):
    machine = MooreMachine[str, str]()

    def output_func(previous_output):
      return previous_output

    def bad_cond(input):
      raise RuntimeError("boom")

    def proc(input):
      return input

    machine.add_state(MooreState("A", output_func, {}))
    machine.add_state(MooreState("B", output_func, {}))
    machine.add_transition("A", "B", bad_cond, proc)
    machine.update_current_data("A", "", "0")

    with pytest.raises(RuntimeError, match="boom"):
      machine.run_once()

  def test_run_all_catches_exception(self):
    machine = MooreMachine[str, str]()

    def output_func(previous_output):
      return previous_output

    def bad_cond(input):
      raise RuntimeError("boom")

    def proc(input):
      return input

    machine.add_state(MooreState("A", output_func, {}))
    machine.add_state(MooreState("B", output_func, {}))
    machine.add_transition("A", "B", bad_cond, proc)
    machine.update_current_data("A", "", "0")

    results = machine.run_all(raise_on_error=False)

    assert len(results) == 1
    assert results[0].reason == StepReason.EXCEPTION
    assert isinstance(results[0].exception, RuntimeError)

  def test_run_all_stop_condition(self):
    machine = MooreMachine[str, str](stop_condition=lambda input: len(input) == 0)

    def output_func(previous_output):
      return previous_output

    def cond(input):
      return True

    def proc(input):
      return input

    machine.add_state(MooreState("A", output_func, {}))
    machine.add_transition("A", "A", cond, proc)
    machine.update_current_data("A", "", "0")

    result = machine.run_all()[-1]
    assert result.reason == StepReason.STOP_CONDITION

  def test_results_methods(self, simple_moore_machine):
    simple_moore_machine.update_current_data("A", 0, 0)
    simple_moore_machine.run_once()

    results = simple_moore_machine.get_results()
    assert len(results) == 1

    data = simple_moore_machine.get_results_data()
    assert len(data) == 1
    assert data[0].output == 1

    tuples = simple_moore_machine.get_results_tuple()
    assert tuples[0] == (1, 1)

    outputs = simple_moore_machine.get_only_results()
    assert outputs[0] == 1

    final = simple_moore_machine.get_final_result()
    assert final == 1

  def test_clear_results(self, simple_moore_machine):
    simple_moore_machine.update_current_data("A", 0, 0)
    simple_moore_machine.run_once()
    simple_moore_machine.clear_results()
    assert simple_moore_machine.get_results() == []

  def test_reset_execution(self, simple_moore_machine):
    simple_moore_machine.update_current_data("A", 0, 0)
    simple_moore_machine.run_once()
    simple_moore_machine.reset_execution()

    assert simple_moore_machine.get_current_state_name() is None
    assert simple_moore_machine.get_current_output() is None
    assert simple_moore_machine.get_current_input() is None
    assert simple_moore_machine.get_results() == []
