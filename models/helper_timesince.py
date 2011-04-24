import datetime
'''
def timesince(sd,st):
    chunks = (
        (60 * 60 * 24 * 365, lambda n: 'one year' if n==1 else '%d years' % n),
        (60 * 60 * 24 * 30, lambda n: 'one month' if n==1 else '%d months' % n),
        (60 * 60 * 24 * 7, lambda n: 'one week' if n==1 else '%d weeks' % n),
        (60 * 60 * 24, lambda n: 'one day' if n==1 else '%d days' % n),
        (60 * 60, lambda n: 'one hour' if n==1 else '%d hours' % n),
        (60, lambda n: 'one minute' if n==1 else '%d minutes' % n),
        (1, lambda n: 'one second' if n==1 else '%d seconds' % n),
    )
    t = datetime.datetime.fromtimestamp(st)
    d = sd
    delta = t - (d - datetime.timedelta(0, 0, d.microsecond))
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0 : return 'an instant'
    for seconds, name in chunks:
        count = since // seconds
        if count != 0: break
    return name(count)

'''

def seconds_since(sd,st):
    t = datetime.datetime.fromtimestamp(st)
    d = sd
    delta = t - (d - datetime.timedelta(0, 0, d.microsecond))
    seconds = delta.days * 24 * 60 * 60 + delta.seconds
    return seconds



def timesince(sd,st):
    chunks = (
        (60 * 60 * 24 * 365, lambda n: 'one year' if n==1 else '%d years' % n),
        (60 * 60 * 24 * 30, lambda n: 'one month' if n==1 else '%d months' % n),
        (60 * 60 * 24 * 7, lambda n: 'one week' if n==1 else '%d weeks' % n),
        (60 * 60 * 24, lambda n: 'one day' if n==1 else '%d days' % n),
        (60 * 60, lambda n: 'one hour' if n==1 else '%d hours' % n),
        (60, lambda n: 'one minute' if n==1 else '%d minutes' % n),
        (1, lambda n: 'one second' if n==1 else '%d seconds' % n),
    )
    since = seconds_since(sd, st)
    if since <= 0 : return 'an instant'
    for seconds, name in chunks:
        count = since // seconds
        if count != 0: break
    return name(count)

