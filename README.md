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

...

Legacy (AS2):

# server_name play.clubpenguin.com (AS2 sub-domain)
location /create_account/create_account.php {
    proxy_pass http://localhost:3000/create/legacy;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

# server_name play.clubpenguin.com (AS2 sub-domain)
location /penguin/activate {
    proxy_pass http://localhost:3000/activate/legacy;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}


Vanilla (AS3):

# server_name play.clubpenguin.com (AS3 sub-domain)
location /penguin/create {
    proxy_pass http://localhost:3000/create/vanilla;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

 # server_name play.clubpenguin.com (AS3 sub-domain)
location /penguin/activate {
    proxy_pass http://localhost:3000/activate/vanilla;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

CardJutsuSnow (AS3):

 # server_name play.clubpenguin.com
location /en/web-service/snfgenerator/session {
		proxy_pass http://localhost:3000/session;
		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
 # server_name play.clubpenguin.com
location /pt/web-service/snfgenerator/session {
		proxy_pass http://localhost:3000/session;
		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
 # server_name play.clubpenguin.com
location /es/web-service/snfgenerator/session {
		proxy_pass http://localhost:3000/session;
		proxy_redirect off;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
	# server_name play.clubpenguin.com
location /api/v0.2/xxx/game/get/world-name-service/start_world_request {
		proxy_pass http://localhost:3000/swrequest;
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
$ python bootstrap.py -c config.sample.py
```

Recaptcha:

To protect your register from bots, your register will require a captcha. The register is built to work with recaptcha v3's API so you will be required to get a pair of recaptcha v3 keys from here:  https://www.google.com/recaptcha/admin/create.

If you are using the legacy (AS2) client for registration, you must add the following HTML embed to your play page in order for the captcha to work with the client. 

```conf
<style type="text/css">
  .grecaptcha-badge {
  display: none;
  }
</style>
<script src="https://www.google.com/recaptcha/api.js?render=SITE_KEY_GOES_HERE"></script>
<script type="text/javascript">
  function onSubmit(){
    grecaptcha.ready(function () {
      grecaptcha.execute('SITE_KEY_GOES_HERE', { action: 'home' }).then(function (token) {
          document.getElementById("game").finishedCaptcha(token);
      });
  });
  }
</script>
<form>
<div id='recaptcha' class="g-recaptcha"
data-sitekey="SITE_KEY_GOES_HERE"
data-callback="onSubmit"
data-size="invisible"></div>
</form>
```

After adding this embed, you must replace `SITE_KEY_GOES_HERE` with the value of your google recaptcha site key. You also must fill in your secret key in config.sample.py.

For the vanilla (AS3) client, you will not be required to add this HTML embed. You only need to get a pair of recaptcha keys and fill them out in your configuration file. Dash will render the HTML templates to have your recaptcha v3 site key placed on it.

## Contributing

:heartpulse: So glad to hear of your interest!

If you have suggestions for how this project can be improved, or want to report a bug, please feel free to open an issue! We welcome any and all contributions. We listen to all your questions and are always active on the [Solero Discord server](https://solero.me/discord).

## License

MIT Licensed