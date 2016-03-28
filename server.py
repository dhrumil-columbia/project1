import os
import json
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

dburl="postgresql://dp2781:LLSZKD@w4111db.eastus.cloudapp.azure.com/dp2781"
engine=create_engine(dburl)

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route("/")
def index():
    query="select uname from Users;"
    result=g.conn.execute(query)
    arr=[]
##    for r in result:
##        arr.append(r[0])
    print 'index'
    return render_template("index.html")
    
@app.route("/vpost")
def vpost():
    query="select course_name from Courses;"
    result=g.conn.execute(query)
    arr=[]
    for r in result:
        arr.append(r[0])
    return render_template("vpost.html",courses=arr)

@app.route("/vposthandle",methods=['GET','POST'])
def vposthandle():
    user=(request.form['user'])
    password=(request.form['password'])
    print user
    if isUser(user,password):
        print 'yes------------'
        c=(request.form['course'])
        query='select p_id,post_time,content,topic,uname from Creates_Post p,Users u,Courses c where p.uid=u.uid and p.course_id=c.course_id and course_name like \''+c+'\';'
        result=g.conn.execute(query)
        pid=[]
        ptime=[]
        content=[]
        topic=[]
        uname=[]
        for r in result:
            pid.append(r[0])
            ptime.append(r[1])
            content.append(r[2])
            topic.append(r[3])
            uname.append(r[4])
        posts=zip(pid,topic,content,uname,ptime)    
        return render_template("postdisplay.html",posts=posts,coursename=c,check="t")
    return render_template("postdisplay.html",check="f")

@app.route("/singlepost")
def singlepost():
    pid=request.args.get('pid')
    query1='select topic,content,post_time,uname,course_name from Creates_Post p,Users u,Courses c where p.uid=u.uid and p.course_id=c.course_id and p.p_id='+pid+';'
    result1=g.conn.execute(query1)
    for r in result1:
      topic=r[0]
      content=r[1]
      ptime=r[2]
      uname=r[3]
      cname=r[4]
    query2='select c.c_id,c.content,c_time,uname from Comments c,Belongs_To_Post b,Replies_Comments r,Users u where c.c_id=b.c_id and r.c_id=c.c_id and r.uid=u.uid and b.p_id='+pid+';'
    result2=g.conn.execute(query2)
    cid=[]
    ccontent=[]
    ctime=[]
    cuname=[]
    for s in result2:
      cid.append(s[0])
      ccontent.append(s[1])
      ctime.append(s[2])
      cuname.append(s[3])
    comments=zip(cid,ccontent,ctime,cuname)
    return render_template("displaysinglepost.html",comments=comments,topic=topic,content=content,ptime=ptime,uname=uname,cname=cname,pid=pid)
  
@app.route("/makecomment",methods=['GET','POST'])
def makecomment():
  pid=request.args.get('pid')
  cname=request.args.get('cname')
  return render_template('addcomment.html',pid=pid,cname=cname)
  
@app.route("/ccomment",methods=['GET','POST'])
def ccomment():
  pid=request.args.get('pid')
  course_name=request.args.get('cname')
  print course_name
  user=(request.form['user'])
  password=(request.form['password'])
  if isUser(user,password):
    queryu='select uid from Users where login like \''+user+'\';'
    uresult=g.conn.execute(queryu)
    for u in uresult:
      uid=u[0]
    queryc='select course_id from Courses where course_name like \''+course_name+'\';'
    cresult=g.conn.execute(queryc)
    for u in cresult:
      courseid=u[0]
    if isRegistered(uid,courseid) or instructs(uid,courseid):
      query4='select count(c_id) from Comments'
      result4=g.conn.execute(query4)
      for s in result4:
        count=s[0]
      cid=count+1
      i=datetime.now()
      dt=i.strftime('%Y-%m-%d %H:%M:%S')
      content=(request.form['content'])
      query1='Insert into Comments(c_id,c_time,content) values(%s,%s,%s);'
      query2='insert into Replies_Comments(c_id,uid) values(%s,%s)'
      query3='insert into Belongs_To_Post(c_id,p_id) values(%s,%s)'
      args1=(cid,dt,content)
      args2=(cid,uid)
      args3=(cid,pid)
      g.conn.execute(query1,args1)
      g.conn.execute(query2,args2)      
      g.conn.execute(query3,args3)
      query1='select topic,content,post_time,uname,course_name from Creates_Post p,Users u,Courses c where p.uid=u.uid and p.course_id=c.course_id and p.p_id='+pid+';'
      result1=g.conn.execute(query1)
      for r in result1:
        topic=r[0]
        content=r[1]
        ptime=r[2]
        uname=r[3]
        cname=r[4]
      query2='select c.c_id,c.content,c_time,uname from Comments c,Belongs_To_Post b,Replies_Comments r,Users u where c.c_id=b.c_id and r.c_id=c.c_id and r.uid=u.uid and b.p_id='+pid+';'
      result2=g.conn.execute(query2)
      cid=[]
      ccontent=[]
      ctime=[]
      cuname=[]
      for s in result2:
        cid.append(s[0])
        ccontent.append(s[1])
        ctime.append(s[2])
        cuname.append(s[3])
      comments=zip(cid,ccontent,ctime,cuname)
      return render_template("displaypostcomment.html",comments=comments,topic=topic,content=content,ptime=ptime,uname=uname,cname=cname,pid=pid,check="t",check2="t")
    return render_template("displaypostcomment.html",check="t",check2="f")
  return render_template("displaypostcomment.html",check="f")


