from src.bootstrap.config import get_settings
from src.main import app

if __name__ == "__main__":
    settings = get_settings()
    app.run(
        host=settings.app.app_host,
        port=settings.app.app_port,
        debug=settings.app.debug,
        access_log=False,
    )
