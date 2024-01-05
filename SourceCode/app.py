# import requests
from flask import Flask, render_template, redirect, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask:flaskPassword@localhost:5431/flaskApi'
db = SQLAlchemy(app)

iris_schema = {
    "type": "object",
    "properties": {
        "sepal_length": {"type": "number", "multipleOf": 0.1, "exclusiveMinimum": 0},
        "sepal_width": {"type": "number", "multipleOf": 0.1, "exclusiveMinimum": 0},
        "petal_length": {"type": "number", "multipleOf": 0.1, "exclusiveMinimum": 0},
        "petal_width": {"type": "number", "multipleOf": 0.1, "exclusiveMinimum": 0},
        "flower_species": {"type": "integer", "minimum": 0},
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


def add_to_db(point):
    db.session.add(point)
    db.session.commit()


def delete_by_id(record_id):
    point = Iris.query.filter_by(id=record_id).first()
    db.session.delete(point)
    db.session.commit()
    return point


@app.route('/')
def home_page():
    result = db.session.scalars(db.select(Iris))
    return render_template('home.html', objects=result)


@app.route('/add', methods=['POST', 'GET'])
def add_data():
    if request.method == "POST":
        try:
            sepal_length = float(request.form['sepal_length'])
            sepal_width = float(request.form['sepal_width'])
            petal_length = float(request.form['petal_length'])
            petal_width = float(request.form['petal_width'])
            flower_species = int(request.form['flower_species'])

            if (sepal_length <= 0 or
                    sepal_width <= 0 or
                    petal_length <= 0 or
                    petal_width <= 0 or
                    flower_species < 0):
                raise ValueError
        except ValueError:
            return abort(400)
        point = Iris(sepal_length=sepal_length,
                     sepal_width=sepal_width,
                     petal_length=petal_length,
                     petal_width=petal_width,
                     flower_species=flower_species)
        add_to_db(point)
        return redirect(url_for('home_page'))
    if request.method == "GET":
        return render_template('addition.html')


@app.route('/delete/<record_id>', methods=['POST'])
def delete_data(record_id):
    if db.session.get(Iris, record_id) is not None:
        delete_by_id(record_id)
        return redirect(url_for("home_page"))
    else:
        return abort(404)


@app.route('/api/data', methods=['GET'])
def api_get_points():
    data_points = db.session.scalars(db.select(Iris))
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
        return {"Data added": point.id}, 302
    except ValidationError:
        return {"Invalid data, the data point should follow the schema": iris_schema}, 400


@app.route('/api/data/<int:record_id>', methods=['DELETE'])
def api_delete_point(record_id):
    if db.session.get(Iris, record_id) is not None:
        delete_by_id(record_id)
        return {'Data deleted': record_id}, 302
    else:
        return {"Record with following id not found": record_id}, 404


# @app.route('/test_get')
# def test_get():
#     response = requests.get('http://127.0.0.1:5000/api/data')
#     return response.json()
#
#
# @app.route('/test_post')
# def test_post():
#     point = {
#         "sepal_length": 'abc',
#         "sepal_width": 1.0,
#         "petal_length": 1.0,
#         "petal_width": 1.0,
#         "flower_species": 5,
#     }
#     response = requests.post('http://127.0.0.1:5000/api/data', json=point)
#     return response.json()
#
#
# @app.route('/test_delete')
# def test_delete():
#     response = requests.delete('http://127.0.0.1:5000/api/data/222')
#     return response.json()


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
