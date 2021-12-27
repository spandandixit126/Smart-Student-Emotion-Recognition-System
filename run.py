from flask import Flask, render_template, request, url_for, redirect, send_file

import json_extractor
import render_video
import call_model
import os
import glob
import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

app = Flask(__name__, static_url_path='/static')  # Initialze flask constructor

# Add your own details
config = {
    "apiKey": "AIzaSyBu9ogguma605JbRcTLXb4ZumnJJ8Q30r0",
    "authDomain": "flask-ecc80.firebaseapp.com",
    "databaseURL": "https://flask-ecc80-default-rtdb.firebaseio.com",
    "projectId": "flask-ecc80",
    "storageBucket": "flask-ecc80.appspot.com",
    "messagingSenderId": "1063288258217",
    "appId": "1:1063288258217:web:fd2ffc850e1e2a908f33b8",
    "measurementId": "G-LJ48MPQ8Z6"
}

vid, vid_dir = "", ""
toggle = 0
# global variables
labels = []
happy_values_line, sad_values_line, angry_values_line, neutral_values_line = [], [], [], []
happy_values_radar, sad_values_radar, angry_values_radar, neutral_values_radar = [], [], [], []
happy, sad, angry, neutral = [], [], [], []


@app.route('/main', methods=['POST', 'GET'])
def main():
    return render_template('main.html')


@app.route('/faculties', methods=['POST', 'GET'])
def faculties():
    return render_template('faculties.html')


@app.route('/chat_room', methods=['POST', 'GET'])
def chat_room():
    return render_template('chat_room.html')


@app.route('/calendar', methods=['POST', 'GET'])
def calendar():
    return render_template('calendar.html')


@app.route('/settings', methods=['POST', 'GET'])
def settings():
    return render_template('settings.html')


@app.route('/HelpCenter', methods=['POST', 'GET'])
def HelpCenter():
    with open('static/SSERS_DOCX.pdf', 'rb') as static_file:
        # return send_file(static_file, attachment_filename='SSERS_DOCX.pdf')
        return render_template('HelpCenter.html',
                               static_file=send_file(static_file, attachment_filename='SSERS_DOCX.pdf'))


@app.route('/main_2', methods=['POST', 'GET'])
def main_2():
    global labels
    global happy_values_line, sad_values_line, angry_values_line, neutral_values_line
    global happy_values_radar, sad_values_radar, angry_values_radar, neutral_values_radar
    global happy, sad, angry, neutral
    if request.method == 'POST':
        # get path to current working directory
        owd = os.getcwd()
        vid_li = []

        # get video from .html
        vid = request.form['vid']
        print("Video name:->", vid)

        # converting video to frames
        vid_dir = render_video.video_to_frames(video_path=vid, frames_dir='video_frames', overwrite=True,
                                               every=100, chunk_size=100)
        print("\nvideo frames created for video : " + vid_dir)  # getting path with \ system
        # reassign the same value to vid_dir according to windows path system having / in use
        vid_dir = "video_frames/" + vid
        os.chdir(vid_dir)
        for file in glob.glob("*.jpg"):
            print("getting file...", file)
            vid_li.append(str(file))
        os.chdir(owd)
        print("files founded:", vid_li)
        index = []
        happy = []
        sad = []
        angry = []
        neutral = []
        for i in range(len(vid_li)):
            pred = call_model.main(vid_li[i], vid_dir)
            index.append(str(i))
            happy.append(pred[0][0])  # (math.trunc(pred[0][0] * 100))
            sad.append(pred[0][1])  # (math.trunc(pred[0][1] * 100))
            angry.append(pred[0][2])  # (math.trunc(pred[0][2] * 100))
            neutral.append(pred[0][3])  # (math.trunc(pred[0][3] * 100))
        labels = [row for row in index]

        # data for line chart
        happy_values_line = [row for row in happy]
        sad_values_line = [row for row in sad]
        angry_values_line = [row for row in angry]
        neutral_values_line = [row for row in neutral]

        # data for radar chart
        happy_values_radar = [row * 100 for row in happy]
        sad_values_radar = [row * 100 for row in sad]
        angry_values_radar = [row * 100 for row in angry]
        neutral_values_radar = [row * 100 for row in neutral]

        # data for doughnut chart
        happy, sad, angry, neutral = sum(happy_values_radar) / 100, sum(sad_values_radar) / 100, sum(
            angry_values_radar) / 100, sum(neutral_values_radar) / 100
        global toggle
        toggle = 1
        data = {"Happy": happy, "Sad": sad, "neutral": neutral, "angry": angry}
        result = request.form
        dep = result['dep']
        c = result['class']
        subject = result['subject']
        teacher = result['teacher']
        date = result['date']

        print(dep, c, subject, teacher, date)
        db.child('data').child(dep).child(c).child(subject).child(teacher).child(date).set(data)

        return render_template('result.html', vid=vid, vid_dir=vid_dir, labels=labels,
                               happy_values_line=happy_values_line, sad_values_line=sad_values_line,
                               angry_values_line=angry_values_line, neutral_values_line=neutral_values_line,
                               happy_values_radar=happy_values_radar, sad_values_radar=sad_values_radar,
                               angry_values_radar=angry_values_radar, neutral_values_radar=neutral_values_radar,
                               happy=happy, sad=sad,
                               angry=angry, neutral=neutral)


