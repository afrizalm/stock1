from flask import Flask, render_template
from stock_utils import get_lq45_kontan, get_stock_metrics
import pandas as pd
import time

app = Flask(__name__)

@app.route("/")
def index():
    df_listed = get_lq45_kontan()
    tickers = df_listed['Ticker'].tolist()

    data = []
    for tk in tickers:
        result = get_stock_metrics(tk)
        data.append(result)
        time.sleep(1)  # throttle to avoid rate-limiting

    df = pd.DataFrame(data)
    return render_template("index.html", tables=[df.to_html(classes='table table-striped', index=False)], titles=df.columns.values)

if __name__ == "__main__":
    app.run(debug=True)
