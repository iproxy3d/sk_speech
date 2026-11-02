# Публикация `sk-speech` на PyPI

Пакет публикуется из GitHub Actions через механизм PyPI Trusted Publishing.
Пароль или API-токен PyPI в репозитории и GitHub Secrets не требуется.

## Подготовка PyPI

Для первой публикации создайте ожидаемого издателя (pending publisher) в
настройках PyPI со следующими значениями:

- владелец репозитория: `iproxy3d`;
- репозиторий: `sk_speech`;
- файл workflow: `publish.yml`;
- окружение GitHub: `pypi`;
- имя проекта: `sk-speech`.

После первой публикации ожидаемый издатель автоматически связывается с
созданным проектом. Если проект уже существует, те же значения нужно добавить
в разделе Trusted Publishers его настроек.

## Проверка перед выпуском

Установите инструменты разработки и выполните проверки:

```bash
python -m pip install -e ".[dev]"
python -m compileall -q src examples tests
python -m pytest
python -m build
python -m twine check --strict dist/*
```

Дополнительно рекомендуется установить собранное колесо в чистое виртуальное
окружение и проверить импорт:

```bash
python -m pip install dist/sk_speech-0.1.0-py3-none-any.whl
python -c "import sk_speech; print(sk_speech.__version__)"
```

## Выпуск версии

1. Обновите `version` в `pyproject.toml` и `__version__` в
   `src/sk_speech/__init__.py`, сохранив одинаковое значение.
2. Убедитесь, что workflow `tests` завершился успешно для ветки `main`.
3. Создайте тег вида `v0.1.0` и GitHub Release для этого тега.
4. Публикационный workflow соберёт wheel и sdist, проверит их и передаст в PyPI.

Загруженную в PyPI версию нельзя заменить тем же номером. Для любого
повторного выпуска необходимо увеличить версию в `pyproject.toml`.

## Токены

Если API-токен PyPI когда-либо был опубликован в сообщении, логе или другом
небезопасном месте, его необходимо отозвать в настройках PyPI. Для workflow из
этого репозитория такой токен не нужен.
