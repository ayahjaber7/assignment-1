
import os
import json
import google.generativeai as genai
from flask import Flask, request, redirect, render_template
from google.cloud import storage

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API"])

app = Flask(__name__)

# Google Cloud Storage settings
BUCKET_NAME = "assignment1-image-store"
storage_client = storage.Client()

# Upload an image and process with Gemini AI
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["form_file"]
        if file and file.filename.endswith((".jpeg", ".jpg")):
            filename = file.filename
            blob = storage_client.bucket(BUCKET_NAME).blob(filename)
            blob.upload_from_file(file)

            # Generate AI description using Gemini
            response = generate_ai_description(filename)
            
            # Save AI-generated JSON metadata
            json_blob = storage_client.bucket(BUCKET_NAME).blob(filename.replace(".jpg", ".json").replace(".jpeg", ".json"))
            json_blob.upload_from_string(json.dumps(response), content_type="application/json")

            return redirect("/")
    
    # List uploaded images
    blobs = storage_client.list_blobs(BUCKET_NAME)
    files = [blob.name for blob in blobs if blob.name.endswith((".jpeg", ".jpg"))]
    return render_template("index.html", files=files)

# Function to generate AI descriptions using Gemini API
def generate_ai_description(image_filename):
    """ Uses Gemini AI to generate image descriptions """
    image_uri = f"gs://{BUCKET_NAME}/{image_filename}"
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    PROMPT = "Describe the image and generate a title. Format the response as a JSON object with 'title' and 'description'."

    response = model.generate_content([image_uri, "\n\n", PROMPT])
    return json.loads(response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

