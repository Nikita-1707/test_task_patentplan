import pytest
from unittest.mock import patch, Mock, call
from parsing.tasks import ParsePage, ValidationError, SiteNotFound404, ParsePrintXml
import requests_mock


@pytest.fixture
def m_request_mocker() -> requests_mock.Mocker:
    with requests_mock.Mocker() as m:
        yield m


@pytest.fixture
def m_sleep() -> Mock:
    with patch('parsing.tasks.sleep') as m:
        yield m


@pytest.fixture
def f_zakupki_page() -> str:
    with open('fixtures/poop.html') as file:
        return file.read()


@pytest.fixture
def f_view_xml() -> str:
    with open('fixtures/poop_xml.xml') as file:
        return file.read()


@pytest.fixture
def parse_page_task() -> ParsePage:
    task = ParsePage()
    task.before_start(
        'test_task',
        [],
        {
            'url': 'https://zakupki.gov.ru/epz'
        }
    )
    return task


@pytest.fixture
def m_parse_print_xml() -> ParsePrintXml:
    with patch('parsing.tasks.ParsePrintXml') as m:
        yield m


def test_before_start_without_url() -> None:
    with pytest.raises(ValidationError, match='You must pass "url" param'):
        ParsePage().before_start('task_id', [], {})


def test_before_start_with_url(
    parse_page_task: ParsePage,
) -> None:
    assert parse_page_task._url == 'https://zakupki.gov.ru/epz'


def test_run_with_valid_data(
    m_request_mocker: requests_mock.Mocker,
    f_zakupki_page: str,
    parse_page_task: ParsePage,
    m_parse_print_xml: Mock,
) -> None:
    f_url = 'https://zakupki.gov.ru/epz'
    reg_numbers = [
        '0188300000924000040',
        '0347100009824000003',
        '0338200008524000081',
        '0138300016924000003',
        '0116300036524000002',
        '0338200008224000005',
        '0338300047924000062',
        '0338300047924000063',
        '0861300002924000093',
        '0338100001824000040',
    ]

    m_request_mocker.register_uri(
        'GET',
        f_url,
        text=f_zakupki_page,
        status_code=200,
    )

    parse_page_task.run()

    for reg_number in reg_numbers:
        assert call().apply_async(
            kwargs={'url': f'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber={reg_number}'}
        ) in m_parse_print_xml.mock_calls


def test_page_source_with_http_404_retries(
    m_request_mocker: requests_mock.Mocker,
    m_sleep: Mock,
    parse_page_task: ParsePage,
) -> None:
    f_url = 'https://zakupki.gov.ru/epz'

    m_request_mocker.register_uri(
        'GET',
        f_url,
        status_code=404,
        text='Not found 404'
    )

    with pytest.raises(SiteNotFound404, match='Site https://zakupki.gov.ru/epz return HTTP 404'):
        parse_page_task._get_page_source()

    assert m_request_mocker.call_count == 3
    assert m_sleep.call_count == 3


def test_page_source_with_http_200(
    m_request_mocker: requests_mock.Mocker,
    f_zakupki_page: str,
    parse_page_task: ParsePage,
) -> None:
    f_url = 'https://zakupki.gov.ru/epz'

    m_request_mocker.register_uri(
        'GET',
        f_url,
        status_code=200,
        text='success',
    )

    page_source = parse_page_task._get_page_source()

    assert page_source == 'success'
    assert m_request_mocker.call_count == 1
