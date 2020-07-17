from flask import Flask,render_template

app= Flask(__name__)          #Instead of app we can use any name


@app.route('/')                #It will open 127.0.0.1.5000/        O/P=Hello,World
def hello():
    return 'Hello,world'

@app.route('/hrithik')         #It will open 127.0.0.1.5000/hrithik    O/P=Hey Hrithik
def hrithik():
    return 'Hey Hrithik'
app.run(debug=True)                      #Use To Run the application