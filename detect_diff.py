import cv2
import time
from skimage.metrics import structural_similarity
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_email(subject, body, image_path):
    # Email configuration
    sender_email = "theftdetection1@gmail.com"
    sender_password = "xzivrwkcirddslea"
    receiver_email = "malekabouda12@gmail.com"

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    # Load the image
    with open(image_path, "rb") as file:
        image_data = file.read()

    # Attach the image to the email
    image = MIMEImage(image_data, name="Stolen_Image.png")
    message.attach(image)

    # Connect to the SMTP server and send the email
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)

def detect_diff(frame1, frame2):
    frame1 = frame1[1]
    frame2 = frame2[1]

    g1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)

    g1 = cv2.blur(g1, (2,2))
    g2 = cv2.blur(g2, (2,2))

    (score, diff) = structural_similarity(g2, g1, full=True)

    #print("Image similarity", score)

    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 100, 255, cv2.THRESH_BINARY_INV)[1]

    contors = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    contors = [c for c in contors if cv2.contourArea(c) > 50]

    if len(contors):
        for c in contors:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(frame1, (x,y), (x+w, y+h), (0,255,0), 2)    
    else:
        print("nothing stolen")
        return 0

    image_path = "Stolen/" + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".png"
    cv2.imwrite(image_path, frame1)

    # Send email with the subject "Stolen Alert" and the captured image
    send_email("Stolen Alert", "Stolen item detected.", image_path)

    return 1
