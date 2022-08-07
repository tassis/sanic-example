from sanic import Sanic

from .struct import AppScheduler

SERVICE_CODE = "app_scheduler"

def get() -> AppScheduler:
    app = Sanic.get_app()
    return getattr(app.ctx, SERVICE_CODE)

def setup(app: Sanic) -> AppScheduler:
    app = Sanic.get_app()
    scheduler = AppScheduler(app)
    setattr(app.ctx, SERVICE_CODE, scheduler)
    return scheduler