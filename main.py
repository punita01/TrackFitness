from flask import Flask, request, render_template, redirect, url_for, flash
from google.cloud import datastore

app = Flask(__name__)
app.secret_key = 'super secret kitty'
datastore_client = datastore.Client()


def add_user(user_data):
    user_key = datastore_client.key('username', str(user_data['user_id']))

    # user_already_exists = datastore_client.get(user_key)
    #
    # if user_already_exists is not None:
    #     return "user_exists"

    user = datastore.Entity(key=user_key)
    user.update({
        'email': user_data['user_id'],
        'password': user_data['password'],
        'weight': user_data['weight'],
        'height': user_data['height'],
        'age': user_data['age'],
        'target': user_data['target']
    })

    datastore_client.put(user)

    print(datastore_client.get(user_key))

    return "user_created"


@app.route('/', methods=['get', 'post'])
def login():

    if request.method == 'POST':
        user_id = request.form.get('email_id')
        password = request.form.get('pass')

        user_key = datastore_client.key('username', str(user_id))
        user = datastore_client.get(user_key)
        print("This is user: {}", user)
        if user is None:
            flash("User not found, please register to get fit!!")
            return redirect(url_for('login'))

        if user['password'] == password:
            flash("Login Successful!!!")
            return redirect(url_for('display_info', name=user_id))

    return render_template('index.html')

@app.route('/formpage', methods=['get', 'post'])
def get_userdata():

    message = ''
    if request.method == 'POST':
        user_data = {}
        user_data['user_id'] = request.form.get('username')
        user_data['password'] = request.form.get('password')
        user_data['weight'] = request.form.get('weight')
        user_data['height'] = request.form.get('height')
        user_data['age'] = request.form.get('age')
        user_data['target'] = request.form.get('target')

        result = add_user(user_data)
        # if result == "user_exists":
        #     flash("User already exists")
        #     return redirect(url_for('login'))

        flash("user created!!")
        # return redirect(url_for('display_info', name= user_data['user_id'],
        #                             weight=user_data['weight'], height=user_data['height'],
        #                             age=user_data['age']))

        return redirect(url_for('display_info', name=user_data['user_id']))

    return render_template('userinfo.html', message=message)

@app.route('/userinfo', methods=['get', 'post'])
def display_info():

    user_key = datastore_client.key('username', str(request.args.get('name')))
    user = datastore_client.get(user_key)
    print("USER data is : {}", user)

    diet = None
    exercise = None
    target = None


    weight = user['weight']
    height = user['height']
    age = user['age']
    target = user['target']

    w = float(weight)
    h = float(height)
    a = int(age)

    #calculate BMI
    bmi = (w * 703) / (h*h)
    bmr = 655 + (4.35 * w) + (4.7 * h) - (4.7 * a)
    bmi_category = ''


# Calculating BMI category
    if bmi < 18.5 :
        bmi_category = 'underweight'
    elif bmi >= 18.5 and bmi <= 24.9:
        bmi_category = 'Normal'
    elif bmi >= 25 and bmi <= 29.9:
        bmi_category = 'Overweight'
    elif bmi >= 30 and bmi <= 34.9:
        bmi_category = 'Obese [class 1]'
    elif bmi >= 35 and bmi <= 39.9:
        bmi_category = 'Obese [class 2]'
    else:
        bmi_category = 'Obese [class 3]'

    print("Target is : {}".format(target))

    if target == "1":
        diet = 200
        exercise = 300
    else:
        diet = 350
        exercise = 650

    if request.method == 'POST':
        intake = int(request.form.get('cal_intake'))
        burnt = int(request.form.get('cal_burnt'))

        total_expected_cal = (bmr - diet) - exercise
        total_user_cal = intake - burnt

        if total_expected_cal >= total_user_cal:
            result = "yes"
        else:
            result = "no"

        return render_template('result.html', result=result)


    return render_template('analysis.html', bmi=int(bmi), bmr=int(bmr), bmi_cat=bmi_category, weight=w, diet=(bmr-diet), exercise=exercise)



if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

