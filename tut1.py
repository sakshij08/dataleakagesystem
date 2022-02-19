import os,socket,smtplib
from flask_mail import Mail, Message
import random,string, ipapi
import sys
from datetime import datetime
from flask import (Flask, Response, flash, redirect, render_template, request,
                   send_file, send_from_directory, session, url_for,jsonify)
from flask_mysqldb import MySQL

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm.session import Session, sessionmaker
from werkzeug.utils import secure_filename

from config import *
# from flask_login import logout_user
app = Flask(__name__)

mail = Mail(app)

app.config['MAIL_SERVER']= 'smtp.gmail.com'
app.config['MAIL_PORT']= 465
app.config['MAIL_USERNAME']='distributor1data@gmail.com'
app.config['MAIL_PASSWORD']='Distributor@1'
app.config['MAIL_USE_SSL']=True
app.config['MAIL_USE_TLS']=False

mail = Mail(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{user}:{password}@{server}/{database}'.format(user='root', password='', server='localhost', database='dataleak')
# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
# )

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'dataleak'
app.secret_key = app_key

#-----UPLOADED FILES' DIRECTORY-----------------
if not os.path.isdir(upload_dest):
    os.mkdir(upload_dest)
app.config['MAX_CONTENT_LENGTH'] = file_mb_max * 1024 * 1024
app.config["IMAGE_UPLOADS"] = "/beproj/static/uploads"

IMAGE_UPLOADS = "/beproj/static/uploads/"

#----------------------MODELS-------------------------------------------------------------

db = SQLAlchemy(app)
mysql= MySQL(app)

class Uploaded_files(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(80),nullable=False)
    keyz = db.Column(db.Text(80),nullable=False)
    # data = db.Column(db.Text,unique=True,nullable=False)

class Request_status(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(80),unique=True)
    file_no = db.Column(db.Integer, nullable=False)
    file_name= db.Column(db.String(30), nullable=False)
    status=db.Column(db.String(30), nullable=False)

class Warnings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(80),unique=True)
    email = db.Column(db.String(80))
    subject= db.Column(db.String(50), nullable=False)
    body=db.Column(db.String(200), nullable=False)
    warn_date = db.Column(db.String(12), nullable=True)

class Agent_register(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.String(80),unique=True, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password= db.Column(db.String(30), nullable=False)
    agent_name = db.Column(db.String(30), nullable=False)
    reg_date = db.Column(db.String(12), nullable=True)
   
class Distributor_register(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    distributor_id = db.Column(db.String(80),unique=True, nullable=False)
    phone_no = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(30), nullable=False)
    password= db.Column(db.String(30), nullable=False)
    distributor_name = db.Column(db.String(30), nullable=False)
    reg_date = db.Column(db.String(12), nullable=True)

class Request(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    distributor_id = db.Column(db.String(80),unique=True, nullable=False)
    file_no = db.Column(db.String(30), nullable=False)
    file_name= db.Column(db.String(30), nullable=False)    

class DbAbsLayer(object):
    def createSession(self):
        Session = sessionmaker()
        self.session = Session.configure(bind=self.engine)

class Contactus(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30),unique=True)
    email = db.Column(db.String(30), nullable=False)
    phone_no= db.Column(db.String(10), nullable=True)
    message=db.Column(db.String(100), nullable=False)

class Guilty(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    agent_id=db.Column(db.String(80), nullable=False)
    reason=db.Column(db.String(100), nullable=False)
    guilt_date = db.Column(db.String(12), nullable=True)
    status = db.Column(db.String(30))

    
class Messages(db.Model):
    srno = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(30),unique=True)
    message=db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable = False)
    replies=db.Column(db.String(100), nullable=False)  

class Allowedip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(40),unique=True)
           

# ---------------------INDEX, REGISTER, LOGIN, ADMIN-----------------------------
# @app.route("/")
# def landing():
#     return render_template('index.html')

