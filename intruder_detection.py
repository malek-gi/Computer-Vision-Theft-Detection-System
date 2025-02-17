import cv2
import numpy as np
import time
import sqlite3
import subprocess

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/malek.yml")
cam_laptop = cv2.VideoCapture(0)
cam_iriun = cv2.VideoCapture(1)      
# Connexion à la base de données
con = sqlite3.connect('mydatabase_copy.db')

# Création d'un curseur pour exécuter des requêtes SQL
cur = con.cursor()

# Exécution d'une requête SQL pour récupérer les données d'une colonne
cur.execute("SELECT id FROM Employees ")

# Récupération de toutes les données de la colonne sous forme de liste
liste = [row[0] for row in cur.fetchall()]
print(liste)
# Fermeture du curseur et de la connexion à la base de données
cur.close()
con.close()

# connect to the database
conn = sqlite3.connect('testy.db')
c = conn.cursor()

ID=""

output = subprocess.check_output(['tasklist']).decode('Windows-1252')
if 'IriunWebcam.exe' in output:
    use_iriun = True
    cam = cam_iriun
    print("Using Iriun webcam")
else:
    use_iriun = False
    cam = cam_laptop
    print("Iriun app is not running, using laptop camera")


# Check if the camera was successfully opened
if not cam.isOpened():
    print("No webcam found")
    exit()


while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceDetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        id, comf = rec.predict(gray[y:y+h, x:x+w])
        if comf <= 70:
                
            if id in liste:
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                ID = id
        else:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)
            ID = "inconnu"
                
        print(ID)
        # check if a table for this person already exists
        table_name = f"person_{ID}"
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
        table_exists = c.fetchone()
            
        if table_exists:
            # table already exists, add a new row with the current time
            current_time = time.ctime()
            if cam == cam_laptop:
                c.execute(f"INSERT INTO {table_name} (ID, Entry) VALUES (?, ?)", (ID, current_time))
            else:
                c.execute(f"INSERT INTO {table_name} (ID, Exit) VALUES (?, ?)", (ID, current_time))
        else:
            # table does not exist, create a new table with ID and time columns
            c.execute(f"CREATE TABLE {table_name} (ID text, Entry text, Exit text)")
            current_time = time.ctime()
            if cam == cam_laptop:
                c.execute(f"INSERT INTO {table_name} (ID, Entry) VALUES (?, ?)", (ID, current_time))
            else:
                c.execute(f"INSERT INTO {table_name} (ID, Exit) VALUES (?, ?)", (ID, current_time))
            
        # commit changes to the database
        conn.commit()

        # display ID and confidence level on the image
        cv2.putText(img, str(ID), (x, y+2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
        cv2.putText(img, str(comf), (x, y+h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

    # display the image
    cv2.imshow('reconnaissance faciale', img)

    # exit if 'q' is pressed
    if cv2.waitKey(1) == ord('q'):
        break

# release the camera and close all windows
cam.release()
cv2.destroyAllWindows()

# close the database connection
conn.close()
