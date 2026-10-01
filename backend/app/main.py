"""Local entry point; single-process synthetic demo."""

from app.api.routes import create_app

app = create_app()
