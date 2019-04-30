from flask import Flask, redirect, url_for, request, render_template
import os
import dir_creation
import importlib
import employee as em
import datetime
from importlib import reload
import training_system as ts
import sys

PEOPLE_FOLDER = os.path.join('static', 'people_photo')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = PEOPLE_FOLDER

db=em.db_connect()
accept_list=[]
@app.route('/auth/<eid>/<pswd>')
def auth(eid,pswd):
   adm=db.admintable
   emp=adm.find({'Email_id':eid,'pwd':pswd}).count()
   if emp == 1:
      return render_template('HOME.HTML')
   else:
      return render_template('unauthorized.html')

@app.route('/responce/<name>/<uid>/<email>')
def responce(name,uid,email):
    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'fni.png')
    return render_template('responce.html',name = name ,uid = uid , email = email )
#os.kill()

@app.route('/success/<name>/<uid>/<email>') 
def success(name,uid,email): 
   #return "welcome {} your id is {} and mail is {}".format(name,uid,email)
   return redirect(url_for('responce',name = name ,uid = uid , email = email))

@app.route('/emp_register')
def emp_register():
   
   return render_template('emp_Register.html')

#, '{1}', '{2}', '{3}', '{4}', '{5}', '{6}'".format(softname, procversion, int(percent), exe, description, company, procurl
@app.route('/')
@app.route('/admin_login')
def admin_login():
   return render_template('admin.html')

@app.route('/home')
def home():
   return render_template('HOME.HTML')
   
@app.route('/login',methods = ['POST', 'GET']) 
def login(): 
   if request.method == 'POST': 
      uname = request.form['nm'] 
      idd = request.form['idd']
      mail = request.form['email'] 

      dir_creation.dir(uname,idd,mail) 
      return redirect(url_for('success',name = uname, uid = idd , email = mail)) 
   else: 
      uname = request.args.get('nm') 
      return redirect(url_for('success',name = uname)) 


@app.route('/register',methods = ['POST', 'GET']) 
def register():   
      importlib.reload(dir_creation)
      return redirect(url_for('emp_register'))
@app.route('/admin',methods=['POST','GET'])
def admin():
   return redirect(url_for('admin_login'))

@app.route('/admin_auth',methods=['POST','GET'])
def admin_auth():
   if request.method == 'POST': 
      eid = request.form["email"] 
      pswd = request.form["pwd"]
   return redirect(url_for('auth',eid=eid,pswd=pswd))

@app.route('/attendence')
def attendence():
   now = datetime.datetime.now()
   date=str(now.strftime("%Y-%m-%d"))
   attd=db.att_test
   att=attd.find({"date":date},{"_id":False,"month":False,"out_time":False})
   return render_template('admin_home.html',attdn=att)

@app.route('/admin_home_d/<f_date>/<t_date>')
def admin_home_d(f_date,t_date):
   attd=db.att_test
   att=attd.find({"date":{'$gte':f_date,'$lt':t_date}},{"_id":False,"month":False,"out_time":False})
   return render_template('admin_home.html',attdn=att)

@app.route('/admin_home_id/<emp_id>')
def admin_home_id(emp_id):
   attd=db.att_test
   att=attd.find({"emp_id":emp_id},{"_id":False,"month":False,"out_time":False})
   return render_template('admin_home.html',attdn=att)

@app.route('/attendence_d',methods=['POST','GET'])
def attendence_d():
   if request.method == 'POST':
      from_date = request.form["from"] 
      to_date = request.form["to"]
   return redirect(url_for('admin_home_d',f_date=from_date,t_date=to_date))

@app.route('/attendence_id',methods=['POST','GET'])
def attendence_id():
   if request.method == 'POST':
      eid=request.form["text"]
   return redirect(url_for('admin_home_id',emp_id=eid))

@app.route('/tr_success')
def tr_success():
   ts.sys_train()
   return render_template("tr_success.html")

@app.route('/training_sys')
def training_sys():
   return redirect(url_for("tr_success"))

@app.route('/employee')
def employee():
   emp=db.employee
   empl=emp.find({},{"_id":False})
   return render_template("employee.html",empl=empl)

@app.route('/employee_d')
def employee_d():
   return redirect(url_for("employee"))

@app.route('/register_page')
def register_page():
   emp=db.employee_temp
   emp_no=emp.find({}).count()
   empl=emp.find({},{"_id":False})
   return render_template("register_list.html",empl=empl,emp_no=emp_no)

@app.route('/register_list')
def register_list():
   return redirect(url_for("register_page"))

@app.route('/accepted_page')
def accepted_page():
   emp=db.employee
   empl=emp.find({},{"_id":False})
   return render_template("accepted_list.html",empl=empl)

@app.route('/accepted_list')
def accepted_list():
   return redirect(url_for("accepted_page"))


@app.route('/reject/<emp_id>')
def reject(emp_id):
   em.emp_status(emp_id,0)
   return render_template("register_list.html")

@app.route('/emp_reject',methods=['POST','GET'])
def emp_reject():
   if request.method == 'POST':
      emp_id = str(request.form["emp_id"])
   return redirect(url_for("reject",emp_id=emp_id))

@app.route('/accept/<emp_id>')
def accept(emp_id):
   em.emp_status(emp_id,1)
   return render_template("register_list.html")

@app.route('/emp_accept',methods=['POST','GET'])
def emp_accept():
   if request.method == 'POST':
      emp_id = str(request.form["emp_id"])
   return redirect(url_for("accept",emp_id=emp_id))

@app.route('/accept_continue/<emp_id_list>')
def accept_continue(emp_id_list):
   emp_t=db.employee_temp
   emp_list_json=[]
   for emp_id in emp_id_list:
      emp_t.find_one({"emp_id":emp_id})
      emp_list_json.append(emp_t)
   return render_template("TestForTrain.html",acpt_l=emp_list_json)

@app.route('/emp_accept_continue')
def emp_accept_continue():
   return redirect(url_for("accept_continue",emp_id_list=accept_list))

if __name__ == '__main__':
   app.run(debug = True,use_reloader=True, use_debugger=True, use_evalex=True)