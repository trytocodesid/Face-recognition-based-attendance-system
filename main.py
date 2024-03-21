import sys
import time
import pyttsx3
import self as self
import winsound
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
from PIL import Image
import mysql.connector
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders
import smtplib,ssl
import pickle
import ctypes
import twilio
from twilio.rest import Client

#step4
window = tk.Tk()
window.title("Face Recognition System")
# window.config(background="lime")
#window.iconbitmap("F:\\PYTHON\\face_recognition_final\\face_recognition.ico")

l1 = tk.Label(window, text="NAME", font=("times new roman", 20))
l1.place(x=20,y=20)
t1 = tk.Entry(window, width=50, bd=5)
t1.place(x=198,y=24)

l2 = tk.Label(window, text="CLASS", font=("times new roman", 20))
l2.place(x=20,y=62)
t2 = tk.Entry(window, width=50, bd=5)
t2.place(x=198,y=67)

l3 = tk.Label(window, text="PHONE_NO", font=("times new roman", 20))
l3.place(x=20,y=104)
t3 = tk.Entry(window, width=50, bd=5)
t3.place(x=198,y=110)

l4 = tk.Label(window, text="ID", font=("times new roman", 20))
l4.place(x=20,y=146)
t4 = tk.Entry(window, width=50, bd=5)
t4.place(x=198,y=153)

def capture_photo():
    if t1.get() == "" or t2.get() == "" or t3.get() == "" or t4.get() == "":
        messagebox.showinfo('Result', 'Please provide complete details of the user')
    else:
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="",
            database="face"
        )
        mycursor = mydb.cursor()
        mycursor.execute("SELECT * from attendance")
        myresult = mycursor.fetchall()
        id = 1
        for x in myresult:
            id += 1
        sql = "insert into attendance(NAME,CLASS,PHONE_NO,ID) values(%s,%s,%s,%s)"
        val = (t1.get(), t2.get(), t3.get(),t4.get())
        mycursor.execute(sql, val)
        mydb.commit()

    cam = cv2.VideoCapture(0)
    img_counter = 0
    id = t4.get()
    while True:
        ret, img = cam.read()
        cv2.imshow("Test",img)
        if not ret:
            print("failed to grab frame")
            break
        k = cv2.waitKey(1)

        if k%256 ==27:
            sys.exit(1)
            print("Escape hit,closing the app")
        elif k%256 ==32:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="",
                database="face"
            )
            mycursor = mydb.cursor()
            mycursor.execute("select NAME from attendance where id=" + str(id))
            s = mycursor.fetchone()
            s = '' + ''.join(s)



            print("Image"+str(img_counter)+"Saved")
            file = 'D:/Mini Project Ours/final/ImagesAttendance/'+str(s)+'.jpg'
            cv2.imwrite(file,img)
            print("screenshot taken")
            img_counter+=1
    cam.release()
    cam.destroyAllWindows()

b1=tk.Button(window,text="CAPTURE PHOTO",font=("times new roman",20),bg='orange',fg='red',command=capture_photo)
b1.place(x=5,y=200)


#CLEAR FUNCTION
def clear():
    l10.destroy()
    l12.destroy()
    l14.destroy()
    return


def clock_in():
    # text to speech
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')
    print(rate)
    engine.setProperty('rate', 115)

    path = 'D:/Mini Project Ours/final/ImagesAttendance'
    images = []
    classNames = []
    mylist = os.listdir(path)
    print(mylist)
    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
        print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('Clock_In.csv', 'r+') as f:
            myDateList = f.readlines()
            nameList = []
            for line in myDateList:
                entry = line.split(',')
                nameList.append(entry[0])


            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                dtString1 = now.strftime('%d/%m/%y')
                f.writelines(f'\n{name},{dtString},{dtString1}')
                print(name)

###################################################################
                try:

                    mydb = mysql.connector.connect(
                        host="localhost",
                        user="root",
                        passwd="",
                        database="face"
                    )
                    mycursor = mydb.cursor()
                    mycursor.execute("select PHONE_NO from attendance where name = %s", (name,))
                    phone_number = mycursor.fetchone()
                    print(phone_number)

                except Exception as e:
                    print(e)
######################################################################
                #sms part

                try:

                    account_sid = "AC0b4e1b6a3ded368a403e75e4d6f6db29"
                    auth_token = "ddc6283084397df3ee2675badd80d9b6"

                    client = Client(account_sid, auth_token)

                    message = client.messages.create(
                        body=" Your Attendance has been taken ",
                        from_="+919448059770",
                        to=phone_number
                    )

                    print(message.sid)
                    print("message sent")
                except Exception as f:
                    print(f)



    #############################################################

    encodeListKnown = findEncodings(images)
    print('encoding complete')

    cap = cv2.VideoCapture(0)


    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                # winsound.PlaySound('sample1.mp3',winsound.SND_ASYNC)
                markAttendance(name)
                engine.say(name)
                engine.say('   your     attendance      is     marked    ')
                engine.runAndWait()

        cv2.imshow('webcam', img)
        k = cv2.waitKey(1)

        if k%256 == 27:
            sys.exit(1)
            print("Escape hit,closing the app")
            cv2.destroyAllWindows()


b2 = tk.Button(window, text="CLOCK IN", font=("times new roman",20), bg="green", fg="orange",command=clock_in)
b2.place(x=313,y=200)

def clock_in_details():
    os.startfile("D:\Mini Project Ours/final/Clock_In.csv")


