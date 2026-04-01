"""
Базовые классы для автоматов Мили и Мура.

Содержит абстрактные классы, определяющие общий интерфейс
и поведение для всех типов конечных автоматов.
"""

from .entity_api import BaseEntityApi
from .machine import BaseMachine
from .state import BaseState
from .transition import BaseTransition


__all__ = [
  "BaseEntityApi",
  "BaseMachine",
  "BaseState",
  "BaseTransition",
]
