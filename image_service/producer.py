from confluent_kafka import Producer


class SendImageUrlProducer:

    """Producer To produce messages containing image bytes to consume in image_service"""

    broker = 'localhost:9092'
    topic = 'dater-image-url'

    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': self.broker,
            'socket.timeout.ms': 100,
            'api.version.request': 'false',
            'broker.version.fallback': '0.9.0',
        })

    def message_report(self, err, msg):
        if err is not None:
            print('Message delivery failed: {}'.format('err'))
        else:
            print('Message delivered to {} [{}]'.format(
                msg.topic(), msg.partition()))

    def send_msg_async(self, msg):
        self.producer.produce(
            self.topic,
            msg,
            callback=lambda err, original_msg=msg: self.message_report(
                err, original_msg),
        )
        self.producer.flush()
