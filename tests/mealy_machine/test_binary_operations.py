import pytest

from tests.utils.binary_machine_helpers import make_binary_machine, run_binary_test


MUL_THREE_STATES = {
  "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
  "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
  "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
}

MUL_THREE_PLUS_ONE_STATES = {
  "S_0": {0: ("S_1", 1), 1: ("S_4", 0)},
  "S_1": {0: ("S_1", 0), 1: ("S_2", 1)},
  "S_2": {0: ("S_1", 1), 1: ("S_3", 0)},
  "S_3": {0: ("S_2", 0), 1: ("S_3", 1)},
  "S_4": {0: ("S_5", 0), 1: ("S_6", 1)},
  "S_5": {0: ("S_1", 1), 1: ("S_4", 0)},
  "S_6": {0: ("S_2", 0), 1: ("S_6", 1)},
}

MUL_THREE_PLUS_TWO_STATES = {
  "S_0": {0: ("S_1", 0), 1: ("S_0", 1)},
  "S_1": {0: ("S_2", 1), 1: ("S_5", 0)},
  "S_2": {0: ("S_2", 0), 1: ("S_3", 1)},
  "S_3": {0: ("S_2", 1), 1: ("S_4", 0)},
  "S_4": {0: ("S_3", 0), 1: ("S_4", 1)},
  "S_5": {0: ("S_1", 0), 1: ("S_6", 1)},
  "S_6": {0: ("S_3", 0), 1: ("S_6", 1)},
}


class TestBinaryOperations:
  @pytest.mark.parametrize(
    "number,expected", [(0, "0"), (1, "11"), (2, "110"), (5, "1111"), (10, "11110")]
  )
  def test_mul_three_small(self, number, expected):
    run_binary_test(MUL_THREE_STATES, "S_0", number, expected)

  def test_mul_three_normal(self):
    for number in range(10000):
      expected = bin(number * 3)[2:]
      run_binary_test(
        MUL_THREE_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  @pytest.mark.parametrize(
    "number,expected", [(0, "1"), (1, "100"), (2, "111"), (5, "10000"), (10, "11111")]
  )
  def test_mul_three_plus_one_small(self, number, expected):
    run_binary_test(MUL_THREE_PLUS_ONE_STATES, "S_0", number, expected)

  def test_mul_three_plus_one_normal(self):
    for number in range(10000):
      expected = bin(number * 3 + 1)[2:]
      run_binary_test(
        MUL_THREE_PLUS_ONE_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  @pytest.mark.parametrize(
    "number,expected", [(0, "10"), (1, "101"), (2, "1000"), (5, "10001"), (10, "100000")]
  )
  def test_mul_three_plus_two_small(self, number, expected):
    run_binary_test(MUL_THREE_PLUS_TWO_STATES, "S_0", number, expected)

  def test_mul_three_plus_two_normal(self):
    for number in range(10000):
      expected = bin(number * 3 + 2)[2:]
      run_binary_test(
        MUL_THREE_PLUS_TWO_STATES, "S_0", number, expected, add_zeros=True, zeros_amount=4
      )

  def test_leading_zeros_mul_three(self):
    machine_with_zeros = make_binary_machine(
      MUL_THREE_STATES, "S_0", "101", add_zeros=True, zeros_amount=4
    )
    machine_with_zeros.run_all()
    result_with_zeros = machine_with_zeros.get_final_result()
    result_with_zeros = result_with_zeros.lstrip("0") if result_with_zeros else "0"

    machine_without_zeros = make_binary_machine(
      MUL_THREE_STATES, "S_0", "101", add_zeros=False
    )
    machine_without_zeros.run_all()
    result_without_zeros = machine_without_zeros.get_final_result()
    result_without_zeros = (
      result_without_zeros.lstrip("0") if result_without_zeros else "0"
    )

    assert result_with_zeros == "1111"
    assert result_without_zeros == "111"
