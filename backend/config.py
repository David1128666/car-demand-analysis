import os

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "car_demand_analysis")
SECRET_KEY = os.getenv("SECRET_KEY", "change-me-before-deploy")
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "change-me-before-deploy")

DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

APP_TITLE = "Car Demand Analysis API"
APP_VERSION = "1.0.0"
