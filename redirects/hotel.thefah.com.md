# Переадресация со старого сайта hotel.thefah.com

hotel.thefah.com был собственным англоязычным сайтом отеля (2016–2021). DNS домена указывает на сервер
**ai-cz-01** (85.137.166.131). Настройки nginx для этого сервера живут не здесь, а в репозитории
**Axis-Hotels/axis-infrastructure**: плейбук `playbooks/fah-placeholder.yml`, шаблон
`roles/axis_ai_nginx/templates/fah-placeholder.conf.j2`, тесты `tests/test_fah_redirect.py`.

Сейчас в axis-infrastructure любой старый адрес ведёт на начало https://axis-hotels.com/en/fah.
Патч `axis-infrastructure-fah-sections.patch` ведёт каждую старую страницу в её раздел:

| Старый адрес на hotel.thefah.com | Куда ведёт |
|---|---|
| `/`, `/index.html`, `/home`, любой неизвестный адрес | `/en/fah` |
| `/accommodation.html`, `/accomodation`, `/gallery.html`, `/gallary` | `/en/fah#fah-rooms` |
| `/gallery_content.html?gallery=superior-double-bed-picture` | `/en/fah#fah-standard-double` |
| `/gallery_content.html?gallery=deluxe-twin-picture` | `/en/fah#fah-deluxe-twin` |
| `/gallery_content.html?gallery=deluxe-kingsize-picture` | `/en/fah#fah-deluxe-double` |
| `/gallery_content.html?gallery=penthouse-picture` | `/en/fah#fah-penthouse-suite` |
| `/gallery_content.html?gallery=hotel-picture` | `/en/fah#fah-hotel` |
| `/facilities.html`, `/facilities` | `/en/fah#fah-hotel` |
| `/contact.html`, `/contactus` | `/en/fah#fah-contacts` |
| `/promotion.html`, `/promotion`, `/specialoffer/…` | `/en/bangkok/booking?hotel_id=515836` |
| `/ru/…`, `/th/…` | `/ru/fah`, `/th/fah` |

Все адреса старого сайта взяты из веб-архива. Ответ — 308, по http и https; проверка сертификатов
(`/.well-known/acme-challenge/`) и заглушка fah.axis-hotels.com не меняются.

## Что сделать (нужен доступ на запись в axis-infrastructure и к серверу автоматизации)

1. Применить патч в своей копии axis-infrastructure и открыть pull request:

   ```bash
   git checkout -b fah-hotel-redirect-sections origin/main
   git am /путь/к/axis-infrastructure-fah-sections.patch
   git push -u origin fah-hotel-redirect-sections
   ```

   Патч сделан от `main` = `28a8569`. В нём: шаблон nginx с картами адресов, шесть новых проверок
   разделов в плейбуке (http и https, с откатом при ошибке), тесты на все архивные адреса и проверка
   на настоящем nginx в CI (`tests/verify_fah_hotel_redirect.py`). Юнит-тесты локально проходят
   (7 из 7); проверку на nginx выполнит CI.

2. После слияния — шаги из сообщения бота: на automation-mow-01 в обновлённом `/opt/axis/axis-infrastructure`

   ```bash
   scripts/ansible-container ansible-playbook playbooks/fah-placeholder.yml --check --diff --limit ai-cz-01
   ```

   посмотреть diff (меняется только блок hotel.thefah.com, заглушка fah.axis-hotels.com — нет) и затем

   ```bash
   scripts/ansible-container ansible-playbook playbooks/fah-placeholder.yml --limit ai-cz-01
   ```

   На сервере должны быть сертификаты `fah.axis-hotels.com` и `hotel.thefah.com`, иначе плейбук
   остановится до изменений.
