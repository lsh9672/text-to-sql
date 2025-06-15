import os


db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "biz_table"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

vector_db_config = {
    "host": os.getenv("VECTOR_DB_HOST", "localhost"),
    "port": os.getenv("VECTOR_DB_PORT", "5432"),
    "database": os.getenv("VECTOR_DB_NAME", "biz_rag"),
    "user": os.getenv("VECTOR_DB_USER", "postgres"),
    "password": os.getenv("VECTOR_DB_PASSWORD", "")
}