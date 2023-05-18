from waitress import serve

from server.wsgi import application

if __name__ == "__main__":
    serve(application, listen="*:8080")
