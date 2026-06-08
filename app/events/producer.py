import json
from aiokafka import AIOKafkaProducer

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

producer = None


async def start_kafka_producer():
    global producer

    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    await producer.start()


async def stop_kafka_producer():
    global producer

    if producer:
        await producer.stop()


async def publish_event(topic: str, event: dict):
    if producer is None:
        raise RuntimeError("Kafka producer not started")

    await producer.send_and_wait(topic, event)