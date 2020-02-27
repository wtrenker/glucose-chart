import decimal as dec
import hashlib, binascii, os
import datetime
import pytz

zulu = pytz.timezone('UTC')
pst = pytz.timezone("America/Vancouver")

dbFileName = "meter.db"

def decimalAverage(num1, num2):
    n1 = dec.Decimal(str(num1))
    n2 = dec.Decimal(str(num2))
    average = (n1 + n2) / dec.Decimal('2.0')
    return average.quantize(dec.Decimal('.1'), rounding=dec.ROUND_UP)

def hash_password(password):
    """Hash a password for storing.
       By Alessandro Molina in https://www.vitoshacademy.com/hashing-passwords-in-python/"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user
       By Alessandro Molina in https://www.vitoshacademy.com/hashing-passwords-in-python/"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password

def dateTimeStr(naive, tzoneStr='GMT', ampm=False, month=False, seconds=True):
    tzone = pytz.timezone(tzoneStr)
    now = tzone.localize(naive)
    wkday = now.strftime('%a')
    month = '%b' if month else '%m'
    ymd = now.strftime(f'%Y-{month}-%d')
    hour = now.strftime('%I')
    if hour[0] == '0':   hour = hour[1]
    seconds = ':%S' if seconds else ''
    minsec = now.strftime(f'%M{seconds}')
    if ampm:
        ampm = now.strftime('%p').replace('AM', 'am').replace('PM', 'pm')
    else:
        ampm = ''
    zone = now.strftime('%Z')
    now = f"{wkday}, {ymd} {hour}:{minsec}{ampm} {zone}"
    return now

def isNone(obj): return obj is None or obj == 'None'


def isFloat(candidateStr=None):
    ok = True
    try:
        _ = float(candidateStr)
    except (TypeError, ValueError):
        ok = False
    return ok

def ymd(msdate):
    dated = datetime.datetime.fromtimestamp(msdate / 1000)
    dated = dated.strftime("%Y-%m-%d")
    return dated

if __name__ == '__main__':
    print(dateTimeStr(datetime.datetime.now(), 'America/Vancouver', ampm=True, month=True, seconds=False))
    # print(timestr)
    # print(isFloat(''))
    # print(hash_password(''))
    print(ymd(1581786089365))