# nokiaWA

Whatsapp for old Nokia Phones, dumbphones, web-based

## Usage

`flask --app secure run`

Go to master branch README for more instructions

This is a more secure implementation for public hosting usage, keeps unwanted users away

## Secret Key
set Flask secret key (line 262) with 

recommended:

run this on the terminal `export SEC_KEY=random-key-here`, make sure random-key-here is a random string

alternative (keep this private ALWAYS):

change the value of "app.secret_key" to your random string of choice

## Login Creds
Set USERNAME and PASSWORD (line 265 and 266) to whatever you want

login at /securelogin on with those credentials.

## User Agent
visit https://whatmyuseragent.com on the device used to access nokiaWA

set allowed_ua (line 269) to your device's user agent
