from flask import Flask, request, render_template, Response
import sys
sys.path.append('../../src/python')
from decoder import decode
from encoder import encode

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return render_template("proton.html")

@app.route("/echo", methods=["GET", "POST"])
def process():
    if request.method == "GET":
        query = request.args.to_dict()
        print("Received GET Query:", query)
        return Response(encode(query), mimetype='proton')
    else:
        decoded = decode(request.data)
        print("Received POST ProtoN Message:", decoded)
        return Response(encode(decoded), mimetype='proton')
