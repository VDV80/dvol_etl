from airflow import DAG
from airflow.operators.bash import BashOperator
import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime.datetime(2023, 6, 1),
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}

dag = DAG(
    'example_dag',
    default_args=default_args,
    description='A simple example DAG',
    schedule_interval='@daily',
)

extract_task = BashOperator(
    task_id='extract',
    bash_command='python /home/airflow/dvol_etl/gme_etl/extract_historical.py',
    dag=dag,
)

transform_and_load_task = BashOperator(
    task_id='transform_and_load',
    bash_command='python /home/airflow/dvol_etl/gme_etl/transform.py',
    dag=dag,
)

start_dash_server_task = BashOperator(
    task_id='start_dash_server',
    bash_command='python /home/airflow/dvol_etl/server.py',
    dag=dag,
)

extract_task >> transform_and_load_task >> start_dash_server_task