#test_poll.py
from flask import Flask, redirect, url_for, render_template, request, jsonify
import json
app = Flask(__name__)


timer_counter = 1
j = {'poll_status':'UNKNOWN', 'timer_counter':timer_counter}
@app.route("/", methods = ['GET','POST'])
def index():
    global timer_counter, j
    timer_counter = 1
    j = {'poll_status':'UNKNOWN', 'timer_counter':timer_counter}
    if request.method == "POST":
        print('Got POST')
        return render_template("poll_test.html") 
    return render_template("poll_test.html")
 
@app.route("/poll", methods = ['GET','POST'])
def poll():
    global timer_counter, j
    timer_counter += 1
    print('POLLING REQUEST')
    j['timer_counter'] = timer_counter
    if timer_counter < 5:
        j['poll_status'] ='RUNNING'
    else:
        j['poll_status'] = 'DONE'
        j['results'] = 'metaview: uid=blah \nconsumer: uid=boo'
    return jsonify(j)

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5001,debug=True)
