from flask import Flask, render_template, request
import time

print("------------------------")
app = Flask(__name__)

@app.route('/')
def index():
	print('XXXXXXXXXXXXXXXXXX')
	return render_template('login_original.html')

@app.route('/',methods = ['POST', 'GET'])
def login():
	print('YYYYYYYYYYYYYYYYYY')
	if request.method == 'POST':
		print("=====================")
		username = request.form.get("uname", None)
		password = request.form.get("pwd", None)

		print("UserName : " + username)
		print("Password : " + password)
		if username != 'aramnath@mycervello.com' and password != '1234':
			#time.sleep(15)
			return render_template('login_original.html', ErrorText="UserName doesn''t exist or password is wrong")
		else:
			return render_template('test.html')

if __name__ == '__main__':
	print('============ Execution started ===========')
	app.run(debug=True)