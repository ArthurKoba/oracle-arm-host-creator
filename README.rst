Описание
--------

Скрипт для получения сервера oracle **VM.Standard.A1.Flex**

Стандартный образ для сервера - **Canonical Ubuntu**

Конфигурации сервера:

- **4 CPU**
- **24 RAM**
- **99 ROM**

Установка
---------

Подготовка окружения::

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt

Подготовка конфигурации:

- В папке запуска должна находиться папка **app**!
- Необходимо в папке запуска расположить файлы *(Названия не обязательно должны совпадать)*:

 - **api.cfg** *(Файл конфигурации при создании ключа api)*
 - **api_key.pem** *(Приватный ключ при создании api)*
 - **server_public.key** *(Ключ который будет установлен на сервер при создании)*

 **Примерное содержание файлов:**

 - **api.cfg**::

    [DEFAULT]
    user=ocid1.user.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    fingerprint=00:00:00:00:00:00:00:00:00:00:00:00:00:00:00:00
    tenancy=ocid1.tenancy.oc1..aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
    region=eu-amsterdam-1

 - **api_key.pem**::

    -----BEGIN PRIVATE KEY-----
      ...
      ...
      ...
    -----END PRIVATE KEY-----

 - **server_public.key**::

    ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC5mDA4...... ssh-key-2021-01-01

Запуск
------

Перед запуском рекомендуется создать `VCN сеть. <https://cloud.oracle.com/networking/vcns>`_

Команда запуска::

 python -m app api.cfg api_key.pem server_public.key
