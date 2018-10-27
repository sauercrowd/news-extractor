from utils.rss_feed import RSSFeed
from utils.rss_feed import array_to_dict_items
from utils.kafka import KafkaNewsSink

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import json
import pickle

default_args = {
    'owner': 'Jonas',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG('BBC', default_args=default_args, schedule_interval=timedelta(seconds=20))


def callback_fn(err, msg):
    print(err if err is not None else msg)

sink = KafkaNewsSink('127.0.0.1', 'news', callback_fn)

def acquire_news_fn(**kwargs):
    filename='bbc_old_items.pickle'
    keyname = 'item_url'

    feed = RSSFeed('http://feeds.bbci.co.uk/news/rss.xml')
    items = feed.get_items_as_dict()

    try:
        with open(filename, 'rb') as f:
            old_items = pickle.load(f)
    except (FileNotFoundError, EOFError):
        with open(filename, 'wb') as f:
            pickle.dump(items, f)
        kwargs['ti'].xcom_push(value=[], key='feed')
        return

    items_dict = array_to_dict_items(items, keyname)
    old_items_dict = array_to_dict_items(old_items, keyname)

    new_items = []
    print(items)
    for ni in items_dict:
        if ni not in old_items_dict:
            new_items.append(items_dict[ni])
    kwargs['ti'].xcom_push(value=new_items, key='feed')

    with open(filename, 'wb') as f:
        pickle.dump(items, f)

acquire_news = PythonOperator(
    task_id='acquire_news',
    python_callable=acquire_news_fn,
    provide_context=True,
    dag=dag)


def news_to_kafka_fn(**kwargs):
    items = kwargs['ti'].xcom_pull(key='feed', task_ids='acquire_news')
    for i in items:
        sink.send(json.dumps(i))
    sink.flush()

news_to_kafka = PythonOperator(
    task_id='news_to_kafka',
    python_callable=news_to_kafka_fn,
    provide_context=True,
    dag=dag)

news_to_kafka.set_upstream(acquire_news)
