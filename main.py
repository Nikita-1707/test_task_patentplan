from parsing.tasks import ParsePage

page_numbers = range(1, 3)

for page_number in page_numbers:
    url = f'https://zakupki.gov.ru/epz/order/extendedsearch/results.html?fz44=on&pageNumber={page_number}'

    ParsePage().apply_async(
        kwargs={
            'url': url,
        },
    )
