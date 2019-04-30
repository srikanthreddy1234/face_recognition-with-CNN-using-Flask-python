import pyttsx3
import urllib
import pymongo as mg
import os
import shutil as shu
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes


def employee_entry(name,uid,email):
    emp_id=uid
    emp_name=name
    Email_id=email
    db=db_connect()
    emp = db.employee_temp
    emp_count=emp.find({"emp_id":emp_id}).count()
    if emp_count ==0:
        employee={"emp_id":emp_id,
                  "name":emp_name,
                  "Email_id":Email_id,
                        }
        result=emp.insert_one(employee)
        if result.acknowledged:
            print("your details entered")
    else:
        print("your details are already in database")
        
    return emp_id,emp_name
    
def dir_create(dirc):
    path="/home/foodni/Research/CNN_project/static/people_photo/temp_train/"+dirc
    # Create target Directory if don't exist
    if not os.path.exists(path):
        os.mkdir(path)
        #engine = pyttsx3.init()
        #engine.say("your directory is created. Iam taking your images.")
        #engine.runAndWait()
        print("Directory " , dirc ,  " Created ")
    else:    
        print("Directory " , dirc ,  " already exists")
        #engine = pyttsx3.init()
        #engine.say("your directory is already created.No need to create again.")
        #engine.runAndWait()
    return path

def db_connect():
    username = urllib.parse.quote_plus('hanmanthreddy')
    password = urllib.parse.quote_plus('hanu@1221')
    mongodb_URL="mongodb://%s:%s@ds115595.mlab.com:15595/facerecognizer"% (username, password)
    client=mg.MongoClient(mongodb_URL,connectTimeoutMS=30000)
    db=client.get_default_database()
    return db

def emailToEmp(Tomail,mssg,subjt):
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    msg['From'] = 'noreply-AI_Attendence@fnibot.com'
    msg['To'] = Tomail
    msg['Subject'] = subjt
    html = """\
    <html>
    <body>
        <p>  Regards,<br>
    Support<br>
    <img src="http://www.foodni.com/images/logo1.png" width:"20px" height="20px"><br>
    www.foodni.com <br>
        Follow us on:<br>
    <a href='https://www.youtube.com/channel/UCPRZseAHut6e_c4fwCGRYQw'>YouTube</a>,
    <a href='https://twitter.com/FNICorp'>Twitter</a>, 
    <a href='https://www.linkedin.com/in/food-n-i-enterprise-hospitality-as-a-service-platform-b19858142/'>LinkedIn</a>,
    <a href='https://foodni.com/blog/'> Blog</a><br>
    E: support@foodni.com <br>
    GSTIN = 36AAGCC0425Q2ZG<br> </p>
    </body>
    </html>
    """
    message = mssg
    part2 = MIMEText(html, "html")
    msg.attach(MIMEText(message))
    msg.attach(part2)
    
    mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
    mailserver.ehlo()
    mailserver.login('noreply-promotions@fnibot.com', 'Fnic@7916')
    
    mailserver.sendmail('noreply-promotions@fnibot.com',Tomail,msg.as_string())
    
    mailserver.quit()

def emailToAdmin(Tomail,mssg,subjt):
    msg = MIMEMultipart()
    msg.set_unixfrom('author')
    fileToSend = "temp.csv"
    msg['From'] = 'noreply-AI_Attendence@fnibot.com'
    msg['To'] = Tomail
    msg['Subject'] = subjt
    html = """\
    <html>
    <body>
        <p>  Regards,<br>
    Support<br>
    <img src="http://www.foodni.com/images/logo1.png" width:"20px" height="20px"><br>
    www.foodni.com <br>
        Follow us on:<br>
    <a href='https://www.youtube.com/channel/UCPRZseAHut6e_c4fwCGRYQw'>YouTube</a>,
    <a href='https://twitter.com/FNICorp'>Twitter</a>, 
    <a href='https://www.linkedin.com/in/food-n-i-enterprise-hospitality-as-a-service-platform-b19858142/'>LinkedIn</a>,
    <a href='https://foodni.com/blog/'> Blog</a><br>
    E: support@foodni.com <br>
    GSTIN = 36AAGCC0425Q2ZG<br> </p>
    </body>
    </html>
    """
    ctype, encoding = mimetypes.guess_type(fileToSend)
    if ctype is None or encoding is not None:
        ctype = "application/octet-stream"

    maintype, subtype = ctype.split("/", 1)


    if maintype == "text":
        fp = open(fileToSend)
        # Note: we should handle calculating the charset
        attachment = MIMEText(fp.read(), _subtype=subtype)
        fp.close()
    else:
        fp = open(fileToSend, "rb")
        attachment = MIMEBase(maintype, subtype)
        attachment.set_payload(fp.read())
        fp.close()
        encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
    msg.attach(attachment)
    message = mssg
    part2 = MIMEText(html, "html")
    msg.attach(MIMEText(message))
    msg.attach(part2)
    
    mailserver = smtplib.SMTP_SSL('smtpout.secureserver.net', 465)
    mailserver.ehlo()
    mailserver.login('noreply-promotions@fnibot.com', 'Fnic@7916')
    
    mailserver.sendmail('noreply-promotions@fnibot.com',Tomail,msg.as_string())
    
    mailserver.quit()

def emp_status(emp_id,status):
    db=db_connect()
    emp_t=db.employee_temp
    dir_src="/home/foodni/Research/CNN_project/static/people_photo/temp_train/"
    dir_dst="/home/foodni/Research/CNN_project/static/people_photo/train_img/"
    src_file = os.path.join(dir_src, emp_id)
    dst_file = os.path.join(dir_dst, emp_id)
    if status == 0:
        emp_l=emp_t.delete_one({"emp_id":emp_id})
        if emp_l.acknowledged:
            shu.rmtree(src_file)
            print("your details are deleted")
    else:
        emp_l=emp_t.find_one({"emp_id":emp_id})
        print(emp_l)
        emp=db.employee
        emp_no=emp.find({"emp_id":emp_id}).count()
        print(emp_no)
        if emp_no != 0:
            emp.delete_one({"emp_id":emp_id})
        res=emp.insert_one(emp_l)
        if res.acknowledged:
            if os.path.exists(dst_file):
                shu.rmtree(dst_file)
            shu.move(src_file, dst_file)
            emp_l=emp_t.delete_one({"emp_id":emp_id})
            if emp_l.acknowledged:
                print("your details are moved")
        else:
            print("your details are not moved")