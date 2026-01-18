# app.py
from flask import Flask, render_template, request
import asyncio
from main import run_process

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
async def index():
    answer = None
    if request.method == "POST":
        question = request.form["question"]
        answer = await run_process(question)
    return render_template("index.html", answer=answer)


if __name__ == "__main__":
    app.run(debug=True)
