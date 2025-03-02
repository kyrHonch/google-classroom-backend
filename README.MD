# How to run the backend code

Google Classroom API sucks.
<h2>The <i>Flow</i></h2>

1. Need to go through the OAuth2.0 process to get the credentials file.
2. A redirect uri has to with a ssl certificate or else it will keep throwing errors.
3. Has a separate endpoint for creating a classroom and inviting students.


   <h2>How to run?</h2>
1. Clone the repository.
2. Run the following commands: `python -m venv venv && source venv/bin/activate && pip install -r requirements.txt` <-- initializes virtual
   environment and initializes all the packages required to run this
3. Initialize a .env file with the following variables: `CLIENT_ID`, `CLIENT_SECRET`
4. Run the flask server using `flask run`.
5. Everything else will hook up automatically.
6. Authorization token is saved using in-memory storage.

# Endpoints and Payloads
<b>GET http://localhost:5000/google_authorize</b> <-- Redirects to the Google OAuth2.0 page and authorizes.<br>
<b>POST http://localhost:5000/create_classroom</b> <-- Creates a classroom with the following payload:
```json
{
  "name": "Classroom Name",
  "section": "Section",
  "description": "Description",
  "students": [
    "email1",
    "email2"
  ]
}
```