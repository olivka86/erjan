import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
GROUPID = int(os.getenv("GROUPID"))
CONFIRMATION_CODE = os.getenv("CONFIRMATION_CODE")

SBER_CARD_NUMBER = os.getenv("SBER_CARD_NUMBER")
SBER_PHONE_NUMBER = os.getenv("SBER_PHONE_NUMBER")

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_IP = os.getenv("POSTGRES_IP")
POSTGRES_DB = os.getenv("POSTGRES_DB")
