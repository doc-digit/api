import os

from sanic import Sanic, response
from sanic_openapi import swagger_blueprint


app = Sanic("docdigit-api")

if os.getenv('DEBUG', False):
    import settings.dev 

    app.config.from_object(settings.dev)
    
from .database import db

db.init_app(app)

# api doc 
app.blueprint(swagger_blueprint)

# api modules 
from .modules import storage

app.blueprint(storage)

# exceptions handling 
from sanic.exceptions import NotFound, ServerError

@app.exception(NotFound)
async def response404(request, exception):
    return response.json({'status': 'fail', 'error': "Page not found"}, status=404)

@app.exception(ServerError)
async def response500(request, exception):
    print(exception) # TODO add logger
    return response.json({'status': 'fail', 'error': "Server error"}, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)