@app.route("/",  methods = ['GET', 'POST'])
def landing():
    if(request.method=='POST'):

        if request.form['submit'] == 'submit_contact':
            '''Fetch data and add it to the database'''
            name = request.form.get('name')
            email = request.form.get('email')
            phone_no = request.form.get('phone')
            message = request.form.get('message')
            entry = Contactus(name= name, email = email, phone_no= phone_no, message=message )
            db.session.add(entry)
            db.session.commit()    
    return render_template('index.html')

@app.route("/register",  methods = ['GET', 'POST'])
def register():
    if(request.method=='POST'):

        if request.form['submit'] == 'submit_agent':
            '''Fetch data and add it to the database'''
            agent_id = request.form.get('id')
            email = request.form.get('email')
            password = request.form.get('password')
            rpassword = request.form.get('rpassword')
            agent_name= request.form.get('namea')
            phone_no= request.form.get('p_no') 
            a_id= Agent_register.query.filter_by(agent_id=agent_id).first()
            e_mail= Agent_register.query.filter_by(email=email).first()
            sl=len(phone_no)
            if a_id == None and e_mail==None:
                if sl!=10:
                    flash('Invalid Phone No.')
                    return render_template('register.html')
                else:
                    if password == rpassword:
                        entry = Agent_register(agent_id= agent_id, phone_no= phone_no, email = email, password= password, agent_name= agent_name, reg_date= datetime.now() )
                        db.session.add(entry)
                        db.session.commit()
                        flash('Registered Successfully!!')
                        return render_template('register.html')
                    else:
                        flash('Passwords do not Match')
                        return render_template('register.html')
                    
            else:
                flash('Already Registered with the AgentID/Email')
                return render_template('register.html')


        if request.form['submit']=='submit_distributor':
            distributor_id = request.form.get('id')
            email = request.form.get('email')
            password = request.form.get('password')
            rpassword = request.form.get('rpassword')
            distributor_name= request.form.get('named')
            d_id= Distributor_register.query.filter_by(distributor_id=distributor_id).first()
            e_mail= Distributor_register.query.filter_by(email=email).first()
            if d_id == None and e_mail==None:
                if password == rpassword:
                    entry = Distributor_register(distributor_id= distributor_id,email = email, password= password, distributor_name= distributor_name, reg_date= datetime.now() )
                    db.session.add(entry)
                    db.session.commit()
                    flash('Registered Successfully!!')
                    return render_template('register.html')
                else:
                    return flash('Passwords do not Match')
            else:
                return flash('Already Registered with the AgenID/Email')

    return render_template('register.html')




@app.route("/login",  methods = ['GET', 'POST'])
def login():
    if(request.method=='POST'):
        if request.form['submit']=='submit_agent_login':
            agent_id = request.form.get('id')
            password = request.form.get('password')
            x_details= Agent_register.query.filter_by(agent_id=agent_id).first()
            if x_details==None:
                 flash('Agent ID does not exist')
                 return render_template('login.html')
            else:    
                c_id=x_details.agent_id
                c_pass=x_details.password
                c_name=x_details.agent_name
                c_email=x_details.email
                c_pno=x_details.phone_no
                if c_id == agent_id and c_pass==password:
                    uname=c_name
                    session["user"]=uname
                    session["agent_id"]=c_id
                    session["email"]=c_email
                    session["phone_no"]=c_pno
                    search = request.form.get('search')
                    data = ipapi.location(ip=search, output='json')
                    session["ip2"]=data['ip']

                    return redirect('/home_a')
                else:
                    flash('Incorrect Password')
                    return render_template('login.html')

        if request.form['submit']=='submit_dist_login':
            distributor_id = request.form.get('id')
            password = request.form.get('password')
            x_details= Distributor_register.query.filter_by(distributor_id=distributor_id).first()
            if x_details==None:
                flash('ID does not exist')
                return render_template('login.html')
            else:    
                c_id=x_details.distributor_id
                c_pass=x_details.password
                c_name=x_details.distributor_name
                c_email=x_details.email
                c_pno=x_details.phone_no
                if c_id == distributor_id and c_pass==password:
                    # uname=c_name
                    # session["user"]=uname
                    # session["agent_id"]=c_id
                    # session["email"]=c_email
                    # session["phone_no"]=c_pno

                    return redirect('/home_d')
                else:
                    flash('Incorrect Password')
                    return render_template('login.html')
    return render_template('login.html')


