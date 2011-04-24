

'''
def register():
    db.person.password.requires = IS_NOT_EMPTY()
    form = SQLFORM(db.person, fields=['username', 'email','show_email', 'password', 'interests'])
    if form.accepts(request.vars, session):
        session.authorized = form.vars.id
        session.email = form.vars.email
        session.username = form.vars.username
        session.flash = "You've been registered"
        redirect(URL(r=request, f='index'))
    return dict(form = form)

def login():
    db.person.email.requires = IS_NOT_EMPTY()
    db.person.password.requires = IS_NOT_EMPTY()
    form = SQLFORM(db.person, fields=['email', 'password'])
    if FORM.accepts(form, request.vars, session):
        users = db(db.person.email == form.vars.email)(db.person.password == form.vars.password).select()
        if len(users):
            session.authorized = users[0].id
            session.username = users[0].username
            session.email = users[0].email
            session.flash = "You are logged in"
            redirect(URL(r = request, f = 'index'))
        else:
            form.errors['password'] = "incorrect password"
    return dict(form=form)

def logout():
    session.authorized = None
    session.email = None
    session.username = None
    session.flash = "You are logged out"
    redirect(URL(r=request, f='index'))


def retrieve_password():
    form = SQLFORM.factory(
        Field('email', requires=IS_EMAIL()))
    if form.accepts(request.vars, session):
        person = db(db.person.email == form.vars.email).select(db.person.email, db.person.password, db.person.username)
        if person:
            mail = Mail()
            mail.settings.server = 'gae'
            mail.settings.sender = 'techclubaf@gmail.com'
            mail.settings.login = 'techclubaf@gmail.com:sap4phire'
            try:
                mail.send(to=[person[0].email], 
                          subject='Reminder',
                          message='Hi %s Your password is %s. You are advised to change it ASAP!\nHappy Hacking.' % (person[0].username, person[0].password))
            except: session.flash = 'Unable to send email.'
            else: 
                session.flash = 'Email sent'
                redirect(URL(r=request, f='index'))
        else:
            session.flash = 'Sorry, email does not exist in database'
            redirect(URL(r=request, f='retrieve_password'))
    return dict(form=form)
            

def change_password():
    if not session.authorized:
        session.flash = 'Not logged in!'
        redirect(URL(r=request, f="index"))
    form = SQLFORM.factory(
        Field('current_password', requires=db.person.password.requires),
        Field('new_password', requires=IS_NOT_EMPTY()),
        Field('new_password_again', requires=[IS_NOT_EMPTY(),IS_EXPR("value=='%s'" % request.vars.new_password, 'passwords do not match')])
        )
    if form.accepts(request.vars, session):
        user = db(db.person.id == session.authorized).select(db.person.ALL)[0]
        if user.password != request.vars.current_password:
            session.flash = 'Incorrect old password'
            redirect(URL(r=request, f='change_password'))
        else:
            user.update_record(password = form.vars.new_password)
            session.flash = 'password changed'
            redirect(URL(r=request, f='index'))
    return dict(form=form)
'''


def user():
#exposes:
#http://.../[app]/default/user/register
#http://.../[app]/default/user/login
#http://.../[app]/default/user/logout
#http://.../[app]/default/user/profile
#http://.../[app]/default/user/change_password
#http://.../[app]/default/user/verify_email
#http://.../[app]/default/user/retrieve_username
#http://.../[app]/default/user/request_reset_password
#http://.../[app]/default/user/reset_password
#http://.../[app]/default/user/impersonate
#http://.../[app]/default/user/groups
#http://.../[app]/default/user/not_authorized
    if auth.user:
        session.authorized = auth.user.id
    else:
        session.authorized = None
    return dict(form=auth())

def view_profile():
    person = db.person(request.args(0))
    form = SQLFORM(db.person, person, deletable=False, fields=['email','show_email','interests'])
    if form.accepts(request.vars, session):
        redirect(URL(r=request, f='index'))
    elif form.errors:
        response.flash = 'Incorrect values entered'
    
    return dict(form=form)


def show_profile():
    record = db.person(request.args(0))
    return dict(record=record)

