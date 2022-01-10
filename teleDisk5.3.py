from tkinter import *
from tkinter import messagebox as msgbox
from tkinter import ttk
from tkinter import simpledialog
import tkinter.filedialog as fd
import tkinter as tk

import os,io
import sys,copy,time,uuid
from datetime import datetime

from PIL import Image, ImageTk
from telethon import TelegramClient, events, functions, types
from FastTelethon import download_file, upload_file
import random
import threading, multiprocessing
import asyncio
import math
import nest_asyncio
nest_asyncio.apply()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

maxS = 1920 # If you increase this size, the file will be divided into parts, a maximum of 2048Mb
readS = 1024 # Part size
limit = None # Maximum number of messages to be uploaded
photoPreload = False
downloadPath = 'download/'

cliId = 1231231
cliHash = 'abc1abc2abc3abc4abc5'

sem=0
qq=''
lock=False

try:
    os.mkdir('./download')
except:
    pass

async def createFolder(name):
    print("папка: ",name)
    async with TelegramClient('myuser', cliId, cliHash) as clientM:
        await clientM.send_file(curDisk, b'abc',caption=qq+'/'+name+'/' if qq else name+'/',attributes=[types.DocumentAttributeFilename('FOLDER')])
            
async def createChat(name):
        async with TelegramClient('myuser', cliId, cliHash) as clientM:
            result = await clientM(functions.messages.CreateChatRequest(
                users=['me','ablakotics'], # to create a group, you need at least 2 participants
                title='|'+name+'|'
            ))

            avv = await clientM.get_entity('|'+name+'|')
            
            await client(EditBannedRequest(avv, 'ablakotics', ChannelBannedRights(
                until_date=None,
                view_messages=True
            ))) # removing an extra participant
            
            await clientM(functions.messages.EditChatDefaultBannedRightsRequest(avv,types.ChatBannedRights(
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True,
                send_polls=True,
                change_info=True,
                invite_users=True,
                pin_messages=True,
                until_date=None
                )))

def getFolders():
    hj = {}
    with TelegramClient('myuser', cliId, cliHash,loop=loop) as clientM:
        for dialog in clientM.iter_dialogs(ignore_migrated=True,):
                try:
                    if (dialog.title[:1] == '|' and dialog.title[-1:] == '|'):
                        yield [str(dialog.title), dialog]
                except:
                    pass 

async def mainD(path,file,revrite=True,open_=True,size1=0,open2_=True):
    if(1==1):
        if(revrite==True):
            global nW, spin_box,label,label2,label3
            nW = tk.Toplevel(win)

            nW.title('Downloading...')
            nW.geometry('300x90')
            label= tk.Label(nW,text= "0% complete",anchor=W)
            label3= tk.Label(nW,text= "")
            spin_box= ttk.Progressbar(nW,orient="horizontal",mode="determinate",maximum=size1,length=280)
            label2= tk.Label(nW,text= "")

            label.place(x=10, y=10)
            label3.place(x=215, y=10)
            spin_box.place(x=10, y=35)
            label2.place(x=10, y=60)
            
    def progress_bar(current, total):
        global start_time
        if('start_time' not in globals()):
            start_time = time.time()
        if(time.time() - start_time >= 1):
            start_time = time.time()
            spin_box['maximum'] = total if size1 == 0 else size1
            spin_box['value'] = current
            label['text'] = str(round((current / (total if size1 == 0 else size1)) * 100,1))+'% complete'
            label2['text'] = str(round(current/(2**20),2))+'Mb of '+str(round((total if size1 == 0 else size1)/(2**20),2))+'Mb'

    async with TelegramClient('myuser1', cliId, cliHash) as clientN:
        print('Dpath: ',path)
        with open(path, "wb" if revrite else "ab") as out:
            t = await download_file(clientN, file.media.document, out, progress_callback=progress_bar)
            
            Npath=str(os.getcwd())+'\\'+path.replace('/','\\')
            #print(Npath)
            if os.path.isfile(Npath) and open_ and open2_:
                print('run: ',Npath)
                os.startfile(Npath)
    if(open_==True):
        nW.destroy()
    print('holla')

