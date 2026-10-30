SMARTQUEUE MANAGEMENT SYSTEM (Python + Flask)

RUN ON WINDOWS:
1. Extract this ZIP file.
2. Open the extracted smartqueue_flask folder in VS Code.
3. Open Terminal > New Terminal.
4. Run these commands one by one:

   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py

5. Open this address in your browser:
   http://127.0.0.1:5000

FEATURES:
- Home page and services page
- User registration and login
- User dashboard
- Generate queue token
- Normal / Senior Citizen priority
- Token history
- Data saved in smartqueue_data.json automatically

The app.py file is the Flask backend. HTML pages are in templates and CSS is in static.
This is an academic demonstration project. Change app.secret_key before any real deployment.
