import pytest

from tests.utils.binary_helpers import make_moore_from_dict


# Автомат Мура для сложения с 3
MOORE_PLUS_THREE = {
  "S_0": ({0: "S_1", 1: "S_2"}, None),
  "S_1": ({0: "S_3", 1: "S_4"}, 1),
  "S_2": ({0: "S_4", 1: "S_1"}, 0),
  "S_3": ({0: "S_5", 1: "S_3"}, 1),
  "S_4": ({0: "S_3", 1: "S_4"}, 0),
  "S_5": ({0: "S_5", 1: "S_3"}, 0),
}


class TestMoorePlusThree:
  @pytest.mark.parametrize(
    "number,expected",
    [
      (0, "11"),
      (1, "100"),
      (2, "101"),
      (3, "110"),
      (4, "111"),
      (5, "1000"),
      (6, "1001"),
      (7, "1010"),
      (8, "1011"),
      (9, "1100"),
      (10, "1101"),
    ],
  )
  def test_plus_three_small(self, number: int, expected: str):
    input_str = "0" * 8 + bin(number)[2:]

    machine = make_moore_from_dict(MOORE_PLUS_THREE, "S_0", input_str)
    machine.run_all(raise_on_error=False)

    result = machine.get_final_result()
    result = (result.lstrip("0") or "0") if result else "0"

    assert result == expected

  def test_plus_three_range(self):
    for number in range(100):
      expected = bin(number + 3)[2:]
      input_str = "0" * 28 + bin(number)[2:]

      machine = make_moore_from_dict(MOORE_PLUS_THREE, "S_0", input_str)
      machine.run_all(raise_on_error=False)

      result = machine.get_final_result()
      result = (result.lstrip("0") or "0") if result else "0"

      assert result == expected
