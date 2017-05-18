import redis
from config import redis_url
from rq import Worker, Queue, Connection

listen = ['tasks']  # 'statuses' if future
redis_connect = redis.from_url(redis_url)


if __name__ == '__main__':
    with Connection(redis_connect):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
