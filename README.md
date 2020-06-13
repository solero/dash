<p align="center">
   <img alt="dash" src="https://user-images.githubusercontent.com/32749673/72632476-3e14bc00-394e-11ea-87e3-be09d8e40909.png">
</p>

#

<p align="center">
  <a href="https://discord.gg/UPnWKfh">
    <img
      alt="Solero Discord"
      src="https://img.shields.io/discord/323290581063172096?color=7289DA&label=discord"
    />
  </a>
  <a href="https://solero.me">
    <img
      alt="Solero Forum"
      src="https://img.shields.io/discourse/https/solero.me/topics?color=73afb6"
    />
  </a>
  <a href="https://github.com/Solero/Houdini-asyncio/issues">
    <img
      alt="Issue Tracker"
      src="https://img.shields.io/github/issues/solero/dash"
    />
  </a>
  <a href="./LICENSE">
    <img
      alt="License"
      src="https://img.shields.io/github/license/solero/dash"
    />
  </a>
</p>

<p align="center">A server for Houdini web-services.</p>

## Features
- Avatar API for igloo likes and friends lists.
- Endpoint for the legacy flash "Create a penguin".
- Auto-complete API for phrase-chat autocomplete.
- Penguin activation via register*
- Provides API for password resets.
- Highly configurable!

**Requires SendGrid API key*

## Installation

Dash provides only very simple routes, for this reason, 
some web server trickery is required to register the routes
required by the Club Penguin client. 

Sample for nginx config:

```conf
# legacy (AS2)

# server_name play.clubpenguin.com 
location /create_account/create_account.php {
    proxy_pass http://localhost:3000/create/legacy;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com 
location /penguin/activate {
    proxy_pass http://localhost:3000/activate/legacy;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# vanilla (AS3)

# server_name play.clubpenguin.com
location ~ ^/(.*)/penguin/create {
    proxy_pass http://localhost:3000/create/vanilla/$1;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location /penguin/create {
    proxy_pass http://localhost:3000/create/vanilla/en;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com 
location ~ ^/(.*)/penguin/activate/(.*) {
    proxy_pass http://localhost:3000/activate/vanilla/$1/$2;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location ~ ^/(.*)/penguin/activate {
    proxy_pass http://localhost:3000/activate/vanilla/$1;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location /penguin/activate {
    proxy_pass http://localhost:3000/activate/vanilla/en;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location ~ ^/(.*)/penguin/forgot-password/(.*) {
    proxy_pass http://localhost:3000/password/$1/$2;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location ~ ^/(.*)/penguin/forgot-password {
    proxy_pass http://localhost:3000/password/$1;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location /penguin/forgot-password {
    proxy_pass http://localhost:3000/password/en;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location ^/(.*)/web-service/snfgenerator/session$ {
    proxy_pass http://localhost:3000/session;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location /api/v0.2/xxx/game/get/world-name-service/start_world_request {
    proxy_pass http://localhost:3000/swrequest;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location ~ ^/avatar/(.*)/cp$ {
    proxy_pass http://localhost:3000/avatar/$1$is_args$args;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name media.clubpenguin.com
location /social/autocomplete/v2/search/suggestions {
    proxy_pass http://localhost:3000/autocomplete;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# server_name secured.clubpenguin.com
location /manager {
    proxy_pass http://dash:3000/manager;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}
```

Dash can be setup as shown:

```shell
$ git clone https://github.com/solero/dash
$ cd dash
$ pip install -r requirements.txt
$ mv config.sample.py config.py
$ python bootstrap.py -c config.py
```

### Recaptcha Support

Dash create endpoints support Google reCAPTCHA. You require reCAPTCHA v3 keys from [here](https://www.google.com/recaptcha/admin/create).

For the legacy create to work, you must add the following HTML embed to your play page in order for the captcha to work with the client. 

```html
<script src="https://www.google.com/recaptcha/api.js?render=site_key"></script>
<script type="text/javascript">
function grecaptchaSubmit(){
  grecaptcha.execute('site_key', { action: 'login' }).then(function (token) {
    document.getElementById("game").finishedCaptcha(token);
  });
}
</script>
```

After adding this embed, you must replace `site_key` with the value of your google recaptcha site key. You also must fill in your secret key in config.sample.py.

Please also add your site and secret keys to Dash configuration file.

## Contributing

:heartpulse: So glad to hear of your interest!

If you have suggestions for how this project can be improved, or want to report a bug, please feel free to open an issue! We welcome any and all contributions. We listen to all your questions and are always active on the [Solero Discord server](https://solero.me/discord).

## License

MIT Licensed
