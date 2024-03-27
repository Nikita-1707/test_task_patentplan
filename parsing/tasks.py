import re
from time import sleep

import celery
import requests
from bs4 import BeautifulSoup, ResultSet

from logger import log


class ValidationError(Exception):
    ...


class ParsePage(celery.Task):
    name = 'parse_page'
    _reg_number_patter = r'regNumber=(\d+)'

    def __init__(self):
        self._url = None

    def before_start(self, task_id, args, kwargs) -> None:
        url = kwargs.get('url')

        if url is None:
            raise ValidationError('You must pass "url" param')

        self._url = url

    def run(self, *args, **kwargs):
        soup = BeautifulSoup(
            self._page_source,
            'html.parser',
        )

        div_buttons = 'w-space-nowrap ml-auto registry-entry__header-top__icon'

        res: ResultSet = soup.find_all('div', attrs={'class': div_buttons})

        for element in res:
            reg_number_match = re.match(self._reg_number_patter, str(element))

            if not reg_number_match:
                raise

            reg_number = reg_number_match.group()
            print(reg_number)

            # reg_numbers = set(re.findall(self._reg_number_patter, res))
        # print(reg_numbers)

    @property
    def _page_source(self) -> str:
        log.warning(self._url)
        response = requests.get(self._url)

        # one time retry
        if response.status_code == 404:
            log.warning('Got 404 on fetching page. Retrying...')
            # sometimes site are down for a long time
            sleep(15)
            response = requests.get(self._url)

        return response.text
