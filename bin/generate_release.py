import os
import fire
import json
import subprocess
from hate_collector import connect_to_db

def generate_mongo_query(query_json):
    """
    Generates a mongo query from a JSON query
    """

    text_query = " ".join(query_json["search_terms"])

    mongo_query = {
        "user": {"$in": query_json["users"]},
        "created_at": {"$gte": {"$date": query_json["min_date"]}},
        "$text": {"$search": text_query},
    }

    return json.dumps(mongo_query)

def generate_release(database, query, out):
    """
    Generate a release of the data

    Parameters
    ----------

    database: string
        Name of mongo database

    query_file: string
        Path to a query file

    out: string
        Output path
    """

    with open(query) as f:
        query = json.load(f)

    mongo_query = generate_mongo_query(query)

    export_command = f"""mongoexport -d {database} -c article --jsonArray --pretty \
--query '{mongo_query}' \
--fields 'tweet_id,text,slug,title,url,user,body,created_at,comments' \
--out {out}"""

    print(export_command)
    os.system(export_command)

if __name__ == '__main__':
    fire.Fire(generate_release)
