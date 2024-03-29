import sys
import time
from PyQt5 import QtCore, QtWidgets, QtGui
from vk_scrape_graphics import *
# import vk_api
# import write_predict
import pandas as pd
import requests
import numpy as np
import csv
import datetime

from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt 
from sklearn.ensemble import ExtraTreesClassifier 
from sklearn.metrics import accuracy_score
import pickle
import aiohttp
import asyncio
import requests
from aiohttp import ClientSession
import pprint
import re
from matplotlib.backends.backend_pdf import PdfPages

start_time = time.time()

# token = '18019db418019db418019db4a01875ed881180118019db447882228875fa30302b2b588'
version = '5.130'

loaded_model = pickle.load(open('model.sav', 'rb'))

class MyWin(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self,parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_start_scrape.clicked.connect(self.start_scrape)
        start_ml_btn = self.ui.btn_analyze_ml
        start_ml_btn.clicked.connect(self.start_ml)
    def start_scrape(self):
        self.ui.progress_bar_id_scrape.setValue(0)
        self.ui.progress_bar_data_scrape.setValue(0)
        self.ui.progress_bar_file_scrape.setValue(0)

        self.phone = False
        self.links = False
        self.instagram = False
        self.skype = False
        self.facebook = False
        self.twitter = False
        
        self.token = self.ui.line_edit_token_scrape.text()
        self.group_id = self.ui.line_edit_domain_scrape.text()
        try:
            self.group_id = self.group_id.split('https://vk.com/')[1]
        except:
            self.group_id = self.group_id
        if 'club' in self.group_id:
            self.group_id = self.group_id.split('club')[1]

        if self.ui.radioButton_2.isChecked():
            self.phone = True
        
        if self.ui.radioButton_4.isChecked():
            self.links = True

        if self.ui.checkBox.isChecked():
            self.instagram = True

        if self.ui.checkBox_2.isChecked():
            self.skype = True

        if self.ui.checkBox_4.isChecked():
            self.facebook = True
        
        if self.ui.checkBox_4.isChecked():
            self.twitter = True

        self.write_csv(self.group_id, self.token, self.phone, self.links, self.instagram, self.skype, self.facebook, self.twitter)

    def write_csv(self, domain, token, phone=False, links=False, instagram=False, skype=False, facebook=False, twitter=False):
        bot_count = 0
        real_count = 0

        start_time = time.time()
        all_info = self.get_all_user_info(domain, token)

        bot_count = all_info.count('banned')
        real_count = all_info.count('verified')
        real_count += all_info.count('private')
        print(len(all_info))
        infos = [i for i in all_info if type(i) != str]
        print(len(infos))
        df = pd.DataFrame(infos)
        if phone == False:
            df.drop('phone', inplace=True, axis=1)
        if links == False:
            df.drop('site', inplace=True, axis=1)
        if instagram == False:
            df.drop('instagram', inplace=True, axis=1)
        if skype == False:
            df.drop('skype', inplace=True, axis=1)
        if twitter == False:
            df.drop('twitter', inplace=True, axis=1)
        if facebook == False:
            df.drop('facebook', inplace=True, axis=1) 

        # columnNames = df.iloc[0] 
        # df = df[1:] 
        # df.columns = columnNames
        # print(feature_df[:20])
        time_df = time.time() 
        print("--- %s seconds ---" % (time_df - start_time))
        file_path = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить','vk_parse', 'Excel *.xlsx')
        if len(file_path[0]) == 0:
            pass
        else:
            df.to_excel(file_path[0])
            print("Done!!!!")
            self.ui.progress_bar_file_scrape.setValue(100)
            QtWidgets.QMessageBox.information(self, 'Завершено', 'Скачивание Эксель файла выполнено')
        return 0

    def get_all_user_info(self, domain, token):
        domain = domain
        token = token
        users_desc = []
        all_ids = []
        users_count = 0
        response = requests.get('https://api.vk.com/method/groups.getMembers?',
                                params={
                                    'access_token': token,
                                    'v': version,
                                    'group_id': domain,
                                    'count': 1
                                }
                                )

        count_items = response.json()['response']['count']
        # print(count_items)

        async def get_ids(session, url):
            async with session.get(url) as resp:
                users = await resp.json()
                return users['response']['items']


        async def main():

            async with aiohttp.ClientSession() as session:

                tasks = []
                count = 100
                for offset in range(0, count_items, count):
                    url = f'https://api.vk.com/method/groups.getMembers?access_token={token}&v={version}&group_id={domain}&count={count}&offset={offset}'
                    tasks.append(asyncio.ensure_future(get_ids(session, url)))

                all_users = await asyncio.gather(*tasks)
                for user in all_users:
                    all_ids.extend(user)

        asyncio.run(main())
        # print("--- %s seconds ---" % (time.time() - start_time))
        print("got: " ,len(all_ids))
        # print(all_ids[:150])

    # commented 


        async def get_info(session, url, id, all_ids):
            async with session.get(url) as resp:
                users = await resp.json()
                index = int((all_ids.index(id) *100) / len(all_ids))
                self.ui.progress_bar_data_scrape.setValue(index)
                user = users['response']

                
                features = {}

                try:
                    banned = user[0]['deactivated']
                except:
                    banned = None
                if banned:
                    features = "banned"
                    return features
                else:
                    mobile = 0
                    site = 0
                    if user[0]['verified']:
                        features = "verified"
                        return features
                    try:
                        IsClosed = user[0]['is_closed']
                    except:
                        closed = 0
                    if  IsClosed:
                        features = "private"
                        return features
                    else:
                        try :
                            mobile = user[0]['mobile_phone']
                            str1 = mobile.replace(' ','')
                            if bool(re.match('^[0-9()+-]+$', str1)):
                                mobile = str1
                            else:
                                mobile = None
                        except:
                            mobile = None
                        # if mobile:
                                            #     print(mobile)


                        try :
                            instagram = user[0]['instagram']
                        except:
                            instagram = None
                        try :
                            facebook = user[0]['facebook']
                        except:
                            facebook = None
                        try :
                            twitter = user[0]['twitter']
                        except:
                            twitter = None
                        try :
                            skype = user[0]['skype']
                        except:
                            skype = None
                        try:
                            verified = user[0]['verified']
                        except:
                            verified = None
                        try:
                            site = user[0]['site']
                        except:
                            site = None

                            

                        # try :
                        #     count_friends = count_user_friends['count']
                        # except:
                        #     count_friends = None







                        features = {}
                        features["id"] = id
                        features["phone"] = mobile
                        features["instagram"] = instagram
                        features["skype"] = skype
                        features["facebook"] = facebook
                        features["twitter"] = twitter
                        features["site"] = site

                    # добавить соотношение друзья/подписчики
                    # try:
                    #     features["following_followers_ratio"] = round(
                    #             count_user_friends / followers_count, 7)
                    # except ZeroDivisionError:
                    #     features["following_followers_ratio"] = 2.8624688005235597

                    # добавить соотношение друзья/фото
                    # try:
                    #     features["following_photos_ratio"] = round(
                    #             count_user_friends / count_photos, 7)
                    # except ZeroDivisionError:
                    #     features["following_photos_ratio"] = 48.6537926973262

                    # # добавить соотношение подписчики/фото
                    # try:
                    #     features["followers_photos_ratio"] = round(
                    #         followers_count / count_photos, 7)
                    # except ZeroDivisionError:
                    #     features["followers_photos_ratio"] = 118.71968859411763
                    
            return features

        all_ids_info = []

        fields = [ " has_mobile, contacts, last_seen, connections, education, city, counters, has_photo,  fields, verified, personal, relatives, relation, schools, site, career, followers_count "]

        async def main_info(all_ids):
            self.ui.progress_bar_id_scrape.setValue(100)
            # if len(all_ids) > 50_000:
            #     for i in range(0, len(all_ids),50_000):
            #         if i + 50_000 > len(all_ids):
            #             ids = all_ids[i:]
            #         else:
            #             ids = all_ids[i:i+50_000]
            #         print("i")
            async with aiohttp.ClientSession() as session:

                tasks = []
                for id in all_ids:
                    
                    url = f'https://api.vk.com/method/users.get?access_token={token}&v={version}&user_ids={id}&fields={fields}'
                    tasks.append(asyncio.ensure_future(get_info(session, url, id, all_ids)))

                all_users_info = await asyncio.gather(*tasks)
                for user_info in all_users_info:
                    all_ids_info.append(user_info)
        if len(all_ids) > 50_000:
            for i in range(0, len(all_ids),50_000):
                if i + 50_000 > len(all_ids):
                    ids = all_ids[i:]
                else:
                    ids = all_ids[i:i+50_000]
                # print("i")

                asyncio.run(main_info(ids))
        else:
            asyncio.run(main_info(all_ids))

        # print(all_ids_info[:100])
        self.ui.progress_bar_data_scrape.setValue(100)
        return all_ids_info

    def start_ml(self):
        self.ui.progress_bar_id_ml.setValue(0)
        self.ui.progress_bar_data_ml.setValue(0)
        self.ui.progress_bar_bot_ml.setValue(0)
        self.ui.progress_bar_file_ml.setValue(0)
        self.ui.progress_bar_real_percentage_ml.setValue(0)

        self.token = self.ui.line_edit_token_ml.text()
        self.group_id = self.ui.line_edit_domain_ml.text()
        try:
            self.group_id = self.group_id.split('https://vk.com/')[1]
        except:
            self.group_id = self.group_id
        if 'club' in self.group_id:
            self.group_id = self.group_id.split('club')[1]
        self.make_pdf(self.group_id, self.token)

    def make_pdf(self, domain, token):
        loaded_model = pickle.load(open('model.sav', 'rb'))

        banned = 0
        verified = 0
        private = 0

        start_time = time.time()
        all_info = self.get_all_user_info_ml(domain, token)

        banned = all_info.count('banned')
        verified = all_info.count('verified')
        private = all_info.count('private')
        print(len(all_info))
        infos = [i for i in all_info if type(i) != str]
        print(len(infos))
        df = pd.DataFrame(infos)
        
        analyze_data = df[['FriendCount', 'bdate', 'sex', 'city', 'country']]
        df.drop('bdate', inplace=True, axis=1)
        df.drop('sex', inplace=True, axis=1)
        df.drop('city', inplace=True, axis=1)
        df.drop('country', inplace=True, axis=1)
        answers = loaded_model.predict(df)
        df['answers'] = answers
        self.ui.progress_bar_bot_ml.setValue(100)
        analyze_data['answers'] = answers
        real_data = analyze_data[analyze_data["answers"] == 1]
        # sex_percentage = real_data.sex.value_counts(normalize=True)
        sex_percentage = real_data.sex.value_counts()

        countries = real_data.country.value_counts()[:10]
        cities = real_data.city.value_counts()[:10]
        max_friends = real_data.FriendCount.max()


        real_count = np.sum(answers == 1)
        bot_count = np.sum(answers == 0)


        friends_1 = max_friends*0.2
        friends_2 = max_friends*0.4
        friends_3 = max_friends*0.6
        friends_4 = max_friends*0.8
        friends_5 = max_friends
        print(len(analyze_data))
        # print(len(analyze_data[analyze_data["FriendCount"] < friends_1]))
        # print(len(analyze_data[analyze_data["FriendCount"] < friends_2]))
        # print(len(analyze_data[analyze_data["FriendCount"] < friends_3]))
        # print(len(analyze_data[analyze_data["FriendCount"] < friends_4]))
        # print(len(analyze_data[analyze_data["FriendCount"] < friends_5]))

        real_percentage = int(real_count/len(all_info) * 100)
        # print(real_count, len(all_info))
        print(real_percentage)
        self.ui.progress_bar_real_percentage_ml.setValue(real_percentage)

        file_path_pdf = QtWidgets.QFileDialog.getSaveFileName(self, 'Сохранить','analyze_vk', 'Pdf *.pdf')
        if len(file_path_pdf[0]) == 0:
            pass
        else:
            with PdfPages(file_path_pdf[0]) as pdf:
                plt.figure(figsize=(6, 6))
                plt.rcParams['font.size'] = '6'
                labels = ['Ж', 'М', 'Не указан']
                sex_percentage.plot.pie(labels=labels, title="Пол участников группы", autopct='%.0f%%', explode = (0.05,0.05,0.05));
                pdf.savefig()
                plt.close()

                # plt.figure(figsize=(6, 6))
                x = countries.index.tolist()
                y = countries.values.tolist()
                # cities.plot(kind='bar')
                fig, ax = plt.subplots()
                width = 0.75
                ind = np.arange(len(y))
                
                ax.barh(x, y, width, color = "green")
                
                for i, v in enumerate(y):
                    ax.text(v + 3, i, str(v), 
                            color = 'blue', fontweight = 'bold')
                labels = ax.set_yticklabels(x,
                    fontsize = 6,    #  Размер шрифта
                    color = 'b',    #  Цвет текста
                    rotation = 0,    #  Поворот текста
                    verticalalignment =  'center')    #  Вертикальное выравнивание

                fig.set_figwidth(10)
                fig.set_figheight(8)
                plt.gca().invert_yaxis()
                pdf.savefig()
                plt.close()

                # plt.figure(figsize=(6, 6))
                x = cities.index.tolist()
                y = cities.values.tolist()
                # cities.plot(kind='bar')
                fig, ax = plt.subplots()
                width = 0.75
                ind = np.arange(len(y))
                
                ax.barh(x, y, width, color = "lavender")
                
                for i, v in enumerate(y):
                    ax.text(v + 3, i, str(v), 
                            color = 'blue', fontweight = 'bold')
                labels = ax.set_yticklabels(x,
                    fontsize = 6,    #  Размер шрифта
                    color = 'b',    #  Цвет текста
                    rotation = 0,    #  Поворот текста
                    verticalalignment =  'center')    #  Вертикальное выравнивание

                fig.set_figwidth(10)
                fig.set_figheight(8)
                plt.gca().invert_yaxis()
                pdf.savefig()
                plt.close()

                # plt.figure(figsize=(6, 6))
                y = np.array([banned, private, verified, bot_count, real_count])
                x = ["Забаненный", "Приватный", "Подтвержденный", "Бот", "Реальный пользователь"]
                # cities.plot(kind='bar')
                fig, ax = plt.subplots()
                width = 0.75
                ind = np.arange(len(y))
                
                ax.barh(x, y, width, color=['red', 'blue', 'purple', 'green', 'lavender'])
                
                for i, v in enumerate(y):
                    ax.text(v + 3, i, str(v), 
                            color = 'blue', fontweight = 'bold')
                labels = ax.set_yticklabels(x,
                    fontsize = 6,    #  Размер шрифта
                    color = 'b',    #  Цвет текста
                    rotation = 0,    #  Поворот текста
                    verticalalignment =  'center')    #  Вертикальное выравнивание

                fig.set_figwidth(10)
                fig.set_figheight(8)
                plt.gca().invert_yaxis()
                pdf.savefig()
                plt.close()


        # print(df[:15])
        # columnNames = df.iloc[0] 
        # df = df[1:] 
        # df.columns = columnNames
        # # print(feature_df[:20])
        # time_df = time.time() 
        # print("--- %s seconds ---" % (time_df - start_time))
        # analyze_data.to_excel('vk_ml.xlsx')
        
            self.ui.progress_bar_file_ml.setValue(100)
            print("Done!!!!")
            QtWidgets.QMessageBox.information(self, 'Завершено', 'Скачивание pdf файла выполнено')
            return 0

    def get_all_user_info_ml(self, domain, token):
        domain = domain
        token = token
        users_desc = []
        all_ids = []
        users_count = 0
        response = requests.get('https://api.vk.com/method/groups.getMembers?',
                                params={
                                    'access_token': token,
                                    'v': version,
                                    'group_id': domain,
                                    'count': 1
                                }
                                )
        print(response)
        count_items = response.json()['response']['count']
        # print(count_items)

        async def get_ids(session, url):
            async with session.get(url) as resp:
                users = await resp.json()
                return users['response']['items']


        async def main():

            async with aiohttp.ClientSession() as session:

                tasks = []
                count = 100
                for offset in range(0, count_items, count):
                    url = f'https://api.vk.com/method/groups.getMembers?access_token={token}&v={version}&group_id={domain}&count={count}&offset={offset}'
                    tasks.append(asyncio.ensure_future(get_ids(session, url)))

                all_users = await asyncio.gather(*tasks)
                for user in all_users:
                    all_ids.extend(user)

        asyncio.run(main())
        # print("--- %s seconds ---" % (time.time() - start_time))
        print("got: " ,len(all_ids))
        # print(all_ids[:150])

    # commented 


        async def get_info(session, url, id, all_ids):
            async with session.get(url) as resp:
                users = await resp.json()
                index = int((all_ids.index(id) *100) / len(all_ids))
                self.ui.progress_bar_data_ml.setValue(index)
                user = users['response']

                
                features = {}

                try:
                    banned = user[0]['deactivated']
                except:
                    banned = None
                if banned:
                    features = "banned"
                    return features
                else:
                    has_mobile = 0
                    last_seen = 0
                    links = 0
                    education = 0
                    city = 0
                    has_photo = 0
                    verified = 0
                    personal = 0
                    relatives = 0
                    relation = 0
                    closed = 1
                    site = 0
                    career = 0
                    followers_count = 0
                    closed = 0
                    if user[0]['verified']:
                        features = "verified"
                        return features
                    try:
                        IsClosed = user[0]['is_closed']
                    except:
                        closed = 0
                    if  IsClosed:
                        try :
                            has_photo = user[0]['has_photo']
                        except:
                            has_photo = 0
                        features = "private"
                        return features
                    else:   
                        try:
                            last_seen = user[0]['last_seen']['time']
                        except:
                            last_seen = 0
                        value = datetime.date.fromtimestamp(last_seen)
                        today = datetime.date.today()
                        diff = today - value
                        diff.days
                        try :
                            instagram = user[0]['instagram']
                        except:
                            instagram = None
                        try :
                            facebook = user[0]['facebook']
                        except:
                            facebook = None
                        try :
                            twitter = user[0]['twitter']
                        except:
                            twitter = None
                        try :
                            skype = user[0]['skype']
                        except:
                            skype = None
                        try :
                            study = user[0]['university_name']
                        except:
                            study = None
                        try :
                            school = user[0]['schools']
                        except:
                            school = None
                        try:
                            verified = user[0]['verified']
                        except:
                            verified = None
                        try :
                            has_photo = user[0]['has_photo']
                        except:
                            has_photo = 0
                        try :
                            city = user[0]['city']['title']
                        except:
                            city = None
                        try:
                            personal = user[0]['personal']
                        except:
                            personal = None
                        try:
                            relation = user[0]['relation']
                        except:
                            relation = None
                        try:
                            relatives = user[0]['relatives']
                        except:
                            relatives = None
                        try:
                            site = user[0]['site']
                        except:
                            site = None
                        try:
                            career = user[0]['career']
                        except:
                            career = None
                        try:
                            followers_count = user[0]['followers_count']
                        except:
                            followers_count = 358
                        try:
                            user['can_access_closed']
                        except:
                            closed = 100
                        if instagram or facebook or skype or twitter:
                            links = 1
                        else:
                            links = 0
                        if study or school:
                            education = 1
                        else:
                            education = 0
                        
                        if personal or relation :
                            personal = 1
                        else:
                            personal = 0
                        if site :
                            site = 1
                        else:
                            site = 0
                        if career :
                            career = 1
                        else:
                            career = 0
                        if city:
                            city = 1
                        else:
                            city = 0

                        

                        try :
                            count_photos = user[0]['counters']['photos']
                        except:
                            count_photos = 0
                        try :
                            count_pages = user[0]['counters']['pages']
                        except:
                            count_pages = 0
                        try :
                            count_albums = user[0]['counters']['albums']
                        except:
                            count_albums = 0
                        try :
                            count_videos = user[0]['counters']['videos']
                        except:
                            count_videos = 0
                        try :
                            count_audios = user[0]['counters']['audios']
                        except:
                            count_audios = 0
                        try :
                            count_user_videos = user[0]['counters']['user_videos']
                        except:
                            count_user_videos = 0


                            

                        # try :
                        #     count_friends = count_user_friends['count']
                        # except:
                        #     count_friends = None







                        features = {}

                        features["IsCity"] = city
                        features["IsProfile"] = personal
                        features["IsLinks"] = links
                        
                        features["PhotoCount"] = count_photos
                        features["PagesCount"] = count_pages
                        features["FollowersCount"] = followers_count
                        features["AlbumsCount"] = count_albums
                        features["VideosCount"] = count_videos
                        features["AudiosCount"] = count_audios
                        features["OfflineDays"] = diff.days
                        features["HasPhoto"] = has_photo
                        features["Site"] = site
                        features["Career"] = career
                        features["Education"] = education


                        try :
                            bdate = user[0]['bdate']
                        except:
                            bdate = None

                        try :
                            sex = user[0]['sex']
                        except:
                            sex = None
                        
                        try :
                            city = user[0]['city']['title']
                        except:
                            city = None
                        
                        try :
                            country = user[0]['country']['title']
                        except:
                            country = None

                        # analyze = {}
                        features['country'] = country
                        features['city'] = city
                        features['sex'] = sex
                        features['bdate'] = bdate

                        

                    # добавить соотношение друзья/подписчики
                    # try:
                    #     features["following_followers_ratio"] = round(
                    #             count_user_friends / followers_count, 7)
                    # except ZeroDivisionError:
                    #     features["following_followers_ratio"] = 2.8624688005235597

                    # добавить соотношение друзья/фото
                    # try:
                    #     features["following_photos_ratio"] = round(
                    #             count_user_friends / count_photos, 7)
                    # except ZeroDivisionError:
                    #     features["following_photos_ratio"] = 48.6537926973262

                    # # добавить соотношение подписчики/фото
                    # try:
                    #     features["followers_photos_ratio"] = round(
                    #         followers_count / count_photos, 7)
                    # except ZeroDivisionError:
                    #     features["followers_photos_ratio"] = 118.71968859411763
                    
            url_f = f'https://api.vk.com/method/friends.get?access_token={token}&v={version}&user_id={id}'
            async with session.get(url_f) as resp:
                users = await resp.json()
                try:
                    count_user_friends = users['response']['count']
                except:
                    count_user_friends = 150
                features["FriendCount"] = count_user_friends
                
                try:
                    features["following_followers_ratio"] = round(
                            count_user_friends / followers_count, 7)
                except ZeroDivisionError:
                    features["following_followers_ratio"] = 2.8624688005235597
                
                try:
                    features["following_photos_ratio"] = round(
                            count_user_friends / count_photos, 7)
                except ZeroDivisionError:
                    features["following_photos_ratio"] = 48.6537926973262

                # добавить соотношение подписчики/фото
                try:
                    features["followers_photos_ratio"] = round(
                        followers_count / count_photos, 7)
                except ZeroDivisionError:
                    features["followers_photos_ratio"] = 118.71968859411763
            
            
                # analyze['friends_count'] = features["FriendCount"]
            return features

        all_ids_info = []

        fields = [ " has_mobile, contacts, last_seen, connections, education, city, counters, country, realtion, sex, bdate, has_photo,  fields, verified, personal, relatives, relation, schools, site, career, followers_count "]

        async def main_info(all_ids):
            self.ui.progress_bar_id_ml.setValue(100)
            # if len(all_ids) > 50_000:
            #     for i in range(0, len(all_ids),50_000):
            #         if i + 50_000 > len(all_ids):
            #             ids = all_ids[i:]
            #         else:
            #             ids = all_ids[i:i+50_000]
            #         print("i")
            async with aiohttp.ClientSession() as session:

                tasks = []
                for id in all_ids:
                    
                    url = f'https://api.vk.com/method/users.get?access_token={token}&v={version}&user_ids={id}&fields={fields}'
                    tasks.append(asyncio.ensure_future(get_info(session, url, id, all_ids)))

                all_users_info = await asyncio.gather(*tasks)
                for user_info in all_users_info:
                    all_ids_info.append(user_info)
        if len(all_ids) > 50_000:
            for i in range(0, len(all_ids),50_000):
                if i + 50_000 > len(all_ids):
                    ids = all_ids[i:]
                else:
                    ids = all_ids[i:i+50_000]
                # print("i")

                asyncio.run(main_info(ids))
        else:
            asyncio.run(main_info(all_ids))

        # print(all_ids_info[:100])
        self.ui.progress_bar_data_ml.setValue(100)
        return all_ids_info


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    myapp = MyWin()
    myapp.show()

    sys.exit(app.exec_())

