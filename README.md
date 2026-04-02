[![Pytest](https://github.com/UmbrellaLeaf5/state_machines_executor/actions/workflows/pytest.yml/badge.svg)](https://github.com/UmbrellaLeaf5/state_machines_executor/actions/workflows/pytest.yml)

# Исполнитель конечных автоматов Мура и Мили

Создание полноценного исполнителя для упрощения создания конечных автоматов Мура и Мили, получающих на вход двоичное число.

## Возможности

- Полноценная реализация автоматов Мили и Мура
- Поддержка generic-типов (вход, выход)
- Гибкое API: добавление состояний и переходов через методы или конструктор
- Поддержка кортежей и готовых объектов при создании переходов
- Общие `kwargs` для всех функций (условий, выходов, процессоров)
- Условия остановки выполнения
- Подробная история выполнения шагов
- Валидация целостности автомата

### Автомат Мили (краткий пример)

```python
from src.state_machines import MealyMachine

def zero_condition(input: str) -> bool:
  return input[-1] == "0"

def add_one(previous_output: str) -> str:
  return "1" + previous_output

def shift(input: str) -> str:
  return input[:-1]

machine = MealyMachine(
  transitions=[
    ("S0", "S0", zero_condition, add_one, shift),
  ],
  initial_state="S0",
  initial_output="",
  initial_input="100",
  stop_condition=lambda input: len(input) == 0,
)

machine.run_all()
result = machine.get_final_result()
```

### Автомат Мура (краткий пример)

```python
from src.state_machines import MooreMachine

def zero_condition(input: str) -> bool:
  return input[-1] == "0"

def add_nothing(previous_output: str) -> str:
  return previous_output

def add_one(previous_output: str) -> str:
  return "1" + previous_output

def shift(input: str) -> str:
  return input[:-1]

machine = MooreMachine(
  states=[
    ("S0", add_nothing),
    ("S1", add_one),
  ],
  transitions=[
    ("S0", "S1", zero_condition, shift),
  ],
  initial_state="S0",
  initial_output="",
  initial_input="100",
  stop_condition=lambda input: len(input) == 0,
)

machine.run_all()
result = machine.get_final_result()
```

## Более подробные примеры

В папке [`examples/`](examples) находятся готовые примеры использования:

| Файл                                                  | Автомат | Описание                        |
| ----------------------------------------------------- | ------- | ------------------------------- |
| [`mealy_mul_three.py`](examples/mealy_mul_three.py)   | Мили    | Умножение двоичного числа на 3  |
| [`moore_plus_three.py`](examples/moore_plus_three.py) | Мура    | Прибавление 3 к двоичному числу |

Запустить примеры можно так:

```bash
uv run -m examples.mealy_mul_three
uv run -m examples.moore_plus_three
```

## Тестирование

```bash
uv run pytest
```

## Что в планах

- [x] Реализовать новое API для автоматов Мура
- [ ] Улучшить GUI-редактор (добавить возможность редактирования переходов)
- [x] Создать примеры использования для нового API
- [ ] Доработать GUI-редактор до состояния полноценного приложения

## Полезные ссылки

- Детерминированные конечные автоматы. — Текст : электронный // Викиконспекты кафедры компьютерных технологий Университета ИТМО : [сайт](https://neerc.ifmo.ru/wiki/index.php?title=%D0%94%D0%B5%D1%82%D0%B5%D1%80%D0%BC%D0%B8%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BA%D0%BE%D0%BD%D0%B5%D1%87%D0%BD%D1%8B%D0%B5_%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D1%8B)

- Недетерминированные конечные автоматы. — Текст : электронный // Викиконспекты кафедры компьютерных технологий Университета ИТМО : [сайт](https://neerc.ifmo.ru/wiki/index.php?title=%D0%9D%D0%B5%D0%B4%D0%B5%D1%82%D0%B5%D1%80%D0%BC%D0%B8%D0%BD%D0%B8%D1%80%D0%BE%D0%B2%D0%B0%D0%BD%D0%BD%D1%8B%D0%B5_%D0%BA%D0%BE%D0%BD%D0%B5%D1%87%D0%BD%D1%8B%D0%B5_%D0%B0%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D1%8B)

- Автоматы Мура и Мили. — Текст : электронный // Викиконспекты кафедры компьютерных технологий Университета ИТМО : [сайт](https://neerc.ifmo.ru/wiki/index.php?title=%D0%90%D0%B2%D1%82%D0%BE%D0%BC%D0%B0%D1%82%D1%8B_%D0%9C%D1%83%D1%80%D0%B0_%D0%B8_%D0%9C%D0%B8%D0%BB%D0%B8)
