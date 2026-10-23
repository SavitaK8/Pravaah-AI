import uvicorn

from . import config

uvicorn.run("pravaah.main:app", host=config.HOST, port=config.PORT)
