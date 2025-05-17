from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

LOGIN_URL = 'https://november2024version01.dicewebfreelancers.com/index.php/login'
LOGIN_POST_URL = 'https://november2024version01.dicewebfreelancers.com/index.php/login?task=user.login'

# Preloaded credentials
PRELOADED_CREDENTIALS = {
    "username": "",
    "password": ""
}

@app.route('/joomla-login', methods=['POST'])
def joomla_login():
    # Use preloaded credentials instead of getting from request
    username = PRELOADED_CREDENTIALS['username']
    password = PRELOADED_CREDENTIALS['password']
    return_url = 'aHR0cHM6Ly9ub3ZlbWJlcjIwMjR2ZXJzaW9uMDEuZGljZXdlYmZyZWVsYW5jZXJzLmNvbS9pbmRleC5waHAvcG9zdC1mcmVlLWFkL3VzZXIvYWRk'

    session = requests.Session()

    # Step 1: Get CSRF token
    get_response = session.get(LOGIN_URL)
    soup = BeautifulSoup(get_response.text, 'html.parser')
    token_input = soup.find('input', {'type': 'hidden', 'value': '1'})

    if not token_input:
        return jsonify({'error': 'CSRF token not found'}), 400

    csrf_token_name = token_input.get('name')

    # Step 2: Send login POST request
    payload = {
        'username': username,
        'password': password,
        'return': return_url,
        csrf_token_name: '1'
    }

    post_response = session.post(LOGIN_POST_URL, data=payload)

    if 'logout' in post_response.text.lower():
        return jsonify({'status': 'success', 'message': 'Logged in successfully'})
    else:
        return jsonify({'status': 'failure', 'message': 'Login failed or token invalid'})

if __name__ == '__main__':
    app.run(debug=True)