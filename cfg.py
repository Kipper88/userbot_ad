from dotenv import load_dotenv
import os

load_dotenv()


api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

API_KEY = os.getenv('API_KEY')

admin_id = [int(x) for x in os.getenv('admin_id').split(',')]
