# Dash

A simple web system/API for houdini-asyncio's registration and avatar generation.

# Setup

Dash was created to emulate the built in registration system in the CP client, which by default sends and receives data from the file create_account.php which is loaded from the play sub domain. For Dash to send and receive this data, you will want to edit your current play sub domain configuration, keep everything how it is but just add the following blocks:


       location /create_account/create_account.php {
            proxy_pass http://127.0.0.1:3000/create_account;
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /activation {
            proxy_pass http://127.0.0.1:3000/activation;
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

        location /avatar {
            proxy_pass http://127.0.0.1:3000/avatar;
            proxy_redirect off;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }

Edit config.py, if you wish to utilize the 'activate an account' feature, Dash will use SendGrid's API for that, which means you require a SendGrid API key in order to send mail to users who register. Just sign up and fetch one, add it to config.py as well as setting `Activation` to `true`.
