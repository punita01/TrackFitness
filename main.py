from flask import Flask, request, render_template
from google.cloud import datastore

app = Flask(__name__)


def store_userdetails(user_data):
    datastore_client = datastore.Client()
    user_key = datastore_client.key('user', '1001')
    user = datastore.Entity(key=user_key)
    user['name'] = user_data['name']
    user['weight'] = user_data['weight']

    datastore_client.put(user)

    result = datastore_client.get(user_key)
    print(result)



@app.route('/userdata', methods=['get', 'post'])
def get_userdata():

    message = ''
    if request.method == 'POST':
        user_data = {}
        username = request.form.get('username')  # access the data inside
        weight = request.form.get('weight')

        if username is not '' and weight is not '':
            message = "User is registered!!"
            user_data['name'] = username
            user_data['weight'] = weight
            store_userdetails(user_data)

        else:
            message = "Details required!!"

    return render_template('userdata.html', message=message)


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)

