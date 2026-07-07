from datetime import datetime
from io import BytesIO
import random
from os import getenv
from dotenv import load_dotenv
import pandas as pd
from faker import Faker
from google.cloud import storage

# ============================================================================
# Configuration
# ============================================================================
load_dotenv()
PROJECT_ID = getenv(PROJECT_ID)
BUCKET_NAME = getenv(BUCKET_NAME)

NUM_EMPLOYEES = 100

today = datetime.now().strftime("%Y%m%d")
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

DESTINATION_BLOB = "employee_data.parquet"

# ============================================================================
# Faker
# ============================================================================

fake = Faker("pt_BR")

JOB_TITLES = [
    "Data Analyst",
    "Data Engineer",
    "Data Scientist",
    "Software Engineer",
    "Cybersecurity Analyst",
    "HR Analyst",
    "Financial Analyst",
    "Project Manager",
    "Database Administrator",
    "Cloud Engineer",
]

DEPARTMENTS = [
    "IT",
    "Finance",
    "Human Resources",
    "Marketing",
    "Sales",
    "Operations",
    "Legal",
]

MARITAL_STATUS = [
    "Single",
    "Married",
    "Divorced",
    "Widowed",
]

BLOOD_TYPES = [
    "A+",
    "A-",
    "B+",
    "B-",
    "AB+",
    "AB-",
    "O+",
    "O-",
]

BANKS = [
    "Banco do Brasil",
    "Bradesco",
    "Itaú",
    "Santander",
    "Caixa",
    "Nubank",
]

EMPLOYMENT_STATUS = [
    "Active",
    "Vacation",
    "Medical Leave",
    "Inactive",
]

# ============================================================================
# Employee Generator
# ============================================================================


def generate_employee(employee_id: int) -> dict:
    return {
        # Identifier
        "employee_id": employee_id,

        # Employment
        "job_title": random.choice(JOB_TITLES),
        "department": random.choice(DEPARTMENTS),
        "salary": random.randint(3500, 22000),
        "hire_date": fake.date_between("-10y", "today"),

        # Personal Information (PII)
        "full_name": fake.name(),
        "cpf": fake.cpf(),
        "rg": fake.rg(),
        "email": fake.email(),
        "phone_number": fake.phone_number(),
        "mobile_number": fake.cellphone_number(),
        "birth_date": fake.date_of_birth(minimum_age=18, maximum_age=65),
        "gender": random.choice(["Male", "Female"]),
        "marital_status": random.choice(MARITAL_STATUS),
        "mother_name": fake.name_female(),
        "father_name": fake.name_male(),

        # Address (PII)
        "postal_code": fake.postcode(),
        "street": fake.street_name(),
        "street_number": random.randint(1, 9999),
        "neighborhood": fake.bairro(),
        "city": fake.city(),
        "state": fake.estado_sigla(),
        "country": "Brazil",

        # Documents (PII)
        "driver_license": fake.license_plate(),
        "passport_number": fake.bothify(text="??########"),

        # Banking (PII)
        "bank_name": random.choice(BANKS),
        "bank_branch": random.randint(1000, 9999),
        "bank_account": f"{random.randint(10000,99999)}-{random.randint(0,9)}",
        "pix_key": fake.email(),

        # Sensitive Data
        "blood_type": random.choice(BLOOD_TYPES),
        "number_of_dependents": random.randint(0, 4),

        # Status
        "employment_status": random.choice(EMPLOYMENT_STATUS),
    }


# ============================================================================
# Generate Dataset
# ============================================================================

employees = [
    generate_employee(employee_id)
    for employee_id in range(1, NUM_EMPLOYEES + 1)
]

df = pd.DataFrame(employees)

# ============================================================================
# Upload Parquet to Google Cloud Storage
# ============================================================================
storage_client = storage.Client(project=PROJECT_ID)

bucket = storage_client.bucket(BUCKET_NAME)

blob = bucket.blob(DESTINATION_BLOB)

buffer = BytesIO()

df.to_parquet(
    buffer,
    engine="pyarrow",
    index=False,
)

buffer.seek(0)

blob.upload_from_file(
    buffer,
    content_type="application/octet-stream",
)

# ============================================================================
# Output
# ============================================================================

print(df.head())

print("\nDataset successfully generated!")
print(f"Total employees: {len(df)}")
print(f"Uploaded to: gs://{BUCKET_NAME}/{DESTINATION_BLOB}")