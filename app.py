from flask import Flask, request, render_template, url_for, redirect, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta


import atexit


from apscheduler.schedulers.background import BackgroundScheduler




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'gntr4n4554h4j5wj5645j5555m5mketmem7k'
db = SQLAlchemy(app)


scheduler = BackgroundScheduler()

class DBF(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False)
    title = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    tm = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return 'DBF %r' % self.id


def delete_by_time():
    with app.app_context():

        tables = DBF.query.all()

        for item_tables in tables:

            if item_tables.tm + timedelta(minutes=5) <= datetime.now():
                db.session.delete(item_tables)
                db.session.commit()


scheduler.add_job(func=delete_by_time, trigger="interval", seconds=360)

scheduler.start()

atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def redirect_login():
    if not session:
        return redirect(url_for('index'))
    else:
        return redirect(url_for("get_ads"))
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect(url_for("get_ads"))
    else:
        return render_template("login.html")

@app.route('/creature', methods=['POST', 'GET'])
def creature():  # создание объявления
    if request.method == "POST":
        username = session['username']
        title = request.form['title']
        content = request.form['content']
        ad = DBF(title=title, content=content, username=username)
        db.session.add(ad)
        db.session.commit()
        return redirect('/ads')

    else:
        return render_template("creature.html")

@app.route('/ads', methods=['POST', 'GET'])
def get_ads(): # функция для вызова объявлений
    data = DBF.query.order_by(DBF.tm.desc()).all()
    return render_template("ads.html", gad=data)

@app.route('/ads/<int:id>')
def additional_information(id): # функция для вывода дополнительной информации
    gad_detail = DBF.query.get(id)
    return render_template("additional_information.html", gad_detail=gad_detail)

@app.route('/ads/<int:id>/removal')
def removal(id): # удаление объявления
    rm = DBF.query.get(id)
    if request.method == "GET":
        if rm.username != session['username']:
            return render_template("return_ads.html")

        else:
            db.session.delete(rm)
            db.session.commit()
            return redirect('/ads')

@app.route('/ads/<int:id>/change', methods=['POST', 'GET'])
def change(id):  # изменение объявления
    rm = DBF.query.get(id)
    if request.method == "POST":
        rm.username = session['username']
        rm.title = request.form['title']
        rm.content = request.form['content']
        db.session.commit()
        return redirect('/ads')

    else:
        if rm.username != session['username']:
            return render_template("return_ads.html")
        else:
            return render_template("change.html", gad_detail=rm)


if __name__ == '__main__':
    app.run()

