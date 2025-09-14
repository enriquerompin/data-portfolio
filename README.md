# Data Portfolio — Enrique Romero Pineda

> Portafolio de proyectos de Data Engineering: ETL, Data Lakes, Orquestación, Data Quality y buenas prácticas en AWS.

## Índice de proyectos
- **ETL Pipeline (Python + SQL)** — `projects/etl-pipeline`
- **Data Lake (AWS S3 + Glue + Athena)** — `projects/data-lake-aws`
- **Orquestación (Airflow)** — `projects/airflow-dags`
- **Data Quality (Great Expectations)** — `projects/data-quality`
- **Templates & Best Practices** — `templates/`

## Cómo ejecutar local (ejemplo ETL)
```bash
cd projects/etl-pipeline
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_etl.py