@app.route("/cpost")
def cpost():
    print 'index'
    query="select course_name from Courses;"
    result=g.conn.execute(query)
    arr=[]
    for r in result:
        arr.append(r[0])
    return render_template("cpost.html",courses=arr)

  
@app.route("/cposthandle",methods=['GET','POST'])
def cposthandle():
    user=(request.form['user'])
    password=(request.form['password'])
    print user
    if isUser(user,password):
        print 'yes------------'
        c=(request.form['course'])
        topic=(request.form['topic'])
        content=(request.form['content'])
        i=datetime.now()
        dt=i.strftime('%Y-%m-%d %H:%M:%S')
        queryc='select count(p_id) from Creates_Post'
        cresult=g.conn.execute(queryc)
        for s in cresult:
          count=s[0]
        pid=count+1
        queryu='select uid from Users where login like \''+user+'\';'
        uresult=g.conn.execute(queryu)
        for u in uresult:
          uid=u[0]
        queryco='select course_id from Courses where course_name like \''+c+'\';'
        coresult=g.conn.execute(queryco)
        for t in coresult:
          cid=t[0]
        args=(pid,uid,dt,content,topic,cid)
        if isRegistered(uid,cid):
          query='insert into Creates_Post(p_id,uid,post_time,content,topic,course_id) values(%s,%s,%s,%s,%s,%s)'
          g.conn.execute(query,args)
          query2='select p_id,post_time,content,topic,uname from Creates_Post p,Users u,Courses c where p.uid=u.uid and p.course_id=c.course_id and course_name like \''+c+'\';'
          result=g.conn.execute(query2)
          pids=[]
          ptimes=[]
          contents=[]
          topics=[]
          unames=[]
          for r in result:
              pids.append(r[0])
              ptimes.append(r[1])
              contents.append(r[2])
              topics.append(r[3])
              unames.append(r[4])
          posts=zip(pids,topics,contents,unames,ptimes)    
          return render_template("cpostdisplay.html",posts=posts,coursename=c,check="t", check2="t")
        else:
          return render_template("cpostdisplay.html",check="t", check2="f")
    return render_template("cpostdisplay.html",check="f")
        

        
@app.route("/vannouncement")
def vannouncement():
    query="select course_name from Courses;"
    result=g.conn.execute(query)
    arr=[]
    for r in result:
        arr.append(r[0])
    return render_template("vannouncement.html",courses=arr)

@app.route("/vannouncementhandle",methods=['GET','POST'])
def vannouncementhandle():
    user=(request.form['user'])
    password=(request.form['password'])
    print user
    if isUser(user,password):
        print 'yes------------'
        c=(request.form['course'])
        query='select ann_id,uname,post_time,content from Makes_Announcements m,Users u,Courses c where m.uid=u.uid and u.uid=c.uid and course_name like \''+c+'\';'
        result=g.conn.execute(query)
        query2='select uname from Courses c,Users u where c.uid=u.uid and c.course_name like \''+c+'\';'
        result2=g.conn.execute(query2)
        for s in result2:
          tname=s[0]
        annid=[]
        atime=[]
        content=[]
        uname=[]
        for r in result:
          annid.append(r[0])
          uname.append(r[1])
          atime.append(r[2])
          content.append(r[3])
        announcements=zip(annid,content,atime)    
        return render_template("announcementdisplay.html",announcements=announcements,coursename=c,uname=tname,check="t")
    return render_template("announcementdisplay.html",check="f")


 
