import requests
from flask import Flask, render_template, redirect, request, url_for, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask:flaskPassword@localhost:5431/flaskApi'
db = SQLAlchemy(app)

iris_schema = {
    "type": "object",
    "properties": {
        "sepal_length": {"type": "number", "multipleOf": 0.1},
        "sepal_width": {"type": "number", "multipleOf": 0.1},
        "petal_length": {"type": "number", "multipleOf": 0.1},
        "petal_width": {"type": "number", "multipleOf": 0.1},
        "flower_species": {"type": "integer"},
    },
    "required": ["sepal_length", "sepal_width", "petal_length", "petal_width", "flower_species"]
}


class Iris(db.Model):
    __tablename__ = 'iris'
    id = db.mapped_column(db.Integer, primary_key=True)
    sepal_length = db.mapped_column(db.Float, nullable=False)
    sepal_width = db.mapped_column(db.Float, nullable=False)
    petal_length = db.mapped_column(db.Float, nullable=False)
    petal_width = db.mapped_column(db.Float, nullable=False)
    flower_species = db.mapped_column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Object({self.id,
                         self.sepal_length,
                         self.sepal_width,
                         self.petal_length,
                         self.petal_width,
                         self.flower_species})"


@app.route('/')
def hello():
    result = db.session.scalars(db.select(Iris))
    return render_template('home.html', objects=result)


@app.route('/add', methods=['POST', 'GET'])
def add_data():
    if request.method == "POST":
        with app.app_context():
            new_obj = Iris(sepal_length=request.form['sepal_length'],
                           sepal_width=request.form['sepal_width'],
                           petal_length=request.form['petal_length'],
                           petal_width=request.form['petal_width'],
                           flower_species=request.form['flower_species'])
            db.session.add(new_obj)
            db.session.commit()
        return "Record added"
    if request.method == "GET":
        return render_template('addition.html')


@app.route('/delete/<record_id>', methods=['POST', 'GET'])
def delete_data(record_id):
    with app.app_context():
        point = Iris.query.filter_by(id=record_id).first()
        db.session.delete(point)
        db.session.commit()
    return f"Deleted record ID: {record_id}"


@app.route('/delete', methods=['POST'])
def delete():
    identity = request.form['to_remove'].split('=')[-1]
    if identity:
        if Iris.query.filter_by(id=identity).first() is not None:
            return redirect(url_for('delete_data', record_id=identity))
        else:
            return abort(404)
    else:
        return abort(404)


def redirect_to_add():
    return redirect('/add', code=302)


@app.route('/api/data', methods=['GET'])
def api_get_all():
    data_points = Iris.query.all()
    data = [{'id': point.id,
             'sepal_length': point.sepal_length,
             'sepal_width': point.sepal_width,
             'petal_length': point.petal_length,
             'petal_width': point.sepal_width,
             'flower_species': point.flower_species}
            for point in data_points]
    return data


@app.route('/api/data', methods=['POST'])
def app_add_point():
    data = request.json
    try:
        validate(instance=data, schema=iris_schema)
        point = Iris(sepal_length=data.get('sepal_length'),
                     sepal_width=data.get('sepal_width'),
                     petal_length=data.get('petal_length'),
                     petal_width=data.get('petal_width'),
                     flower_species=data.get('flower_species'))
        db.session.add(point)
        db.session.commit()
        return jsonify({"Data added": point.id})
    except ValidationError:
        return {404: "Invalid data"}, 404


@app.route('/api/data/<int:record_id>', methods=['DELETE'])
def api_delete_point(record_id):
    try:
        with app.app_context():
            point = Iris.query.filter_by(id=record_id).first()
            db.session.delete(point)
            db.session.commit()
        return jsonify({'primary key': point.id})
    except:
        return jsonify({404: "Record not found"})


@app.route('/test_get')
def test_get():
    response = requests.get('http://127.0.0.1:5000/api/data')
    return response.json()


@app.route('/test_post')
def test_post():
    point = {
        "sepal_length": 1.0,
        "sepal_width": 1.0,
        "petal_length": 1.0,
        "petal_width": 1.0,
        "flower_species": 5,
    }
    response = requests.post('http://127.0.0.1:5000/api/data', json=point)
    return response.json()


@app.route('/test_delete')
def test_delete():
    response = requests.delete('http://127.0.0.1:5000/api/data/173')
    return response.json()


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
