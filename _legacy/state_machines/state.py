from dataclasses import dataclass
from typing import Literal


BinaryDigit = Literal[0, 1]
StateNameType = str | int


@dataclass
class MealyState:
  state_if_0: StateNameType
  state_if_1: StateNameType

  digit_if_0: BinaryDigit
  digit_if_1: BinaryDigit

  def DigitIf(self, digit: BinaryDigit) -> BinaryDigit:
    return self.digit_if_0 if digit == 0 else self.digit_if_1

  def StateIf(self, digit: BinaryDigit) -> StateNameType:
    return self.state_if_0 if digit == 0 else self.state_if_1


@dataclass
class MooreState:
  state_if_0: StateNameType
  state_if_1: StateNameType

  digit: BinaryDigit | None

  def StateIf(self, digit: BinaryDigit) -> StateNameType:
    return self.state_if_0 if digit == 0 else self.state_if_1

  def Digit(self) -> BinaryDigit | None:
    return self.digit
