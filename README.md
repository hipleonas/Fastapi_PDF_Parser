# Fastapi_PDF_Parser

The goal of this project is to utilize fastapi and pdf parser

# Setup the Repository

Create your folder Example: fastapi-pdf-parser
Then create a virtual env

python3 -m venv venv
source venv/bin/activate

Install the necessary packages

pip install fastapi uvicorn python-multipart PyPDF2
pip install "docling[pdf]"

## Deploying the app on Heroku

### Step 1: Install Heroku on your environment

+ In the scope of this project, Heroku will be installed on WSL/Ubuntu using the command

+ Install Heroku: ```curl https://cli-assets.heroku.com/install-ubuntu.sh | sh```

+ After the installation is completed, check the version: ```heroku --version```

+ If we see the notification such as ```heroku/7.XX.X linux-x64 node-v14.X.X```, it means we have successfully installed Heroku on WSL, For my case it is ```heroku/10.12.0 wsl-x64 node-v20.19.1```

### Step 2: Create the app

+ Create the app on heroku ```heroku create pdf-parser```

+ Configuration setup ```heroku config:set BEARERE_TOKEN = your_own_secret_key```

+ Pushing it onto main: ```git push heroku main```




