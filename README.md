# Data Source API — Dirty Data Generator

REST API developed with **FastAPI** to generate synthetic datasets containing intentionally dirty sales and order records. The project is designed as the data source for a data engineering pipeline, where raw data will later be cleaned, transformed, and validated using ETL tools.

The main goal is to simulate real-world data quality problems and practice an architecture using **FastAPI, Docker, Amazon S3, Apache Airflow, and Apache Spark**.

## Project Status

**Current stage:** Local API development and AWS S3 integration.

The API structure, data generator, Docker configuration, and S3 storage implementation have been created. However, S3 permissions and the complete upload/retrieval workflow still need to be validated.

## What Does This Project Do?

The API generates synthetic order records with configurable data quality issues, such as:

- Invalid dates.
- Inconsistent city names.
- Negative quantities.
- Missing values.
- Negative prices.

Generated batches contain metadata, including a batch ID, total record count, number of intentionally dirty records, and creation timestamp.

The original records are stored in Amazon S3 under a raw data prefix. The goal is to preserve the data in its original state before the ETL process cleans it.

## Architecture Overview

The planned workflow is:

1. FastAPI generates synthetic order records.
2. The generated batch is uploaded to Amazon S3.
3. Amazon S3 stores the raw data and batch metadata.
4. Apache Airflow will orchestrate the ETL workflow.
5. Apache Spark will clean and transform the raw data.
6. The cleaned data will be stored in a separate destination for further analysis.

A scheduled AWS execution is also planned to generate batches automatically every 30 minutes, without requiring a manual API request.

**Note:** The scheduled AWS execution and the Airflow/Spark pipeline are planned components, not yet confirmed as operational.

## Technology Stack

- **Python** — data generation and application logic.
- **FastAPI** — REST API.
- **Pydantic** — request validation and configuration.
- **Boto3** — Amazon S3 integration.
- **Docker and Docker Compose** — local containerized development.
- **Amazon S3** — raw data storage.
- **Apache Airflow** — planned workflow orchestration.
- **Apache Spark** — planned data cleaning and transformation.

## Project Structure

```text
data-source-api/
├── app/
│   ├── main.py
│   ├── generate_batch.py
│   ├── core/
│   │   └── config.py
│   ├── models/
│   │   └── record.py
│   ├── routers/
│   ├── schemas/
│   │   └── batch.py
│   └── services/
│       ├── order_generator.py
│       └── s3_storage.py
├── schema/
├── .dockerignore
├── .gitignore
├── compose.yaml
├── dockerfile
├── requirements.txt
└── README.md
```

The structure above describes the intended organization. Some folders may not contain implemented functionality yet.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check whether the API is running. |
| POST | `/api/v1/batches/generate` | Generate a batch and upload it to S3. |
| GET | `/api/v1/batches` | List stored batch metadata. |
| GET | `/api/v1/batches/{batch_id}` | Retrieve a batch and its records. |

Interactive documentation is available at `/docs` when the API is running.

### Generate a Batch

Example request:

```json
{
  "amount": 100,
  "error_percentage": 20,
  "seed": 42
}
```

- `amount`: number of records to generate, from 1 to 20,000.
- `error_percentage`: percentage of records that should contain intentional errors.
- `seed`: optional value to make the generated data reproducible.

## Setup on a New Computer

### 1. Install the prerequisites

Install:

- Git
- Docker Desktop
- Python, if you also want to run or debug the application outside Docker
- AWS CLI, for configuring and testing local AWS access

### 2. Clone the repository

```bash
git clone https://github.com/Alexandra009mm/data-source-api.git
cd data-source-api
```

### 3. Configure environment variables

Create a local `.env` file if the application configuration loads environment variables from it.

Example:

```dotenv
S3_BUCKET=your-s3-bucket-name
AWS_DEFAULT_REGION=your-aws-region
```

Replace these example values with the actual bucket name and region.

**Never commit `.env` or AWS credentials to GitHub.**

### 4. Configure AWS access

Configure an AWS CLI profile using an appropriate authentication method.

Verify the identity:

```bash
aws sts get-caller-identity
```

The identity used locally must have the required S3 permissions for the configured bucket.

For local Docker development, ensure the container can access the intended AWS profile and credentials. The current Docker Compose configuration may need to mount the AWS configuration directory or use another secure credential method.

For a future ECS deployment, use an IAM task role instead of embedding access keys in the container.

### 5. Start the API

```bash
docker compose up --build -d
```

Check the logs:

```bash
docker compose logs -f api
```

Open the API documentation:

http://localhost:8000/docs

Check the health endpoint:

http://localhost:8000/health

Stop the containers:

```bash
docker compose down
```

## Pending Tasks

### Phase 1 — Finish the API and S3 integration

- [ ] Create or configure an IAM identity with least-privilege access to the S3 bucket.
- [ ] Verify that the bucket name and AWS region are correct.
- [ ] Configure local AWS credentials securely for Docker.
- [ ] Test `GET /api/v1/batches`.
- [ ] Test `POST /api/v1/batches/generate` with a small batch.
- [ ] Verify that the data file and metadata are created in S3.
- [ ] Test `GET /api/v1/batches/{batch_id}`.
- [ ] Handle and test common AWS errors.

### Phase 2 — Improve the data generator

- [ ] Review the record schema and the available data quality errors.
- [ ] Validate that the requested dirty-record percentage matches the generated results.
- [ ] Test reproducibility when a seed is supplied.
- [ ] Add automated tests for the generator, request validation, and storage service.

### Phase 3 — Automate batch generation

- [ ] Build and publish the Docker image to Amazon ECR.
- [ ] Create an ECS Fargate task that runs `python -m app.generate_batch`.
- [ ] Configure the ECS task role for S3 access.
- [ ] Create an EventBridge Scheduler schedule to run the task every 30 minutes.
- [ ] Verify task execution, logs, failures, and costs.

### Phase 4 — Build the ETL pipeline

- [ ] Configure the raw S3 prefix as the input data source.
- [ ] Set up Apache Airflow as the orchestrator.
- [ ] Develop the Spark transformation and cleaning process.
- [ ] Define a separate destination for cleaned data.
- [ ] Validate record counts, rejected records, and data quality metrics.
- [ ] Make the pipeline idempotent so reruns do not accidentally duplicate output.

### Phase 5 — Documentation and deployment

- [ ] Document the AWS architecture.
- [ ] Add deployment and troubleshooting instructions.
- [ ] Add automated testing to the development workflow.
- [ ] Document the cost assumptions and AWS resources that need cleanup.

## Important Notes

- This is a learning project and is still under development.
- The API does not use PostgreSQL for storing the generated batches; Amazon S3 is the intended storage layer.
- The raw data is intentionally dirty. Cleaning belongs to the future ETL pipeline.
- The automatic schedule and the Airflow/Spark pipeline should be marked as complete only after they have been implemented and tested.
- Never commit AWS access keys, secret keys, session tokens, or local environment files.

## Repository

GitHub: https://github.com/Alexandra009mm/data-source-api