@app.route("/login")
def login2():
    return render_template('login.html')


@app.route("/admin")
def admin():
    return render_template('admin.html')

@app.route("/get_my_ip", methods = ["GET","POST"])
def get_my_ip():
    search = request.form.get('search')
    data = ipapi.location(ip=search, output='json')
    ip2=data['ip']
    # ipaddr= data.ip
    # for key, value in data.items():
    #    flash(key, value)
    hostname = socket.gethostname()   
    IPAddr = socket.gethostbyname(hostname)   
 
    
    return render_template('get_my_ip.html', data=data, ip2=ip2, hostname=hostname, IPAddr=IPAddr)
    # return jsonify({'ip':request.remote_addr}),200

# other imports as necessary

@app.route("/logout")
def logout():
    return redirect(url_for('login'))


# ------------------DISTRIBUTOR----------------------------------------------
@app.route("/view_outflow")
def view_outflow():






    return render_template('view_outflow.html')


@app.route("/home_d")
def home_distributor():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(status) AS notif FROM guilty WHERE status='Unresolved'")
    data = cur.fetchone()

    
    cur.close()
    return render_template('home_dist.html', notif=data)


@app.route("/message_a", methods=["POST","GET"])
def messaging_sec():
    agent_id=session["agent_id"]
    if request.method == "POST":

        if request.form['submit'] == 'submit_mess':

            agent_id=session["agent_id"]

            message = request.form.get('mess')
        #  = request.form.get('fname')
            entry = Messages(sender=agent_id, message= message, date=datetime.now(), replies='' )
            db.session.add(entry)
            db.session.commit()

    cur = mysql.connection.cursor()
    cur.execute("SELECT message,date,replies FROM messages WHERE sender=%s",(agent_id,))
    data = cur.fetchall()
    cur.close()
    return render_template('mess.html',messages=data)



# @app.route("/data_out")
# def data_out():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM guilty ")
#     data = cur.fetchall()
#     cur.close()
#     return render_template('data_outflow.html',guilty=data)  

@app.route("/data_out")
def data_out():
 
    cur = mysql.connection.cursor()
    # cur.execute("SELECT * FROM guilty where status='Unresolved' ")
    cur.execute("SELECT guilty.srno, guilty.agent_id, agent_register.email, guilty.reason, guilty.guilt_date FROM guilty INNER JOIN agent_register ON guilty.agent_id=agent_register.agent_id WHERE status = 'Unresolved'")
    data = cur.fetchall()
    # cur.execute("SELECT * FROM agent_register status='Unresolved' ")
    cur.close()
    return render_template('data_outflow.html',guilty=data)  

@app.route("/history")
def history():
 
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM guilty where status='Resolved' ")
    data = cur.fetchall()
    cur.close()
    return render_template('history.html',guilty=data)

@app.route("/message_d", methods=["POST","GET"])
def messaging_secd():
    if request.method == "POST":

        if request.form['submit'] == 'submit_mess':

            agent_id=session["agent_id"]

            reply = request.form.get('reply')
            sno= request.form.get('sno')
            cur = mysql.connection.cursor()
            cur.execute("UPDATE messages SET replies=%s WHERE srno= %s",(reply,sno,) )
            mysql.connection.commit()
        

    cur = mysql.connection.cursor()
    cur.execute("SELECT srno,sender, message,date,replies FROM messages WHERE replies='' ")
    data = cur.fetchall()
    cur.close()
    return render_template('mess_reply.html', messages = data)




# @app.route("/mess", methods=["POST", "GET"])
# def message():
#     if request.method == "POST":

#         agent_id=session["agent_id"]

#         message = request.form.get('mess')
#         #  = request.form.get('fname')
#         entry = Messages(sender=agent_id, message= message, date=datetime.now(), replies='' )
#         db.session.add(entry)
#         db.session.commit()



    # return render_template('mess.html')  

    



#     return render_template('messaging_section.html')

# MANAGE FILES, UPLOAD, DELETE , DOWNLOAD----------------------- 

