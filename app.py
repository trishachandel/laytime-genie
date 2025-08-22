from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import plotly.express as px
import plotly.io as pio
import os
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
       
        file = request.files["file"]
        if file.filename == "":
            return render_template("index.html", error="No file selected")
        
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        return redirect(url_for("analyze", filename=file.filename))

    return render_template("index.html")

@app.route("/analyze/<filename>")
def analyze(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    df = pd.read_csv(filepath)

   
    df["Start"] = pd.to_datetime(df["Start"])
    df["End"] = pd.to_datetime(df["End"])

   
    df["Duration (hrs)"] = (df["End"] - df["Start"]).dt.total_seconds() / 3600

   
    used_time = df[df["Type"].str.lower() == "used"]["Duration (hrs)"].sum()
    excluded_time = df[df["Type"].str.lower() == "excluded"]["Duration (hrs)"].sum()

    
    allowed = 72
    result = None
    extra, saved = 0, 0
    if used_time > allowed:
        extra = used_time - allowed
        result = f"⚠️ Demurrage: Laytime exceeded by {extra:.2f} hours."
    else:
        saved = allowed - used_time
        result = f"✅ Despatch: Laytime saved {saved:.2f} hours."

   
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="End",
        y="Event",
        color="Type",
        title="SOF Event Timeline",
        labels={"Event": "Operation", "Type": "Category"},
    )
    fig.update_yaxes(autorange="reversed")
    chart_html = pio.to_html(fig, full_html=False)

    return render_template(
        "result.html",
        tables=[df.to_html(classes="table table-bordered", index=False)],
        used_time=used_time,
        excluded_time=excluded_time,
        result=result,
        chart_html=chart_html,
    )

if __name__ == "__main__":
    app.run(debug=True)

