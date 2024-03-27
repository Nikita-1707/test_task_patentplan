import abc
import re
from time import sleep

import celery
import requests
from bs4 import BeautifulSoup

from logger import log


class ValidationError(Exception):
    ...


class SiteNotFound404(Exception):
    ...


REG_NUMBER_PATTER = r'regNumber=(\d+)'
BUTTONS_DIV = 'w-space-nowrap ml-auto registry-entry__header-top__icon'


class BaseParse(abc.ABC, celery.Task):

    def __init__(self):
        self._url = None

    def before_start(self, task_id, args, kwargs) -> None:
        url = kwargs.get('url')

        if url is None:
            raise ValidationError('You must pass "url" param')

        self._url = url

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _get_page_source(self) -> str:
        for _ in range(3):
            response = requests.get(self._url)

            if response.status_code == 404:
                log.warning('Got 404 on fetching page. Retrying...')
                # sometimes site are down for a long time
                sleep(15)
                continue

            return response.text

        raise SiteNotFound404(f'Site {self._url} return HTTP 404')


class ParsePage(BaseParse):
    name = 'parse_page'

    def run(self, *args, **kwargs):
        soup = BeautifulSoup(
            self._get_page_source(),
            'html.parser',
        )

        res = soup.find_all('div', attrs={'class': BUTTONS_DIV})

        for element in res:
            reg_number_match = re.search(REG_NUMBER_PATTER, str(element))

            if not reg_number_match:
                log.debug(f'regNumber not found in element: {element}')
                continue

            reg_number = reg_number_match.group(1)
            print_xml_url = f'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber={reg_number}'
            ParsePrintXml().apply_async(
                kwargs={
                    'url': print_xml_url,
                },
            )


class ParsePrintXml(BaseParse):
    name = 'parse_print_xml'

    def run(self, *args, **kwargs):
        ...
