from flask import Flask, render_template
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

app = Flask(__name__)


# 地図に現在地を表示するページ
@app.route("/")
def index():
    google_maps_api = os.getenv("GOOGLE_MAPS_API")
    return render_template("index.html", google_maps_api=google_maps_api)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
