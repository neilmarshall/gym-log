import os

from dotenv import load_dotenv

if __name__ == '__main__':
    basedir = os.path.abspath(os.path.split(os.path.dirname(__file__))[0])
    load_dotenv(os.path.join(basedir, '.env'))

    apiKey = os.environ.get('apiKey')

    collectionUID = os.environ.get('collectionUID')
    collection_url = f"https://api.getpostman.com/collections/{collectionUID}?apikey={apiKey}"

    envUID = os.environ.get('envUID')
    env_url = f"https://api.getpostman.com/environments/{envUID}?apikey={apiKey}"

    request = f"newman run {collection_url} --environment {env_url}"

    os.system(request)
