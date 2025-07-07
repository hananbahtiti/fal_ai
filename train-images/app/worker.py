from redis import Redis
import redis
from rq import Worker, Queue
import logging
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.INFO)


redis_conn = redis.Redis(host="train-images-redis", port=6379)


queue_name = "train_image_requests"

if __name__ == "__main__":
    worker = Worker([queue_name], connection=redis_conn)
    logging.info("Train Image Worker started, waiting for training jobs...")
    worker.work()
