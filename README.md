# nokiaWA

**WhatsApp for old Nokia phones and other dumbphones, web-based.**  
> **Self-host this project for your own safety.**

---

##  Notice

If you get a 403 Forbidden on /securelogin or any endpoint, remove the user-agent.txt file, and re-request from the device you will be using for nokiaWA

---

##  Setup

Ensure Python and Chrome/Chromium is installed.

Install the required libraries via pip:

```
git clone https://github.com/RaynardGerraldo/nokiaWA
cd nokiaWA/
pip install -r requirements.txt
```
Then, input credentials needed for /securelogin:
```
flask --app routes run
```

---

##  Usage

```bash
cd nokiaWA/
flask --app routes run --host=0.0.0.0
```

Then:

1. Go to `/login`, scan the QR code.
2. Go to `/chats`, click a contact.
3. Start reading and sending messages!

---

##  Features

-  Read messages
-  Send plain text messages
-  Send media: images, videos, audio, files (as attachments)
-  View/download images
-  View stickers
-  View emojis (text-based)
-  Download videos
-  Download audio
-  Download files (ZIP, PDF, DOCX, XLSX, etc.)

---


## Endpoints/Routes

- /securelogin: login before login, only user with creds is allowed
- /login: whatsapp qr code scan
- /logged-in: check if you are logged in or not
- /chats: list of whatsapp chats
- /processnum: passes number to be processed
- /chatsession: chat session for every number
- /send: send messages
- /downmedia: download media
- /pgdown: down button to load older messages
- /logout: logout from both whatsapp login and securelogin

---


##  Roadmap

Open to suggestions

Feel free to contribute!

---

##  Credits

- Code Snippets: [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js/)
- UI Inspiration: [Mpgram](https://github.com/shinovon/mpgram-web)
