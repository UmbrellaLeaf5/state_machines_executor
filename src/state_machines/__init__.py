"""
Пакет state_machines.

Предоставляет реализацию конечных автоматов Мили и Мура для обработки
последовательных входных данных.
"""

from .mealy import MealyMachine, MealyState, MealyTransition
from .moore import MooreMachine, MooreState, MooreTransition
from .utils.protocols import (
  InputProcessorProtocol,
  OutputFunctionProtocol,
  StopConditionProtocol,
  TransConditionProtocol,
)
from .utils.step import StepData, StepReason, StepResult
from .utils.types import Kwargs


__all__ = [
  "InputProcessorProtocol",
  "Kwargs",
  "MealyMachine",
  "MealyState",
  "MealyTransition",
  "MooreMachine",
  "MooreState",
  "MooreTransition",
  "OutputFunctionProtocol",
  "StepData",
  "StepReason",
  "StepResult",
  "StopConditionProtocol",
  "TransConditionProtocol",
]
