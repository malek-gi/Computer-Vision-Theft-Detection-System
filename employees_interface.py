from tkinter import*
import sqlite3
from tkinter import ttk
import numpy as np
import cv2
from PIL import Image
import os
from tkinter import messagebox

root = Tk()
root.geometry("700x600")

def createData():
    # récupération des données du formulaire
    id = entryID.get()
    first_name = entryFirstName.get()
    last_name = entryLastName.get()
    CIN = entryCIN.get()
    
    entryID.delete(0, END)
    entryFirstName.delete(0, END)
    entryLastName.delete(0, END)
    entryCIN.delete(0, END)
    
    conn = sqlite3.connect('mydatabase_copy.db')
    cur = conn.cursor()
    req1 = "CREATE TABLE IF NOT EXISTS Employees(id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, CIN INTEGER NOT NULL UNIQUE)"
    cur.execute(req1)    
    req2 = "INSERT INTO Employees (id, first_name, last_name, CIN) values (?, ?, ?, ?)"
    cur.execute(req2 , (id, first_name, last_name, CIN))
    conn.commit()
    #conn.close()
    
    # refresh the table to display the new data
    tree.delete(*tree.get_children())
    select = cur.execute("select * from Employees")
    for row in select:
        tree.insert('', END, values=row)
    
    conn.close()
    faceDetect=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0)
    sampleNum=0
    while(True):
        ret,img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,0,255),2)
            sampleNum=sampleNum+1
            cv2.imwrite("dataset/User."+str(id)+'.'+str(sampleNum)+".png", gray[y:y+h,x:x+w])
            cv2.waitKey(100)
        cv2.imshow('reconnaissance faciale', img)
        cv2.waitKey(100)
        if(sampleNum>30):
            break
    cam.release()
    cv2.destroyAllWindows()

validated = False

def validate():
    global validated
    #train the model 
    recognizer=cv2.face.LBPHFaceRecognizer_create()
    path='dataset'
    def getImagesWithID(path) :
        imagepaths=[os.path.join(path,f) for f in os.listdir(path)]
        faces=[]
        IDs=[]
        for imagepath in imagepaths :
            faceImg=Image.open(imagepath).convert('L')
            faceNp=np.array(faceImg,'uint8')
            ID=int(os.path.split(imagepath)[-1].split('.')[1])
            faces.append(faceNp)
            print(ID)
            IDs.append(ID)
            cv2.imshow('training',faceNp)
            cv2.waitKey(10)
        return IDs,faces
    IDs,faces=getImagesWithID(path)
    recognizer.train(faces,np.array(IDs))
    recognizer.save('recognizer/malek.yml')
    cv2.destroyAllWindows()
    validated = True
    root.destroy()

def on_closing():
    if not validated:
        messagebox.showwarning("Validation nécessaire", "Veuillez valider avant de quitter.")
    else:
        root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
    
 
#==============================
# create a form to insert data
#==============================
# Label & Entry for id
lblID = Label(root , text = "id : ")
lblID.place(x = 10 , y = 10)
entryID = Entry(root )
entryID.place(x = 100 , y = 10 , width = 200)
 
# Label & Entry first_name
lblFirstName = Label(root , text = "first_name")
lblFirstName.place( x = 10 , y = 40 ) 
entryFirstName = Entry(root)
entryFirstName.place( x = 100 , y = 40 , width = 200)

# Label & Entry last_name
lblLastName = Label(root , text = "last_name")
lblLastName.place( x = 10 , y = 70 ) 
entryLastName = Entry(root)
entryLastName.place( x = 100 , y = 70 , width = 200)
 
# Label & Entry CIN
lblCIN = Label(root , text = "CIN")
lblCIN.place( x = 10 , y = 100 ) 
entryCIN = Entry(root)
entryCIN.place( x = 100 , y = 100 , width = 200)

# Button Photo
btnPhoto = Button(root , text = "Photo" , command = createData)
btnPhoto.place(x = 100 , y = 130, width = 200 , height = 25)

# Button Validate
btnValidate = Button(root , text = "Validate" , command = validate)
btnValidate.place(x = 400 , y = 50, width = 200 , height = 25)



#==============================
# display Data
#==============================

# Créer le Scrollbar
scrollbar = Scrollbar(root, orient=VERTICAL)

# Créer la Treeview avec yscrollcommand lié au Scrollbar
tree = ttk.Treeview(root, columns = (1,2,3,4), height = 10, show = "headings", yscrollcommand=scrollbar.set)

# Configurer le Scrollbar pour faire défiler la Treeview
scrollbar.config(command=tree.yview)

# Placer la Treeview et le Scrollbar dans la fenêtre
tree.place(x = 50, y = 170, width = 600 , height = 300)
scrollbar.place(x=650, y=170, height=300)

tree.heading(1, text = "id")
tree.heading(2, text = "first_name")
tree.heading(3, text = "last_name")
tree.heading(4, text = "CIN")

tree.column(1, width = 50)
tree.column(2, width = 100)
tree.column(3, width = 100)
tree.column(4, width = 100)


conn = sqlite3.connect('mydatabase.db')
cur = conn.cursor()
req = "CREATE TABLE IF NOT EXISTS Employees(id INTEGER PRIMARY KEY AUTOINCREMENT, first_name TEXT NOT NULL, last_name TEXT NOT NULL, CIN INTEGER NOT NULL UNIQUE)"
cur.execute(req)

select = cur.execute("select * from Employees")
for row in select:
    tree.insert('' , END, values = row)

root.mainloop()
