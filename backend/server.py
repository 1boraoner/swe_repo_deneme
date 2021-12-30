from flask import Flask, jsonify
from database_connector import fetch_db_data
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route('/get_graph_data', methods=(['GET']))
def publish_data():
    response = fetch_db_data()
    return jsonify(response)


# optional
@app.route('/refresh_database', methods=(['GET']))
def refresh_database():
    pass
    # response = fetch_db_data()
    # return jsonify(response)


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000)
