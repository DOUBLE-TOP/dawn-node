# Dawn Node

## Общая информация

Софт для запуска множества нод Dawn на одном сервере без браузера

## Основные особенности 

* **Поддержка прокси**
* **Детальное логирование**
* **Выполнение доп квестов для получения 15к поинтов(твиттер, дискорд, телеграм)**
* **Обработка ошибок**
* **Получение дополнительных данных о ноде**
* **Сохранение логов в файлы по дням**
* **Параллельный запуск аккаунтов**

## Требования к серверу
* **Ubuntu 22.04**
* **3.8.x <= python <= 3.11.x**
> Проверить версию питона можно командой **_python3 -V_**
* **tmux**
> Установка **_apt install tmux -y_**


## Подготовка к запуску

### 1.  Регистрация аккаунта 2captcha

1. Регистрируем аккаунт https://2captcha.com/
2. Пополняем счет. 5-10$ хватит на очень долго для этого скрипта.
3. Генерируем API ключ.

### 2. Регистрация аккаунтов Dawn

1. Регистрируем аккаунты Dawn
2. Не забываем подтвердить регистрацию через почту. Без этого вы не сможете залогиниться.

### 3. Покупаем прокси под каждый аккаунт

1. Покупал прокси через astroproxy. 30 центов за аккаунт 100мб - уходит в день меньше 1мб траффика
2. Сохраняем прокси в формате `http://user:password@host:port`

### 4. Клонирование репозитория

```bash
git clone https://github.com/DOUBLE-TOP/dawn-node.git
```
Для выполнения следующих команд перейдите в терминале в папку с проектом.

### 5. Добавление ключа с капчей. 
    
1. Копируем файл _settings.example.txt_ в файл _settings.txt_. 
```bash
cp ./data/settings.example.txt ./data/settings.txt
```
2. Вписываем 2сaptcha API ключ в файл

### 6. Добавление аккаунтов Dawn. 

1. Копируем файл _accounts.example.csv_ в файл _accounts.csv_
```bash
cp ./data/accounts.example.csv ./data/accounts.csv
```
2. Заполняем документ
   1. **Email** - адрес почты для аккаунта
   2. **Password** - пароль для авторизации в ноду Dawn(это не пароль от почты).
   3. **Proxy** - прокси для каждого аккаунта в формате `http://user:password@host:port`. 
3. Итого одна запись для аккаунта будет выглядить как строка
```bash
some_email@gmail.com,some_password,http://user:proxy_pwd@host:port
```

##  Установка и запуск проекта

> Устанавливая проект, вы принимаете риски использования софта(вас могут в любой день побрить даже если вы не спорите за цену Neon).

Для установки необходимых библиотек, пропишите в консоль

```bash
pip install -r requirements.txt
```

Запуск проекта

```bash
tmux new-session -s dawn_bot -d 'python3 main.py'
```

>Не удаляйте папку `accounts` в папке `data`. Это данные о каждом из ваших аккаунтов. Чтобы не собирать ее при каждом запуске, она хранится локально у вас на сервере. Никакой супер важной ифнормации там нет.

##  Полезные дополнительные штучки

### 1. Проверка логов

Логи можно проверить, как в папке logs, так и открыв сессию tmux. Чтобы отсоединиться от сессии и оставить ее работающей в фоне, просто нажмите Ctrl + b, затем d.
```bash
tmux attach-session -t dawn_bot
```

### 2. Вывести статистику по поинтам

```bash
bash stats.sh
```
