from unittest.mock import patch

import pytest
import requests_mock

from parsing.tasks import ParsePage


@pytest.fixture
def f_request_mocker() -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def f_zakupki_page() -> str:
    with open('poop.html') as file:
        return file.read()


@pytest.fixture
def parse_page_task():
    with patch('parsing.tasks.ParsePage') as mock_task:
        yield mock_task


def test_should_sync_config_from_master(
    f_request_mocker: requests_mock.Mocker,
    f_zakupki_page: str,
) -> None:
    f_url = 'https://zakupki.gov.ru/epz'

    f_request_mocker.register_uri(
        method='GET',
        url=f_url,
        text=f_zakupki_page,
    )

    obj = ParsePage()
    obj.apply_async(
        kwargs={
            'url': f_url,
        }
    )
