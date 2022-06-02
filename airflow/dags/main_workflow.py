from airflow import DAG
from airflow.decorators import dag
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

import datetime
# from pathlib import Path
import os, sys

from ETL.extract import extract_data_from_source
from ETL.transform import transform_data
from ETL.load import load_data_to_target

from data_ingestion.sourcedb_order_schedule import dummy_order_ingestion

# root_dir = Path(__file__).parent.parent.absolute()
# print(root_dir)

default_args = {
    'owner': 'airflow',
    'depends_on_past': True,
    'retries': 1,
    'retry_delay': datetime.timedelta(minutes=5),
}


# ETL Pipeline
@dag(
    dag_id = "etl_pipeline",
    description='ETL Pipeline',
    start_date=datetime.datetime(2022, 1 ,1), 
    schedule_interval="0 * * * *",
    default_args=default_args,
    is_paused_upon_creation=True,
    catchup=False
)
def etl():     
    extract_task_id = PythonOperator(
        task_id='extract',
        python_callable=extract_data_from_source,
        op_kwargs={
            "time1" : "{{execution_date.strftime('%Y-%m-%d %H:%M:%S')}}",
            "time2" : "{{next_execution_date.strftime('%Y-%m-%d %H:%M:%S')}}"
        }
    )

    transform_task_id = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
    )

    load_data_task_id = PythonOperator(
        task_id="load",
        python_callable=load_data_to_target,
    )

    extract_task_id >> transform_task_id >> load_data_task_id


# Dummy order ingestion pipeline
@dag(
    dag_id = "dummy_data_pipeline",
    description='Dummy order ingestion Pipeline',
    start_date=datetime.datetime(2022, 1 ,1), 
    schedule_interval="*/3 * * * *", 
    default_args=default_args,
    catchup=False
)
def dummy_order():
    t1 = BashOperator(
        task_id="display",
        bash_command="echo {{ execution_date.strftime('%Y-%m-%d %H:%M:%S') }} {{ next_execution_date.strftime('%Y-%m-%d %H:%M:%S') }}",
    )
        
    dummy_order_task = PythonOperator(
        task_id='dummy_order',
        python_callable=dummy_order_ingestion
    )

    t1>>dummy_order_task


# Define DAGs
etl_dag = etl()
dummy_order_dag = dummy_order()




