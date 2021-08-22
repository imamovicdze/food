## Start

You need to download or clone this repo using link below:

`git clone https://github.com/imamovicdze/food.git`

Then navigate to folder `food` and

`pipenv shell` and `pipenv install` or `pip install -r requirements.txt`

After installing dependencies go to mysql server and create database with name: `food`

Now run command:
`python` then `from app import db` and `db.create_all()`


Now run `flask run` and go on `http://127.0.0.1:5000/`


`food api.postman_collection.json` file import to postman and test routes

