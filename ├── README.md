# Daime
# UNIX Shell Emulator

Эмулятор командной строки UNIX-подобной операционной системы,
реализованный на Python 3.

## Возможности

Поддерживаются:

- интерактивный CLI;
- приглашение вида `username@hostname:/path$`;
- раскрытие переменных окружения `$HOME`, `$USER` и `${VAR}`;
- выполнение стартового скрипта;
- комментарии в скриптах;
- виртуальная файловая система в памяти;
- загрузка VFS из ZIP-архива;
- сохранение VFS командой `vfs-save`;
- обработка ошибок команд;
- команды:

```text
ls
ls -l
cd
pwd
date
uniq
chmod
vfs-save
exit
```
# Требования
- Python 3.10 или новее;
- стандартная библиотека Python;
- дополнительные пакеты не требуются.


## Интерактивный режим:

python3 emulator.py
## С VFS:

python3 emulator.py --vfs vfs/test.zip
## Со стартовым скриптом:

python3 emulator.py --startup scripts/stage5.txt
## С VFS и стартовым скриптом:

python3 emulator.py \
    --vfs vfs/test.zip \
    --startup scripts/stage5.txt

# Параметры командной строки
## --vfs
- Путь к ZIP-архиву виртуальной файловой системы.

Если параметр не указан, создаётся VFS по умолчанию в памяти.

Пример:
```
python3 emulator.py --vfs vfs/minimal.zip
```
## --startup
- Путь к стартовому скрипту.
```
python3 emulator.py --startup scripts/stage1.txt
```
# Стартовые скрипты
- Пустые строки и строки, начинающиеся с #, считаются комментариями.

Пример:

Проверка базовых команд
```
pwd
ls
cd /home/user
pwd
ls -l
exit
```
# Команды
## ls 
- Показывает содержимое каталога.
```
ls
ls /
ls -l
ls /home/user
```
## cd 
- Изменяет текущий виртуальный каталог.
```
cd /home
cd ..
cd /
```
## pwd 
- Показывает текущий виртуальный каталог.
```
pwd
```
## date 
- Показывает текущую дату и время.
```
date
```
## uniq 
- Удаляет соседние повторяющиеся строки файла.
```
uniq /home/user/example.txt
```
## chmod 
- Изменяет права доступа файла или каталога в памяти VFS.
```
chmod 755 /home/user/example.txt
ls -l /home/user/example.txt
```
## vfs-save 
- Сохраняет текущее состояние VFS в ZIP-архив.
```
vfs-save result.zip
```
## exit 
- Завершает работу эмулятора.
```
exit
```
# Переменные окружения
Поддерживается раскрытие переменных окружения операционной системы:  
```
vfs-save $HOME/result.zip
```
Также поддерживается форма: 
```
vfs-save ${HOME}/result.zip
```
# Обработка ошибок
## Пример неизвестной команды: unknown
Результат: 
```
error: unknown: command not found
```
## Пример перехода в несуществующий каталог: cd /missing
Результат:
```
error: cd: /missing: No such directory
```
## Пример неверного количества аргументов: pwd test
Результат:
```
error: pwd: too many arguments
```
## Запуск тестов
```
python3 -m unittest discover -s tests -v
```
## Проверка синтаксиса:
```
python3 -m py_compile emulator.py
```
# Создание VFS-архива
Пример содержимого VFS:
```
vfs/source/
├── README.txt
└── home/
    └── user/
        └── file.txt
```
# Создание архива:
```
mkdir -p vfs/source/home/user

printf "Virtual file system\n" \
    > vfs/source/README.txt

printf "hello\n" \
    > vfs/source/home/user/file.txt

cd vfs/source
zip -r ../test.zip .
cd ../..
```
## Пример запуска
```
python3 emulator.py \
    --vfs vfs/test.zip \
    --startup scripts/stage5.txt
```
# Рекомендуемые Git-коммиты
```
git add emulator.py README.md
git commit -m "feat: implement interactive shell prototype"

git add scripts
git commit -m "feat: add startup scripts and CLI configuration"

git add emulator.py vfs
git commit -m "feat: implement in-memory virtual file system"

git add emulator.py scripts
git commit -m "feat: implement core shell commands"

git add emulator.py scripts
git commit -m "feat: implement chmod command"
```
