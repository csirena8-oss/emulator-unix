# Эмулятор командной строки (Вариант 25)

## 1. Общее описание

Учебный проект — эмулятор командной строки UNIX-подобной ОС,
выполненный в виде REPL. Проект разбит на этапы, определённые в  
методических указаниях:

- **Этап 1 (REPL)** — базовый диалог с пользователем: приглашение  
  из реальных данных ОС, раскрытие переменных окружения, заглушки  
  `ls`, `cd`, команда `exit`, обработка ошибок.
- **Этап 2 (Конфигурация)** — параметры командной строки  
  (`--vfs`, `--script`), отладочный вывод всех заданных параметров  
  при запуске и выполнение стартового скрипта с комментариями в  
  режиме имитации диалога.
- **Этапы 3–5** (VFS, основные и дополнительные команды) будут  
  добавлены позже.

Запуск — в терминале UNIX-подобной ОС с Python 3.9+.

## 2. Описание всех функций и настроек

### 2.1. Модуль `src/shell_emulator.py`

| Функция | Назначение |
|---------|------------|
| `current_user()` | имя пользователя (`getpass.getuser()`); |
| `current_host()` | имя хоста (`socket.gethostname()`); |
| `display_cwd()` | текущий каталог, `~` для домашнего пути; |
| `build_prompt()` | строка приглашения `user@host:dir$`; |
| `expand_env(token)` | подстановка `$NAME` и `${NAME}`; |
| `parse_line(line)` | разбор строки на команду и аргументы; |
| `report_error(name, msg)` | вывод ошибки в `stderr`; |
| `command_ls(args)` | заглушка `ls`; |
| `command_cd(args)` | заглушка `cd`; |
| `build_registry()` | словарь имён → обработчиков; |
| `dispatch(reg, name, args)` | поиск и вызов команды из реестра; |
| `execute_line(line, reg)` | выполнение одной строки ввода; |
| `run_interactive(reg)` | интерактивный цикл REPL; |
| `run_from_script(reg, cmds)` | режим выполнения команд скрипта; |
| `run_script_mode(path)` | запуск в режиме стартового скрипта; |
| `run_interactive_mode()` | запуск в интерактивном режиме; |
| `main(argv)` | точка входа, разбор аргументов, выбор режима. |

### 2.2. Модуль `src/config.py`

| Функция | Назначение |
|---------|------------|
| `build_parser()` | собрать парсер `argparse`; |
| `parse_args(argv)` | разобрать argv в `Config`; |
| `describe_path(value)` | отобразить путь или `<не задан>`; |
| `format_debug(config)` | сформировать отладочный вывод параметров. |

Параметры командной строки:

| Ключ | Длинная форма | Значение |
|------|---------------|----------|
| `-v` | `--vfs` | путь к физическому расположению VFS; |
| `-s` | `--script` | путь к стартовому скрипту эмулятора. |

### 2.3. Модуль `src/script_runner.py`

| Функция | Назначение |
|---------|------------|
| `is_comment(line)` | true, если строка начинается с `#`; |
| `is_blank(line)` | true, если строка пуста/из пробелов; |
| `clean_lines(raw)` | удалить комментарии и пустые строки; |
| `load_script(path)` | прочитать и очистить стартовый скрипт; |
| `run_script(cmds, exec, prompt)` | выполнить команды, имитируя диалог. |
| `ScriptError` | исключение об ошибке чтения скрипта. |

Синтаксис стартового скрипта:

- одна команда эмулятора на строку;
- строки, начинающиеся с `#`, — комментарии;
- пустые строки игнорируются;
- при выполнении на экран выводятся приглашение, сама команда и её  
  результат (имитация диалога с пользователем);
- при ошибке чтения файла — сообщение в `stderr`, код возврата 1.

### 2.4. Настройки (константы модула)

| Константа | Значение | Смысл |
|-----------|----------|-------|
| `PROMPT_END` | `"$ "` | завершение приглашения; |
| `HOME_SHORTCUT` | `"~"` | обозначение домашнего каталога; |
| `MAX_CD_ARGS` | `1` | максимум аргументов для `cd`; |
| `EXIT_COMMAND` | `"exit"` | имя команды выхода; |
| `ENV_PATTERN` | regex | шаблон `$NAME` / `${NAME}`; |
| `COMMENT_PREFIX` | `"#"` | префикс комментария скрипта; |
| `SCRIPT_ERROR_PREFIX` | `"script"` | префикс сообщений об ошибках; |
| `EMPTY_MARKER` | `"<не задан>"` | вид незаданного параметра. |

## 3. Описание команд для сборки проекта и запуска тестов

### Подготовка (один раз)
```
python3 -m venv .venv
source .venv/bin/activate
pip install pytest
```
### Запуск эмулятора
```
chmod +x run.sh
./run.sh
```
### Запуск с параметрами командной строки
```
./run.sh --vfs samples/vfs.zip --script samples/demo.esh
```
### Запуск тестов
```
python3 -m pytest -v
```
## Демонстрационные shell-скрипты реальной ОС
```
chmod +x scripts/*.sh
./scripts/run_default.sh
./scripts/run_with_vfs.sh
./scripts/run_with_script.sh
./scripts/run_all_params.sh
```

## 4. Примеры использования

### 4.1. Интерактивный режим (этап 1)
```
$ ./run.sh

Отладка: параметры запуска эмулятора
VFS-путь : <не задан>
скрипт-путь : <не задан>
Эмулятор оболочки ОС. Введите 'exit' для выхода.
student@debian:/home/student$ ls
ls: []
student@debian:/home/student$ ls -l $HOME
ls: ['-l', '/home/student']
student@debian:/home/student$ cd a b
cd: слишком много аргументов
student@debian:/home/student$ unknown
unknown: команда не найдена
student@debian:/home/student$ exit
```

### 4.2. Режим стартового скрипта (этап 2)

Файл `samples/demo.esh`:
## Демонстрационный стартовый скрипт эмулятора.
### Пустые строки игнорируются.
```
ls
ls -l $HOME
cd /tmp
cd ${HOME}
cd /tmp /var
some_unknown_command
exit
```

# Запуск:
```
$ ./run.sh --script samples/demo.esh
Отладка: параметры запуска эмулятора
VFS-путь : <не задан>
скрипт-путь : samples/demo.esh
Эмулятор оболочки ОС. Режим стартового скрипта.
student@debian:/home/student$ ls
ls: []
student@debian:/home/student$ ls -l $HOME
ls: ['-l', '/home/student']
student@debian:/home/student$ cd /tmp
cd: ['/tmp']
student@debian:/home/student$ cd ${HOME}
cd: ['/home/student']
student@debian:/home/student$ cd /tmp /var
cd: слишком много аргументов
student@debian:/home/student$ some_unknown_command
some_unknown_command: команда не найдена
student@debian:/home/student$ exit
```

### 4.3. Ошибка чтения стартового скрипта
```
$ ./run.sh --script missing.esh
Отладка: параметры запуска эмулятора
VFS-путь : <не задан>
скрипт-путь : missing.esh
script: файл не найден: missing.esh
```

### 4.4. Тестирование параметров через скрипты реальной ОС

```
$ ./scripts/run_all_params.sh
Отладка: параметры запуска эмулятора
VFS-путь : /path/to/repo/samples/vfs.zip
скрипт-путь : /path/to/repo/samples/demo.esh
Эмулятор оболочки ОС. Режим стартового скрипта.
```
