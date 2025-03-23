from flask import Flask, render_template,redirect,url_for,request
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import base64
import threading

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--headless=new')
chrome_options.add_argument(f'user-agent={user_agent}')

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://web.whatsapp.com/")

def login():
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.TAG_NAME, 'canvas')))

    # this is the qr
    qr_elm = driver.find_element(By.TAG_NAME, 'canvas')
    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", qr_elm)
    canvas_png = base64.b64decode(canvas_base64)

    # write qr png data to actual png
    with open("static/images/qrcode.png", "wb") as f:
        f.write(canvas_png)

def load_send():
    driver.execute_script("window.Store.User = window.require('WAWebUserPrefsMeUser');")
    driver.execute_script("window.Store.MsgKey = window.require('WAWebMsgKey');")
    driver.execute_script("window.Store.SendMessage = window.require('WAWebSendMsgChatAction');")

def send_message(ids,response):
    driver.execute_script(f"document.chat = window.Store.Chat.get('{ids}');")
    driver.execute_script("document.meUser = window.Store.User.getMaybeMeUser();")
    driver.execute_script("document.newId = await window.Store.MsgKey.newId();")
    driver.execute_script("""document.newMsgId = new window.Store.MsgKey({
        from: document.meUser,
        to: document.chat.id,
        id: document.newId,
        participant: document.chat.id.isGroup() ? document.meUser : undefined,
        selfDir: 'out',
    });""")

    driver.execute_script(f"""document.message = {{
        id: document.newMsgId,
        ack: 0,
        body: "{response}",
        from: document.meUser,
        to: document.chat.id,
        local: true,
        self: 'out',
        t: parseInt(new Date().getTime() / 1000),
        isNewMsg: true,
        type: 'chat',
    }};""")

    driver.execute_script("window.Store.SendMessage.addAndSendMsgToChat(document.chat, document.message)")


app = Flask(__name__)
session = {"logged_in": False}

def check_login():
    if WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Chats']"))):
        print("hey it works")
        session["logged_in"] = True

@app.route("/login")
def hello_world():
    # by the time this is called its already fully loaded, thats why speed
    login()
    response = render_template('qr.html')
    threading.Thread(target=check_login).start()
    return response

@app.route("/logged-in")
def logged_in():
    if session.get("logged_in"):
        # continue this, instead of only displaying ur in, start displaying chats!
        return "<p>Ur in...</p>"
    return "<p>U aint in bro...</p>"

@app.route("/chats")
def chats():
    load_chats = driver.execute_script("window.Store = Object.assign({}, window.require('WAWebCollections'));")

    contacts = driver.execute_script("return window.Store.Chat.map(contacts => contacts.formattedTitle);")
    
    latest_msg = driver.execute_script("return window.Store.Chat._models.flatMap(chatd => window.Store.Chat.get(chatd.id._serialized).msgs._models.slice(-1).map(msg => msg.body));")
    
    load_send()
    contact_msg = dict(zip(contacts,latest_msg))
    return render_template("chats.html", contactmsg=contact_msg)

@app.route("/processnum", methods=['POST'])
def process_num():
    contacts = driver.execute_script("return window.Store.Chat.map(contacts => contacts.formattedTitle);")
    contact_num = driver.execute_script("return window.Store.Chat.map(contacts => contacts.id._serialized);")

    name_num = dict(zip(contacts,contact_num))
    
    num = request.form.get("contact")

    return redirect(url_for("chat_session", num=name_num.get(num)))

@app.route("/chatsession")
def chat_session():
    num = request.args.get("num", None)
    if num is None:
        return "<p>No chats available</p>"
    
    # get all chats of num here and display
    driver.execute_script(f"document.chat = window.Store.Chat.get('{num}');")
    driver.execute_script("window.Store.ConversationMsgs = window.require('WAWebChatLoadMessages');")
    driver.execute_script("document.msgdata = await window.Store.ConversationMsgs.loadEarlierMsgs(document.chat);")
    messages = driver.execute_script("return document.msgdata.map(msg => msg.body);")
    print(messages)
    print(type(messages))
    return render_template("messages.html", messages=messages, num=num)

@app.route("/send", methods=['POST'])
def send():
    msg_to_send = request.form.get("sendbox")
    num = request.form.get("num")
    send_message(num,msg_to_send)
    return redirect(url_for("chat_session", num=num))
