from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
import io

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

app = Flask(__name__, static_folder='/public', static_url_path='')
app.config['DEBUG'] = False

def compress_and_save_image(image, file_path):
    quality = 100
    while True:
        img_buffer = io.BytesIO()
        image.save(img_buffer, format='JPEG', optimize=True, quality=quality)
        if img_buffer.tell() <= MAX_FILE_SIZE:
            break

        quality -= 5
        if quality < 15:
            break

    img_buffer.seek(0)
    with open(file_path, 'wb') as f:
        f.write(img_buffer.getvalue())



@app.route('/')
def index():
    return app.send_static_file('index.html')


# Directory where uploaded files will be stored
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB limit

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)   

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'myImage' not in request.files:
        return jsonify(success=False, message='No file part in the request'), 400
    file = request.files['myImage']
    # If user does not select file, browser also submits an empty part without filename
    if file.filename == '':
        return jsonify(success=False, message='No file selected for uploading'), 400
    if file and allowed_file(file.filename):
        barcode = secure_filename(request.form['textInput'])
        # Save the file with the barcode as the filename and keep the original extension
        filename = f"{barcode}{os.path.splitext(file.filename)[1].lower()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        compress_and_save_image(Image.open(file), file_path)
        
        return jsonify(success=True, message='File uploaded successfully', filename=filename), 200
    else:
        return jsonify(success=False, message='Allowed file types are png, jpg, jpeg, gif'), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

