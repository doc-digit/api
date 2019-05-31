import os

SECRET_KEY = os.getenvb(b"SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

# minio
MINIO_HOST = os.getenv("MINIO_HOST")
MINIO_ACCESS = os.getenv("MINIO_ACCESS")
MINIO_SECRET = os.getenv("MINIO_SECRET")
BUCKET_NAME_PDF = os.getenv("BUCKET_NAME_PDF")
BUCKET_NAME_SCAN = os.getenv("BUCKET_NAME_SCAN")

# database
DB_SERVER = os.getenv("DB_SERVER")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_DATABASE}"
)