def addToDwldBig(file, B,open2_=True):
    global sem
    while(sem == 1):
        time.sleep(1)
    sem=1
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    if(B==1):
        try:
            threading.Thread(target=asyncio.run(mainD(downloadPath+str(file.message.replace("~","") if file.message else (file.media.document.attributes[-1].file_name if type(file.media) != types.MessageMediaPhoto else 'Photo.jpg')),file,open2_=open2_))).start()
        except:
            print(type(file.media))#file.stringify())
    elif(B==2):
        for i in range(1,len(file[1])):
            thread = threading.Thread(target=asyncio.run(mainD(downloadPath+file[0],file[1][str(i)],True if i==1 else False,open_= True if i == len(file[1])-1 else False,size1=file[2],open2_=open2_))).start()
    elif(B==3):
        uo = 1
        label= tk.Label(win,text= str(uo),anchor=W)
        label.place(x=10, y=527)
        
        for i in file:
            label['text'] = str(uo)+' of '+str(len(file))
            uo=uo+1
            #global win
            
            try:
                os.makedirs(downloadPath+i.message.rpartition('/')[0])
            except: pass
            if type(i) != dict:
                thread = threading.Thread(target=asyncio.run(mainD(downloadPath+i.message,i,open2_=open2_))).start()
            else:
                for ii in range(1,len(i)):
                    thread = threading.Thread(target=asyncio.run(mainD(downloadPath+i[str(ii)].message.rpartition('._part_')[0],i[str(ii)],
                    True if ii==1 else False,open_= True if ii == len(i)-1 else False,size1=i['size'],open2_=open2_))).start()
        label.destroy()
    sem = 0

async def FolderToFiles(q,folder):
    async with TelegramClient('myuser1', cliId, cliHash) as clientM:
        abc = await clientM.get_entity(folder)
        jojo=[]
        listo={}
        
        async for dia in clientM.iter_messages(abc,limit=limit,search=q):
            #print('q: ',q)
            if(dia.message.partition(q)[2].partition('/')[0] != '' or (dia.media == None) or (q not in dia.message)):
                continue
            dia.message = q.rpartition('/')[2]+dia.message.partition(q)[2]

            try:
                if dia.media.document.attributes[-1].file_name == "FOLDER":
                    continue
            except: pass

            if('_part_' in dia.message.rpartition('.')[2]):
                if(dia.message.rpartition('.')[0] not in listo):
                    listo[dia.message.rpartition('.')[0]] = {'size':0}
                listo[dia.message.rpartition('.')[0]][dia.message.rpartition('._part_(')[2][:-1].split('-')[0]] = dia
                listo[dia.message.rpartition('.')[0]]['size'] = listo[dia.message.rpartition('.')[0]]['size'] + dia.media.document.size

            else:         
                jojo.append(dia)
                
        for i in listo:
            jojo.append(listo[i])
        return jojo
                
def addToDwld(type_,file,open2_=True):
    print('dwnld: ',file)
    
    if(type_ in ['us','photo','video']):
        file=file[0]
        threading.Thread(target=addToDwldBig,args=(file,1,open2_)).start()

    elif(type_=='big'):
        threading.Thread(target=addToDwldBig,args=(file,2,open2_)).start()

    elif(type_=='dir'):
        jojo = asyncio.run(FolderToFiles(file[0],file[1]))
        print(jojo)
        threading.Thread(target=addToDwldBig,args=(jojo,3,open2_)).start()

def reloader():
    while(1==1):
        win.update()
        time.sleep(1)

