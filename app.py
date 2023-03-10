from flask import Flask, render_template, session, g, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = '1F7VkTpXpSBo9P6Oskv9Kq$23QwD9FG44U'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(15), nullable=False)


class Routes(db.Model):
    routeId = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(10), nullable=False)
    routePoints = db.Column(db.String(500), nullable=False)
    create_time = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))


class Static(db.Model):
    routeId = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('users.id'))
    startPoint = db.Column(db.String(20), nullable=False)
    finishPoint = db.Column(db.String(20), nullable=False)


@app.before_request
def before_request():
    if 'user_id' in session:
        user = [person for person in Users.query.all() if person.id == session['user_id']][0]
        g.user = user


@app.route('/')
def index():
    if session:
        history_routes = [routes for routes in Routes.query.all() if
                          g.user.id == routes.userId and routes.type == "history"]
        history_routes = [rt.routePoints.split(",") for rt in history_routes]

        favorite_routes = [routes for routes in Routes.query.all()
                          if g.user.id == routes.userId and routes.type == "favorites"]
        favorite_routes = [rt.routePoints.split(",") for rt in favorite_routes]
        print(favorite_routes)
    else:
        history_routes = []
        favorite_routes = []
    return render_template("index.html", history=history_routes, favorites=favorite_routes)


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)
        login = request.form.get('login')
        password = request.form.get('password')
        user = [person for person in Users.query.all() if person.login == login]
        if not user:
            return "???????????????????????? ?? ???????????? ?????????????? ???? ????????????????????"
        elif not check_password_hash(user[0].password, password):
            return "???????????? ???????????????? ????????????"
        else:
            session['user_id'] = user[0].id
            return redirect(url_for('index'))
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route("/registration", methods=["POST", "GET"])
def registration():
    if request.method == 'POST':
        if any([True if person.login == request.form.get('login') else False for person in Users.query.all()]):
            return "???????????????????????? ?? ?????????? ?????????????? ?????? ????????????????????"
        elif request.form.get('password') != request.form.get('repassword'):
            return "?????????????????? ???????????? ???? ??????????????????"
        else:
            u = Users(login=request.form.get('login'),
                      password=generate_password_hash(request.form.get('password')))
            db.session.add(u)
            db.session.flush()
            db.session.commit()
            return redirect(url_for('login'))
    return render_template("registration.html")


# ?????????????????? ?????????????? JQuery

@app.route("/favorites")
def favorites():
    start, finish = request.args.get('start', 0, type=str), request.args.get('finish', 0, type=str)
    if session:
        print(start, finish)
        db.session.add(Routes(type="favorites",
                              userId=g.user.id,
                              routePoints=start + ',' + finish))
        db.session.flush()
        db.session.commit()
    return jsonify(result=" ")


@app.route("/history")
def history():
    start, finish = request.args.get('start', 0, type=str), request.args.get('finish', 0, type=str)
    if session:
        print(start, finish)
        db.session.add(Routes(type="history",
                              userId=g.user.id,
                              routePoints=start + ',' + finish))
        db.session.flush()
        db.session.commit()
    return jsonify(result=" ")


@app.route("/favorites_dynamic")
def favorites_dynamic():
    pnts = request.args.get('pnts', 0, type=str).rstrip(",")
    if session:
        print(pnts)
        db.session.add(Routes(type="favorites",
                              userId=g.user.id,
                              routePoints=pnts))
        db.session.flush()
        db.session.commit()
    return jsonify(result=" ")


@app.route("/history_dynamic")
def history_dynamic():
    pnts = request.args.get('pnts', 0, type=str).rstrip(",")
    if session:
        print(pnts)
        db.session.add(Routes(type="history",
                              userId=g.user.id,
                              routePoints=pnts))
        db.session.flush()
        db.session.commit()
    return jsonify(result=" ")


if __name__ == '__main__':
    app.run()
