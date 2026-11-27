# Переадресация со старого сайта hotel.thefah.com

hotel.thefah.com был собственным англоязычным сайтом отеля (2016–2021). Теперь у the Fah три адреса,
язык первым, как у всего axis-hotels.com:

- https://axis-hotels.com/en/fah — английский, основной;
- https://axis-hotels.com/ru/fah — русский;
- https://axis-hotels.com/th/fah — тайский.

Отдельных адресов для разделов нет. Старый сайт был только на английском, поэтому **любая** его ссылка
(главная, номера, галерея, контакты, акции, любой другой путь, по http и https) ведёт на
https://axis-hotels.com/en/fah с кодом 308.

## Где это настроено

DNS hotel.thefah.com указывает на сервер **ai-cz-01** (85.137.166.131). Его nginx настраивается не из этого
репозитория, а из **Axis-Hotels/axis-infrastructure**: плейбук `playbooks/fah-placeholder.yml`, шаблон
`roles/axis_ai_nginx/templates/fah-placeholder.conf.j2`, тесты `tests/test_fah_redirect.py`. Там уже ровно
такое правило — `location / { return 308 https://axis-hotels.com/en/fah; }` для http и https; менять в
axis-infrastructure ничего не нужно.

## Что сделать (нужен доступ к серверу автоматизации)

На automation-mow-01 в обновлённом `/opt/axis/axis-infrastructure`:

```bash
scripts/ansible-container ansible-playbook playbooks/fah-placeholder.yml --check --diff --limit ai-cz-01
```

посмотреть diff и затем применить:

```bash
scripts/ansible-container ansible-playbook playbooks/fah-placeholder.yml --limit ai-cz-01
```

На сервере должны быть сертификаты `fah.axis-hotels.com` и `hotel.thefah.com`, иначе плейбук остановится
до изменений. После установки он сам проверяет nginx, переадресацию http/https на `/en/fah` и то, что
https://axis-hotels.com/en/fah открывается с кодом 200; при ошибке возвращает прежние настройки.

## Старые адреса на самом axis-hotels.com

См. `tilda-old-addresses.md`: `/fah`, `/en/the-fah` → `/en/fah`; `/fah/ru`, `/ru/the-fah` → `/ru/fah`;
`/fah/th`, `/th/the-fah` → `/th/fah`.
