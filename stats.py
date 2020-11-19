import os
import redis
from rq import Worker, Queue, Connection, version as rq_version

CONN = redis.from_url(os.getenv('RQ_REDIS_URI'))

def scrape():
    enqueued_jobs = []
    workers = []

    queues = Queue.all(connection=CONN)
    enqueued_jobs = [dict(queue_name=q.name, size=q.count) for q in queues]
    if rq_version.VERSION.startswith("1"):
        enqueued_jobs.extend([
            dict(queue_name=f"{q.name}-failed", size=q.failed_job_registry.count) for q in queues
        ])

    workers = [
        dict(name=w.name, queues=_serialize_queue_names(w), state=str(w.get_state()))
        for w in Worker.all(connection=CONN)
    ]

    return enqueued_jobs, workers

def _serialize_queue_names(worker):
    return ",".join([q.name for q in worker.queues])
