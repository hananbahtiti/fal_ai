import os
import logging
from redis import Redis
from rq import Worker

 
logging.basicConfig(level=logging.INFO)

 
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = int(os.getenv("REDIS_PORT", 6379))
queue_name = os.getenv("QUEUE_NAME", "default")

 
redis_conn = Redis(host=redis_host, port=redis_port)

if __name__ == "__main__":
    logging.info(f"Connecting to Redis at {redis_host}:{redis_port}")
    logging.info(f"Listening on queue: {queue_name}")

    worker = Worker([queue_name], connection=redis_conn)
    logging.info("Worker started, waiting for jobs...")
    worker.work()
