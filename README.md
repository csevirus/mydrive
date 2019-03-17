# mydrive
# About :
A system allowing verified users to upload sensitive data in the form of large files
# How to use:
You must have Flask installed in your computer.
- **step 1** : clone or download zip of this project.
- **step 2** : open project directory and execute following command "pip install -e"
- **step 3** : You can manage project’s dependencies. "pip install mydrive.whl" installs them.
- **step 4** : To initialise the database use "flask init-db"
- **step 5** : To run application "flask run"
- **step 6** : you must change these variables according to your requirements in **myfiles.py**
  - ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) 
  - UPLOAD_FOLDER = "/home/csevirus/project/mydrive/uploads"
  - DOMAIN_NAME = "http://127.0.0.1:5000"
