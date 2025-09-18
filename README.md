# nokiaWA

**WhatsApp for old Nokia phones and other dumbphones, web-based.**  
> **Self-host this project for your own safety.**

---

##  Notice

If you encounter the following errors during `/login`:

- `SessionNotCreatedException: DevToolsActivePort file doesn't exist`

Refer to the [Chromedriver Instructions](#chromedriver-instruction).

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
flask --app waweb run
```

---

##  Usage

```bash
cd nokiaWA/
gunicorn waweb:app -b 127.0.0.1:5000 --workers 3
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

##  Chromedriver Instruction

Only follow this section if you experience the errors in the [notice](#notice) above. Default ChromeDriver should work fine otherwise.

### For Linux, Windows, macOS

1. Download from: [Chromedriver Official](https://googlechromelabs.github.io/chrome-for-testing/#stable)
2. Use version: `131.0.6778.264` download both **chrome** and **chromedriver** for your OS.
3. Unzip both files. Move `chromedriver` into the same folder as `chrome` for convenience.
4. In `waweb.py`:
   - Set `chrome_path` to the full path of your **chrome** binary.
   - Set `chromedriver_path` to the full path of your **chromedriver** binary.

### For Termux on Android

- Download from: [Termux Chromium Releases](https://github.com/termux-user-repository/chromium-builder/releases/)
- Get release: `131.0.6778.264` for your CPU architecture.
- Unzip and set the `chrome_path` and `chromedriver_path` variables in `waweb.py`.

---

##  Roadmap

Open to suggestions

Feel free to contribute!

---

##  Credits

- Code Snippets: [whatsapp-web.js](https://github.com/pedroslopez/whatsapp-web.js/)
- UI Inspiration: [Mpgram](https://github.com/shinovon/mpgram-web)
