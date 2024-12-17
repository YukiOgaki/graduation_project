from flask import Flask, render_template
from dotenv import load_dotenv
import os

# .envファイルを読み込む
load_dotenv()

app = Flask(__name__)


# 地図に現在地を表示するページ
@app.route("/")
def index():
    mapbox_access_token = os.getenv("MAPBOX_ACCESS_TOKEN")
    return render_template("index.html", mapbox_access_token=mapbox_access_token)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
