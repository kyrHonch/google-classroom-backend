import json

from flask import Flask, request, jsonify, redirect
import dotenv
import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError

app = Flask(__name__)
app.secret_key = "super secret key"


@app.route('/create_classroom', methods=['POST'])
def create_classroom():
    if request.method == 'POST':
        credentials = Credentials.from_authorized_user_info(session["credentials"])
        service = build('classroom', 'v1', credentials=credentials)
        request_data = request.get_json()
        if not request_data:
            request_data["name"] = "test classroom"
            request_data["section"] = "test section"
            request_data["description"] = "test description"
        course = {
            "name": request_data["name"],
            "section": request_data["section"],
            "description": request_data["description"],
            "ownerId": "me"
        }
        try:
            course_list = service.courses().list().execute()
        except HttpError as e:
            return jsonify({"message": f"Unable to list classrooms: {e}"})
        exists = False
        course_id = None
        for course in course_list["courses"]:
            if course["name"] == request_data["name"]:
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


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
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
        auth_url, _ = flow.authorization_url()
        return redirect(auth_url)


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
    return jsonify({"message": "Authorization successful!", "token": session["credentials"]["token"]})


if __name__ == "__main__":
    app.run(ssl_context="adhoc", debug=True)
