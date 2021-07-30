# Микросервис для скачивания файлов

> ### Обновления:
> 1. Ну во-первых, сервис теперь заработал.
> 2. Добавлена параметризация запуска сервера, причем двумя способами:   
> 2.1. С помощью файла `.env`. Просто создайте файл `.env` в папке со скриптом, следующего содержания:  
> ```
> LOG_LEVEL=INFO # необходимый уровень логирования (INFO, DEBUG, etc.)  
> DELAY=0 # задержка ответа при скачивании файла в секундах  
> PHOTO_DIR='test_photos' # имя папки с фотографиями    
> KBYTES=100 # размер фрагмента скачиваемого файла в Кбайтах
> ```
> 2.2. С помощью аргументов командной строки, где:  
> ```
> --debug, включение логирования уровня DEBUG  
> --delay, включение задержки ответа в секундах  
> --photo_dir, имя папки с фотографиями   
> --fragment, размер фрагмента скачиваемого файла в Кбайтах  
> --help, справка  
> ```
> 
> Пример запуска (включаем debug, задержка 2 секунды, папка с фотографиями `new_folder`, файл отправлять по 20 Кбайт).  
> `python server.py --debug --delay 2 --photo_dir new_folder --fragment 20`  
> 
>**ВАЖНО:** Команды `командной строки` переопределяют значения, указанные в файле `.env`.  
>**ТОЖЕ ВАЖНО:** Использование `командной строки` и/или файла `.env` - обязательно.    
> 
> Далее идет общее описание сервиса, включая установку и развертывание.  
> **Однако** вы также можете воспользоваться `Docker` для запуска сервиса. Достаточно запустить:  
> `docker-compose up`  
> Настройки запуска(командной строки) ждут вас в `docker-compose.yml`.  

<br>
Микросервис помогает работе основного сайта, сделанного на CMS и обслуживает
запросы на скачивание архивов с файлами. Микросервис не умеет ничего, кроме упаковки файлов
в архив. Закачиваются файлы на сервер через FTP или админку CMS.

Создание архива происходит на лету по запросу от пользователя. Архив не сохраняется на диске, вместо этого по мере упаковки он сразу отправляется пользователю на скачивание.

От неавторизованного доступа архив защищен хешом в адресе ссылки на скачивание, например: `http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/`. Хеш задается названием каталога с файлами, выглядит структура каталога так:

```
- photos
    - 3bea29ccabbbf64bdebcc055319c5745
      - 1.jpg
      - 2.jpg
      - 3.jpg
    - af1ad8c76fda2e48ea9aed2937e972ea
      - 1.jpg
      - 2.jpg
```


## Как установить

Для работы микросервиса нужен Python версии не ниже 3.6.

```bash
pip install -r requirements.txt
```

## Как запустить

```bash
python server.py
```

Сервер запустится на порту 8080, чтобы проверить его работу перейдите в браузере на страницу [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Как развернуть на сервере

```bash
python server.py
```

После этого перенаправить на микросервис запросы, начинающиеся с `/archive/`. Например:

```
GET http://host.ru/archive/3bea29ccabbbf64bdebcc055319c5745/
GET http://host.ru/archive/af1ad8c76fda2e48ea9aed2937e972ea/
```

# Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).