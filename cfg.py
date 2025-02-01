from dotenv import load_dotenv
import os

load_dotenv()


api_id = os.getenv('api_id')
api_hash = os.getenv('api_hash')

API_KEY = os.getenv('API_KEY')

admin_id = [int(x) for x in os.getenv('admin_id').split(',')]

proxies = [
    {
        "scheme": "https",
        "hostname": "213.166.74.10",
        "port": 9918,
        "username": "McBSRj",
        "password": "J5ws6G"       
    },
    {
        "scheme": "https",
        "hostname": "194.67.202.205",
        "port": 9991,
        "username": "McBSRj",
        "password": "J5ws6G"
    },
    {
        "scheme": "https",
        "hostname": "147.45.54.195",
        "port": 9775,
        "username": "McBSRj",
        "password": "J5ws6G"
    }
]