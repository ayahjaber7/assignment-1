from flask import Flask, request, redirect, render_template
from google.cloud import storage
import os

app = Flask(__name__)
storage_client = storage.Client()
BUCKET_NAME = "assignment1-image-store"

@app.route("/")
def index():
    """Show upload form and list of uploaded files"""
    files = get_list_of_files(BUCKET_NAME)
    return render_template("index.html", files=files)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["form_file"]
    if file:
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file)
        return redirect("/")
    return "No file uploaded", 400

def get_list_of_files(bucket_name):
    """List all files in the bucket"""
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [blob.name for blob in blobs]

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
