import celery

from parsing.tasks import ParsePage, ParsePrintXml

app = celery.Celery('celery_app')

app.register_task(ParsePage())
app.register_task(ParsePrintXml())
