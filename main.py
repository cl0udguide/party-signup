import os
import uuid
import redis
import json
from flask import Flask, render_template, request, url_for

# Loggly logging
import logging
import logging.config
import loggly.handlers

logging.config.fileConfig('python.conf')
logger = logging.getLogger('myLogger')

app = Flask(__name__)
my_uuid = str(uuid.uuid1())
BLUE = "#0000FF"
GREEN = "#33CC33"
RED = "#FF0000"

REGKEY = 'emailreg'

COLOR = BLUE


# Get Redis credentials
if 'VCAP_SERVICES' in os.environ:
    services = json.loads(os.getenv('VCAP_SERVICES'))
    redis_env = services['rediscloud'][0]['credentials']
else:
	logger.error('Redis service not defined for the app')
	
r_hostname = services['rediscloud'][0]['credentials']['hostname']
r_port = services['rediscloud'][0]['credentials']['port']
r_password = services['rediscloud'][0]['credentials']['password']


# Connect to redis
try:
    r = redis.StrictRedis(host=r_hostname, port=r_port, password=r_password)
    r.info()
except redis.ConnectionError:
	logger.error('Could not connect to Redis service')
	r = None


@app.route('/')
def main():

	global logger
	global r
	
	logger.info('Opened main registration page')

	counter = r.incr('hits')

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is root page</h1>
	
    <form method="post" action="{}">
		First Name:<input type="text" name="f_firstname"></input><br>
		Last Name:<input type="text" name="f_lastname"></input><br>
		E-mail:<input type="text" name="f_email"></input><br>
		<input type="submit" value="Register"></input>
	</form>
	<br><br>
	Visitors: {}
	</center>

	</body>
	</html>
	""".format(GREEN,url_for('process'),counter)

@app.route('/admin')
def admin():

	global logger
	global r
	
	logger.info('Opened admin page')
	
	email_list = r.smembers(REGKEY)
	registered_n = r.scard(REGKEY)
	registration_html = ''

	#registration_html = email_list
	
	for email in email_list:
		f_firstname = str(r.hget(email, 'first_name'))
		f_lastname = str(r.hget(email, 'last_name'))
		registration_html = registration_html + email + " " + f_firstname + " " + f_lastname + "<br>"
	
	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is admin page</h1><br>
		Registrations number: {}<br><br>
		Registrations:<br>{}
	</center>

	</body>
	</html>
	""".format(BLUE,registered_n,registration_html)

@app.route('/delete')
def delete():

	global logger
	global r
	
	logger.warning('Deleted registration records')

	email_list = r.smembers(REGKEY)
	for email in email_list:
		r.delete(email)
	
	r.delete(REGKEY)

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is cleanup page
	</center>

	</body>
	</html>
	""".format(RED)


@app.route('/process', methods = ['POST'])
def process():

	global logger
	global r
	
	logger.info('Processed registration information')

	f_firstname = request.form['f_firstname']
	f_lastname = request.form['f_lastname']
	f_email = request.form['f_email']
	
	r_status = ""
	registered = r.sadd(REGKEY, f_email)
	
	if (registered == 0):
		r_status = "This e-mail address was already registered. Please contact @SD_Cloudy or @cl0udguide."
	else:
		user = r.hset(f_email, 'email', f_email)
		user = r.hset(f_email, 'first_name', f_firstname)
		user = r.hset(f_email, 'last_name', f_lastname)
		r_status = "Added a new registration"
		logger.info(r_status + " " + f_email)

	return """
	<html>
	<body bgcolor="{}">

	<center>
		<h1><font color="white">This is process page</h1><br>
		First Name: {}<br>
		Family Name: {}<br>
		E-mail: {}<br><br>
		Status: {}
	</center>

	</body>
	</html>
	""".format(BLUE,f_firstname,f_lastname,f_email,r_status)


if __name__ == "__main__":
	app.run(host='0.0.0.0', port=int(os.getenv('VCAP_APP_PORT', '5000')))