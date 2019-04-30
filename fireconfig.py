import pyrebase

def firebaseconfig():
    config = {
        "apiKey": "AIzaSyCOvQ_-SJdIKR2kxF897Uoq80TTAJGKHEM",
        "authDomain": "my-project-cnn1221.firebaseapp.com",
        "databaseURL": "https://my-project-cnn1221.firebaseio.com",
        "projectId": "my-project-cnn1221",
        "storageBucket": "my-project-cnn1221.appspot.com",
        "messagingSenderId": "672701644743"
    }
    
    firebase = pyrebase.initialize_app(config)
    
    return firebase.storage()
    
