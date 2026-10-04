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
