from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_required, LoginManager
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

class Workingstudents(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    Paypal = db.Column(db.String(80), unique=True, nullable=False)

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day = db.Column(db.String(50), nullable=False)
    meal = db.Column(db.String(200), nullable=False)
    Price = db.Column(db.String(200), nullable=False)

    user = db.relationship('User', backref=db.backref('meals', lazy=True))

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_name):
    return User.query.filter_by(name=user_name).first()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['name'] = request.form['name']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'name' not in session:
        return redirect(url_for('login'))
    user = User.query.filter_by(name=session['name']).first()
    if user is None:
        user = User(name=session['name'])
        db.session.add(user)
        db.session.commit()
    if request.method == 'POST':
        price = request.form.get('Price')
        if not price:
            price = 0
        meal = Meal(user_id=user.id, day=request.form['day'], meal=request.form['meal'], Price=price)
        db.session.add(meal)
        db.session.commit()
        return redirect(url_for('index'))
    days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
    students = Workingstudents.query.all() 
    meals = {day: Meal.query.filter_by(user_id=user.id, day=day).all() for day in days}
    return render_template('index.html', meals=meals,students=students)

@app.route('/delete_meal/<int:meal_id>', methods=['POST'])
def delete_meal(meal_id):
    meal = Meal.query.get(meal_id)
    if meal is not None:
        db.session.delete(meal)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/update_meal/<int:meal_id>', methods=['GET', 'POST'])
def update_meal(meal_id):
    meal = Meal.query.get(meal_id)
    if request.method == 'POST':
        meal.meal = request.form['meal']
        meal.Price = request.form['price']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('update_meal.html', meal=meal)
@app.route('/secretgame')
def secretgame():
    return render_template('secretgame.html')
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, host='0.0.0.0', port=5050)