async def mainU(folder,file,io = False,size=None,name='',qq=''):
    if qq: qq=qq+'/'

    ye=False
    if((size if size else os.path.getsize(file)) >= 1024*1024*5):
        if(io==False or name.rpartition('_part_')[2][1:-1].split('-')[0] == '1'):
            ye=True
            global nW, spin_box,label,label2,label3
            nW = tk.Toplevel(win)

            nW.title('Uploading...')
            nW.geometry('300x90')
            label= tk.Label(nW,text= "0% complete",anchor=W)
            label3= tk.Label(nW,text= "")
            spin_box= ttk.Progressbar(nW,orient="horizontal",mode="determinate",maximum=size if size else os.path.getsize(file),length=280)
            label2= tk.Label(nW,text= "")

            label.place(x=10, y=10)
            label3.place(x=215, y=10)
            spin_box.place(x=10, y=35)
            label2.place(x=10, y=60)
            
    def progress_bar1(current, total):
        pass
    
    def progress_bar(current, total):
        global start_time
        if('start_time' not in globals()):
            start_time = time.time()
        if(time.time() - start_time >= 1):
            start_time = time.time()
            spin_box['maximum'] = total
            spin_box['value'] = current
            label['text'] = str(round((current / total) * 100,1))+'% complete'
            label2['text'] = str(round(current/(2**20),2))+'Mb of '+str(round(total/(2**20),2))+'Mb'
            if('._part_(' in name):
                label3['text'] = '' if name=='' else 'part '+name.rpartition('_part_')[2][1:-1].split('-')[0]+' of '+name.rpartition('_part_')[2][1:-1].split('-')[1]

    async with TelegramClient('myuser1', cliId, cliHash) as clientN:
        if io:
            a = await upload_file(clientN, file, progress_callback=progress_bar,size=size)
        else:
            with open(file, "rb") as out:
                a = await upload_file(clientN, out, progress_callback=progress_bar if ye else progress_bar1)
        if not qq:qq=''
        attributes=[types.DocumentAttributeFilename(name.rpartition("/")[2])] if name !='' else [types.DocumentAttributeFilename(str(file).rpartition("/")[2])]
        await clientN.send_file(folder, a,caption=qq+name if name !='' else qq+str(file).rpartition("/")[2],attributes=attributes)

        if((io == False or name.rpartition('_part_')[2][1:-1].split('-')[0] == name.rpartition('_part_')[2][1:-1].split('-')[1])):
            try:
                nW.destroy()
            except: pass
    print('holla')

def addToUpldBig(folder,file,self,qq=''):
    global sem
    while(sem == 1):
        time.sleep(1)
    sem=1
    
    for j in file:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if(os.path.isfile(j)):
            if(os.path.getsize(j) > 1024*1024*maxS):
                allP = math.ceil(os.path.getsize(j) / (1024*1024*readS))
                with open(j, "rb") as f:
                    byte = f.read(1024* 1024 * readS)
                    si = 1024* 1024 * readS
                    ii = 1
                    while(byte):
                        stream_str = io.BytesIO(byte)
                        thread = threading.Thread(target=asyncio.run(mainU(folder,stream_str,True,size =si,name=j.rpartition('/')[2]+'._part_('+str(ii)+'-'+str(allP)+')',qq=qq))).start()

                        byte = f.read(1024* 1024 * readS)
                        si=f.tell() - si*ii
                        ii=ii+1
            else:
                thread = threading.Thread(target=asyncio.run(mainU(folder,j,qq=qq))).start()
        if(os.path.isdir(j)):
            file_list = []
            
            uo = 1
            label= tk.Label(win,text= str(uo),anchor=W)
            label.place(x=10, y=527)
            
            for path, folders, files in os.walk(j):
                    for file in files:
                        label['text'] = str(uo)+' of '+str(sum(len(files) for _, _, files in os.walk(j)))
                        uo=uo+1
                        
                        NEnorm = os.path.join(path, file).replace('\\','/').replace(j.rpartition('/')[0],'')[1:]
                        norm = os.path.join(path, file).replace('\\','/')
                        
                        if(os.path.getsize(norm) > 1024*1024*maxS):
                            allP = math.ceil(os.path.getsize(norm) / (1024*1024*readS))
                            with open(norm, "rb") as f:
                                byte = f.read(1024* 1024 * readS)
                                si = 1024* 1024 * readS
                                ii = 1
                                while(byte):
                                    stream_str = io.BytesIO(byte)
                                    thread = threading.Thread(target=asyncio.run(mainU(folder,stream_str,True,size =si,name=NEnorm+'._part_('+str(ii)+'-'+str(allP)+')',qq=qq))).start()

                                    byte = f.read(1024* 1024 * readS)
                                    si=f.tell() - si*ii
                                    ii=ii+1                   
                        else:
                            thread = threading.Thread(target=asyncio.run(mainU(folder,norm,name=NEnorm,qq=qq))).start()
            label.destroy()

    asyncio.run(self.full_files(curDisk,qq))
    sem=0

