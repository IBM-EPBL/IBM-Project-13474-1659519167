from flask import Flask, render_template, request,redirect,session, url_for
from flask_mail import Mail, Message
import pickle
import cv2
from skimage import feature
import os.path
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import mysql.connector
import os
from flask_mysqldb import MySQL

model = pickle.loads(open('parkinson.pkl', "rb").read())

if(model):
    print("load success")

app = Flask(__name__)
app.secret_key=os.urandom(24)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'test'


mail_settings = {
    "MAIL_SERVER": 'smtp.gmail.com',
    "MAIL_PORT": 465,
    "MAIL_USE_TLS": False,
    "MAIL_USE_SSL": True,
    "MAIL_USERNAME": 'parkdisease.pred@gmail.com',
    "MAIL_PASSWORD": 'stgeyjhvokuwcyzi'
}

app.config.update(mail_settings)
mysql = MySQL(app)
mail = Mail(app)

s = URLSafeTimedSerializer('Thisisasecret!')

@app.route('/')
def login():
    return render_template('login.html')

@app.route('/register/')
def about():
    return render_template('register.html')

@app.route('/home')
def home():
    if 'email' in session:
        return render_template('home.html')
    else:
        return redirect('/')

@app.route('/login_validation',methods=['POST'])
def login_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    if mysql:
        print("Connection Successful!")
        cursor = mysql.connection.cursor()
        cursor.execute(
            """SELECT * FROM `user_details` where `email` LIKE '{}' and `password` LIKE '{}'""".format(email, password))
        users = cursor.fetchall()
        cursor.close()
    else:
        print("Connection Failed!")

    if len(users)>0:
        session['email'] = users[0][1]
        return redirect('/home')
    else:
        return redirect('/')
    return "Vetri Nitchayam"

@app.route('/adduser',methods=['POST'])
def add_user():
    username=request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    occupation = request.form.get('occupation')
    phone = request.form.get('phone')
    if mysql:
        cursor = mysql.connection.cursor()
        cursor.execute(
            """INSERT INTO `user_details` (`username`,`email`,`phone`,`occupation`,`password`) VALUES ('{}','{}','{}','{}','{}')""".format(username,email,phone,occupation,password))

        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Confirm Email', sender='db0096299ef646', recipients=[email])

        link = url_for('confirm_email', token=token, _external=True)

        msg.body = 'Your link is {}'.format(link)
        print(email)
        mail.send(msg)

        mysql.connection.commit()
        cursor.close()
    else:
        print("Connection Failed!")
    return "User Registered Successfully. Kindly Confirm the Mail sent to the provided Mail ID"

@app.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return '<h1>The token is expired!</h1>'
    return '<h1>Account Verified!</h1>'


@app.route('/predict/')
def predict():
    return render_template('predictor.html')

@app.route('/prediction',methods=['POST'])
def prediction():
    print("Inside")
    if request.method == 'POST':
        f = request.files['file']  # requesting the file
        #filename_secure = secure_filename(f.filename)
        basepath = os.path.dirname(
            '__file__')  # storing the file directory
        # storing the file in uploads folder
        filepath = os.path.join(basepath, "uploads", f.filename)
        f.save(filepath)  # saving the file

        # Loading the saved model
        print("[INFO] loading model...")
        '''local_filename = "./uploads/"
        local_filename += filename_secure
        print(local_filename)'''

        # Pre-process the image in the same manner we did earlier
        image = cv2.imread(filepath)
        output = image.copy()

        # Load the input image, convert it to grayscale, and resize
        output = cv2.resize(output, (128, 128))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (200, 200))
        image = cv2.threshold(image, 0, 255,
                              cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]

        # Quantify the image and make predictions based on the extracted features using the last trained Random Forest
        features = feature.hog(image, orientations=9,
                               pixels_per_cell=(10, 10), cells_per_block=(2, 2),
                               transform_sqrt=True, block_norm="L1")
        preds = model.predict([features])
        print(preds)
        ls = ["Healthy", "Parkinsons"]
        result = ls[preds[0]]
        '''color = (0, 255, 0) if result == "healthy" else (0, 0, 255)
        cv2.putText(output, result, (3, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        cv2.imshow("Output", output)
        cv2.waitKey(0)'''
        if(result=="Healthy"):
            return render_template('prediction_results_healthy.html', utc_dt=result)
        else:
            return render_template('prediction_results_park.html', utc_dt=result)
    return None


@app.route('/logout')
def logout():
    session.pop('email')
    return redirect('/')

if __name__=="__main__":
    app.run(debug=True)

