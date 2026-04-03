#!/usr/bin/env python3
import os
from app import create_app, socketio

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    socketio.run(app, host="0.0.0.0", port=port, debug=(os.getenv("FLASK_ENV") == "development"))