@app.route("/manage-files")
def manage():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM uploaded_files")
    data = cur.fetchall()
    cur.close()
    return render_template('manage_files.html', uploaded_files = data)





@app.route("/upload-files", methods=["GET", "POST"])
def upload_image():

    if request.method == "POST":

        if request.files:
            size=6
            chars=string.ascii_uppercase + string.digits
            keys= ''.join(random.choice(chars) for _ in range(size))
            image = request.files["image"]
            filename = secure_filename(image.filename)
            new_file = Uploaded_files(name=filename,keyz=keys)#, data = image.read())
            db.session.add(new_file)
            db.session.commit()

            image.save(os.path.join(app.config["IMAGE_UPLOADS"], secure_filename(image.filename)))

            print(image)

            return redirect(request.url)

            


    return render_template("upload_files.html")


@app.route('/delete/<string:id_data>', methods = ['GET'])
def delete(id_data):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM uploaded_files WHERE id=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('manage'))

@app.route('/remove/<email>', methods = ['GET'])
def remove(email):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM agent_register WHERE email=%s", (email,))
    mysql.connection.commit()
    return redirect(url_for('data_out'))



# @app.route('/uploads/<name>')
# def download_file(name):
#     return send_from_directory(app.config["IMAGE_UPLOADS"], name)
@app.route('/warn/<email>', methods = ['GET'])
def warn(email):
   
    email= email
    subject="Warning"

    msg= "Through your account, data leak possibilities have been detected, so we would like to warn you regarding the same. We hope such activities don't reoccur from your side in future."
        
    message = Message(subject, sender="distributor1data@gmail.com", recipients=[email])
    message.body= msg

    mail.send(message)
    warn_date=datetime.now()


    cur = mysql.connection.cursor()
    cur.execute("INSERT into warnings(email,subject,body,warn_date) VALUES (%s,%s,%s,%s)",(email,subject,msg,warn_date,))
    
    # # cur.execute("UP request_status SET status='Approved' WHERE srno= %s",(srno,) )
    # mysql.connection.commit()

    cur = mysql.connection.cursor()
    cur.execute("UPDATE guilty SET status='Resolved' WHERE agent_id=(SELECT agent_id FROM agent_register where email=%s)",(email,))
    # cur.execute("UP request_status SET status='Approved' WHERE srno= %s",(srno,) )
    mysql.connection.commit()

    
        
    return render_template('data_outflow.html')


    
@app.route('/decline/<srno>', methods = ['GET'])
def decline(srno):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE request_status SET status='Declined' WHERE srno= %s",(srno,) )
    mysql.connection.commit()
    return redirect(url_for('data_requests'))





@app.route('/view_outflow/<agent_id>', methods = ['GET'])
def view_out(agent_id):
    cur = mysql.connection.cursor()
    cursor=mysql.connection.cursor()
    # cur.execute("SELECT * FROM guilty where status='Unresolved' ")
    cur.execute("SELECT agent_name, email, phone_no from agent_register where agent_id=%s",(agent_id,))
    cursor.execute("SELECT guilty.srno, guilty.agent_id, agent_register.email, guilty.reason, guilty.guilt_date, guilty.status FROM guilty INNER JOIN agent_register ON guilty.agent_id=agent_register.agent_id  where guilty.agent_id=%s",(agent_id,))
    data = cur.fetchall()
    guilty = cursor.fetchall()
    return render_template('view_outflow.html',data=data,guilty=guilty)





@app.route('/send_key/<srno>', methods = ['GET'])
def send_key(srno):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE request_status SET status='Approved' WHERE srno= %s",(srno,) )
    # cur.execute("UP request_status SET status='Approved' WHERE srno= %s",(srno,) )
    cur.execute("update request_status r inner join uploaded_files u on r.file_no = u.id set r.keyz = u.keyz where r.status='Approved'")
    mysql.connection.commit()
    return redirect(url_for('data_requests'))

@app.route("/getfile/<filename>", methods = ['GET'])
def download_file(filename):
    return render_template('download.html',value=filename)

@app.route('/return-files/<filename>')
def return_files_tut(filename):
    file_path = IMAGE_UPLOADS + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')


