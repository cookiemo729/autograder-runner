from flask import Flask, jsonify, request

app = Flask(__name__)


@app.get("/")
def home():
    return "AutoGrade API"


@app.post("/api/grade")
def grade():

    data = request.get_json()

    print("=" * 50)
    print("Received grading request")
    print(data)
    print("=" * 50)

    return jsonify({
        "status": "received",
        "score": 20,
        "max_score": 20
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8000
    )