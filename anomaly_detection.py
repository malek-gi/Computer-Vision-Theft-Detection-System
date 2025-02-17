import cv2
import numpy as np
import time
from datetime import datetime
import sqlite3
from detect_diff import detect_diff

faceDetect = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
rec = cv2.face.LBPHFaceRecognizer_create()
rec.read("recognizer/malek.yml")

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
conn = sqlite3.connect('test.db')
c = conn.cursor()

ID = ""
should_restart = False  # Added variable to control loop restart
is_recording = False  # Added variable to track recording state
current_recording = None  # Added variable to store the current recording

while True:
    motion_detected = False
    is_start_done = False

    cap = cv2.VideoCapture(0)

    check = []

    frame1 = cap.read()

    _, frm1 = cap.read()
    frm1 = cv2.cvtColor(frm1, cv2.COLOR_BGR2GRAY)

    if is_recording:
        current_recording.write(frame1)

    while True:
        _, frm2c = cap.read()
        if frm1 is not None:
            frm2 = cv2.cvtColor(frm2c, cv2.COLOR_BGR2GRAY)

            faces = faceDetect.detectMultiScale(frm2, 1.3, 5)

            for (x, y, w, h) in faces:
                id, comf = rec.predict(frm2[y:y + h, x:x + w])
                if comf >= 70:

                    if id in liste:
                        cv2.rectangle(frm2c, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        ID = id
                    else:
                        cv2.rectangle(frm2c, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        ID = "inconnu"

                print(ID)

                # display ID and confidence level on the image
                cv2.putText(frm2c, str(ID), (x, y + 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                cv2.putText(frm2c, str(comf), (x, y + h), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

            if ID == "inconnu":
                if frm1 is not None:
                    frm1_resized = cv2.resize(frm1, (frm2.shape[1], frm2.shape[0]))
                    diff = cv2.absdiff(frm1, frm2)

                    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

                    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]

                    contours = [c for c in contours if cv2.contourArea(c) > 25]

                    if len(contours) > 5:
                        cv2.putText(frm2c, "motion detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 2)
                        motion_detected = True
                        is_start_done = False

                    elif motion_detected and len(contours) < 3:
                        if not is_start_done:
                            start = time.time()
                            is_start_done = True
                            end = time.time()

                        end = time.time()

                        #print(end - start)
                        if (end - start) > 4:
                            frame2 = cap.read()
                            cap.release()
                            cv2.destroyAllWindows()
                            x = detect_diff(frame1, frame2)
                            if x == 0:
                                print("Continue")
                                should_restart = True  # Set to True to restart the loop
                                if is_recording:
                                    current_recording.release()
                                    is_recording = False
                                    current_recording = None
                            else:
                                print("Theft Detection Trigger Alert")
                                should_restart = True  # Set to True to restart the loop
                                if is_recording:
                                    current_recording.release()
                                    is_recording = False
                                    current_recording = None

                    else:
                        cv2.putText(frm2c, "no motion detected", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                    (0, 255, 0), 2)

                    # display the image
                    cv2.imshow('reconnaissance faciale', frm2c)

                    if is_recording:
                        current_recording.write(frm2c)

                    _, frm1 = cap.read()

                    if frm1 is not None:
                        frm1 = cv2.cvtColor(frm1, cv2.COLOR_BGR2GRAY)

        if should_restart:
            break  # Break the inner loop and restart the outer loop

        if cv2.waitKey(1) == ord('q'):
            break

        if motion_detected and not is_recording:
            # Start a new recording
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            filename = f'recordings/{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi'
            current_recording = cv2.VideoWriter(filename, fourcc, 20.0, (640, 480))
            is_recording = True

    if should_restart:
        should_restart = False  # Reset the variable for the next iteration
        continue  # Skip the rest of the code and restart the outer loop

    if cv2.getWindowProperty('reconnaissance faciale', cv2.WND_PROP_VISIBLE) < 1:
        break

cap.release()
if current_recording is not None:
    current_recording.release()
cv2.destroyAllWindows()
