from confluent_kafka import Producer


class SendEmailProducer:

    """ Producer to produce message to email topic that is consumed in email_service"""

    broker = "localhost:9092"    # broker connection
    topic = 'dater-email'              # manually created topic in confluent kafka
    # producer is None for the first time (optional, as it is done automatically)
    producer = None

    def __init__(self):
        self.producer = Producer({
            'bootstrap.servers': self.broker,
            'socket.timeout.ms': 100,
            'api.version.request': 'false',
            'broker.version.fallback': '0.9.0',
        })

    def message_report(self, err, msg):
        """ Called once for each message produced to indicate delivery result.
                        Triggered by poll() or flush(). """
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