@app.route('/returnf/<filename>')
def return_it(filename):
    file_path = IMAGE_UPLOADS + filename
    return send_file(file_path, as_attachment=True, attachment_filename='')

@app.route('/resolve/<srno>')
def resolve(srno):
    cur = mysql.connection.cursor()
    cur.execute("UPDATE guilty SET status='Resolved' WHERE srno= %s",(srno,) )
    # cur.execute("UP request_status SET status='Approved' WHERE srno= %s",(srno,) )
    mysql.connection.commit()
    return redirect(url_for('data_out'))

@app.route("/queries")
def queries():
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM contactus")
    data=cur.fetchall()
    cur.close()
    return render_template('queries.html',contactus=data)     

#CHECK DATA REQUESTS SENT BY AGENTS---------------------------

@app.route("/data_req")
def data_requests():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM request_status where status='pending'")
    data = cur.fetchall()
    cur.close()
    return render_template('data_req.html',request=data)  


# -----------------------AGENT ------------------------------------------------------

#AGENT HOME

@app.route("/home_a")
def home_agent():
    if "user" in session:
        username =session["user"]
        agent_id=session["agent_id"]
        email=session["email"]
        d_a="AGENT"
        phone=session["phone_no"]
        return render_template('home_agent.html',username = username,a_id=agent_id,d_a=d_a,email=email,phone=phone)
    else:
        return render_template('login.html')


#TO REQUEST FILES FROM DISTRIBUTOR


#TO CHECK THE REQUEST STATUS

@app.route("/request_status")
def request_status():
    agent_id=session["agent_id"]
    cur=mysql.connection.cursor()
    cur.execute("SELECT * FROM request_status WHERE agent_id=%s",(agent_id,))
    data=cur.fetchall()
    cur.close()
    return render_template('request_status.html',request=data) 


@app.route('/delete_req/<string:id_data>', methods = ['GET'])
def delete_req(id_data):
    flash("Record Has Been Deleted Successfully")
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM request_status WHERE srno=%s", (id_data,))
    mysql.connection.commit()
    return redirect(url_for('request_status'))


@app.route("/request_file", methods=["POST", "GET"])

def request_file():
    cur=mysql.connection.cursor()
    cur.execute("SELECT id,name FROM uploaded_files")
    data=cur.fetchall()
    cur.close()
    

    if request.method == "POST":

        agent_id=session["agent_id"]
        file_no = request.form.get('fid')
        filename = request.form.get('fname')
        entry = Request_status(agent_id=agent_id, file_no= file_no, file_name=filename )
        db.session.add(entry)
        db.session.commit()



    return render_template('request_file.html',uploaded_files=data)




@app.route('/request_data/<string:id_data>', methods = ['GET'])
def request_data(id_data):
    # flash("Record Has Been Deleted Successfully")
    
    f_no=id_data
    agent_id=session["agent_id"]
    x_details= Request_status.query.filter_by(agent_id=agent_id, file_no = f_no ).first()
    if(x_details==None):
        cur = mysql.connection.cursor()
        
        cur.execute("INSERT INTO request_status(file_no, file_name) SELECT id,name FROM uploaded_files WHERE id=%s", (id_data,))
    # mysql.connection.commit()
        cur.execute("UPDATE request_status SET agent_id=%s WHERE agent_id=''",(agent_id,))
        # mysql.connection.commit()
        cur.execute("UPDATE request_status SET status='pending' WHERE status=''")
        mysql.connection.commit()
    return redirect(url_for('request_file'))


@app.route("/view_file")
def view_file(): 
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,name FROM uploaded_files")
    data=cur.fetchall()
    cur.close()
    return render_template('view_file.html',data=data)

@app.route("/notification")
def notification(): 
    cur = mysql.connection.cursor()
    email=session["email"]
    cur.execute("SELECT * FROM warnings WHERE email=%s",(email,))
    data=cur.fetchall()
    cur.close()
    return render_template('notification.html',data=data)




