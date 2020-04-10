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

# server_name play.clubpenguin.com
location /create_account/create_account.php {
    proxy_pass http://localhost:3000/create;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

...

# server_name play.clubpenguin.com
location /create/activate {
    proxy_pass http://localhost:3000/create/activate;
    proxy_redirect off;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
}

```

## Contributing

:heartpulse: So glad to hear of your interest!

If you have suggestions for how this project can be improved, or want to report a bug, please feel free to open an issue! We welcome any and all contributions. We listen to all your questions and are always active on the [Solero Discord server](https://solero.me/discord).

## License

MIT Licensed