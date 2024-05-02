import os
import requests
from loguru import logger

def download_file(url, filename):
    response = requests.get(url)
    if response.status_code == 200:
        with open(filename, 'wb') as file:
            file.write(response.content)
        logger.info(f"Arquivo {filename} baixado com sucesso!")
    else:
        logger.info(f"Falha ao baixar o arquivo. Código de status: {response.status_code}")

def download_bootstrap(modules):
    url = "https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css.map"
    for module in modules:
        localpath = os.path.join(
            os.sep.join(os.path.abspath(module.__file__).split(os.sep)[:-1]),
            "frontend/build/bootstrap.min.css.map"
        )
        download_file(url, localpath)