def post():
    if not session.authorized:
        redirect(URL(r=request, f='user/login'))
    if request.vars['type'] == 'link':
        form = SQLFORM.factory(
            Field('title', requires=IS_NOT_EMPTY()),
            Field('url', requires=IS_NOT_EMPTY())
            )
        if form.accepts(request.vars, session):
            db.submission.insert(
                title = form.vars.title,
                url = form.vars.url,
                author = session.authorized,
                body = '')
            session.flash = 'Post successful'
            redirect(URL(r=request, f='index', vars=dict(type='latest')))
    
        return dict(form=form)
    else:
        form = SQLFORM.factory(
            Field('title', requires=IS_NOT_EMPTY()),
            Field('body','text', requires=IS_NOT_EMPTY())
        )
        if form.accepts(request.vars, session):
            db.submission.insert(
                title = request.vars['type']+": "+form.vars.title,
                url = 'self',
                author = session.authorized,
                body = form.vars.body)
            session.flash = 'Post successful'
            redirect(URL(r=request, f='index', vars=dict(type='latest')))
        return dict(form=form)

def index():
    if auth.user:
        session.authorized = auth.user.id
    else:
        session.authorized = None

    if len(request.args): page = int(request.args[0])
    else: page = 0
    items_per_page = 20
    limitby = (page*items_per_page, (page+1)*items_per_page +1)
    if request.vars.type == 'latest':
        posts = db().select(db.submission.ALL,orderby=~db.submission.post_time, limitby=limitby)
    else:
        posts = db().select(db.submission.ALL,orderby=~db.submission.score, limitby=limitby)
    return dict(posts=posts, page=page, items_per_page=items_per_page)


def comments():
    news_comments = db(db.comment.submission == request.args(0)).select(db.comment.ALL, orderby=~db.comment.score)
    tree = {}
    for comment in news_comments:
        if not tree.has_key(comment.parent_): tree[comment.parent_] = [comment]
        else: tree[comment.parent_].append(comment)
    if session.authorized:
        form = SQLFORM.factory(
            Field('body','text', requires=IS_NOT_EMPTY()))
        if form.accepts(request.vars, session):
            db.comment.insert(
                author = session.authorized,
                body = form.vars.body,
                submission = request.args(0)
            )
            curr_comments = int(db.submission[request.args(0)].comments) + 1
            
            db(db.submission.id == request.args(0)).update(comments = curr_comments)
            redirect(URL(f='comments', args = request.args(0)))
    else:
        form = None
        
    return dict(tree=tree, news_item=db.submission[request.args(0)], form=form)


def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


def vote():
    if request.args(2) == 'upvote':
        if request.args(1) == 'submission':
            item = db(db.submission.id == request.args(0)).select()[0]
        elif request.args(1) == 'comment':
            item = db(db.comment.id == request.args(0)).select()[0]
        new_vote = item.points + 1
        item.update_record(points = new_vote)
        #record vote
        db.vote.insert(item_type=request.args(1),
                       item_id=request.args(0),
                       author=session.authorized)
        #increase author's points
        new_points = db.person(request.args(3)).points + 1
        db.person(request.args(3)).update_record(points = new_points)
 
    return str(new_vote)
    
def insert_comment():
    if not request.vars['body'+str(request.args(1))] == '':
        db.comment.insert(
            body = request.vars['body'+str(request.args(1))],
            submission = request.args(0),
            parent_ = request.args(1),
            author = session.authorized
            )
        
        curr_comments = int(db.submission[request.args(0)].comments) + 1
        db(db.submission.id == request.args(0)).update(comments = curr_comments)
        
        session.flash = "comment posted"
    else:
        session.flash = "please enter comment"
    
def calculate_score(points, hour_age, gravity=1.8):
    return (points-1.0)/(hour_age+2.0)**gravity

def rank():
    news_items = db().select(db.submission.points, db.submission.post_time, db.submission.score, db.submission.id)
    for item in news_items:
        new_score = calculate_score(item.points, seconds_since(item.post_time, now)/3600)
        item.update_record(score = new_score)
        db.commit()
    
    comments = db().select(db.comment.points, db.comment.post_time, db.comment.score, db.comment.id)
    for item in comments:
        new_score = calculate_score(item.points, seconds_since(item.post_time, now)/3600)
        item.update_record(score = new_score)
        db.commit()
    return

def about():
    return dict()
