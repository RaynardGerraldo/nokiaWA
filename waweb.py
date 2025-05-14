from flask import Flask, render_template,redirect,url_for,request, Response
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from datetime import datetime
import time
import base64
import threading
import os
import ast
import emoji

user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument('--headless=new')
chrome_options.add_argument("--remote-debugging-port=9222")  # helps fix DevToolsActivePort error
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument(f"--user-agent={user_agent}")

chrome_path = "" # your chrome path here
chromedriver_path = "" # your chromedriver path here

if chromedriver_path and chrome_path:
    chrome_options.binary_location = chrome_path
    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service,options=chrome_options)
else:
    driver = webdriver.Chrome(options=chrome_options)

driver.get("https://web.whatsapp.com/")
print("Chromedriver Version: ", driver.capabilities["chrome"]["chromedriverVersion"])
media_download = {}
session_reload = {}
mediainfo = {}
def login():
    if session["logged_in"] is True:
       return False 
    if os.path.exists("static/images/qrcode.png"):
        os.remove("static/images/qrcode.png")
    WebDriverWait(driver,30).until(EC.presence_of_element_located((By.TAG_NAME, 'canvas')))

    # this is the qr
    qr_elm = driver.find_element(By.TAG_NAME, 'canvas')
    canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", qr_elm)
    canvas_png = base64.b64decode(canvas_base64)

    # write qr png data to actual png
    directory = "static/images"
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Directory '{directory}' created.")
    with open("static/images/qrcode.png", "wb") as f:
        f.write(canvas_png)
    
    return True

def check_login():
    if WebDriverWait(driver,60).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[aria-label='Chats']"))):
        print("hey it works")
        driver.execute_script("window.Store = Object.assign({}, window.require('WAWebCollections'));")
        contact_num = driver.execute_script("return window.Store.Chat.map(contacts => contacts.id._serialized);")

        for num in contact_num:
            session_reload[num] = 0
        session["logged_in"] = True

def load_msg(num):
    driver.execute_script(f"document.chat = window.Store.Chat.get('{num}');")
    driver.execute_script("window.Store.ConversationMsgs = window.require('WAWebChatLoadMessages');")
    driver.execute_script("await window.Store.ConversationMsgs.loadEarlierMsgs(document.chat);")

def load_send():
    driver.execute_script("window.Store.User = window.require('WAWebUserPrefsMeUser');")
    driver.execute_script("window.Store.MsgKey = window.require('WAWebMsgKey');")
    driver.execute_script("window.Store.SendMessage = window.require('WAWebSendMsgChatAction');")
    driver.execute_script("window.Store.MediaObject = window.require('WAWebMediaStorage');")
    driver.execute_script("window.Store.OpaqueData = window.require('WAWebMediaOpaqueData');")
    driver.execute_script("window.Store.MediaTypes = window.require('WAWebMmsMediaTypes');")
    driver.execute_script("window.Store.MediaPrep = window.require('WAWebPrepRawMedia');")
    driver.execute_script("window.Store.MediaUpload = window.require('WAWebMediaMmsV4Upload');")

    driver.execute_script("""document.mediaInfoToFile = ({ data, mimetype, filename }) => {
        const binaryData = window.atob(data);

        const buffer = new ArrayBuffer(binaryData.length);
        const view = new Uint8Array(buffer);
        for (let i = 0; i < binaryData.length; i++) {
            view[i] = binaryData.charCodeAt(i);
        }

        const blob = new Blob([buffer], { type: mimetype });
        return new File([blob], filename, {
            type: mimetype,
            lastModified: Date.now()
        });
    };""")

