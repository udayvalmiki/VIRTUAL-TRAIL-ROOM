import cv2
from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/myDatabase"  # Adjust the database name as needed
app.secret_key = 'your_secret_key'
CORS(app)

mongo = PyMongo(app)

@app.route('/index')
def index():
    if 'username' in session:
        return render_template('index.html')
    return render_template('index.html')


@app.route('/shirt')
def shirt():
    return render_template('shirt.html')

@app.route('/pant')
def pant():
    return render_template('pant.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = mongo.db.users.find_one({'username': username})
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if mongo.db.users.find_one({'username': username}):
            return 'User already exists'
        hashed_password = generate_password_hash(password)
        mongo.db.users.insert_one({'username': username, 'password': hashed_password})
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        return redirect(url_for('login'))

    shirtno = int(request.form["shirt"])
    pantno = int(request.form["pant"])

    cv2.waitKey(1)
    cap = cv2.VideoCapture(0)
    ih = shirtno
    i = pantno

    imgarr_shirts = ["static/assets/shirt1.png", "static/assets/shirt2.png", "static/assets/shirt51.jpg", "static/assets/floral.png", "static/assets/Red T-shirt.png"]
    imgarr_pants = ["static/assets/pant7.jpg", "static/assets/pant21.png"]

    imgshirt = cv2.imread(imgarr_shirts[ih-1])
    imgpant = cv2.imread(imgarr_pants[i-1])

    while True:
        # Ensure both shirt and pant images are read properly
        if imgshirt is None or imgpant is None:
            print("Error loading image.")
            break

        # Convert shirt to grayscale
        shirtgray = cv2.cvtColor(imgshirt, cv2.COLOR_BGR2GRAY)
        ret, orig_masks = cv2.threshold(shirtgray, 1, 255, cv2.THRESH_BINARY)

        # Ensure mask type is CV_8U
        orig_masks = orig_masks.astype('uint8')
        orig_masks_inv = cv2.bitwise_not(orig_masks)

        origshirtHeight, origshirtWidth = imgshirt.shape[:2]

        # Convert pant to grayscale
        pantgray = cv2.cvtColor(imgpant, cv2.COLOR_BGR2GRAY)
        ret, orig_mask = cv2.threshold(pantgray, 1, 255, cv2.THRESH_BINARY)

        # Ensure mask type is CV_8U
        orig_mask = orig_mask.astype('uint8')
        orig_mask_inv = cv2.bitwise_not(orig_mask)

        origpantHeight, origpantWidth = imgpant.shape[:2]

        ret, img = cap.read()
        if ret:
            # Resize logic for pant and shirt and placing them on the image
            # Your logic for resizing and bitwise operations remains here

            # Example resizing shirt and pant images (ensure they are resized correctly)
            pant = cv2.resize(imgpant, (100, 200), interpolation=cv2.INTER_AREA)  # Adjust dimensions
            mask = cv2.resize(orig_mask, (100, 200), interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(orig_mask_inv, (100, 200), interpolation=cv2.INTER_AREA)

            # The region of interest where you'll place the pant
            roi = img[100:300, 200:400]  # Adjust coordinates

            # Apply bitwise operations
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
            roi_fg = cv2.bitwise_and(pant, pant, mask=mask)

            # Combine background and foreground
            dst = cv2.add(roi_bg, roi_fg)
            img[100:300, 200:400] = dst  # Place the combined image back

            # Display result
            cv2.imshow("img", img)

        if cv2.waitKey(100) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
