from aiokafka import AIOKafkaProducer

producer = None


async def start_kafka_producer():
    global producer

    try:
        producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092"
        )
        await producer.start()
        print("Kafka producer started")
    except Exception as error:
        producer = None
        print(f"Kafka skipped: {error}")


async def stop_kafka_producer():
    global producer

    if producer:
        await producer.stop()
        print("Kafka producer stopped")


async def publish_event(topic: str, event: dict):
    if not producer:
        return {
            "status": "skipped",
            "message": "Kafka is not running locally",
            "topic": topic,
            "event": event,
        }

    await producer.send_and_wait(
        topic,
        str(event).encode("utf-8")
    )

    return {
        "status": "published",
        "topic": topic,
        "event": event,
    }