b3 = tk.Button(window, text=" CLOCK IN DETAILS  ", font=("times new roman",13), bg="pink", fg="black",command=clock_in_details)
b3.place(x=525,y=63)

def clock_out_details():
    os.startfile("D:\Mini Project Ours/finalClock_Out.csv")


b3 = tk.Button(window, text="CLOCK OUT DETAILS", font=("times new roman",13), bg="pink", fg="black",command=clock_out_details)
b3.place(x=522,y=108)

def clock_out():
    # text to speech
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    rate = engine.getProperty('rate')
    print(rate)
    engine.setProperty('rate', 115)

    path = 'ImagesAttendance'
    images = []
    classNames = []
    mylist = os.listdir(path)
    print(mylist)
    for cl in mylist:
        curImg = cv2.imread(f'{path}/{cl}')
        images.append(curImg)
        classNames.append(os.path.splitext(cl)[0])
        print(classNames)

    def findEncodings(images):
        encodeList = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            encodeList.append(encode)
        return encodeList

    def markAttendance(name):
        with open('Clock_Out.csv', 'r+') as f:
            myDateList = f.readlines()
            nameList = []
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            dtString1 = now.strftime("%d/%m/%y")
            for line in myDateList:
                entry = line.split(',')
                nameList.append(entry[0])

            if name not in nameList:

                f.writelines(f'\n{name},{dtString},{dtString1}')


    encodeListKnown = findEncodings(images)
    print('encoding complete')

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        facesCurFrame = face_recognition.face_locations(imgS)
        encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

        for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print(faceDis)
            matchIndex = np.argmin(faceDis)

            if matches[matchIndex]:
                name = classNames[matchIndex].upper()
                # print(name)
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
                # winsound.PlaySound('sample1.mp3',winsound.SND_ASYNC)
                markAttendance(name)
                engine.say(name)
                engine.say('  Thank you have a good day...    ')
                engine.runAndWait()

        cv2.imshow('webcam', img)
        k = cv2.waitKey(1)

        if k%256 == 27:
            sys.exit(1)
            print("Escape hit,closing the app")
            cv2.destroyAllWindows()


b4 = tk.Button(window, text="CLOCK OUT", font=("times new roman",20), bg="red", fg="black",command=clock_out)
b4.place(x=530,y=200)

#####################################

def clock_in_file():



    fromaddr = "facerecognitionwithattendances@gmail.com"
    toaddr = t5.get()

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "mail send from pythonl"

    # string to store the body of the mail
    body = "Body_of_the_mail"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "Clock_In.csv"
    attachment = open("Clock_In.csv", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "wqqs vmsb nmce rpsu")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    l12.config(text='Clock-In File sent to your email address.!')
    print('mail sent')

l12 = tk.Label(window, fg='green', font=('Arial', 14))
l12.place(x=30, y=425)

b5 = tk.Button(window, text=" Clock  In  File", font=("times new roman",13), bg="blue", fg="white",command=clock_in_file)
b5.place(x=570,y=270)

####################################
def clock_out_file():

    fromaddr = "facerecognitionwithattendances@gmail.com"
    toaddr = t5.get()

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "mail send from pythonl"

    # string to store the body of the mail
    body = "Body_of_the_mail"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "Clock_Out.csv"
    attachment = open("Clock_Out.csv", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "wqqs vmsb nmce rpsu")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    seconds = int(3)
    l10.config(text='Clock-Out File sent to your email address.!')
    print('mail sent')

    # terminating the session
    #s.quit()
l10=tk.Label(window,fg='green',font=('Arial',14))
l10.place(x=30,y=425)

l5 = tk.Label(window, text="E-Mail :", font=("times new roman", 20))
l5.place(x=30,y=290)
t5 = tk.Entry(window, width=50, bd=5)
t5.place(x=230,y=295)

#l11 = tk.Label(window, text="OUTPUT : ",fg="brown",font=("times new roman",20))
#l11.place(x=20,y=390)

#b11 = tk.Button(window,text="Clear",fg="blue",bg="brown",font=("times new roman",10),command=clear)
#b11.place(x=170,y=395)

b6 = tk.Button(window, text="Clock Out File", font=("times new roman",13), bg="blue", fg="white",command=clock_out_file)
b6.place(x=569,y=313)

#l7 = tk.Label(window, text="Send database via mail", font=("times new roman", 20))
#l7.place(x=255,y=330)

def send():
    # sms part
    try:
        msg = t13.get()
        account_sid = "AC0b4e1b6a3ded368a403e75e4d6f6db29"
        auth_token = "ddc6283084397df3ee2675badd80d9b6"

        client = Client(account_sid, auth_token)

        message = client.messages.create(
            body=msg,
            from_="+919448059770",
            to=""
        )

        print(message.sid)
        l14.config(text='Thank you,your report has been sent to Developer.!')
        print("message sent")
    except Exception as f:
        print(f)


l14 = tk.Label(window,fg='green',font=('Arial',13))
l14.place(x=13,y=425)
l13 = tk.Label(window, text="REPORT",fg="red", font=("times new roman", 20))
l13.place(x=430,y=350)
t13 = tk.Entry(window, width=40, bd=5)
t13.place(x=350,y=400)
b13 = tk.Button(window,text=" Send ",bg="black",fg="white",command=send)
b13.place(x=625,y=400)


window.geometry("717x450")
window.mainloop()


