import time
now = time.time()

from gluon.tools import Auth, Mail
from gluon.settings import settings


# if running on Google App Engine
if settings.web2py_runtime_gae:
    from gluon.contrib.gql import *
    # connect to Google BigTable
    db = DAL('gae')
    # and store sessions there
    session.connect(request, response, db=db)
else:
    # if not, use SQLite or other DB
    db = DAL('sqlite://storage.sqlite')


class IS_SELF_OR_URL:
    def __call__(self, value):
        value = value.strip()
        if value.lower()=='self':
            return (value.lower(), None)
        try: fetch(value)
        except:
            return (value, 'unreachable url')
        else: 
            return (value, None)

auth = Auth(globals(), db)

auth.settings.table_user_name = 'person'
auth.settings.table_group_name = 'auth_group'
auth.settings.table_membership_name = 'auth_membership'
auth.settings.table_permission_name = 'auth_permission'
auth.settings.table_event_name = 'auth_event'

db.define_table(
    auth.settings.table_user_name,
    Field('username', unique=True, readable=False),
    Field('first_name', length=128, default='', readable=False, writable=False),
    Field('last_name', length=128, default='', readable=False, writable=False),
    Field('email', length=128, default='', unique=True),
    Field('show_email', 'boolean', default=False),
    Field('password', 'password', length=512,
          readable=False, label='Password'),
    Field('registration_key', length=512,
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,
          writable=False, readable=False, default=''),
    Field('points', 'integer',readable=False, writable=False, default=1),
    Field('interests', 'text', default=''),
    Field('active', 'boolean', default=True, readable=False, writable=False))

custom_auth_table = db[auth.settings.table_user_name] # get the custom_auth_table
custom_auth_table.username.requires = [IS_NOT_EMPTY(), IS_NOT_IN_DB(db, custom_auth_table.username)]
#custom_auth_table.first_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
#custom_auth_table.last_name.requires = IS_NOT_EMPTY(error_message=auth.messages.is_empty)
custom_auth_table.password.requires = [CRYPT()]
custom_auth_table.email.requires = [
  IS_EMAIL(error_message=auth.messages.invalid_email),
  IS_NOT_IN_DB(db, custom_auth_table.email)]

auth.settings.table_user = custom_auth_table # tell auth to use custom_auth_table
auth.settings.hmac_key = "your-phrase"


auth.define_tables()

'''
db.define_table('person',
    Field('username', unique=True, readable=False),
    Field('email', length=128, unique=True),
    Field('show_email', 'boolean', default=False),
    Field('password', 'password', length=512, readable=False, label="Password"),
    Field('points', 'integer',readable=False, writable=False, default=1),
    Field('interests', 'text', default=''),
    Field('active', 'boolean', default=True))

db.person.username.requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, db.person.username)]
db.person.email.requires=[IS_EMAIL(), IS_NOT_IN_DB(db, db.person.email)]
db.person.password.requires = [CRYPT(), IS_NOT_EMPTY()]
'''
db.define_table('submission',
    Field('author', db.person),
    Field('points', 'integer', default=1),
    Field('post_time', 'datetime', default=request.now),
    Field('comments', 'integer', default=0),
    Field('title', length=128),
    Field('body', 'text', default=''),
    Field('url', length=128, default=''),
    Field('score', 'double', default=0.0))

db.submission.title.requires=IS_NOT_EMPTY()
db.submission.url.requires=IS_SELF_OR_URL()

db.define_table('comment',
    Field('points', 'integer', default=1),
    Field('post_time', 'datetime', default=request.now),
    Field('author', db.person),
    Field('body', 'text', default=''),
    Field('submission', db.submission),
    Field('parent_', 'integer', default=0),
    Field('score', 'double', default=0.0))

db.submission.body.requires = IS_NOT_EMPTY()

db.define_table('vote',
    Field('item_type', default=''),
    Field('author', db.person),
    Field('item_id', 'integer', default=0))

db.vote.item_type.requires = IS_NOT_EMPTY()


mail = Mail(globals())
mail.settings.server = 'gae'
mail.settings.sender = 'sender@domain'
mail.settings.login = 'sender@domain:password'
auth.settings.mailer = mail
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
#auth.messages.verify_email = 'Click on the link http://' + request.env.http_host + \
#    URL(r=request,c='default',f='user',args=['verify_email']) + '/%(key)s to verify your email'
auth.messages.reset_password = 'Click on the link http://' + request.env.http_host + \
    URL(r=request,c='default',f='user',args=['reset_password']) + '/%(key)s to reset your password'
