from confluent_kafka import Producer

class KafkaNewsSink:
    def __init__(self, server_str, topic, callback_fn):
        self.producer = Producer({'bootstrap.servers' : server_str})
        self.callback_fn = callback_fn
        self.topic = topic

    def send(self, item):
        self.producer.poll(0)
        self.producer.produce(self.topic, item.encode('utf-8'), callback=self.callback_fn)

    def flush(self):
        self.producer.flush()

