#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import json
import requests
import configparser

# user_agent = 'Mozilla/5.0 (X11; U; Linux x86_64; ru; rv:1.9.0.4) Gecko/2008120916 Gentoo Firefox/3.0.4'

API_ENDPOINT = 'https://translate.yandex.net/api/v1.5/tr.json/'
API_KEY = None

CONFIG = None


def config_load():
    global API_KEY, CONFIG
    CONFIG = configparser.SafeConfigParser()
    CONFIG.read('config.ini')
    API_KEY = CONFIG['SECURITY']['API_KEY']


def send_request(api_url, params=None, headers=None):
    try:
        response = requests.get(api_url, params=params, headers=headers)
    except Exception as e:
        print(e)
    rv = json.loads(response.text)
    return rv


def get_langs_handler():
    """Возвращает словарь, содержащий допустимые языки и направления перевода.
    """
    headers = {}
    params = {
        'key': API_KEY,
        'ui': 'ru',
        # 'callback': None,
    }
    api_url = API_ENDPOINT + 'getLangs'

    rv = send_request(api_url, params, headers)
    if 'code' in rv:
        raise Exception(rv.get('code'))
    else:
        return rv.get('langs', None)


def translate_handler(text, langpair):
    headers = {}
    params = {
        'key': API_KEY,
        'text': text,
        'lang': '-'.join(langpair[0:2]),
        'format': ('plain', 'html')[0],
        # 'options': None,
        # 'callback': None,
    }
    api_url = API_ENDPOINT + 'translate'

    rv = send_request(api_url, params, headers)
    if rv.get('code', None) == 200:
        return rv.get('text', '(Текст не обнаружен.)')[0]
    else:
        return rv.get('message', 'Ошибка.')


if __name__ == '__main__':
    # нужно загрузить конфигурацию
    config_load()

    # нужно определить допустимые языки
    LANGUAGES = get_langs_handler() or ['ru', 'en']

    # аргументы должны содержать язык и текст для перевода
    lang = ' '.join(sys.argv[1:2]) or 'en'
    text = ' '.join(sys.argv[2:]) or 'Привет, мир!'

    # если можно перевести на указанный язык
    if lang in LANGUAGES:
        langpair = (lang, 'ru')
        if lang != 'ru':
            langpair = langpair[::-1]
        answer = translate_handler(text, langpair)
        print(answer)
    else:
        mess = translate_handler('Available languages:', ('en', 'ru'))
        available_langs = ('{} - {}'.format(k,v) for k, v in LANGUAGES.items())
        print(mess)
        print('\n'.join(available_langs))

