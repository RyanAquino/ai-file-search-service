from celery import current_app

from settings import Settings


def init_celery(settings: Settings):
    app = current_app
    app.config_from_object(settings)
    app.autodiscover_tasks(["jobs.job1"])

    return app
