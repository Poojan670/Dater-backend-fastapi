from confluent_kafka import Consumer
import json
import main
import asyncio
import nest_asyncio
nest_asyncio.apply()

consumer = Consumer(
    {
        'bootstrap.servers': 'localhost:9092',
        'group.id': 'email-group-id',
        'auto.offset.reset': 'latest',
        'enable.auto.commit': 'false',
        'max.poll.interval.ms': '86400000'
    }
)

consumer.subscribe(['dater-chat', ])


while True:
    msg = consumer.poll(1.0)
    print(msg)
    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    object = msg.value().decode('utf8')
    obj = json.loads(object)

    print(obj)
    
    if obj['msg_to'] == '':
        main.get_message(main.get_db)
    