import os
import uuid
import redis
import json
from flask import Flask, render_template, request, url_for

app = Flask(__name__)
my_uuid = str(uuid.uuid1())
BLUE = "#0000FF"
GREEN = "#33CC33"
RED = "#FF0000"

COLOR = BLUE

@app.route('/')
def main():

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is root page</h1>
	
    <form method="post" action="{}">
		<input type="text" name="email"></input>
		<input type="submit" value="Signup"></input>
	</form>
	</center>

	</body>
	</html>
	""".format(GREEN,url_for('process'))

@app.route('/admin')
def admin():

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is admin page
	</center>

	</body>
	</html>
	""".format(BLUE)

@app.route('/process', methods = ['POST'])
def process():
    email = request.form['email']

#    print("The email address is '" + email + "'")
#    return redirect('/')

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is process page</h1><br/>
		The e-mail address is {}
	</center>

	</body>
	</html>
	""".format(RED,email)

if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(os.getenv('VCAP_APP_PORT', '5000')))