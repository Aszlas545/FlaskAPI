from flask import Flask
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
    return "Hello, this is your Flask API!"


@app.route('/test')
def get_data():
    return "test"


with app.app_context():
    db.create_all()

with app.app_context():
    obj = Object(feature_one=0.1, feature_two=1.1, feature_strat=5)
    db.session.add(obj)
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
