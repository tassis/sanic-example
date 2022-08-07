from sanic import Sanic, HTTPResponse, Request, response
from .view import bp
from . import scheduler

app = Sanic(__name__)

@app.before_server_start
async def startup(app: Sanic):
    scheduler.setup(app)

app.blueprint(bp)
