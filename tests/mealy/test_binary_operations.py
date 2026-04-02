import pytest

from tests.utils.binary_helpers import make_mealy_from_dict


# Автомат Мили для умножения на 3
MEALY_MUL_THREE = {
  "S_0": {0: ("S_0", 0), 1: ("S_1", 1)},
  "S_1": {0: ("S_0", 1), 1: ("S_2", 0)},
  "S_2": {0: ("S_1", 0), 1: ("S_2", 1)},
}


class TestMealyMulThree:
  @pytest.mark.parametrize(
    "number,expected",
    [
      (0, "0"),
      (1, "11"),
      (2, "110"),
      (3, "1001"),
      (4, "1100"),
      (5, "1111"),
      (6, "10010"),
      (7, "10101"),
      (8, "11000"),
      (9, "11011"),
      (10, "11110"),
    ],
  )
  def test_mul_three_small(self, number: int, expected: str):
    input_str = "0" * 4 + bin(number)[2:]

    machine = make_mealy_from_dict(MEALY_MUL_THREE, "S_0", input_str)
    machine.run_all(raise_on_error=False)

    result = machine.get_final_result()
    result = (result.lstrip("0") or "0") if result else "0"

    assert result == expected

  def test_mul_three_range(self):
    for number in range(0, 100):
      expected = bin(number * 3)[2:]
      input_str = "0" * 10 + bin(number)[2:]

      machine = make_mealy_from_dict(MEALY_MUL_THREE, "S_0", input_str)
      machine.run_all(raise_on_error=False)

      result = machine.get_final_result()
      result = (result.lstrip("0") or "0") if result else "0"

      assert result == expected
