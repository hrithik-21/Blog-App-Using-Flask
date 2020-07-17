from flask import Flask,render_template
a=Flask(__name__)
@a.route('/')
def hello():
    name1="Hrithik"
    return render_template('index.html',name=name1)   #It will return index.html which must be located in templates folder
a.run(debug=True)