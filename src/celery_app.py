from celery import Celery
from src.utils.config import Config

# Load config
config = Config()

# Create Celery app
celery_app = Celery(
    'slot_hunter',
    broker=config.celery_broker_url,
    backend=config.celery_result_backend,
    include=['src.tasks']
)

celery_app.conf.update(
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Tehran',
    enable_utc=True,
    beat_schedule={
        'monitor-all-doctors-every-30-seconds': {
            'task': 'src.tasks.monitor_all_doctors',
            'schedule': 30.0, # Run every 30 seconds
        },
    }
)

if __name__ == '__main__':
    celery_app.start()
