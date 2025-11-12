import os


def _normalize_database_url(url: str) -> str:
    # Normaliza esquema y añade SSL si Render Postgres
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://"):
        # Usar psycopg3 (psycopg) en lugar de psycopg2
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    # Render Postgres requiere SSL en conexiones externas
    if "render.com" in url and "sslmode=" not in url and "ssl=" not in url:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}sslmode=require"
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave_segura")
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.environ.get(
            "DATABASE_URL",
            # Valor por defecto: Render Postgres externo provisto
            "postgresql://alex1:DKVGIi5VUNnzTB2E9COqVpCMZ38TksOH@dpg-d4786hjipnbc73cmaf30-a.oregon-postgres.render.com/mascotas01",
        )
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False