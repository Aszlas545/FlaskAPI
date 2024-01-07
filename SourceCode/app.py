import requests
from flask import Flask, render_template, redirect, request, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from jsonschema import validate, ValidationError
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler

knn = KNeighborsClassifier(n_neighbors=5)
knn2 = KNeighborsClassifier(n_neighbors=5)
scaler = StandardScaler()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://flask:flaskPassword@localhost:5431/flaskApi'
db = SQLAlchemy(app)

iris_schema = {
    "type": "object",
    "properties": {
        "sepal_length": {"type": "number", "exclusiveMinimum": 0},
        "sepal_width": {"type": "number", "exclusiveMinimum": 0},
        "petal_length": {"type": "number", "exclusiveMinimum": 0},
        "petal_width": {"type": "number", "exclusiveMinimum": 0},
        "flower_species": {"type": "integer", "minimum": 0},
    },
    "required": ["sepal_length", "sepal_width", "petal_length", "petal_width", "flower_species"]
}

iris_prediction_schema = {
    "type": "object",
    "properties": {
        "sepal_length": {"type": "number", "exclusiveMinimum": 0},
        "sepal_width": {"type": "number", "exclusiveMinimum": 0},
        "petal_length": {"type": "number", "exclusiveMinimum": 0},
        "petal_width": {"type": "number", "exclusiveMinimum": 0},
    },
    "required": ["sepal_length", "sepal_width", "petal_length", "petal_width"]
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
    train_model()
    train_model_std()


def delete_by_id(record_id):
    point = Iris.query.filter_by(id=record_id).first()
    db.session.delete(point)
    db.session.commit()
    train_model()
    train_model_std()
    return point


def predict(sepal_length, sepal_width, petal_length, petal_width):
    sample = [[sepal_length, sepal_width, petal_length, petal_width]]
    return knn.predict(sample)


def predict_std(sepal_length, sepal_width, petal_length, petal_width):
    sample = scaler.transform([[sepal_length, sepal_width, petal_length, petal_width]])
    return knn2.predict(sample)


def train_model():
    data_points = db.session.scalars(db.select(Iris))
    data = [[point.sepal_length,
             point.sepal_width,
             point.petal_length,
             point.sepal_width]
            for point in data_points]
    target = list(db.session.scalars(db.select(Iris.flower_species)))
    knn.fit(data, target)


def train_model_std():
    data_points = db.session.scalars(db.select(Iris))
    data = [[point.sepal_length,
             point.sepal_width,
             point.petal_length,
             point.sepal_width]
            for point in data_points]
    target = list(db.session.scalars(db.select(Iris.flower_species)))
    scaler.fit(data)
    train_data = scaler.transform(data)
    knn2.fit(train_data, target)


@app.route('/')
def home_page():
    result = db.session.scalars(db.select(Iris))
    return render_template('home.html', objects=result)


@app.route('/add', methods=['POST', 'GET'])
def add_point():
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
def delete_point(record_id):
    if db.session.get(Iris, record_id) is not None:
        delete_by_id(record_id)
        return redirect(url_for("home_page"))
    else:
        return abort(404)


@app.route('/predict', methods=['POST', 'GET'])
def predict_point():
    if request.method == "POST":
        try:
            sepal_length = float(request.form['sepal_length'])
            sepal_width = float(request.form['sepal_width'])
            petal_length = float(request.form['petal_length'])
            petal_width = float(request.form['petal_width'])

            if (sepal_length <= 0 or
                    sepal_width <= 0 or
                    petal_length <= 0 or
                    petal_width <= 0):
                raise ValueError

            flower_species = int(predict(sepal_length, sepal_width, petal_length, petal_width)[0])
            flower_species_std = int(predict_std(sepal_length, sepal_width, petal_length, petal_width)[0])
        except ValueError:
            return abort(400)

        return render_template('predicted.html',
                               flower_species=flower_species,
                               flower_species_std=flower_species_std)
    if request.method == "GET":
        return render_template('prediction.html')


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
def api_add_point():
    data = request.json
    try:
        validate(instance=data, schema=iris_schema)
        point = Iris(sepal_length=data.get('sepal_length'),
                     sepal_width=data.get('sepal_width'),
                     petal_length=data.get('petal_length'),
                     petal_width=data.get('petal_width'),
                     flower_species=data.get('flower_species'))
        add_to_db(point)
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


@app.route('/api/predictions', methods=['POST'])
def api_predict_point():
    data = request.json
    try:
        validate(instance=data, schema=iris_prediction_schema)

        sepal_length = data.get('sepal_length')
        sepal_width = data.get('sepal_width')
        petal_length = data.get('petal_length')
        petal_width = data.get('petal_width')

        flower_species = int(predict(sepal_length, sepal_width, petal_length, petal_width)[0])
        flower_species_std = int(predict_std(sepal_length, sepal_width, petal_length, petal_width)[0])

        return {"predicted_without_std": flower_species,
                "predicted_with_std:": flower_species_std}, 302
    except ValidationError:
        return {"Invalid data, the data point should follow the schema": iris_prediction_schema}, 400


@app.route('/test_get')
def test_get():
    response = requests.get('http://127.0.0.1:5000/api/data')
    return response.json()


@app.route('/test_post')
def test_post():
    point = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
        "flower_species": 0,
    }
    response = requests.post('http://127.0.0.1:5000/api/data', json=point)
    return response.json()


@app.route('/test_delete')
def test_delete():
    response = requests.delete('http://127.0.0.1:5000/api/data/222')
    return response.json()


@app.route('/test_predict')
def test_predict():
    point = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = requests.post('http://127.0.0.1:5000/api/predictions', json=point)
    return response.json()


with app.app_context():
    db.create_all()
    train_model()
    train_model_std()

if __name__ == '__main__':
    app.run(debug=True)
