from flask import Flask, render_template,request
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
from datetime import date,timedelta
import random
import time

def cm():
    return round(time.time() * 1000)

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///Covid.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	rString = db.Column(db.String(20),nullable=False)
	name = db.Column(db.String(200),nullable=False)
	dateCreated = db.Column(db.DateTime,default=datetime.utcnow)
	location = db.Column(db.String(200),nullable=False)
	phone = db.Column(db.String(11),nullable=False)
	email = db.Column(db.String(100),nullable=False)
	password = db.Column(db.String(100),nullable=False)
	vacdate = db.Column(db.String(700))
	vachosp = db.Column(db.String(700))
	beddate = db.Column(db.String(700))
	bedhosp = db.Column(db.String(700))

	def __repr__(self):
		return '<Name %r>' % self.id 

class mmonth(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	HospID = db.Column(db.Integer,nullable=False)
	dates = db.Column(db.String(200),nullable=False)
	vLeft = db.Column(db.Integer,nullable=False)
	def __repr__(self):
		return '<Name %r>' % self.id 

class bbed(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	HospID = db.Column(db.Integer,nullable=False)
	bLeft = db.Column(db.Integer,nullable=False)
	def __repr__(self):
		return '<Name %r>' % self.id

NumberOfHospitals = 10
TotalVaccine = 2
TotalBed = 2
Days = 30


def update():
	global TotalVaccine
	global TotalBed
	global Days
	global NumberOfHospitals
	
	_bed = bbed.query.all()
	if not _bed:
		for i in range(NumberOfHospitals):
			stdt = bbed(HospID = i, bLeft = TotalBed)
			db.session.add(stdt)
			db.session.commit()

	_mon = mmonth.query.filter(mmonth.dates == str(date.today())).all()
	if _mon:
		for i in range(1,Days):
			nday  = date.today()-timedelta(days=i)
			_mon2 = mmonth.query.filter(mmonth.dates == str(nday)).all()
			for j in _mon2:
				db.session.delete(j)
				db.session.commit()
	else:
		mm=mmonth.query.all()
		for i in mm:
			db.session.delete(i)
			db.session.commit()

	for i in range(0,Days):
		nday  = date.today()+timedelta(days=i)
		_mon2 = mmonth.query.filter(mmonth.dates == str(nday)).all()
		if not _mon2:
			for j in range(NumberOfHospitals):
				stdt=mmonth(dates=nday,HospID=j,vLeft=TotalVaccine)
				db.session.add(stdt)
				db.session.commit()
			
# home
@app.route('/')
def page_0():
	update()
	ii = cm()%8
	return render_template("home.html",ii=ii)


#about
@app.route('/about')
def about():
	return render_template("about.html")

# signup
@app.route('/signup',methods=["POST"])
def signup():
	FirstName = request.form.get("fs_name")
	LastName = request.form.get("sc_name")
	Address = request.form.get("address")
	Phone = request.form.get("phone")
	Email = request.form.get("email_name")
	Password1 = request.form.get("password1")
	Password2 = request.form.get("password2")


	if not FirstName or not LastName or not Phone or not Address or not  Email or not Password1 or not Password2:
		error_1="All fields need to be filled"
		return render_template("login2.html",Password1=Password1,Password2=Password2,error_1=error_1,FirstName=FirstName,LastName=LastName,Email=Email,Phone=Phone,Address=Address)

	if Password1 != Password2:
		error_1="Password is not matching"
		return render_template("login2.html",Password1=Password1,Password2=Password2,error_1=error_1,FirstName=FirstName,LastName=LastName,Email=Email,Phone=Phone,Address=Address)

	flag = User.query.filter_by(email = Email).first()
	if flag:
		error_1="This email is already registered"
		return render_template("login2.html",Password1=Password1,Password2=Password2,error_1=error_1,FirstName=FirstName,LastName=LastName,Email=Email,Phone=Phone,Address=Address)
	new_name = FirstName+" "+LastName
	stdt=User(name=new_name,location=Address,rString="",phone=Phone,email=Email,password=Password1)
   
	stdt.rString = ""
	for i in range(20):
		stdt.rString += chr(ord('a')+random.randint(0,25))
	try:
		db.session.add(stdt)
		db.session.commit()
	except:
		return "error 404"

	return render_template("thanks.html")


# sign in
@app.route('/login',methods=["POST","GET"])
def login():
	if request.method == "POST":
		Email = request.form.get("email_name")
		Password = request.form.get("password")	

		if not Email or not Password:
			error_1="All fields need to be filled"
			return render_template("login2.html",error_1=error_1,Password=Password,Email=Email)

		flag = User.query.filter_by(email = Email).first()
		if not flag:
			error_1="Email doesn't exist"
			return render_template("login2.html",error_1=error_1,Password=Password,Email=Email)
		if flag.password != Password:
			error_1="Password doesn't match"
			return render_template("login2.html",error_1=error_1,Password=Password,Email=Email)
		s = "2/"+flag.rString
		return render_template("inter.html",sender = s)
	else:
		return render_template("login2.html")


#Landing page after sign in
@app.route('/2/<rs>')
def page_2(rs):
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	ii = cm()%8
	names = flag.name
	datess=(str(flag.dateCreated))[0:10]
	return render_template("page2.html",rs=rs,ii=ii,names=names,datess=datess)

#Vaccine start
@app.route('/vaccine/<rs>',methods=["GET","POST"])
def vaccine(rs):
	global Month
	global Days
	global NumberOfHospitals
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")

	ii = cm()%8
	return render_template("vaccine.html",NumberOfHospitals=NumberOfHospitals,rs=rs,ii=ii)



@app.route('/cal/<int:id>/<rs>',methods=['POST','GET'])
def calender(id,rs):
	global Month
	global Days
	global NumberOfHospitals
	mont = mmonth.query.filter(mmonth.HospID==id).all()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	update()
	return render_template("calender.html",mont=mont,Days=Days,NumberOfHospitals=NumberOfHospitals,id=id,rs=rs)



@app.route('/confirm/<int:id1>/<id2>/<rs>')
def confimation(id1,id2,rs):
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	return render_template("confirm.html",id1=id1,id2=id2,rs=rs)


@app.route('/vacFinal/<int:id1>/<id2>/<rs>')
def vacFinal(id1,id2,rs):
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	mess1 = "Your vaccine slot has been booked"
	mont = mmonth.query.filter(mmonth.HospID==id1).all()
	for i in mont:
		if i.dates == id2:
			if i.vLeft == 0:
				mess1="Abnormal number of requests"
				return render_template("Done.html",mess1=mess1,rs=rs)
			else:
				i.vLeft -=1

				db.session.commit()
	if not flag.vacdate:
		flag.vacdate=str(id2+'#')
		db.session.commit()
		flag.vachosp=str(str(id1)+'#')
		db.session.commit()
	else:
		flag.vacdate+=(id2+str('#'))
		db.session.commit()
		flag.vachosp+=str(str(id1)+'#')
		db.session.commit()
	

	return render_template("Done.html",mess1=mess1,rs=rs)


@app.route('/myVacOrder/<rs>')
def my_vac_order(rs):
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	a1=[]
	a2=[]
	a3=[]
	a4=[]
	i=0 
	j=0
	s1=""
	s2=""
	if not flag.vacdate:
		return render_template("my_vac_order.html",futureDate=a1,futureId=a2,pastDate=a3,pastId=a4,rs=rs)

	while i<len(flag.vacdate):
		if flag.vacdate[i]=='#':
			while flag.vachosp[j]!='#':
				s2+=flag.vachosp[j]
				j+=1
			j+=1
			ss = date.today()
			if s1 < str(ss):
				a3.append(s1)
				a4.append(s2)
			else:
				a1.append(s1)
				a2.append(s2)
			s1=""
			s2=""
		else:
			s1+=flag.vacdate[i]
		i+=1
	
	return render_template("my_vac_order.html",futureDate=a1,futureId=a2,pastDate=a3,pastId=a4,rs=rs)

@app.route('/cancel/<id1>/<id2>/<rs>')
def cancel(id1,id2,rs):
	return render_template("cancel.html",id1=id1,id2=id2,rs=rs)

@app.route('/vacCancel/<id1>/<id2>/<rs>')
def vacCancel(id1,id2,rs):
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	i = 0
	j = 0
	s1=""
	s2=""
	while i<len(flag.vacdate):
		temp = ""
		while flag.vacdate[i] != str('#'):
			temp+=flag.vacdate[i]
			i+=1
		i+=1
		temp2=""
		while flag.vachosp[j] != str('#'):
			temp2+=flag.vachosp[j]
			j+=1
		j+=1
		if temp == id1 and temp2 == id2:
			while i< len(flag.vacdate):
				s1+=flag.vacdate[i]
				i+=1
			while j< len(flag.vachosp):
				s2+=flag.vachosp[j]
				j+=1
			flag2 = mmonth.query.filter(mmonth.dates==id1).all()
			for z in flag2:
				if str(z.HospID) == id2:
					z.vLeft+=1
					db.session.commit()
					break
				
			flag.vacdate = s1
			db.session.commit()
			flag.vachosp = s2
			db.session.commit()
		else:
			s1+=temp+str('#')
			s2+=temp2+str('#')
	ii = cm()%8
	names = flag.name
	datess=(str(flag.dateCreated))[0:10]
	return render_template("page2.html",vacdate=flag.vacdate,vachosp=flag.vachosp,rs=rs,ii=ii,names=names,datess=datess)
#Vaccine end

#Bed starts
@app.route('/bedbook/<rs>')
def bedbook(rs):
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	global NumberOfHospitals
	global TotalBed
	beds = bbed.query.all()
	return render_template("bedbook.html",NumberOfHospitals = NumberOfHospitals,TotalBed = TotalBed,beds = beds,rs=rs)

@app.route('/confirm2/<int:id>/<rs>')
def confirm2(id,rs):
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	return render_template("confirm2.html", id=id,rs=rs)

@app.route('/bedfinal/<int:id>/<rs>')
def bedfinal(id,rs):
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")

	mess1 = "Your bed has been booked"

	id2=date.today()
	if not flag.beddate:
		flag.beddate=str(str(id2)+'#')
		db.session.commit()
		flag.bedhosp=str(str(id)+'#')
		db.session.commit()
	else:
		flag.beddate+=str(str(id2)+'#')
		db.session.commit()
		flag.bedhosp+=str(str(id)+'#')
		db.session.commit()
	bed = bbed.query.filter_by(HospID=id).first()
	bed.bLeft-=1
	db.session.commit()
	return render_template("Done.html", mess1=mess1,rs=rs)



@app.route('/myBedOrder/<rs>')
def my_bed_order(rs):
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	a1=[]
	a2=[]
	a3=[]
	a4=[]
	i=0 
	j=0
	s1=""
	s2=""
	if not flag.beddate:
		return render_template("my_bed_order.html",futureDate=a1,futureId=a2,pastDate=a3,pastId=a4,rs=rs)
	while i<len(flag.beddate):
		if flag.beddate[i]=='#':
			while flag.bedhosp[j]!='#':
				s2+=flag.bedhosp[j]
				j+=1
			j+=1
			ss = date.today()
			if s1 < str(ss):
				a3.append(s1)
				a4.append(s2)
			else:
				a1.append(s1)
				a2.append(s2)
			s1=""
			s2=""
		else:
			s1+=flag.beddate[i]
		i+=1
	
	return render_template("my_bed_order.html",futureDate=a1,futureId=a2,pastDate=a3,pastId=a4,rs=rs)

@app.route('/cancel2/<id1>/<id2>/<rs>')
def cancel2(id1,id2,rs):
	return render_template("cancel2.html",id1=id1,id2=id2,rs=rs)

@app.route('/bedCancel/<id1>/<id2>/<rs>')
def bedCancel(id1,id2,rs):
	update()
	flag = User.query.filter_by(rString = rs).first()
	if not flag:
		return render_template("inter.html",sender = "login")
	i = 0
	j = 0
	s1=""
	s2=""
	while i<len(flag.beddate):
		temp = ""
		while flag.beddate[i] != str('#'):
			temp+=flag.beddate[i]
			i+=1
		i+=1
		temp2=""
		while flag.bedhosp[j] != str('#'):
			temp2+=flag.bedhosp[j]
			j+=1
		j+=1
		if temp == id1 and temp2 == id2:
			while i< len(flag.beddate):
				s1+=flag.beddate[i]
				i+=1
			while j< len(flag.bedhosp):
				s2+=flag.bedhosp[j]
				j+=1
			flag2 = bbed.query.filter_by(HospID=int(id2)).first()
			flag2.bLeft+=1
			db.session.commit()
			flag.beddate = s1
			db.session.commit()
			flag.bedhosp = s2
			db.session.commit()
		else:
			s1+=temp+str('#')
			s2+=temp2+str('#')
	ii = cm()%8
	names = flag.name
	datess=(str(flag.dateCreated))[0:10]
	return render_template("page2.html",beddate=flag.beddate,bedhosp=flag.bedhosp,rs=rs,ii=ii,names=names,datess=datess)
#Bed ends