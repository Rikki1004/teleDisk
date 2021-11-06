import time
from telethon import TelegramClient, events, functions, types
import random
import os
import threading
import asyncio
import numpy as np
import cv2
import PySimpleGUI as sg
import socket
import winreg
import string
import copy
import math

######
#
#C:\Users\user\AppData\Local\Programs\Python\Python38\Lib\site-packages\telethon\client\uploads.py  633
#C:\Users\user\AppData\Local\Programs\Python\Python38\Lib\site-packages\telethon\client\downloads.py 547
#
######

import nest_asyncio
nest_asyncio.apply()
#__import__('IPython').embed()


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

clientM = TelegramClient('myuser', 6, 'eb06d4abfb49dc3eeb1aeb98ae0f581e',loop=loop)
users=['myuser0','myuser1','myuser2','myuser3','myuser4','myuser5']
sem = threading.Semaphore(6)
needDwld = []
progress={}
unics = {}
#maxS = 1024*1024*1920
#readS = 1024*1024*512
maxS = 80
readS = 10
maxV = 5
window = None


try:
    os.mkdir('./download')
except:
    pass
try:
    os.mkdir('./temp')
except:
    pass


def reestr(Mname):
    try:
        key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram1', reserved=0, access=winreg.KEY_WRITE)
        #key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram', 0, winreg.KEY_WRITE)
        winreg.CloseKey(key)
        #return True
        raise 'запись'
    except Exception as e:
        #print(e)
        #time.sleep(9999)
        if(str(e) == '[WinError 5] Отказано в доступе'):
            return True



        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_WRITE)
            winreg.SetValueEx(key, 'TeleDisk', None, winreg.REG_SZ, "C:\telepy\TeleDisk.exe")
            winreg.CloseKey(key)
            
            key = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram', 0, winreg.KEY_WRITE)
            winreg.CloseKey(key)
            return True
        except:
            
            #time.sleep(9999)
            key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram', reserved=0, access=winreg.KEY_WRITE)
            winreg.SetValueEx(key, 'MUIVerb', None, winreg.REG_SZ, Mname)
            winreg.SetValueEx(key, 'Icon', None, winreg.REG_SZ, "xpsrchvw.exe")
            winreg.SetValueEx(key, 'Position', None, winreg.REG_SZ, "Top")
            winreg.SetValueEx(key, 'SubCommands', None, winreg.REG_SZ, "")
            #winreg.SetValueEx(key, 'Extended', None, winreg.REG_SZ, "")
            winreg.CloseKey(key)

            letters = string.ascii_lowercase*10

            with clientM:
                ii = -1
                #print(clientM.loop.run_until_complete(getFoldersSort()))
                for keyM in clientM.loop.run_until_complete(getFoldersSort()):
                    ii=ii+1
                    rand_string = ''.join(random.choice(letters) for i in range(15))

                    key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram\shell\\'+letters[ii]+rand_string, reserved=0, access=winreg.KEY_WRITE)
                    winreg.SetValueEx(key, 'MUIVerb', None, winreg.REG_SZ, keyM)
                    winreg.CloseKey(key)

                    key = winreg.CreateKeyEx(winreg.HKEY_CLASSES_ROOT, r'AllFilesystemObjects\\shell\\telegram\shell\\'+letters[ii]+rand_string+'\\command', reserved=0, access=winreg.KEY_WRITE)
                    winreg.SetValueEx(key, '', None, winreg.REG_SZ, 'C:\\telepy\\context.exe \"%1\" "' + keyM + '"')
                    winreg.CloseKey(key)


reestr('Выгрузить')


async def getFolders():
    hj = {}
    async for dialog in clientM.iter_dialogs(ignore_migrated=True):
            try:
                if (dialog.title[:1] == '|' and dialog.title[-1:] == '|'):
                    hj[str(dialog.title)] = str(dialog.id)
            except:
                pass
    
    return hj


async def getNameFolders():
    hj = {}
    async for dialog in clientM.iter_dialogs(ignore_migrated=True):
            try:
                if (dialog.title[:1] == '|' and dialog.title[-1:] == '|'):
                    hj[str(dialog.title)] = str(dialog.id)
            except:
                pass
    
    return hj


