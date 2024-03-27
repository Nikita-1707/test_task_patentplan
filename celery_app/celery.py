import celery

from parsing.tasks import ParsePage

app = celery.Celery('celery_app')

app.register_task(ParsePage())
