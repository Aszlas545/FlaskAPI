from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask:flaskPassword@localhost:5431/flaskApi'
db = SQLAlchemy(app)


class Object(db.Model):
    __tablename__ = 'api'
    id = db.mapped_column(db.Integer, primary_key=True)
    feature_one = db.mapped_column(db.Float, nullable=False)
    feature_two = db.mapped_column(db.Float, nullable=False)
    feature_strat = db.mapped_column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Object({self.id, self.feature_one, self.feature_two, self.feature_strat})"


@app.route('/')
def hello():
    result = db.session.scalars(db.select(Object))
    return render_template('home.html', objects=result)


@app.route('/add')
def add_data():
    return "add"


@app.route('/delete/<record_id>')
def remove_data(record_id):
    return "delete" + str(record_id)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