@app.route("/mannouncement")
def mannouncement():
    print 'index'
    print 'index'
    query="select course_name from Courses;"
    result=g.conn.execute(query)
    arr=[]
    for r in result:
        arr.append(r[0])
    return render_template("mannouncement.html",courses=arr)

@app.route("/mannhandle",methods=['GET','POST'])
def mannhandle():
    user=(request.form['user'])
    password=(request.form['password'])
    print user
    if isInstructor(user,password):
        print 'yes------------'
        c=(request.form['course'])
        content=(request.form['content'])
        i=datetime.now()
        dt=i.strftime('%Y-%m-%d %H:%M:%S')
        queryc='select count(ann_id) from Makes_Announcements'
        cresult=g.conn.execute(queryc)
        for s in cresult:
          count=s[0]
        annid=count+1
        queryu='select uid from Users where login like \''+user+'\';'
        uresult=g.conn.execute(queryu)
        for u in uresult:
          uid=u[0]
        queryco='select course_id from Courses where course_name like \''+c+'\';'
        coresult=g.conn.execute(queryco)
        for t in coresult:
          cid=t[0]
        query3='select course_id from Courses c,Users u where u.uid=c.uid and login like \''+user+'\';'
        result3=g.conn.execute(query3)
        check2='f'
        for r in result3:
            if cid==r[0]:
              check2='t'
        args=(annid,uid,dt,content)
        if check2=='t':
          query='insert into Makes_Announcements(ann_id,uid,post_time,content) values(%s,%s,%s,%s)'
          g.conn.execute(query,args)
          query='select ann_id,uname,post_time,content from Makes_Announcements m,Users u,Courses c where m.uid=u.uid and u.uid=c.uid and course_name like \''+c+'\';'
          result=g.conn.execute(query)
          query2='select uname from Courses c,Users u where c.uid=u.uid and c.course_name like \''+c+'\';'
          result2=g.conn.execute(query2)
          for s in result2:
            tname=s[0]
          annids=[]
          atime=[]
          contents=[]
          uname=[]
          for r in result:
            annids.append(r[0])
            uname.append(r[1])
            atime.append(r[2])
            contents.append(r[3])
          announcements=zip(annids,contents,atime)    
          return render_template("manndisplay.html",announcements=announcements,coursename=c,uname=tname,check="t", check2="t")
        else:
          return render_template("manndisplay.html",check="t", check2="f")
    return render_template("manndisplay.html",check="f")

 
@app.route("/vstudents")
def vstudents():
  query="select course_name from Courses;"
  result=g.conn.execute(query)
  arr=[]
  for r in result:
    arr.append(r[0])
  return render_template("vstudent.html",courses=arr)

@app.route("/vstudenthandle",methods=['GET','POST'])
def vstudenthandle():
    user=(request.form['user'])
    password=(request.form['password'])
    print user
    if isInstructor(user,password):
        print 'yes------------'
        c=(request.form['course'])
        query='select course_name,course_id from Courses c,Users u where u.uid=c.uid and login like \''+user+'\';'
        result=g.conn.execute(query)
        check2='f'
        for r in result:
            if c==r[0]:
              check2='t'
              cid=r[1]
        if check2=='t':
          query2='select uname from Students_Enrolled s, Users u where s.uid=u.uid and s.course_id='+str(cid)+';'
          result2=g.conn.execute(query2)
          students=[]
          for s in result2:
            students.append(s[0])
          return render_template("studentsdisplay.html",students=students,coursename=c,check="t", check2=check2)
        return render_template("studentsdisplay.html",check="t", check2=check2)
    return render_template("studentsdisplay.html",check="f")
    


def isStudent(user,password):
    query="select login,password from Users u,Students s where u.uid=s.uid"
    result=g.conn.execute(query)
    for r in result:
        if user==r[0] and password==r[1]:
            return True
    return False
  
def isRegistered(uid,cid):
  query='select course_id from Students_Enrolled where uid='+str(uid)+';'
  result1=g.conn.execute(query)
  for r in result1:
    if cid==r[0]:
      return True
  return False

def instructs(uid,cid):
  query='select course_id from Courses where uid='+str(uid)+';'
  result1=g.conn.execute(query)
  for r in result1:
    if cid==r[0]:
      return True
  return False

def isInstructor(user,password):
    query="select login,password from Users u,Instructors i where u.uid=i.uid"
    result=g.conn.execute(query)
    for r in result:
        if user==r[0] and password==r[1]:
            return True
    return False

def isUser(user,password):
    query="select login,password from Users"
    result=g.conn.execute(query)
    for r in result:
        if user==r[0] and password==r[1]:
            return True
    return False

if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()
