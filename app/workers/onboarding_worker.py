import asyncio
import json
from aiokafka import AIOKafkaConsumer


async def main():
    consumer = AIOKafkaConsumer(
        "employee.onboarding.requested",
        bootstrap_servers="localhost:9092",
        group_id="zero-touch-onboarding-worker",
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
    )

    await consumer.start()

    try:
        async for msg in consumer:
            event = msg.value
            print("Received onboarding event:", event)
            print(f"Would create Google Workspace user: {event.get('employee_email')}")
            print(f"Would create JumpCloud user: {event.get('employee_email')}")
            print("Would send Slack notification")
            print("Would write audit evidence")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())