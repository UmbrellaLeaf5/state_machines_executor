Судя по названию `update`, ожидается второе поведение.

### 1. Отсутствие геттеров для текущего состояния

Для отладки и тестирования полезно иметь методы:

```python
def get_current_state_name(self) -> str | None:
    if isinstance(self.__current_state, _UNSET):
        return None
    return self.__current_state.name

def get_current_output(self) -> OutputType | None:
    if isinstance(self.__current_output, _UNSET):
        return None
    return self.__current_output

def get_current_input(self) -> InputType | None:
    if isinstance(self.__current_input, _UNSET):
        return None
    return self.__current_input
```

### 2. Отсутствие метода `get_states()`

Полезно для обхода всех состояний. Можно вернуть копию списка имён:

```python
def get_state_names(self) -> list[str]:
    return list(self.__states.keys())
```

Или сами объекты:

```python
def get_states(self) -> list[MealyState[InputType, OutputType]]:
    return list(self.__states.values())
```

### 3. Метод `run_all` возвращает `self.__results`, но не очищает его перед запуском

Если вызвать `run_all` повторно, он продолжит добавлять шаги к старым. Возможно, стоит добавить флаг `clear_before_run` или по умолчанию очищать, но это нарушит ожидания тех, кто хочет дозапустить. Лучше оставить как есть, но задокументировать, что результаты накапливаются.

### 4. Отсутствие метода для проверки готовности к запуску

Сейчас `run_once` сам проверяет, но пользователь мог бы вызывать `is_ready()`, чтобы не ловить исключения. Можно добавить публичный метод:

```python
def is_ready(self) -> bool:
    return not (
        isinstance(self.__current_state, _UNSET)
        or isinstance(self.__current_output, _UNSET)
        or isinstance(self.__current_input, _UNSET)
    )
```

## 5. Добавить опциональную очистку переходов в `remove_state`

**Проблема**: при удалении состояния остаются переходы, ведущие в него.

**Решение**: добавить параметр `cleanup_transitions`.

```python
def remove_state(self, state_name: str, cleanup_transitions: bool = False) -> None:
    """
    Удаляет состояние.

    Args:
        state_name: Имя состояния
        cleanup_transitions: Если True, удаляет все переходы, ведущие в это состояние
    """
    if state_name not in self.__states:
        raise KeyError(f"State '{state_name}' is not found")

    # Если удаляем текущее состояние, сбрасываем его
    if (
        not isinstance(self.__current_state, _UNSET)
        and self.__current_state.name == state_name
    ):
        warnings.warn(
            f"Removing current state '{state_name}', machine reset",
            UserWarning,
            stacklevel=2
        )
        self.clear_current_data()

    # Удаляем переходы, ведущие в это состояние
    if cleanup_transitions:
        for state in self.__states.values():
            if state_name in state.transitions:
                del state.transitions[state_name]

    del self.__states[state_name]
```

## 6. Добавить docstring для публичных методов

**Проблема**: отсутствие документации.

**Решение**: добавить краткие описания для каждого метода.

```python
def add_state(self, state: MealyState[InputType, OutputType]) -> None:
    """Добавляет состояние в автомат."""
    self.__states[state.name] = state

def remove_state(self, state_name: str, cleanup_transitions: bool = False) -> None:
    """
    Удаляет состояние.

    Args:
        state_name: Имя удаляемого состояния
        cleanup_transitions: Удалить все переходы, ведущие в это состояние
    """
    # ... тело метода

def fill_states(self, states: list[str | MealyState[InputType, OutputType]]) -> None:
    """
    Добавляет несколько состояний, проверяя дубликаты.

    Args:
        states: Список имён или объектов MealyState

    Raises:
        ValueError: При дубликате состояния
        TypeError: При неверном типе элемента
    """
    # ... тело метода
```
