from fastapi import FastAPI
from slack_helloworld.slack_helloworld.helloworld import HelloWorld
import logging

app = FastAPI()
logger = logging.getLogger("main")


@app.get("/helloWorld")
async def root():
    logger.info("http request in")
    return HelloWorld.getMessage()
