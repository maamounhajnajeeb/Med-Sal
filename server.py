from waitress import serve
from core.wsgi import application


if __name__ == "__main__":
    print("Running waitress")
    serve(app=application, host="127.0.0.1", port="8000")
