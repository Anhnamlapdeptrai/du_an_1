from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from Extract.extract_file import get_all_data

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}
dag = DAG(
    dag_id="dag_anh_lap",
    default_args=default_args,
    description="chạy thử từ extract qua transform",
    schedule_interval="@once",
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["example"],
) 

def extract_data():
    get_all_data(symbol="FPT", page=60)

t1 = BashOperator(
    task_id="print_airflow_version",
    bash_command=f"echo 'Airflow version'",
    dag=dag,
)

t2 = PythonOperator(
    task_id="extract_data",
    python_callable=extract_data,
    dag=dag,
)

t3 = BashOperator(
    task_id="transform_data",
    bash_command="docker exec -it producer-2 java -jar /app/producer/target/kafka-csv-producer-1.0.0-jar-with-dependencies.jar",
    dag=dag,
)

t1 >> t2 >> t3

