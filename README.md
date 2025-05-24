# nokiaWA

Whatsapp for old Nokia Phones, dumbphones, web-based

Self Host this please, for your own safety

Notice: If there is a "SessionNotCreatedException: DevToolsActivePort file doesn't exist" error, or, "selenium.common.exceptions.TimeoutException: Message:" during /login, follow the [Chromedriver Instruction](#chromedriver-instruction)

## Dependencies

- Python

(pip install)
- Flask
- selenium
- emoji
- Werkzeug (included with Flask)

## Usage

```
git clone https://github.com/RaynardGerraldo/nokiaWA
cd nokiaWA/
flask --app waweb run

-- go to /login, scan qr code
-- console should output "hey it works" or check "/logged-in", go to /chats after
-- click on any contact you want
-- now you can read and send messages

```

### Features
- Read messages
- Send plain text messages
- Send images,videos,audios,files (also as attachments)
- View and download images
- View stickers
- View emojis (text based)
- Download videos
- Download audios
- Download files (zip,pdf,docx,xlsx,etc)

## Chromedriver Instruction
Note: Do this only if you face the errors mentioned in notice. Default ChromeDriver should work just fine.

[Chromedriver Linux,Win,Mac](https://googlechromelabs.github.io/chrome-for-testing/#stable)

replace the stable version in the download links with "131.0.6778.264", download both "chrome" and "chromedriver" for your platform

unzip both zip files, for ease of access, move the chromedriver executable to the chrome folder

set the variable chrome_path (in waweb.py) to the full path of your chrome executable

and set the variable chromedriver_path on line (in waweb.py) to the full path of your chromedriver executable

[Chromedriver Termux Android](https://github.com/termux-user-repository/chromium-builder/releases/)

Download release 131.0.6778.264 for your architecture, unzip ,set above mentioned variables to the full path of chrome and chromedriver executables.

## Roadmap

Open to suggestions

Feel free to contribute :)

## Credits

 - [Whatsapp-Web.js for the snippets](https://github.com/pedroslopez/whatsapp-web.js/)
 - [Mpgram for the UI inspiration](https://github.com/shinovon/mpgram-web)  

