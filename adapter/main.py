from sanic import Sanic
from sanic.response import json, text, stream
from sanic_openapi import swagger_blueprint, openapi_blueprint, doc


app = Sanic()

# api doc
app.blueprint(openapi_blueprint)
app.blueprint(swagger_blueprint)

@app.route("/")
async def index(request):
    return json({'hi':True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)