@app.route('/Dashboard', methods=['POST', 'GET'])
def Dashboard():
    global labels, toggle
    global happy_values_line, sad_values_line, angry_values_line, neutral_values_line
    global happy_values_radar, sad_values_radar, angry_values_radar, neutral_values_radar
    global happy, sad, angry, neutral
    return render_template('Dashboard.html', toggle=toggle, labels=labels, happy_values_line=happy_values_line,
                           sad_values_line=sad_values_line,
                           angry_values_line=angry_values_line, neutral_values_line=neutral_values_line,
                           happy_values_radar=happy_values_radar, sad_values_radar=sad_values_radar,
                           angry_values_radar=angry_values_radar, neutral_values_radar=neutral_values_radar,
                           happy=happy, sad=sad,
                           angry=angry, neutral=neutral)


# if __name__ == '__main__':
# app.run()


##############################################################################


# initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}
admin_detail = {"is_logged_in": False, "name": "", "email": ""}


# admin_login
@app.route("/admin", methods=['POST'])
def admin():
    return render_template('admin_login.html')


# Login
@app.route("/")
def login():
    return render_template("login.html")


# Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html")
    # after that it will redirected to register route


# Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", email=person["email"], name=person["name"])
    else:
        return redirect(url_for('login'))


# if someone clicks on admin and login.
@app.route("/admin_dashboard", methods=["POST", "GET"])
def admin_dashboard():
    if request.method == "POST":
        result = request.form
        # name = result['name']
        a_email = result['admin-email']
        # print(a_email)
        a_password = result['admin-password']
        person = db.child('users').child('admin').get()
        for person in person.each():
            print(person.val())
            print(person.val())
            if person.val() == a_email:
                print("Welcome virpal")

                global admin_detail
                admin_detail['email'] = a_email
                admin_detail['is_logged_in'] = True

                try:
                    # Try signing in the user with the given information
                    user = auth.sign_in_with_email_and_password(a_email, a_password)
                    # Insert the user data in the global person

                    return render_template('admin_dashboard.html')
                except:
                    # If there is any error, redirect back to login
                    # flash("please try agin ",error)
                    return render_template("admin_login.html")

                # ##############
                # flash("welcome back  ",info)
                # return render_template('admin_dashboard.html')
            else:
                # flash("your email password not same to admins")
                return "Sorry you are not admin! try using different credential if you think this was a mistake."
    else:
        # flash("your email password not same to admins")
        return redirect(url_for("admin_login.html"))