def media_send(ids, mediainfo, caption, as_attach):
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

    driver.execute_script("document.file = document.mediaInfoToFile(arguments[0])", mediainfo)
    
    # init file
    driver.execute_script(f"""document.mData = await window.Store.OpaqueData.createFromData(document.file, document.file.type);
                              document.mediaPrep = window.Store.MediaPrep.prepRawMedia(document.mData, {{ asDocument: {as_attach} }});
                              document.mediaData = await document.mediaPrep.waitForPrep();
                              document.mediaObject = window.Store.MediaObject.getOrCreateMediaObject(document.mediaData.filehash);
                              document.mediaType = window.Store.MediaTypes.msgToMediaType({{
                                  type: document.mediaData.type,
                                  isGif: document.mediaData.isGif
                              }});
    """)

    # init upload
    driver.execute_script(""" 
                              if (!(document.mediaData.mediaBlob instanceof window.Store.OpaqueData)) {
                                  document.mediaData.mediaBlob = await window.Store.OpaqueData.createFromData(document.mediaData.mediaBlob, document.mediaData.mediaBlob.type);
                              }
                              document.mediaData.renderableUrl = document.mediaData.mediaBlob.url();
                              document.mediaObject.consolidate(document.mediaData.toJSON());
                              document.mediaData.mediaBlob.autorelease();


                              document.uploadedMedia = await window.Store.MediaUpload.uploadMedia({
                                 mimetype: document.mediaData.mimetype,
                                 mediaObject: document.mediaObject,
                                 mediaType: document.mediaType
                              });

                              document.mediaEntry = document.uploadedMedia.mediaEntry;
                              if (!document.mediaEntry) {
                                 throw new Error('upload failed: media entry was not created');
                              }
    """)
    
    # init send
    driver.execute_script("""document.mediaData.set({
                                clientUrl: document.mediaEntry.mmsUrl,
                                deprecatedMms3Url: document.mediaEntry.deprecatedMms3Url,
                                directPath: document.mediaEntry.directPath,
                                mediaKey: document.mediaEntry.mediaKey,
                                mediaKeyTimestamp: document.mediaEntry.mediaKeyTimestamp,
                                filehash: document.mediaObject.filehash,
                                encFilehash: document.mediaEntry.encFilehash,
                                uploadhash: document.mediaEntry.uploadHash,
                                size: document.mediaObject.size,
                                streamingSidecar: document.mediaEntry.sidecar,
                                firstFrameSidecar: document.mediaEntry.firstFrameSidecar
                             });

    """)
    
    # prepare message obj
    driver.execute_script(f"""document.message = {{
        id: document.newMsgId,
        ack: 0,
        body: document.mediaData.preview,
        from: document.meUser,
        to: document.chat.id,
        local: true,
        self: 'out',
        t: parseInt(new Date().getTime() / 1000),
        isNewMsg: true,
        ...document.mediaData,
        caption: "{caption}"
    }};""")

    driver.execute_script("window.Store.SendMessage.addAndSendMsgToChat(document.chat, document.message)")

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

def gather_msg(msgs):
    messages = []
    for msg in msgs:
        if msg["type"] == "chat":
            messages.append(emoji.demojize(msg["body"]))
        elif msg["type"] == "image" or msg["type"] == "sticker":
            # using mimetype for stickers
            messages.append([(msg["type"], msg["mimetype"], decrypt_media(msg), emoji.demojize(msg["caption"]))])
        elif msg["type"] == "revoked":
            messages.append("Message deleted")
        else:
            msg["caption"] = emoji.demojize(msg["caption"])
            messages.append(msg)
    return messages

def decrypt_media(msg):
    driver.execute_script(f"""try {{ document.decryptedMedia = await window.Store.DownloadManager.downloadAndMaybeDecrypt({{
	    directPath: "{msg["directPath"]}",
	    encFilehash: "{msg["encFilehash"]}",
	    filehash: "{msg["filehash"]}",
	    mediaKey: "{msg["mediaKey"]}",
	    mediaKeyTimestamp: "{msg["mediaKeyTimestamp"]}",
	    type: "{msg["type"]}",
	    signal: (new AbortController).signal
    }}) }} catch(e) {{ if(e.status && e.status == 404) document.decryptedMedia = undefined }};""")
    
    
    driver.execute_script("""document.base64str = (arrayBuffer) =>
        new Promise((resolve, reject) => {
            const blob = new Blob([arrayBuffer], {
                type: 'application/octet-stream',
            });
            const fileReader = new FileReader();
            fileReader.onload = () => {
                const [, data] = fileReader.result.split(',');
                resolve(data);
            };
            fileReader.onerror = (e) => reject(e);
            fileReader.readAsDataURL(blob);
    });""")

    base64str = driver.execute_script("if(document.decryptedMedia != undefined) return await document.base64str(document.decryptedMedia)")

    return base64str
    
app = Flask(__name__)
session = {"logged_in": False}

@app.route("/login")
def hello_world():
    if login():
        response = render_template('qr.html')
        threading.Thread(target=check_login).start()
        return response
    else:
        return "<p>Ur logged in bro..go to /chats</p>"

@app.route("/logged-in")
def logged_in():
    if session.get("logged_in"):
        return "<p>Ur in...</p>"
    return "<p>U aint in bro...</p>"


