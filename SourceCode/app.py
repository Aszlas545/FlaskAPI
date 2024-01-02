from flask import Flask, render_template, redirect, request, url_for, abort
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


@app.route('/add', methods=['POST', 'GET'])
def add_data():
    if request.method == "POST":
        with app.app_context():
            new_obj = Object(feature_one=request.form['feature_one'],
                             feature_two=request.form['feature_two'],
                             feature_strat=request.form['feature_strat'])
            db.session.add(new_obj)
            db.session.commit()
        return "Record added"
    if request.method == "GET":
        return render_template('addition.html')


@app.route('/delete/<record_id>', methods=['POST', 'GET'])
def delete_data(record_id):
    with app.app_context():
        record_to_delete = Object.query.filter_by(id=record_id).first()
        db.session.delete(record_to_delete)
        db.session.commit()
    return f"Deleted record ID: {record_id}"


@app.route('/delete', methods=['POST'])
def delete():
    identity = request.form['to_remove'].split('=')[-1]
    if identity:
        if Object.query.filter_by(id=identity).first():
            return redirect(url_for('delete_data', record_id=identity))
    else:
        return abort(404)


def redirect_to_add():
    return redirect('/add', code=302)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
