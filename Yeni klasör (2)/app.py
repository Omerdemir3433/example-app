from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DATABASE = 'scores.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    db = get_db()
    cur = db.execute('SELECT MAX(score) FROM scores')
    best_score = cur.fetchone()[0]

    return render_template('quiz.html', best_score=best_score)


@app.route('/submit', methods=['POST'])
def submit():
    answers = {
        'q1': '8',
        'q2': '6',
        'q3': '6',
        'q4': '4',
        'q5': '13'
    }

    score = 0
    max_score = 100
    points_per_question = max_score / len(answers)
    
    for question, correct_answer in answers.items():
        if request.form.get(question) == correct_answer:
            score += points_per_question

    score = int(score)

    db = get_db()
    db.execute('INSERT INTO scores (score) VALUES (?)', [score])
    db.commit()

    cur = db.execute('SELECT MAX(score) FROM scores')
    best_score = cur.fetchone()[0]

    return redirect(url_for('result', score=score, best_score=best_score))

@app.route('/result')
def result():
    score = request.args.get('score')
    best_score = request.args.get('best_score')

    db = get_db()
    cur = db.execute('SELECT score FROM scores')
    all_scores = cur.fetchall()

    return render_template('result.html', score=score, best_score=best_score, all_scores=all_scores)

@app.route('/delete_scores', methods=['POST'])
def delete_scores():
    db = get_db()
    db.execute('DELETE FROM scores')
    db.commit()
    return redirect(url_for('result', score=0, best_score=0))

if __name__ == '__main__':
    app.run(debug=True)
