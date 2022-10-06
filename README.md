
# VK_Inder
### Программа для поиска пары в Vk по данным пользователя"

Предварительные настройки:

1. Вставить user_vk_token в первую строчку config\user_token_.txt
2. Вставить в первую строчку пароль для БД (PostrgeSQL) config\db_pwd_.txt
3. Создать локальную базу данных (PostrgeSQL) - запустить скрипт DB\create_db.py

Затем запустить **app_main.py**.

Адрес группы в VK: [Appinder](https://vk.com/public216109193).

Для начала общения с ботом напишите: **"hi"** или **"привет"**.

### Управление / Общение
При общении будут доступны кнопки управления.

Так же есть список команд, которые можно отправить в чат:
1. "/n" или "Next" - для просмотра следующего;
2. "/af" - добавить в список избранных;
3. "/abl" - добавить в черный список;
4. "/sf" - показать список избранных;
5. "/sbl" - показать черный список;
6. "/fm" - запустить доп. поиск.


Зависимости хранятся в "requirements.txt"