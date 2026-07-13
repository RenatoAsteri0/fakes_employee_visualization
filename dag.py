from datetime import datetime, timedelta
from airflow.providers.google.cloud.operators.datafusion import CloudDataFusionStartPipelineOperator
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "Renato",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="employee_data_pipeline",
    start_date=datetime(2026, 7, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["etl", "gcp"],
) as dag:

    extract_data = BashOperator(
        task_id="extract_and_upload_gcs",
        bash_command="python3 /home/airflow/gcs/dags/scripts/extract.py",
    )

    start_pipeline = CloudDataFusionStartPipelineOperator(
        location='us-east1',
        pipeline_name='etl-pipelin',
        instance_name='etl-employee',
        pipeline_timeout=1000,
        task_id="start_datafusion_pipeline",
        asynchronous=True
    )
    extract_data >> start_pipeline