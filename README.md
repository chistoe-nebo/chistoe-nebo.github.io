# Сайт экопоселения Чистое небо

Цель сайта: развитие поселения через привлечение туристов.
Рассказать какое у нас интересное поселение, чтобы все захотели приехать.


## О сайте

Сайт статический.
В этом репозитории лежат исходники в Markdown и преобразователь на питоне.
Для быстрого внесения изменений можно использовать [веб-интерфейс BitBucket][1].
Изменения вступают в силу в течение 5 минут.

Добавлять двоичные файлы (картинки итп) через веб-интерфейс нельзя, для этого придётся задействовать один из клиентов для работы с репозиториями Mercurial.

Текущая версия сайта доступна по адресу [nebo.dev.umonkey.net][2].


## Вспомогательная документация

- [Оформление сайта](https://bitbucket.org/umonkey/website-nebo-welcome/src/default/doc/Design.md)


## Форматирование страниц

В теле страниц можно использовать любую разметку Markdown и некоторые специальные функции.

### Вставка уменьшенного изображения

    {{ thumbnail("files/welcome.jpg", 300, 200) }}


[1]: https://bitbucket.org/umonkey/website-nebo-welcome/src/default/input/
[2]: http://nebo.dev.umonkey.net/
