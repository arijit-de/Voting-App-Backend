# Voting App Backend

This Repository will serve as the backend for the Repository:https://github.com/themagedigest/votingapp

**Note : This is just a prototype and is not intended for production purpose.**

Follow the below steps for installing repository and starting the server.

* Install the Database and Table
  * ```mysql -u yourusername -p yourpassword yourdatabase < table.sql```
* Install Python3
  * Python3 can be installed from here: https://www.python.org/downloads/. Choose your preffered OS and install.
* Install PIP
  * ```python3 -m pip install --user --upgrade pip```
  * Verify the installation using ```python3 -m pip --version```
* Virtual Environment
  * Installation : ```python3 -m pip install --user virtualenv```
  * Create : ```python3 -m venv env```
  * Activate : ```source env/bin/activate```
  * Deactivate : ```deactivate```
* Go to the preferred location and activate the virtual environment
* Install the various library used for this repository
  * ```python3 -m pip install --user flask  flask-jsonpify flask-sqlalchemy flask-restful flask-api flask-mysql pymysql```
* Lastly, start server using ```python3 api.py```. Default port is 3000. If you want you can change it from api.py.