async def getFiles(folder,messages=False,clientM=clientM):
    hj = []
    hjj=[]
    async for dialog in clientM.iter_dialogs():
        if dialog.is_group:
            try:
                if (dialog.title[:1] == '|' and dialog.title[-1:] == '|'):
                    #print(dialog.stringify())
                    #try:
                    #    if(dialog.entity.migrated_to):
                    #        #print(dialog.entity.migrated_to.channel_id)
                    #        for i in hj:
                    #            print(i)
                    #            if(i[1][0] == dialog.entity.migrated_to.channel_id or str(i[1][0]) == '-100'+str(dialog.entity.migrated_to.channel_id)):
                    #                hj[i].append(dialog.entity.migrated_to.channel_id)
                    #except Exception as e:
                    #    print(e)
                    #    pass
                    #print(dir(dialog.entity.restricted))
                    #time.sleep(9999)
                    hj.append([str(dialog.title), str(dialog.id)])
                    hjj.append(str(dialog.title))
                    #print(dialog.title,' ',dialog.id)
            except Exception as e:
                print(e)
            
    hjj = list(set(hjj)) #дубликаты
    #print(hjj)
    #time.sleep(9999)
    #for i in hjj:
    #print(hj)
    #print(hjj)
    #print(dir())
    abb=[]
    for i in hj:
        if('|'+folder+'|' == i[0]):
            #print(i[1])
            abb = abb + await clientM.get_messages(abs(int(i[1])),limit=None)
    #time.sleep(9999)
    #ho = int(hj['|'+folder+'|'])
    #print(ho)
    
    #username = await clientM.get_entity(ho)
    
    yu = []
    #abn = await clientM.get_messages('|'+folder+'|',limit=None)
    #abm = await clientM.get_messages(username,limit=None)
    #abb = abn #+ abn
    abbc = {}
    for i in abb:
        #abbc.append(i.massage)
        abbc[i.message] = i

    abb=list(abbc.values())
    #abb = [x for x in abb if x]
    #abb = list(set(abb)) #дубликаты
    big=[]
    big1=[]
    for i in abb:
        if(i.message):
            if('_part_' in i.message.split('.')[-1]):
                #big[i.message.rsplit('.',1)[0]] = []
                #abb.remove(i)
                big.append(i)
                big1.append(i.message.rsplit('.',1)[0])
                #abb.remove(abb[i])
                #abb.pop(i)
                #print('<<removed>> ',i.message)
            else:
                if(i.media):
                    yu.append(i)
    big1 = list(set(big1)) #дубликаты
    for i in big1:
        lbox = []
        for ii in big:
            if(i == ii.message.rsplit('.',1)[0]):
                lbox.append(ii)
            #abb.remove(ii)
        yu.append({'(Big)'+str(i):lbox})
    #print(yu)
    #time.sleep(9999)
    if messages:
        yuyu = []
        for i in yu:
            if type(i)== dict:
                yuyu.append(str(list(i.keys())[0]).partition('(Big)')[2])
            else:
                yuyu.append(i.message)
        return yuyu
                
    #for i in abb:
    #    if(i.message):
    #        if('_part_' in i.message.split('.')[-1]):
    #            big[i.message.rsplit('.',1)[0]].append(i)
    #            abb.remove(i)

    #for i in big:
    #    yu.append(i)
        
    #big = list(set(big)) #дубликаты
    #for i in abb:
    #    yu.append(i)
    #yu = [x for x in yu if x]
    return yu


def message_poll_start(file,folder,upload = True):
        with sem:
                try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        user = random.choice(users)
                        users.remove(user)
                        with TelegramClient(user, 5764805, 'c1cc5aafbf3c6e498e55e3f4eaedfbe2', loop=loop) as client:
                                if(upload):
                                        client.loop.run_until_complete(main(file,folder,client,user))
                                else:
                                        client.loop.run_until_complete(mainDwld(file,folder,client,user))
                except Exception as e:
                        print('err ',e)