@app.route("/chats")
def chats():
    driver.execute_script("window.Store.DownloadManager = window.require('WAWebDownloadManager').downloadManager;")
    contacts = driver.execute_script("return window.Store.Chat.map(contacts => contacts.formattedTitle);")
    latest_msg = driver.execute_script("""return window.Store.Chat._models.flatMap(chatd => window.Store.Chat.get(chatd.id._serialized).msgs._models.slice(-1).map(m => (    {
        body: m.body,
        timestamp: m.t,
        from: m.from,
        type: m.type,
        filename: m.filename || "",
        mimetype: m.mimetype,
        caption: m.caption || "",
	    directPath: m.directPath,
	    encFilehash: m.encFilehash,
	    filehash: m.filehash,
	    mediaKey: m.mediaKey,
	    mediaKeyTimestamp: m.mediaKeyTimestamp,
    })));""");
    
    all_l_msg = gather_msg(latest_msg)
    load_send()
    contact_msg = dict(zip(contacts,all_l_msg))
    
    yourname = driver.execute_script("return window.Store.Contact.get(window.Store.User.getMeUser()._serialized).name")

    return render_template("chats.html", contactmsg=contact_msg, yourname=yourname)

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
    error = request.args.get("error", "")
    if num is None:
        return "<p>No chats available</p>"
    
    if error:
        error = "File upload failed, check file name for any special characters."
    if session_reload[num] == 0:
        load_msg(num)
        session_reload[num] += 1
        
    msgdata = driver.execute_script(f"""return document.msgdata = window.Store.Chat.get('{num}').msgs._models.map(m => ({{
        body: m.body,
        timestamp: m.t,
        from: (m.from.server == "g.us" ? null : window.Store.Contact.get(m.from._serialized).name) || window.Store.Contact.get(m.author._serialized).name || m.senderObj.verifiedName || m.senderObj.pushname,
        type: m.type,
        filename: m.filename || "",
        mimetype: m.mimetype,
        caption: m.caption || "",
	    directPath: m.directPath,
	    encFilehash: m.encFilehash,
	    filehash: m.filehash,
	    mediaKey: m.mediaKey,
	    mediaKeyTimestamp: m.mediaKeyTimestamp,
    }}));""")

    messages = gather_msg(msgdata)
    # using name in contact (if available) or whatsapp name (verified for business acc, push for non business acc)
    who = driver.execute_script("return document.msgdata.map(m => m.from);")
    time = [datetime.fromtimestamp(timestamp["timestamp"]).time().strftime("%H:%M") for timestamp in msgdata]

    messages.reverse()
    who.reverse()
    time.reverse()

    who_msg_t = list(zip(who,messages,time))

    print(who_msg_t)

    return render_template("messages.html", who_msg_t=who_msg_t, num=num, error=error)

@app.route("/send", methods=['POST'])
def send():
    num = request.form.get("num")
    msg = request.form.get("sendbox")
    fileupload = request.files['file']
    filename = secure_filename(fileupload.filename)
    file_bytes = fileupload.read()

    if mediainfo and request.method == 'POST':
        mediainfo.clear()

    if fileupload:
        if fileupload.filename == '' or not file_bytes:
            error = True
            return redirect(url_for("chat_session", num=num, error=error))
        else:
            mimetype = fileupload.content_type
            file_base64 = base64.b64encode(file_bytes).decode('utf-8')
            mediainfo["data"] = file_base64
            mediainfo["mimetype"] = mimetype
            mediainfo["filename"] = filename

    # if there is file attached
    if mediainfo:
        checkbox = request.form.get("asattach")
        if checkbox == "yes":
            as_attach = "true"
        else:
            as_attach = "false"
        media_send(num, mediainfo, msg, as_attach) # for attachments request.form.get("asAttach"))
    # plain text
    else:
        send_message(num,msg)
    return redirect(url_for("chat_session", num=num))

@app.route("/downmedia", methods=['POST', 'GET'])
def download_media():
    if media_download and request.method == 'POST':
        media_download.clear()

    if not media_download and request.method == 'POST':
        media = request.form.get("media")
        media_type = request.form.get("type")
        filename = request.form.get("filename")
        mimetype = request.form.get("mimetype")

        media_download["type"] = media_type
        media_download["media"] = media
        media_download["filename"] = filename
        media_download["mimetype"] = mimetype

    if media_download["type"] == "image":
        file_bytes = base64.b64decode(media_download["media"])
        response = Response(file_bytes, mimetype="image/jpeg")
        response.headers["Content-Disposition"] = "attachment; filename=image.jpg"

    elif media_download["type"] == "video":
        video = ast.literal_eval(media_download["media"])
        file_bytes = base64.b64decode(decrypt_media(video))
        response = Response(file_bytes, mimetype="video/mp4")
        response.headers["Content-Disposition"] = "attachment; filename=video.mp4"
    
    elif media_download["type"] == "audio":
        audio = ast.literal_eval(media_download["media"])
        file_bytes = base64.b64decode(decrypt_media(audio))
        response = Response(file_bytes, mimetype="audio/mpeg")
        response.headers["Content-Disposition"] = "attachment; filename=audio.mp3"

    elif media_download["type"] == "document":
        document = ast.literal_eval(media_download["media"])
        file_bytes = base64.b64decode(decrypt_media(document))
        response = Response(file_bytes, mimetype=media_download["mimetype"])
        response.headers["Content-Disposition"] = f"""attachment; filename={media_download["filename"]}"""
    
    if request.method == 'GET':
        media_download.clear()

    return response

@app.route("/pgdown", methods=['POST'])
def down():
    num = request.form.get("num")
    driver.execute_script(f"document.lengthc = await window.Store.Chat.find('{num}')")
    length_old = driver.execute_script("return document.lengthc.msgs.length")
    length_new = driver.execute_script("return document.lengthc.msgs.length")
    while length_old == length_new:
        load_msg(num)
        length_new = driver.execute_script("return document.lengthc.msgs.length")
        print("old: ", length_old)
        print("new: ", length_new)
    return redirect(url_for("chat_session", num=num))
