import os
from mongoengine import connect

def connect_to_db(database, port=None, host=None):
    mongo_host = host or os.environ.get("MONGO_HOST", 'localhost')
    mongo_port = port or int(os.environ.get("MONGO_PORT", 27017))

    print(f"Connecting to {mongo_host}:{mongo_port} - db : {database}")
    client = connect(database, host=mongo_host, port=mongo_port)
    print(client)
    return client[database]
