# worker for handling queues
# redis
import redis
from config import redis_url
# rq
from rq import Worker, Queue, Connection

# listened queue
listen = ['tasks']  # 'statuses' if future
redis_connect = redis.from_url(redis_url)


if __name__ == '__main__':
    with Connection(redis_connect):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