# If someone clicks on login, they are redirected to /result
@app.route("/result", methods=["POST", "GET"])
def result():
    if request.method == "POST":  # Only if data has been posted
        result = request.form  # Get the data
        email = result["email"]
        password = result["pass"]
        try:
            # Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            # Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            # Get the name of the user
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            # Redirect to welcome page
            return redirect(url_for('welcome'))
        except:
            # If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))


# If someone clicks on register, they are redirected to /register
@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":  # Only listen to POST
        result = request.form  # Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            # Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            # Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            # Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            # Append data to the firebase realtime database
            data = {"name": name, "email": email, "role": "student"}
            db.child("users").child(person["uid"]).set(data)
            # Go to welcome page
            return redirect(url_for('welcome'))
        except:
            # If there is any error, redirect to register
            return redirect(url_for('register'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))


# add data from

@app.route("/add", methods=["POST", "GET"])
def add():
    return render_template("data_add.html")


@app.route("/add_data", methods=["POST", "GET"])
def add_data():
    if request.method == "POST":  # Only listen to POST
        global vid, vid_dir
        vid = request.form['vid']
        print("Video name:->", vid)
        vid_dir = render_video.video_to_frames(video_path=vid, frames_dir='video_frames', overwrite=True,
                                               every=100, chunk_size=100)
        print("\nvideo frames created for video : " + vid_dir)
        data = json_extractor.main(vid)
        print("below file ")
        print(type(data))
        print(data['emotions'])
        happy = 0.00000
        sad = 0.00000
        angry = 0.00000
        neutral = 0.0000

        for i in data['emotions']:
            h = float(i['happy'])
            happy = happy + h
            s = float(i['sad'])
            sad = sad + s
            a = float(i['angry'])
            angry = angry + a
            n = float(i['neutral'])
            neutral = neutral + n
            # print(type(i['happy']))
            # print(type(i))
        # return render_template('main_2.html', vid=vid)
        print(happy)
        print(sad)
        print(angry)
        print(neutral)
        # return redirect(url_for('result_s'))
        data = {"Happy": happy, "Sad": sad, "neutral": neutral, "angry": angry}
        result = request.form
        dep = result['dep']
        c = result['class']
        subject = result['subject']
        teacher = result['teacher']
        date = result['date']

        print(dep, c, subject, teacher, date)
        db.child('data').child(dep).child(c).child(subject).child(teacher).child(date).set(data)
        return redirect(url_for('welcome'))
    return redirect(url_for('welcome'))


# find data
@app.route("/find", methods=["POST", "GET"])
def find():
    return render_template("find_data.html")


# store data in to database
@app.route("/find_data", methods=["POST", "GET"])
def find_data():
    if request.method == "POST":  # Only listen to POST
        result = request.form
        dep = result['dep']
        c = result['class']
        subject = result['subject']
        teacher = result['teacher']
        date = result['date']

        print(dep, c, subject, teacher, date)
        data_from_fire_base = db.child('data').child(dep).child(c).child(subject).child(teacher).child(date).get()

        # vir = data_from_fire_base.val()
        '''for  value in vir.val():
            print( value)'''
        vir = []
        try:
            for key in data_from_fire_base.each():
                vir.append(key.val())
        except:
            vir.append(['NaN', 'NaN', 'NaN', 'NaN'])
        return render_template('find_result.html', vir=vir)
    else:
        return redirect(url_for('welcome'))

    ## add or delete user


@app.route("/add_user", methods=["POST", "GET"])
def add_user():
    val_user = {"ce": "ce"}
    d_d = db.child("Department").set(val_user)
    print(d_d)
    return render_template("data_add.html", val=val_user)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('page-404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    return render_template('page-403.html'), 403


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('page-500.html'), 500


if __name__ == "__main__":
    app.run(debug=True)
