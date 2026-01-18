# app.py
from flask import Flask, render_template, request
from delphi import run_delphi_process

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    answer = None
    if request.method == 'POST':
        question = request.form['question']
        answer = run_delphi_process(question)
    return render_template('index.html', answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