async def mainDwld(h,ho,client,user):
    def callback(current, total, name):
        #print(str(h.message)," -> {0:.2f}".format(current/(2**20)), 'из', "{0:.2f}".format(total/(2**20)))
        progress[str(h.message)] = [str("{0:.2f}".format(current/(2**20))), str("{0:.2f}".format(total/(2**20))), str('{:.2%}'.format(current / total))]
        #print(list(progress.keys()))
        listSelection1.delete(0,'end')
        for i in list(progress.keys()):
            #pass
            #if(str(progress[i][2] == '100.00%')):
                #print('ок')
                #del progress[i]
                #progress[i] = ''
            listSelection1.insert(END, str(i)+' -> '+str(progress[i][0])+'Mb из '+ str(progress[i][1])+ 'Mb |' + str(progress[i][2]))
            
        #print(current/(2**20),' из ',total/(2**20))
        #    'Mb: {:.2%}'.format(current / total))
        #progress[h] = str("{0:.2f}".format(current/(2**20)))+' из '+str("{0:.2f}".format(total/(2**20)))+str('Mb: {:.2%}'.format(current / total))
        #if(not progress[h]):
        #    progress[h]=[0,0,0,1]
        #progress[h] = [str("{0:.2f}".format(current/(2**20))), str("{0:.2f}".format(total/(2**20))), str('{:.2%}'.format(current / total))]
        
    async with client:
        atemp = 1
        while atemp < 6:
            try:
                #print(h,ho,client,user)
                #time.sleep(9999)
                #await client.send_file('me', h,progress_callback=callback)
                await client.download_media(h,'download/'+str(h.message).replace('\\','/').rpartition('/')[2], progress_callback=callback)
                #await client.send_file(ho, h,thumb=t,force_document=v,silent=True,supports_streaming=w , progress_callback=callback,caption=h, part_size_kb=512)
                print('holla')
                break
            except Exception as e:
                atemp=atemp+1
                print('attemp: '+ str(atemp) + ' not holla -> ',e)
                continue
            
        for i in list(progress.keys()):
            if(str(progress[i][2] == '100.00%')):
                del progress[i]
        users.append(user)
        needDwld.remove(h.message)
        #if('_part_' in h.message.split('.')[-1].lower()):
        #    os.remove('download/'+str(h.message).replace('\\','/').rpartition('/')[2])



def waiting(rm, val):
    #print(list(val.values())[0])
    for i in rm:
        if i == 0:
            continue
        i.join()
    with open('./download/'+list(val.keys())[0].replace('\\','/').rpartition('/')[2].partition('(Big)')[2],'wb') as f:
        ryt = list(val.values())[0]
        #ryt.sort(reverse=True)
        rytp = []
        for i in ryt:
            rytp.append(str(i.message).rpartition('_part_')[2][1:-1].split('-')[0])
        #rytp.sort
        #print(sorted(rytp))
        rytps = []
        for i in sorted(rytp):
            for ii in ryt:
                if(str(ii.message).rpartition('_part_')[2][1:-1].split('-')[0] == i):
                    rytps.append(ii)
        #print(rytps)
        #time.sleep(9999)
        for i in rytps:
            print('собирается: ',i.message)
            with open('./download/'+str(i.message).replace('\\','/').rpartition('/')[2],'rb') as ff:
                f.write(ff.read())
            os.remove('./download/'+str(i.message).replace('\\','/').rpartition('/')[2])
        print('успешно собран')

    
