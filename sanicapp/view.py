from sanic import Blueprint, HTTPResponse, Request, response
from . import scheduler

bp = Blueprint("peon")

def typed(request: Request) -> HTTPResponse:
    """
    get Done(sync)
	
    :param reuqest [sanic.Request]
    """
    _scheudler = scheduler.get()
    print(_scheudler)
    return response.text("Done")

# register route by decorator
@bp.get("/async_typed/<tag>")
async def async_typed(request: Request, tag: str) -> HTTPResponse:
    """
    get Done(async)
	
    :param reuqest [sanic.Request]
    """
    return response.text("Done")

# register route by add_route()
bp.add_route(typed, "/typed", methods=["GET"])