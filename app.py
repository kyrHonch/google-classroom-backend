import json

from flask import Flask, request, jsonify, redirect
import dotenv
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = "super secret key"
CORS(app)

ASSETS_DIR = os.path.dirname(os.path.abspath(__file__))


@app.route('/')
def hello_world():
    response = {"message": "Hello, World!"}
    if session.get("credentials"):
        response["status"] = "authorized"
    else:
        response["status"] = "unauthorized"
    return jsonify(response)


@app.route('/create_classroom', methods=['POST'])
def create_classroom():
    if request.method == 'POST':
        credentials = Credentials.from_authorized_user_info(session["credentials"])
        service = build('classroom', 'v1', credentials=credentials)
        request_data = request.get_json()
        if not request_data:
            request_data["name"] = "test classroom"
        # "name": "Python Class Test",
        # "section": "Section",
        # "description": "Test Classroom",
        # "ownerId": "me",
        course = {
            "name": request_data["name"],
            "section": "Section",
            "description": "Test Classroom",
            "ownerId": "me"
        }
        try:
            course_list = service.courses().list().execute()
        except HttpError as e:
            return jsonify({"message": f"Unable to list classrooms: {e}"})
        exists = False
        course_id = None
        for course_ in course_list["courses"]:
            if course_["name"] == request_data["name"] and course_["state"] == "ACTIVE":
                course_id = course["id"]
                exists = True
                break


        if not exists:
            try:
                course = service.courses().create(body=course).execute()
            except HttpError as e:
                return jsonify({"message": f"Unable to create classroom: {e}"})
            course_id = course["id"]

        if request_data.get("students"):
            for student in request_data["students"]:
                student = {
                    "courseId": course_id,
                    "userId": student,
                    "role": "STUDENT"
                }
                try:
                    response = service.invitations().create(body=student).execute()
                except HttpError as e:
                    print(f"Unable to invite student {student} to classroom: ", e)
        return jsonify({"message": "Classroom created successfully!", "course": course})


dotenv.load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses",
    "https://www.googleapis.com/auth/classroom.rosters"
]
session = {}
flow = Flow.from_client_config(
    {
        "web": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    },
    scopes=SCOPES,
    redirect_uri='https://localhost:5000/oauth2callback'
)


@app.route('/google_authorize', methods=['GET'])
def google_authorize():
    if request.method == 'GET':
        try:
            auth_url, _ = flow.authorization_url(access_type="offline", prompt="consent")
            return jsonify({"status": "success", "auth_url": auth_url})
        except Exception as e:
            return jsonify({"status": "error", "message": f"Unable to authorize: {e}"})


@app.route('/oauth2callback')
def oauth2callback():
    flow.fetch_token(authorization_response=request.url)

    session["credentials"] = {
        "token": flow.credentials.token,
        "refresh_token": flow.credentials.refresh_token,
        "token_uri": flow.credentials.token_uri,
        "client_id": flow.credentials.client_id,
        "client_secret": flow.credentials.client_secret,
        "scopes": flow.credentials.scopes
    }
    print(session["credentials"]["token"])
    return redirect("http://localhost:3000/create-classroom")


if __name__ == "__main__":
    context = ('local.crt', 'local.key')
    app.run(ssl_context=context, debug=True)