async def main(h,ho,client,user):
    hoho = h.replace('\\','/').rpartition('/')[2]
    #print(asyncio.get_event_loop().run_until_complete(getFiles(str('|OTHER|')[1:-1],messages=False,clientM=client)))
    #time.sleep(9999)
    #async with client:
        #print(client.loop.run_until_complete(getFiles('OTHER',messages=True,clientM=client)))
    #async with client:
    #if 1==1:
    #    a = await client.get_entity(ho)
    #    print(str(a.title)[1:-1])
    #    
    #    for i in client.loop.run_until_complete(getFiles(str(a.title)[1:-1],messages=False,clientM=client)):
    #        if(type(i)==dict):
    #            if(list(i.keys())[0] == hoho):
    #                b = list(set(i[hoho]) - set(doooo))
    #                print(b)
    #time.sleep(9999)
    def callback(current, total,momo):
        #2/0
        print(momo," -> {0:.2f}".format(current/(2**20)), 'из', "{0:.2f}".format(total/(2**20)))
        #    'Mb: {:.2%}'.format(current / total))
        #progress[h] = str("{0:.2f}".format(current/(2**20)))+' из '+str("{0:.2f}".format(total/(2**20)))+str('Mb: {:.2%}'.format(current / total))
        #if(not progress[h]):
        #    progress[h]=[0,0,0,1]
        #progress[hoho] = [str("{0:.2f}".format(current/(2**20))), str("{0:.2f}".format(total/(2**20))), str('{:.2%}'.format(current / total))]
        
    def callback1(current, total,momo):
        #print(momo," -> {0:.2f}".format(current/(2**20)), 'из', "{0:.2f}".format(total/(2**20)))
        progress[str(momo)] = [str("{0:.2f}".format(current/(2**20))), str("{0:.2f}".format(total/(2**20))), str('{:.2%}'.format(current / total))]
        listSelection1.delete(0,'end')
        for i in list(progress.keys()):
            listSelection1.insert(END, str(i)+' -> '+str(progress[i][0])+'Mb из '+ str(progress[i][1])+ 'Mb |' + str(progress[i][2]))
        
    async with client:
        w = False
        v = True
        t = ''
        if((h.split('.')[-1].lower() == 'mp4') and (os.path.getsize(h) < maxS)):
            w = True
            v = False

            try:
                #---------------------cv2-not-empty----------------------
                cap = cv2.VideoCapture(h)           
                cap.set(cv2.CAP_PROP_POS_FRAMES,0)
                ret, frame = cap.read()
                cv2.imwrite(h.rsplit('.',1)[0].lower()+"_previu.jpg", frame)
                t= h.rsplit('.',1)[0].lower()+"_previu.jpg" #'DJI_0162.JPG'
                cap.release()
                cv2.destroyAllWindows()
                pass
            except:
                pass
            #print('видео')

        if(os.path.getsize(h) > maxS*1024*1024):
            #print('файл ',h,' весит больше чем ',maxS)
            try:
                os.mkdir('./temp')
            except:
                pass
            #readS
            with open(h, "rb") as f:
                pr  =int(math.ceil(os.path.getsize(h)/(1024*1024*readS)))
                #print('----------------------')
                byte = f.read(readS*1024* 1024)
                #print('----------------------')
                sh = 0
                dooo = []
                doooo = []
                #tasks=[]
                while byte:
                        
                    sh=sh+1
                        #print(str(os.path.dirname(i))+'/'+str(os.path.basename(i)))
                        #time.sleep(9999)
                    #print('----------------------')
                    #print(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')
                    with open(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')','wb') as ff:
                        #print('----------------------')
                        ff.write(byte)
                        #needDwld.append(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')
                        #print('->>>>',os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')
                        #dooo.append(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(i).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'/'+str(pr)')')
                        #dooo.append(client.send_file(ho, os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'/'+str(pr)+')',force_document=True,silent=True,progress_callback=callback1,caption= os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'/'+str(pr)+')', part_size_kb=512))
                        #dooo.append(asyncio.ensure_future(main2(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')',ho,client,user)))
                        dooo.append(asyncio.ensure_future(client.send_file(ho,os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' + os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')',progress_callback=callback1,force_document=v,silent=True, part_size_kb=512,caption= os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')))
                        doooo.append(os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')
                        print("в doooo добавлен: "+ os.path.basename(h).replace('\\\\','/').replace('\\','/')+'._part_('+str(sh)+'-'+str(pr)+')')
                        #print(i)
                        
                        #if(len(dooo) >= maxV):
                        #    client.loop.run_until_complete(asyncio.gather(*dooo,return_exceptions=True))
                        #    dooo = []
                        #    for iiii in doooo:
                        #            doooo.remove(iiii)
                        #            os.remove(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' +iiii)
                        
                        #print(byte[:10])
                        #await client.send_file('me', file=byte,progress_callback=callback)
                        #time.sleep(1)
                        #dii.append(byte)
                        #break
                    byte = f.read(readS*1024*1024)
                    if(len(dooo) >= maxV):
                            
                            client.loop.run_until_complete(asyncio.gather(*dooo,return_exceptions=True))
                            print("удаление: ",doooo)
                            dooo = []
                            for iiii in list(doooo):
                                    print(iiii)
                                    os.remove(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' +iiii)
                                    doooo.remove(iiii)
                                    
                #print('----------------------')
                #print(dooo)
                u = asyncio.gather(*dooo,return_exceptions=True)
                #start_recur = time.time()
                client.loop.run_until_complete(u)
                a = await client.get_entity(ho)
                print('все')
                #print(asyncio.get_event_loop().run_until_complete(getFiles(str(a.title)[1:-1],messages=False,clientM=client)))
                while 1==1:
                    dooo = []
                    #a = await client.get_entity(ho)
                    #with client:
                    for i in asyncio.get_event_loop().run_until_complete(getFiles(str(a.title)[1:-1],messages=False,clientM=client)):
                        if(type(i)==dict):
                            #print(list(i.keys())[0],'--------------------------------',hoho)
                            if(hoho in list(i.keys())[0].partition('(Big)')[2]):
                                #print('да равны')
                                #print(i,'----------------',hoho,'----------------',doooo)
                                c = []
                                for iiii in list(i.values())[0]:
                                    c.append(iiii.message)
                                b = list(set(doooo) - set(c))
                                
                                for iiii in list(set(doooo) & set(c)):
                                    doooo.remove(iiii)
                                    os.remove(os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' +iiii)
                                #print(b,'----------------',c,'----------------',doooo)
                                if(len(b) == 0):
                                    return 0
                                print('догружаем: ',b)
                                for iii in b:
                                    dooo.append(asyncio.ensure_future(client.send_file(ho,os.getcwd().replace('\\\\','/').replace('\\','/') + '/temp/' +iii,progress_callback=callback1,force_document=True,silent=True, part_size_kb=512,caption= iii)))
                                    if(len(dooo) > maxV):
                                        client.loop.run_until_complete(asyncio.gather(*dooo,return_exceptions=True))
                                        dooo = []
                                client.loop.run_until_complete(asyncio.gather(*dooo,return_exceptions=True))
                                
                                #for ii in i[hoho]:
                                    
            print('закончили')        
        else:
            
            try:
                #print(h,ho,client,user)
                #time.sleep(9999)
                #await client.send_file('me', h,progress_callback=callback)
                await client.send_file(ho, h,thumb=t,force_document=v,silent=True,supports_streaming=w , progress_callback=callback1,caption=hoho, part_size_kb=512)
                print('holla')
                return True
            except Exception as e:
                print('not holla -> ',e)
            #if(not multi):
            users.append(user)
            needDwld.remove(h)
            if(h.split('.')[-1].lower() == 'mp4'):
                if(t != ''):
                    os.remove(h.rsplit('.',1)[0].lower()+"_previu.jpg")
                #if('_part_' in h.split('.')[-1].lower()):
                #    os.remove(h)
    #return True


def addToUpld(folder,file):
        #sem = threading.Semaphore(2+4)
        with clientM:
                
                folder = '|'+folder+'|'
                global unics
                if(folder not in unics):
                    unics[folder] = [int(clientM.loop.run_until_complete(getFolders())[folder]),clientM.loop.run_until_complete(getFiles(folder[1:-1],messages=True))]
                #unic = clientM.loop.run_until_complete(doople(folder,file))
                #print(unics)
                if(('.' in file) and (os.path.getsize(file) != 0) and (file.replace('\\','/').rpartition('/')[2] not in unics[folder][1])):
                    needDwld.append(file)
                    threading.Thread(target=message_poll_start,args=(file,unics[folder][0], True)).start()
                #print(files,unic)
                #nomFolder = int(clientM.loop.run_until_complete(getFolders())[folder])
                #for i in unic:
                        #needDwld.append(i)
                        #print(i,nomFolder,sem)
                        #threading.Thread(target=message_poll_start,args=(i,nomFolder)).start()


def addToDwld(folder,file):
        #print('./download/'+str(list(file.keys())[0]).replace('\\','/').rpartition('/')[2])
        #time.sleep(9999)
        #sem = threading.Semaphore(2+4)
        if(type(file) == dict):
            if(os.path.exists('./download/'+str(list(file.keys())[0]).replace('\\','/').rpartition('/')[2])):
                #print('exist')
                return 0
            rm = []
            for i in list(file.values())[0]:
                rm.append(addToDwld(folder,i))
            threading.Thread(target=waiting,args=(rm, file)).start()
            return 0

        #print('./download/'+str(file.message).replace('\\','/').rpartition('/')[2])
        if(os.path.exists('./download/'+str(file.message).replace('\\','/').rpartition('/')[2])):
            return 0
        #print('./download/'+str(file.message).replace('\\','/').rpartition('/')[2])
        #time.sleep(9999)
        with clientM:
                
                folder = '|'+folder+'|'
                #unic = clientM.loop.run_until_complete(doople(folder,files))
                #print(files,unic)
                nomFolder = int(clientM.loop.run_until_complete(getFolders())[folder])
                needDwld.append(file.message)
                        #print(i,nomFolder,sem)
                #message_poll_start(file,nomFolder)
                th = threading.Thread(target=message_poll_start,args=(file,nomFolder,False))
                th.start()
                return th





#with clientM:
    #print(clientM.loop.run_until_complete(getFiles('OTHER',messages=True)))
#time.sleep(9999)
addToUpld('OTHER',"./100MB.a")
#time.sleep(5)



with clientM:
    b = clientM.loop.run_until_complete(getFolders())
    #a = clientM.loop.run_until_complete(getFiles('Dji Media'))
    a = clientM.loop.run_until_complete(getFiles('OTHER'))
    c = 'OTHER'




from tkinter import *
import tkinter.filedialog as fd

def onselect(event):
    w = event.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    info = find_info(value)
    listSelection.delete(0, END)
    listSelection.insert(END, "Node ID: " + info[0])
    listSelection.insert(END, "Owner/Description: " + info[1])
    listSelection.insert(END, "Last Latitude: " + info[2])
    listSelection.insert(END, "Last Longitude: " + info[3])
    print('----')

#mapNodes = "http://ukhas.net/api/mapNodes"
#nodeData = "http://ukhas.net/api/nodeData"
current_id = 0

window = Tk() # create window
#window1 = Tk()
window.configure(bg='lightgrey')
window.title("TeleDiskDwld")
window.geometry("860x400")
n=0
m = None
lbl1 = Label(window, text="files:", fg='black', font=("Helvetica", 16, "bold"))
lbl2 = Label(window, text="folders:", fg='black', font=("Helvetica", 16,"bold"))
btn = Button(text="Сreate folder",command=lambda:add_field())
btn_file = Button(text="Выбрать файл",command=lambda:add_file())
lbl1.grid(row=0, column=0, sticky=W)
lbl2.grid(row=0, column=1, sticky=W)
btn.grid(row=0, column=1, sticky=E)
btn_file.grid(row=0, column=2, sticky=E)
def add_field():
    global n
    if n == 0:
        n=1
        global m
        m = Entry(window)
        m.grid(row=0, column=1, sticky=E, padx=83)
        #print(m.get())
    else:
        n = 0
        print(m.get())
        m.grid_forget()
        #createFolder(str(m.get()))
        
def add_file():
    filetypes = (("Любой", "*"),)
    filename = fd.askopenfilename(title="Открыть файл", initialdir="/",
                filetypes=filetypes)
    if filename:
        print(filename)
        addToUpld("OTHER",filename)
        
frm = Frame(window)
frm.grid(row=1, column=0, sticky=N+S)
window.rowconfigure(1, weight=1)
window.columnconfigure(1, weight=1)

scrollbar = Scrollbar(frm, orient="vertical")
scrollbar.pack(side=RIGHT, fill=Y)

scrollbar1 = Scrollbar(frm, orient="horizontal")
scrollbar1.pack(side=BOTTOM, fill=X)


listNodes = Listbox(frm, width=50, yscrollcommand=scrollbar.set, xscrollcommand=scrollbar1.set, font=("Helvetica", 12))
def onselect1(event):
    listNodes.after(1, _endre_font_listbox1)
def _endre_font_listbox1():
    valgte_indekser = listNodes.curselection()
    #print(valgte_indekser)
    #print(listNodes.get(valgte_indekser))
    #print(a[valgte_indekser[0]].message)
    #print('c= ',c,' <-> ',a[valgte_indekser[0]].message)
    addToDwld(c,a[valgte_indekser[0]])
    
listNodes.bind("<Button-1>", onselect1)
listNodes.bind("<Return>", onselect1)
listNodes.pack(expand=True, fill=Y)

scrollbar.config(command=listNodes.yview)
scrollbar1.config(command=listNodes.xview)



listSelection = Listbox(window, height=4, font=("Helvetica", 12))
def onselect2(hendelse):
    listSelection.after(1, _endre_font_listbox)

def _endre_font_listbox():
    valgte_indekser = listSelection.curselection()
    #print(valgte_indekser)
    #print(listSelection.get(valgte_indekser))
    listNodes.delete(0,'end')
    global c
    c = listSelection.get(valgte_indekser)
    #print('c= ',c)
    with clientM:
            global a
            print(str(listSelection.get(valgte_indekser)))
            a = clientM.loop.run_until_complete(getFiles(str(listSelection.get(valgte_indekser))))
            for x in a:
                #print(x)
                #print(x.stringify())
                #time.sleep(9999)
                if(type(x) != dict):
                    #if(x.media.document):
                    try:
                        listNodes.insert(END, str(x.message)+' ('+str(format(x.media.document.size/(1024*1024), '.2f'))+')')
                    except:
                        listNodes.insert(END, str(x.message)+'(?)')
                else:
                    #print(str(list(x.keys())[0])))
                    si = 0
                    for i in list(x.values())[0]:
                        si =si + i.media.document.size
                    listNodes.insert(END, str(list(x.keys())[0])+' ('+str(format(si/(1024*1024), '.2f')+')'))
                    #listNodes.insert(END, list(x.keys())[0])
            #for x in a:
            #    if(type(x) != dict):
            #        listNodes.insert(END, x.message)
            #    else:
            #        listNodes.insert(END, list(x.keys())[0])

#def onselect2(event):
#    pass
    #ff = listSelection.curselection()[0]
    #print( ff)
    #return 0
    #for i in listSelection.curselection():
    #    print(listSelection.get(i))
    #    listNodes.delete(0,'end')
    #    with clientM:
    #        a = clientM.loop.run_until_complete(getFiles(str(listSelection.get(i))))
    #        for x in a:
    #            listNodes.insert(END, x.message)
    #print(listSelection.get(listSelection.curselection()))
listSelection.bind("<Button-1>", onselect2)
listSelection.bind("<Return>", onselect2)



listSelection1 = Listbox(window, height=15, font=("Helvetica", 12))
listSelection1.grid(row=1, column=1, sticky=S+W+E)

#scrollbar2 = Scrollbar(frm, orient="vertical")
#scrollbar2.grid(row=3, column=1, sticky=E+W+N)
#scrollbar2.config(command=listSelection1.yview)

listSelection.grid(row=1, column=1, sticky=E+W+N)


for x in a:
    #print(x.stringify())
    #time.sleep(9999)
    if(type(x) != dict):
        try:
            listNodes.insert(END, str(x.message)+' ('+str(format(x.media.document.size/(1024*1024), '.2f'))+')')
        except:
            listNodes.insert(END, str(x.message)+'(?)')
    else:
        #print(str(list(x.keys())[0])))
        si = 0
        for i in list(x.values())[0]:
            si =si + i.media.document.size
        listNodes.insert(END, str(list(x.keys())[0])+' ('+str(format(si/(1024*1024), '.2f')+')'))
        #listNodes.insert(END, list(x.keys())[0])
for x in b.keys():
    listSelection.insert(END, x[1:-1])

#listNodes['text']='фбла абла'
window.mainloop()



print('точно все')

