
import tkinter as tk
import cv2
from PIL import Image, ImageTk
import os
import numpy as np
import cv2 
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten
from keras.layers import Conv2D
from keras.optimizers import Adam
from keras.layers import MaxPooling2D
from keras.preprocessing.image import ImageDataGenerator
import threading


emotion_model=Sequential()
emotion_model.add(Conv2D(32,kernel_size=(3,3),activation='relu',input_shape=(48,48,1)))
emotion_model.add(Conv2D(32,kernel_size=(3,3),activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2,2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Conv2D(128,kernel_size=(3,3),activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2,2)))
emotion_model.add(Conv2D(128,kernel_size=(3,3),activation='relu'))
emotion_model.add(MaxPooling2D(pool_size=(2,2)))
emotion_model.add(Dropout(0.25))
emotion_model.add(Flatten())
emotion_model.add(Dense(1024,activation='relu'))
emotion_model.add(Dropout(0.5))
emotion_model.add(Dense(7,activation='softmax'))
emotion_model.load_weights('C:/Users/veera/OneDrive/Desktop/mini-project/src/model.h5')
cv2.ocl.setUseOpenCL(False)

emotion_dict={0:'Angry',1:'Disgusted',2:'Fearful',3:'Happy',4:'Neutral',5:'Sad',6:'Surprise'}

emoji_dist={0:'angry.png',
            1:"disgusted.png",
            2:"fearful.png",
            3:"happy.png",
            4:"neutral.png",
            5:"sad.png",
            6:"surprised.png"}

global last_frame1
last_frame1=np.zeros((480,640,3),dtype=np.uint8)
global cap1
show_text=[0]
global frame_number

def show_subject():
    cap1=cv2.VideoCapture(0)
    if not cap1.isOpened():
        print("Can't open the Camera")
    global frame_number
    length=int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_number+=1
    if frame_number>=length:
        exit()
    cap1.set(1,frame_number)
    flag1,frame1=cap1.read()
    frame1=cv2.resize(frame1,(600,500))
    bounding_box=cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    gray_frame=cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    num_faces=bounding_box.detectMultiScale(gray_frame,scaleFactor=1.3,minNeighbors=5)
    for (x,y,w,h) in num_faces:
        cv2.rectangle(frame1,(x,y-50),(x+w,y+h+10),(255,0,0),2)
        roi_gray_frame=gray_frame[y:y+h,x:x+w]
        cropped_img=np.expand_dims(np.expand_dims(cv2.resize(roi_gray_frame,(48,48)),-1),0)
        prediction=emotion_model.predict(cropped_img)
        maxindex=int(np.argmax(prediction))
        cv2.putText(frame1,emotion_dict[maxindex],(x+20,y-60),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),2,cv2.LINE_AA)
        show_text[0]=maxindex
    if flag1 is None:
        print("Major Error")
    elif flag1:
        global last_frame1
        last_frame1=frame1.copy()
        pic=cv2.cvtColor(last_frame1,cv2.COLOR_BGR2RGB)
        img=Image.fromarray(pic)
        imgtk=ImageTk.PhotoImage(image=img)
        lmain.imgtk=imgtk # type: ignore
        lmain.configure(image=imgtk)
        root.update()
        lmain.after(10,show_subject)
    if cv2.waitKey(1) & 0xFF==ord('q'):
        exit()

def show_avatar():
    frame2=cv2.imread(emoji_dist[show_text[0]])
    pic2=cv2.cvtColor(frame2,cv2.COLOR_BGR2RGB)
    img2=Image.fromarray(pic2)
    imgtk2=ImageTk.PhotoImage(image=img2)
    lmain2.imgtk2=imgtk2 # type: ignore
    lmain3.configure(text=emotion_dict[show_text[0]],font=('arial',45,'bold'))
    lmain2.configure(image=imgtk2)
    root.update()
    lmain2.after(10,show_avatar)



if __name__=='__main__':
    frame_number=0
    root=tk.Tk()
    lmain=tk.Label(master=root,padx=50,bd=10)
    lmain2=tk.Label(master=root,bd=10)
    lmain3=tk.Label(master=root,bd=10,fg="#CDCDCD",bg='black')
    lmain.pack(side=tk.LEFT) #video
    lmain.place(x=700,y=150)
    lmain3.pack()
    lmain2.pack(side=tk.RIGHT) #avatar
    lmain2.place(x=100,y=150)

    root.title("Face to Emoji")
    root.geometry("1400x900+100+10")
    root['bg']='black'
    exitButton=tk.Button(root,text='Quit',fg='red',command=root.destroy,font=('arial',25,'bold')).pack(side=tk.BOTTOM)
    threading.Thread(target=show_subject).start()
    threading.Thread(target=show_avatar).start()
    root.mainloop()
