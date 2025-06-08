# finrisk

## Структура проекта
```
risk-project/
│
├── airflow_dags/                # оркестрация пайплайнов  
│   ├── ingest_dag.py            # сбор данных (ЦБ, MOEX, …)  
│   ├── transform_dag.py         # валидация + feature-store  
│   ├── risk_dag.py              # симуляции VaR/ES, backtesting  
│   └── report_dag.py            # генерация витрин и pdf/ppt отчётов
│
├── src/
│   ├── config/                  # pydantic-схемы, YAML/ENV  
│   ├── data_ingestion/          # клиентские обёртки API, web-scrapers  
│   ├── data_validation/         # Great-Expectations/ pandera tests  
│   ├── feature_engineering/     # PCA, факторный анализ  
│   ├── modelling/               # стохастические модели, MLE  
│   ├── risk_simulation/         # Monte-Carlo, VaR 99 %, ES 97.5 % :contentReference[oaicite:0]{index=0}  
│   ├── backtesting/             # Kupiec, Christoffersen, … тесты :contentReference[oaicite:1]{index=1}  
│   ├── reporting/               # генерация таблиц/графиков для Streamlit  
│   └── utils/                   # общие утилиты и типы
│
├── dashboards/                  # Streamlit или Panel приложения  
│   └── app.py                   # интерактивный монитор портфеля и хода расчётов
│
├── notebooks/                   # исследовательские прототипы (не входят в prod)  
├── tests/                       # pytest + coverage  
├── docker/
│   ├── Dockerfile               # единая базовая среда (Poetry)  
│   └── docker-compose.yml       # local-stack S3, Airflow, MLflow UI
├── .github/                     # CI/CD (workflows: lint, tests, build, deploy)
└── README.md                    # как развернуть и запустить end-to-end
```

## Setup работы 

1. Создайте файл .env в корне проекта со следующими переменными:
```
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_DEFAULT_REGION=ru-central1
MLFLOW_S3_BUCKET=your_bucket_name
MLFLOW_S3_ENDPOINT_URL=https://storage.yandexcloud.net
MLFLOW_ARTIFACT_ROOT=s3://your_bucket_name/mlflow
```

2. Создайте виртуальное окружение и активируйте его:
```
bash setup_env.sh
source .venv/bin/activate  # для Linux/Mac
# или
.venv\Scripts\activate  # для Windows
```