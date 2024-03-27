import abc
import re
from time import sleep

import celery
import requests
import xmltodict
from bs4 import BeautifulSoup

from logger import log


class ValidationError(Exception):
    ...


class SiteNotFound404(Exception):
    ...


REG_NUMBER_PATTERN = r'regNumber=(\d+)'
BUTTONS_DIV_CLASS = 'w-space-nowrap ml-auto registry-entry__header-top__icon'
RETRY_COUNT = 10
RETRY_SLEEP_DURATION = 15


class BaseParse(abc.ABC, celery.Task):

    def __init__(self) -> None:
        super().__init__()
        self._url = None
        self.session = requests.Session()

    def before_start(self, task_id, args, kwargs) -> None:
        url = kwargs.get('url')

        if url is None:
            raise ValidationError('You must pass "url" param')

        self._url = url

    def run(self, *args, **kwargs):
        raise NotImplementedError

    def _get_page_source(self) -> str:
        # NOTE(NikitaS): sometimes site returns HTTP 404 for a long time. Fixed with retries
        for _ in range(RETRY_COUNT):
            response = self.session.get(self._url)

            if response.status_code == 404:
                log.debug('Got 404 on fetching page. Retrying...')
                sleep(RETRY_SLEEP_DURATION)
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

        button_divs = soup.find_all('div', attrs={'class': BUTTONS_DIV_CLASS})

        for element in button_divs:
            reg_number_match = re.search(REG_NUMBER_PATTERN, str(element))

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
        result = xmltodict.parse(
            xml_input=self._get_page_source(),
        )

        for notification_name, data in result.items():
            publish_dti = data.get('commonInfo', {}).get('publishDTInEIS')
            print(
                f'Notification name: {notification_name}'
                f'\tpublishDTInEIS:{publish_dti}'
            )
