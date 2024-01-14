from core.wsgi import application
from waitress import serve
import os



if __name__ == "__main__":
    print("Waitress server is running")
    
    application = serve(
            app=application,
            host=os.environ.get("RAILWAY_HOST", "127.0.0.1"),
            port=os.environ.get("PORT", 8000)
            )