def addToUpld(folder,file,self,qq=''):            
    thread = threading.Thread(target=addToUpldBig,args=(folder,file,self,qq)).start()

curDisk=''
glo=0

win=Tk()
win.title('TeleDisk')
win.iconphoto(True, PhotoImage(file='img\\app_icon.png'))

async def firstTime():
    while 1==1:
        client = TelegramClient('myuser', cliId, cliHash)
        await client.connect()
        
        if not await client.is_user_authorized():
            newname=simpledialog.askstring('Input phone nomber','Input phone nomber: ')
            if newname:
                nomb = await client.send_code_request(newname)
                newname2=simpledialog.askinteger('Input code','Input code: ')
                if newname2:
                    await client.sign_in(newname,newname2)
                    if await client.is_user_authorized():
                        await client.disconnect()
                        with open('myuser1.session','wb')as f:
                            with open('myuser.session','rb') as ff:
                                f.write(ff.read())
                        break
        else:
            await client.disconnect()
            break
asyncio.run(firstTime())

class FileFrame(Frame):
    def __init__(self,window=None,master=None,width=80,height=25):
        self.window=window

        self.sfl_dict={}
        ttk.Style().theme_use('vista')
        self._w=Frame(master)

        self.cmd_img=PhotoImage(file='img\\upload.png')
        self.cmd1_img=PhotoImage(file='img\\upload1.png')
        self.dir_img=PhotoImage(file='img\\dir.png')
        self.newdir_img=PhotoImage(file='img\\new_dir.png')
        self.desktop_img=PhotoImage(file='img\\desktop.png')
        self.documents_img=PhotoImage(file='img\\documents.png')
        self.images_img=PhotoImage(file='img\\images.png')
        self.videos_img=PhotoImage(file='img\\videos.png')
        self.drive_img=PhotoImage(file='img\\drives.png')
        self.drives_img=PhotoImage(file='img\\drives2.png')
        self.Adddrives_img=PhotoImage(file='img\\drives3.png')
        self.user_img=PhotoImage(file='img\\user.png')
        self.music_img=PhotoImage(file='img\\music.png')
        self.unselect_img=PhotoImage(file='img\\un-select.png')
        self.download_img=PhotoImage(file='img\\download.png')
        self.simplefilelist=ttk.Treeview(self._w,height=25)
        self.simplefilelist.grid(row=0,column=0,rowspan=4)
        self.full_libs()
        self.simplefilelist.bind('<Button-1>',self.click2)
        ttk.Button(self._w,text='Upload file',command=self.upld_start,image=self.cmd_img).grid(row=1,column=5)
        ttk.Button(self._w,text='Upload folder',command=self.upld1_start,image=self.cmd1_img).grid(row=2,column=5)
        ttk.Button(self._w,text='New folder',command=self.new_dir1,image=self.newdir_img).grid(row=3,column=5)
        self.img_lib=os.getcwd()+'\\img\\'
        self.filelistframe=Frame(self._w)
        self.filelistframe.grid(column=1,row=1,columnspan=3,rowspan=4)
        self.tk=master.tk
        self.listbox=ttk.Treeview(self.filelistframe,columns=("1n","2n",'3n'),height=25)
        self.listbox.heading("#0", text="             Name",anchor=W)
        self.listbox.heading("1n", text="Create date",anchor=W)
        self.listbox.heading("2n", text="type",anchor=W)
        self.listbox.heading("3n", text="Size",anchor=W)
        self.listbox.pack(side=LEFT)
        scrolly = Scrollbar(self.filelistframe)
        self.listbox.config(yscrollcommand=scrolly.set)
        scrolly.pack(side=RIGHT,fill=Y)
        scrolly.config(command=self.listbox.yview)
        hbar=Scrollbar(self._w,orient=HORIZONTAL)
        hbar.grid(column=1,row=5,columnspan=3,ipadx=385)
        hbar.config(command=self.listbox.xview)
        self.listbox.config(xscrollcommand=hbar.set)
        self.width=width
        self.height=height
        self.files={}
        self.images=[]
        
        self.listbox.bind('<Double-Button-1>',self.click)
        self.context_menu = Menu(tearoff=0,bg='#fffff0',font=('arial',9
                                                              ))
        self.context_menu.add_command(label="Download", command=self.OPEN)
        self.context_menu.add_command(label="Rename", command=self.RENAME)
        self.context_menu.add_command(label="Delete", command=self.DELETE)
        
        self.listbox.bind('<Button-3>',self.context)

    def full_libs(self):
       
        for it in self.sfl_dict.keys():
            self.simplefilelist.delete(it)
        self.sfl_dict={}
        self.drives=getFolders()
        self.simplefilelist.heading("#0", text=" Groups = Disks",anchor=W)
        
        i=0
        for logical_drive in self.drives:
            global glo
            if(glo == 0):
                glo == 1
                global curDisk
                curDisk = logical_drive[1]
            i+=1
            logdrive=self.simplefilelist.insert("",i,None,text=logical_drive[0][1:-1],image=self.drives_img)
            self.sfl_dict[logdrive]=[logical_drive[0],logical_drive[1]]
            win.update()
        logdrive=self.simplefilelist.insert("",i,None,text="new disk",image=self.Adddrives_img)
        self.sfl_dict[logdrive]=['ADDDISK']

    def check_size(self,bsize):
        if bsize>2**30:
            return str(round(bsize/2**30,1))+'Gb'
        if bsize>2**20:
            return str(round(bsize/2**20,1))+'Mb'
        if bsize>2**10:
            return str(round(bsize/2**10,1))+'Kb'
        else:
            return str(bsize)+'B'
        
    def new_dir(self):
        newname=simpledialog.askstring('Disc (group) name','Input name: ')
        if(newname):
            asyncio.run(createChat(newname))
            self.full_libs()
            
    def new_dir1(self):
        newname=simpledialog.askstring('Folder name','Input name: ')
        if(newname):
            asyncio.run(createFolder(newname))
            asyncio.run(self.full_files(curDisk,qq))

    def click2(self,event=None):
        self.simplefilelist.after(1, self._endre_font_listbox1)

    def _endre_font_listbox1(self):
        el=self.sfl_dict[self.simplefilelist.selection()[0]][0]
        if(el == 'ADDDISK'):
            self.new_dir()
            return 0
        global curDisk

        curDisk =self.sfl_dict[self.simplefilelist.selection()[0]][1]
        thread = threading.Thread(target=asyncio.run(self.full_files(el))).start()
  
    def click(self,event=None):
        el=self.files[self.listbox.selection()[0]]
        try:
            if el[0] == 'dir':
                thread = threading.Thread(target=asyncio.run(self.full_files(el[2],q=el[1]))).start()
            else:
                addToDwld(el[0],el[1:])
                win.update()
        except Exception as e:
            msgbox.showerror('err',str(e))

    async def full_files(self,el,q=None):
        global lock
        if lock == False:
            lock = True
        else:
            return 0
        
        global qq
        qq=q
        for it in self.files.keys():
            self.listbox.delete(it)
        
        #print("-> ",el)
        win.update()
        
        files=['..']+list(os.listdir())
        self.images=[]
        self.files={}

        if(q):
            if('/' in q):
                self.files[self.listbox.insert("",0,None,text='..', values=('','',''),image=self.dir_img)]= ["dir",q.rpartition('/')[0],el]
            else:
                self.files[self.listbox.insert("",0,None,text='..', values=('','',''),image=self.dir_img)]= ["dir",None,el]
                
        i=1
        Flist = []
        listo={}

        def delL(word):
            if(word[:1] == '/' or word[:1] == '.'):
                word = delL(word[1:])
            return word

        if(q):
            win.title('TeleDisk - '+q)
        else:
            win.title('TeleDisk')
            
        async with TelegramClient('myuser', cliId, cliHash) as clientM:
            abc = await clientM.get_entity(el)
            #print('q = ',q)
            
            async for dialog in clientM.iter_messages(abc,limit=limit,search=q):
                #print(dialog.stringify())
                if q:
                    if(dialog.message.partition(q)[2].partition('/')[0] != '' or q not in dialog.message):
                        continue
                if dialog.message:
                    dialog.message = dialog.message.replace('\\','/')   
                    dialog.message = delL(dialog.message)

                try:
                    if(dialog.message):
                        if('._part_(' in dialog.message):
                            fff=dialog.message.rpartition('._part_')[0]
                        else:
                            fff=dialog.message
                            
                        if('.' not in fff):
                            self.images+=[PhotoImage(file=self.img_lib+dialog.media.document.mime_type.partition('/')[2]+'.png')]
                            dialog.message = dialog.message+'.'+dialog.media.document.mime_type.partition('/')[2]
                        else:
                            self.images+=[PhotoImage(file=self.img_lib+fff.rpartition('.')[2]+'.png')]
                    else: 1/0
                except:
                    try:
                        self.images+=[PhotoImage(file=self.img_lib+dialog.media.document.attributes[-1].file_name.rpartition('.')[2]+'.png')]
                        dialog.message = dialog.media.document.attributes[-1].file_name
                    except Exception as e:
                        try:
                            self.images+=[PhotoImage(file=self.img_lib+dialog.media.document.mime_type.partition('/')[2]+'.png')]
                            try:
                                dialog.media.document.attributes[-1].file_name
                            except:
                                dialog.message = dialog.media.document.mime_type.replace('/','.')
                        except:
                            self.images+=[PhotoImage(file=self.img_lib+'who.png')]

                ttt=''
                if(q):
                    ttt = dialog.message.partition(q)[1]+'/'
                    dialog.message = dialog.message.partition(q)[2][1:]
                    
                try:
                    res=dialog.media.document.mime_type
                except:
                    res=str(type(dialog.media)).partition('MessageMedia')[2][:-2]

                if(dialog.media == None):
                    continue
                elif(type(dialog.media) == types.MessageMediaWebPage):
                    continue
                elif("/" in dialog.message):
                    if(dialog.message.partition('/')[0] not in Flist):
                        self.files[self.listbox.insert("",i,None,text=str(dialog.message.partition('/')[0]), values=(str(dialog.date)[:-6],'Folder',''),image=self.dir_img)]= ["dir",ttt+dialog.message.partition('/')[0],abc]
                        Flist.append(dialog.message.partition('/')[0])
                        i=i+1
                elif(type(dialog.media) == types.MessageMediaPhoto or (("image" in dialog.media.document.mime_type) if dialog.media.document != None else False)):
                    if(photoPreload):
                        t = io.BytesIO(await clientM.download_media(dialog,thumb=-1,file=bytes))
                        t = Image.open(t)
                        t = t.resize((25, 18))
                        t = ImageTk.PhotoImage(t)
                    else:
                        t = self.images_img
                    
                    #Tpath = "temp/"+str(uuid.uuid4())+'.jpg'
                    #await clientM.download_media(dialog,thumb=0,file=Tpath)
                    #t = Image.open(Tpath)
                    #t = t.resize((25, 18))
                    #t = ImageTk.PhotoImage(t)  
                    #t.save(Tpath.replace('.jpg','.png'),"PNG")
                    #t=Tpath.replace('.jpg','.png')
                    
                    try:
                        self.files[self.listbox.insert("",i,None,text=str(dialog.message) if dialog.message != "" else "Photo", values=(str(dialog.date)[:-6],res,self.check_size(dialog.media.photo.sizes[-1].sizes[-1])),image=t)]= ["photo",dialog]
                    except Exception as e:
                        self.files[self.listbox.insert("",i,None,text=str(dialog.message) if dialog.message != "" else "Photo", values=(str(dialog.date)[:-6],res,self.check_size(dialog.media.document.size)),image=t)]= ["photo",dialog]
                    i=i+1
                elif(("video" in dialog.media.document.mime_type) if dialog.media.document != None else False):
                    if("video" in dialog.media.document.mime_type):
                        #print('!-> ',dialog.message == '')
                        if dialog.message == "": dialog.message = 'Video'
                        self.files[self.listbox.insert("",i,None,text=str(dialog.message), values=(str(dialog.date)[:-6],res,self.check_size(dialog.media.document.size)),image=self.images[-1])]= ["video",dialog]
                        i=i+1

                elif('_part_' in dialog.message.rpartition('.')[2]):
                    #print('рассматривается: ', dialog.message)
                    if(dialog.message.rpartition('.')[0] not in listo):
                        listo[dialog.message.rpartition('.')[0]] = {}
                        
                    if("(1-" in dialog.message.rpartition('.')[2]):
                        obj = self.listbox.insert("",i,i,text=str(dialog.message.rpartition('.')[0]), values=(str(dialog.date)[:-6],res,self.check_size(dialog.media.document.size)),image=self.images[-1])
                        self.files[obj]= ["big",dialog.message.rpartition('.')[0]]
                        #i=i+1
                        listo[dialog.message.rpartition('.')[0]][dialog.message.rpartition('_part_')[2][1:-1].split('-')[0]] = dialog
                        listo[dialog.message.rpartition('.')[0]]['obj'] = [obj,i]
                        i=i+1  
                        
                    else:
                        listo[dialog.message.rpartition('.')[0]][dialog.message.rpartition('_part_')[2][1:-1].split('-')[0]] = dialog
                    #print(dialog.message.rpartition('.')[0],' | сравнивается: ',len(listo[dialog.message.rpartition('.')[0]]), ' and ' ,int(dialog.message.rpartition('_part_')[2][1:-1].split('-')[1]))
                    if(1==1):
                        if(len(listo[dialog.message.rpartition('.')[0]]) == int(dialog.message.rpartition('_part_')[2][1:-1].split('-')[1]) + 1):
                            if(1==1):
                                raz=0
                                for iii in listo[dialog.message.rpartition('.')[0]]:
                                    if(iii == 'obj'):
                                        obj1 = listo[dialog.message.rpartition('.')[0]][iii][0]
                                        i1 = obj1 = listo[dialog.message.rpartition('.')[0]][iii][1]
                                    else:
                                        raz = raz + listo[dialog.message.rpartition('.')[0]][iii].media.document.size
                                
                                self.listbox.item(i1, values=(str(dialog.date)[:-6],res,self.check_size(raz)))
                                self.files[listo[dialog.message.rpartition('.')[0]]['obj'][0]] = ['big',dialog.message.rpartition('.')[0],listo[dialog.message.rpartition('.')[0]],raz]
                else:
                    try:
                        if(dialog.media.document.attributes[-1].file_name == 'FOLDER'):
                            continue
                    except: pass
                    
                    ab = types.DocumentAttributeFilename
                    self.files[self.listbox.insert("",i,None,text=str(dialog.message) if dialog.message != "" else dialog.media.document.attributes[-1].file_name, values=(str(dialog.date)[:-6],res,self.check_size(dialog.media.document.size)),image=self.images[-1])]= ["us",dialog]
                    i=i+1
                win.update()
        #print('элементов: ',i)
        if(i==1):
            self.files[self.listbox.insert("",i,None,text="No files")] = '..'
            win.update()
        lock = False

    async def asyncRENAME(self,el,newname):
        async with TelegramClient('myuser1', cliId, cliHash) as clientM:          
            if(el[0] == 'dir'):
                abc = await clientM.get_entity(el[2])
                jojo=[]
                async for dia in clientM.iter_messages(abc,limit=limit,search=el[1]):
                    if(dia.message.partition(el[1])[2].partition('/')[0] != '' or dia.media != None):
                        continue
                    await clientM.edit_message(curDisk, dia, dia.message.replace(el[1],el[1].rpartition('/')[0]+'/'+newname))
            elif(el[0] == 'big'):
                jojo=[]
                for d in range(1,len(el[2])):
                    jojo.append(el[2][str(d)].id)
                nMes = await clientM.get_messages(curDisk,ids = jojo)
                for nmes in nMes:
                    await clientM.edit_message(curDisk, nmes, nmes.message.rpartition('/')[0]+'/'+newname)
            else:
                nMes = await clientM.get_messages(curDisk,ids = el[1].id)
                await clientM.edit_message(curDisk, el[1], nMes.message.rpartition('/')[0]+'/'+newname)
                
    def RENAME(self):
        el=self.files[self.listbox.selection()[0]]
        print(el)       
        if(el[0] == 'dir'):
            oldName = el[1]
        elif(el[0] == 'big'):
            oldName = el[1]
        else:
            oldName = el[1].message
        newname1=simpledialog.askstring('Input new name','Old name: '+oldName, initialvalue=oldName)
        if(newname1):
            asyncio.run(self.asyncRENAME(el,newname1))
            asyncio.run(self.full_files(curDisk,qq))
                
    async def asyncDELETE(self,el):
        async with TelegramClient('myuser1', cliId, cliHash) as clientM:
            print(el)
            if(el[0] == 'dir'):
                abc = await clientM.get_entity(el[2])
                jojo=[]
                async for dia in clientM.iter_messages(abc,limit=limit,search=el[1]):
                    print(dia.message)
                    if(dia.message.partition(el[1])[2].partition('/')[0] != '' or dia.media == None):
                        continue
                    jojo.append(dia)
                await clientM.delete_messages(abc, jojo)
            elif(el[0] == 'big'):
                jojo=[]
                for d in range(1,len(el[2])):
                    jojo.append(el[2][str(d)].id)
                await clientM.delete_messages(curDisk, jojo)
            else:
                await clientM.delete_messages(curDisk, el[1])
                 
    def DELETE(self):
        try:
            for x in self.listbox.selection():
                el = self.files[x]
                asyncio.run(self.asyncDELETE(el))
        except Exception as e:
                msgbox.showerror('Err',str(e))
        asyncio.run(self.full_files(curDisk,qq))
                
    def OPEN(self):
        for x in self.listbox.selection():
            el = self.files[x]     
            print(el)
            try:
                    addToDwld(el[0],el[1:],open2_=False)
                    win.update()
            except Exception as e:
                msgbox.showerror('Err',str(e))

    def upld_start(self):
        filetypes = (("Any", "*"),)
        filename = fd.askopenfilenames(title="Choose file", initialdir="/",
                    filetypes=filetypes)
        if filename:
            global curDisk
            addToUpld(curDisk,filename,self,qq)
            
    def upld1_start(self):
        filename = fd.askdirectory(title="Choose folder", initialdir="/")
        if filename:
            global curDisk
            addToUpld(curDisk,[filename],self,qq)
        
    def context(self,event=None):
        try:
            self.context_menu.post(event.x_root, event.y_root)    
        except: pass
filesys=FileFrame(win,win)
filesys.pack(fill=BOTH,expand=1)

"""
async def main(interval=0.05):
    try:
        while True:
            # We want to update the application but get back
            # to asyncio's event loop. For this we sleep a
            # short time so the event loop can run.
            #
            # https://www.reddit.com/r/Python/comments/33ecpl
            win.update()
            await asyncio.sleep(interval)
    except KeyboardInterrupt:
        pass
    except tkinter.TclError as e:
        if 'application has been destroyed' not in e.args[0]:
            raise
asyncio.run(main())
"""
win.mainloop()
