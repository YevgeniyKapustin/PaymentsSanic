from sanic import Sanic

from src.bootstrap.app import SanicApplicationBuilder

app: Sanic = SanicApplicationBuilder().build()