@app.route("/view/<fileid>", methods = ['GET','POST'])
def view(fileid):
    f_id = fileid
    session["f_id"]=f_id
    

    return render_template('authenticate.html',data=f_id)


    
    # return redirect(url_for('authenticate'))

@app.route("/authenticate", methods = ['GET','POST'] )
def authenticate():
    if(request.method=='POST'):
        f_id = request.form.get('fi_id')  
        f_key = request.form.get('password')
        agent_id=session["agent_id"]
        x_details=Uploaded_files.query.filter_by(id=f_id).first()
        # cur = mysql.connection.cursor()
        # cur.execute("SELECT * FROM uploaded_files WHERE id=%s AND keyz=%s",(f_id,f_key))

        if x_details==None:
            return render_template('authenticate.html',)
        else:
            # search = request.form.get('search')
            # data = ipapi.location(ip=search, output='json')
            # session["ip2"]=data['ip']
            ip_add=session["ip2"]
            c_key=x_details.keyz
            f_name=x_details.name
            if (c_key==f_key):
                cur = mysql.connection.cursor()
                data2=cur.execute("SELECT * FROM allowedip WHERE ip=%s",(ip_add,))
                data2=cur.fetchone()
                cur.execute("SELECT * FROM request_status WHERE agent_id=%s AND file_no=%s AND status='Approved'",(agent_id,f_id,))
                data=cur.fetchone()
                
                if (data==None and data2==None):
                    entry = Guilty(agent_id= agent_id, reason="Unauthorized access with Correct Key and external ip: "+ip_add, guilt_date= datetime.now(), status="Unresolved" )
                    db.session.add(entry)
                    db.session.commit()
                    return render_template('download2.html')

                if (data==None):
                    entry = Guilty(agent_id= agent_id, reason="Unauthorized access with Correct Key", guilt_date= datetime.now(), status="Unresolved" )
                    db.session.add(entry)
                    db.session.commit()
                    return render_template('download2.html')

                elif (data2==None):
                    entry = Guilty(agent_id= agent_id, reason="Accessed through external IP: "+ ip_add, guilt_date= datetime.now(), status="Unresolved" )
                    db.session.add(entry)
                    db.session.commit()
                    return render_template('download2.html')

                else:
                    return render_template('download.html', value=f_name)

            else:
                flash("Wrong Key")
                return render_template('authenticate.html',f_id=f_key)

    return render_template('authenticate.html',f_id=c_key)


@app.route("/download2")
def download2(): 
    return render_template('download2.html')


@app.route("/email")
def email(): 
    return render_template('email.html')


@app.route("/send_message", methods=['GET','POST'])
def send_message():
    if request.method == "POST":
        email= "sakshirajendrajadhav@gmail.com"
        subject="Warning"
        msg= "Warning Regarding the Data Leak Detected"
        
        message = Message(subject, sender='distributor1data@gmail.com', recipients=['sakshirajendrajadhav@gmail.com'])
        message.body= msg

        mail.send(message)

        success="Email Sent"
        
        return render_template("test1.html",success= success)


app.run(debug=True,port=8000)


# @app.route("/authenticate", methods = ['GET','POST'] )
# def authenticate():
#     if(request.method=='POST'):
#         f_id = request.form['fid']

#         agent_id=session["agent_id"]
#         f_id=session["f_id"]
#     #     f_key = request.form.get('auth_key')

#     #     x_details= Uploaded_files.query.filter_by(id=f_id).first()
#     #     # if x_details==None:
#     #     #     return render_template('authenticate.html')
#     #     # else:
#     #     c_key=x_details.keyz
#     #     if (c_key==f_key):
#     #         cur = mysql.connection.cursor()
#     #         cur.execute("SELECT * FROM request_status WHERE agent_id=%s AND file_no=%s AND status='Approved'",(agent_id,f_id,))
#     #         data=cur.fetchall()

#     #         if (data==None):
#     #             cur.execute("INSERT INTO Guilty(agent_id,reason) VALUES %s,'Unauthorized access with correct Key'", (agent_id,))
#     #         else:
#     #             return render_template('download.html')
                
                

#     # else:
#     #     flash("Wrong Key")

#     # return render_template('authenticate.html')








            