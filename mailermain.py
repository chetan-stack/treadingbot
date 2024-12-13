import json
import sqlite3
from flask import Flask, request, jsonify, render_template
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


app = Flask(__name__)

# Database setup
connection = sqlite3.connect("ecommerce.db")
print('connection built')

connection.execute('''CREATE TABLE IF NOT EXISTS ECOMMERCEDATA(
            id INTEGER PRIMARY KEY,
            alldata TEXT NOT NULL
        )''')

def insert_into_table(data):
    connection = sqlite3.connect("ecommerce.db")
    print('connection built')

    query = 'INSERT INTO ECOMMERCEDATA(alldata) VALUES(?);'
    connection.execute(query, (data,))
    connection.commit()

def delete_item(delete_id):
    connection = sqlite3.connect("ecommerce.db")
    query = 'DELETE FROM ECOMMERCEDATA WHERE id = ?;'
    connection.execute(query, (delete_id,))
    connection.commit()

def update_data(update, update_id):
    connection = sqlite3.connect("ecommerce.db")
    query = 'UPDATE ECOMMERCEDATA SET alldata= ? WHERE id = ?;'
    connection.execute(query, (update, update_id))
    connection.commit()

def get_all_data():
    connection = sqlite3.connect("ecommerce.db")
    query = 'SELECT * FROM ECOMMERCEDATA;'
    cursor = connection.execute(query)
    data = [{'id': row[0], 'alldata': row[1]} for row in cursor.fetchall()]
    return data

def get_data(id):
    connection = sqlite3.connect("ecommerce.db")
    query = 'SELECT * FROM ECOMMERCEDATA WHERE id = ?;'

    # Pass id as a tuple (id,)
    cursor = connection.execute(query, (id,))

    data = [{'id': row[0], 'alldata': row[1]} for row in cursor.fetchall()]

    # Close the connection
    connection.close()

    return data

def send_email(subject, body, to_email):
    # Set up the SMTP server
    smtp_server = 'smtp.example.com'  # Update this with your SMTP server address
    smtp_port = 587  # Update this with your SMTP server port number
    smtp_username = 'your_username'  # Update this with your SMTP username
    smtp_password = 'your_password'  # Update this with your SMTP password

    # Create a message container
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the email body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS for security
        server.login(smtp_username, smtp_password)  # Log in to the SMTP server

        # Send the email
        server.sendmail(smtp_username, to_email, msg.as_string())

        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email:", str(e))
    finally:
        # Close the SMTP server connection
        server.quit()


# Routes for CRUD operations

@app.route('/')
def getch():
    return 'home'

@app.route('/getdata', methods=['POST'])
def fetch_all_data():
    data = get_all_data()
    return jsonify(data), 200

@app.route('/getparticulardata', methods=['POST'])
def fetch_data():
    req = request.get_json()
    data = get_data(req['id'])
    return jsonify(data)

@app.route('/create-user', methods=['POST'])
def create_data():
    data = request.get_json()
    json_string = json.dumps(data)
    insert_into_table(json_string)
    return jsonify(data), 201

@app.route('/deletedata', methods=['POST'])
def delete_data():
    data = request.get_json()
    delete_item(data['id'])
    return jsonify({'message': 'Data deleted successfully'})

@app.route('/updatedata', methods=['POST'])
def update_data_endpoint():
    data = request.get_json()
    json_string = json.dumps(data)
    update_data(json_string, data['id'])
    return jsonify({'message': 'Data updated successfully'})

@app.route('/uploadfolderfile', methods=['GET'])
def getuploadedfiles():
    uploads_folder_path = 'ecommerce/uploads'
    data = get_image_names(uploads_folder_path)

    # Replace 'uploads' with the actual path to your uploads folder
    uploads_folder_path = 'uploads'
    image_names = get_image_names(uploads_folder_path)

    return image_names

@app.route('/send-mail', methods=['POST'])
def send_mail():
    data = request.get_json()
    json_string = json.dumps(data)
    # insert_into_table(json_string)

    # Send email notification
    subject = "New User Created"
    body = f"New user created with data: {json_string}"
    to_email = "business@grasberg.ca"
    send_email(subject, body, to_email)

    return jsonify(data), 201


@app.route('/uploadfile', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    # Handle the file as needed, for example, save it to a specific directory
    file.save('uploads/' + file.filename)

    return 'File uploaded successfully'


def get_image_names(directory_path):
    image_names = []

    # Check if the directory exists
    if os.path.exists(directory_path):
        # Get a list of all files in the directory
        files = os.listdir(directory_path)

        # Filter out only the image files (you can customize the extensions)
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
        image_names = [file for file in files if any(file.lower().endswith(ext) for ext in image_extensions)]

    return image_names




if __name__ == '__main__':
    app.run(debug=True)
