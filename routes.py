import os
import ast
import bcrypt
import base64
from werkzeug.utils import secure_filename
from flask import Flask, Response, render_template, session, render_template_string, redirect, url_for, request
import waweb

def sec_key(app):
    if os.path.exists("secret-key.txt") and not os.path.getsize("secret-key.txt") == 0:
        with open("secret-key.txt", "r") as f:
            return f.read()
    else:
        key = base64.b64encode(os.urandom(32)).decode()
        with open("secret-key.txt", "w") as f:
            f.write(key)
            return key

app = Flask(__name__)
app.secret_key = sec_key(app)
mediainfo = {}
# preload before logging-in, it works
waweb.preload()

@app.route('/securelogin', methods=['GET', 'POST'])
def secure_login_route():
    if request.method == 'GET' and 'seclogged_in' in session:
        if session['seclogged_in']:
            if waweb.logged_in():
                return redirect(url_for('chats_route'))
            return redirect(url_for('login_route'))

    if request.method == 'POST':
        creds = waweb.secure_login()
        if request.form['username'] == creds[0] and bcrypt.checkpw(request.form['password'].encode(), creds[1].encode()):
            session['seclogged_in'] = True
            if waweb.logged_in():
                return redirect(url_for('chats_route'))
            return redirect(url_for('login_route'))
        return 'Invalid credentials', 401
    return render_template_string('''
        <form method="post">
          <input name="username">
          <input name="password" type="password">
          <input type="submit">
        </form>
    ''')

@app.before_request
def require_login():
    allowed = ['secure_login_route']
    ua = request.headers.get('User-Agent', '')
    if os.path.exists("user-agent.txt") and not os.path.getsize("user-agent.txt") == 0:
        with open("user-agent.txt", "r") as f:
            allowed_ua = f.read()
    else:
        with open("user-agent.txt", "w") as f:
            allowed_ua = ua
            f.write(ua)
 
    if ua != allowed_ua:
        return "Forbidden", 403
    elif request.endpoint not in allowed and not session.get('seclogged_in'):
        return redirect(url_for('secure_login_route'))

@app.route("/login")
def login_route():
    response = ""
    if not waweb.logged_in():
        waweb.login()
        response = render_template('qr.html')
        return response
    else:
        return redirect(url_for('chats_route'))

@app.route("/logged-in")
def logged_in():
    if waweb.logged_in():
        return "<p>You are logged in</p>"
    return "<p>You are not logged in</p>"

@app.route("/logout")
def logout_route():
    waweb.logout()
    session['seclogged_in'] = False
    print(session)
    return redirect(url_for('secure_login_route'))

@app.route("/chats")
def chats_route():
    contact_msg = waweb.chats()
    name = waweb.your_name()
    return render_template("chats.html", contactmsg=contact_msg, yourname=name)

@app.route("/processnum", methods=['POST'])
def process_num_route():
    zip_contact = waweb.process_num()
    name_num = dict(zip_contact)
    num = request.form.get("contact")
    return redirect(url_for("chat_session_route", num=name_num.get(num)))

@app.route("/chatsession")
def chat_session_route():
    num = request.args.get("num", None)
    error = session.pop('flash', "")
    if num is None:
        return "<p>No chats available</p>"
    waweb.load_msg(num)
    who_msg_t = waweb.chat_session(num)
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
            error = "File upload failed, check file name for any special characters."
            session['flash'] = error
            return redirect(url_for("chat_session_route", num=num))
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
        waweb.media_send(num, mediainfo, msg, as_attach)
    # plain text
    else:
        waweb.send_message(num, msg)
    return redirect(url_for("chat_session_route", num=num))

@app.route("/downmedia", methods=['POST', 'GET'])
def download_media():
    if request.method == 'POST':
        media = request.form.get("media")
        media_type = request.form.get("type")
        filename = request.form.get("filename")
        mimetype = request.form.get("mimetype")

    if media_type == "image":
        file_bytes = base64.b64decode(media)
        response = Response(file_bytes, mimetype="image/jpeg")
        response.headers["Content-Disposition"] = "attachment; filename=image.jpg"

    elif media_type == "video":
        video = ast.literal_eval(media)
        file_bytes = base64.b64decode(waweb.decrypt_media(video))
        response = Response(file_bytes, mimetype="video/mp4")
        response.headers["Content-Disposition"] = "attachment; filename=video.mp4"

    elif media_type == "audio":
        audio = ast.literal_eval(media)
        file_bytes = base64.b64decode(waweb.decrypt_media(audio))
        response = Response(file_bytes, mimetype="audio/mpeg")
        response.headers["Content-Disposition"] = "attachment; filename=audio.mp3"

    elif media_type == "document":
        document = ast.literal_eval(media)
        file_bytes = base64.b64decode(waweb.decrypt_media(document))
        response = Response(file_bytes, mimetype=mimetype)
        response.headers["Content-Disposition"] = f"""attachment; filename={filename}"""

    return response

@app.route("/pgdown", methods=['POST'])
def down_route():
    num = request.form.get("num")
    error = waweb.down(num)
    session['flash'] = error
    return redirect(url_for("chat_session_route", num=num))
