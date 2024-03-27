from parsing.tasks import ParsePage

start_page = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber=1'

ParsePage().apply_async(
    kwargs={
        'url': start_page,
    },
)
