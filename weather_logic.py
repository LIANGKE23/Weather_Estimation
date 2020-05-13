import pdb

from weather_ui import Ui_Class
import sys
import time
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import *
import requests

from PyQt5.QtChart import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


TIMER_CYCLE = 900
MY_WEATHER_KEY = r"d2ae781d61744d65a2ef2156eef2cb64"    
URL_NOW_WEATHER = r"https://free-api.heweather.net/s6/weather/now?location=auto_ip&key="+MY_WEATHER_KEY 
URL_FOR_WEATHER = r"https://free-api.heweather.net/s6/weather/forecast?location=auto_ip&key="+MY_WEATHER_KEY 

URL_NOW_WEATHER_CID = r"https://free-api.heweather.net/s6/weather/now?location="
URL_FOR_WEATHER_CID = r"https://free-api.heweather.net/s6/weather/forecast?location="
URL_TAIL_CID = r"&key="+MY_WEATHER_KEY

g_cid = ""


class Update_Thread(QThread):

    wt_up_now_sig = pyqtSignal(str, str, str, int)  
    wt_up_oth_sig = pyqtSignal(int, str, str, int) 
    wt_up_gra_sig = pyqtSignal(list)
    tray_message_sig = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.working = True
        self.isManuMode = False 
        self.url_now=URL_NOW_WEATHER
        self.url_forecast=URL_FOR_WEATHER
        self.bad_wea=["Light Rain","Moderate Rain","Heavy Rain","Shower Rain","Thundershower","Storm","Heavy Storm","Severe Storm","Light to moderate rain","Moderate to heavy rain","Heavy rain to storm","Storm to heavy storm","Rain"]
        
        self.tem = []
        self.is_bad = False
        self.time_list = []
        

    def __is_bad_weather(self, wae_str):
        if wae_str in self.bad_wea:
            return 1
        else:
            return 0
                 
    def run(self):
        if self.isManuMode==False:
            self.url_now      = URL_NOW_WEATHER
            self.url_forecast = URL_FOR_WEATHER
        else:
            global g_cid
            self.url_now = URL_NOW_WEATHER_CID + g_cid + URL_TAIL_CID
            self.url_forecast = URL_FOR_WEATHER_CID + g_cid + URL_TAIL_CID
                
        while self.working == True:
            try:
                self.try_msg_str=""
                rs_we = requests.get(self.url_now).json()


                city_name = rs_we["HeWeather6"][0]["basic"]["admin_area"] + " - " + rs_we["HeWeather6"][0]["basic"]["parent_city"] + " - " +rs_we["HeWeather6"][0]["basic"]["location"]
                print(city_name)
                time_info = rs_we["HeWeather6"][0]["update"]["loc"]
                self.time_list.append(time_info[:10])
                wea_info_str = rs_we["HeWeather6"][0]["now"]["cond_txt"]
                weat_info = ('Weather: ' + wea_info_str + "  " + str(round(int(rs_we["HeWeather6"][0]["now"]["tmp"]) * 9 / 5 + 32)) + "F  "+ "Wind: " + 
                            rs_we["HeWeather6"][0]["now"]["wind_dir"] + "  " + rs_we["HeWeather6"][0]["now"]["wind_sc"] + " level")
                self.tem.append(int(rs_we["HeWeather6"][0]["now"]["tmp"]))
                detag = self.__is_bad_weather(wea_info_str)
                self.is_bad = detag

                if detag == 1:

                    self.wt_up_now_sig.emit(city_name, weat_info, time_info, 1)
                    self.try_msg_str = "Current Weather" + " :  " + wea_info_str
                else:
                    self.wt_up_now_sig.emit(city_name, weat_info, time_info, 0)
                

                rs_we = requests.get(self.url_forecast).json()



                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][0]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][0]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(0, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(0, weat_info, time_info, 0)


                time_info = rs_we["HeWeather6"][0]["daily_forecast"][1]["date"]
                wea_info_str = rs_we["HeWeather6"][0]["daily_forecast"][1]["cond_txt_d"]
                weat_info = ('Weather: ' + wea_info_str + "  " + 
                            str(round(int(rs_we["HeWeather6"][0]["daily_forecast"][1]["tmp_min"]) * 9 / 5 + 32)) + " ~ " + 
                            str(round(int(rs_we["HeWeather6"][0]["daily_forecast"][1]["tmp_max"]) * 9 / 5 + 32)) + "F  " + 'Wind: ' + 
                            rs_we["HeWeather6"][0]["daily_forecast"][1]["wind_dir"] + " " + 
                            rs_we["HeWeather6"][0]["daily_forecast"][1]["wind_sc"] + " level")
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][1]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][1]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(1, weat_info, time_info, 1)

                    if len(self.try_msg_str)>5:   
                        self.try_msg_str = self.try_msg_str + "\n" + time_info + " :  " + wea_info_str
                    else:
                        self.try_msg_str = time_info + " :  " + wea_info_str
                else:
                    self.wt_up_oth_sig.emit(1, weat_info, time_info, 0)
                    

                time_info = rs_we["HeWeather6"][0]["daily_forecast"][2]["date"]
                wea_info_str = rs_we["HeWeather6"][0]["daily_forecast"][2]["cond_txt_d"]
                weat_info = ('Weather: ' + wea_info_str + "  " + 
                            str(round(int(rs_we["HeWeather6"][0]["daily_forecast"][2]["tmp_min"]) * 9 / 5 + 32)) + " ~ " + 
                            str(round(int(rs_we["HeWeather6"][0]["daily_forecast"][2]["tmp_max"]) * 9 / 5 + 32)) + "F  " + 'Wind: ' + 
                            rs_we["HeWeather6"][0]["daily_forecast"][2]["wind_dir"] + " " + 
                            rs_we["HeWeather6"][0]["daily_forecast"][2]["wind_sc"] + " level")
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][2]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][2]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(2, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(2, weat_info, time_info, 0)

                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][3]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][3]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(3, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(3, weat_info, time_info, 0)


                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][4]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][4]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(4, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(4, weat_info, time_info, 0)
                

                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][5]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][5]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(5, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(5, weat_info, time_info, 0)


                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][6]["tmp_min"]))
                self.tem.append(int(rs_we["HeWeather6"][0]["daily_forecast"][6]["tmp_max"]))
                detag = self.__is_bad_weather(wea_info_str)
                if detag == 1:
                    self.wt_up_oth_sig.emit(6, weat_info, time_info, 1)
                else:
                    self.wt_up_oth_sig.emit(6, weat_info, time_info, 0)


                self.tray_message_sig.emit(self.try_msg_str)
                time.sleep(TIMER_CYCLE)  

            except Exception as e:
                pass
    

class Weather_Class(QObject):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Class()
        self.up_thread = Update_Thread()
    

    def up_now_wea(self, str_city, str_wea, str_time, bad_tag):
        # self.ui.update_location(str_city)
        if bad_tag==1:
            self.ui.set_now_weathercolor("red")
        else:
            self.ui.set_now_weathercolor("blue")
        self.ui.update_now_weather(str_wea)
        self.ui.update_time(str_time)
        self.ui.set_bad(self.up_thread.is_bad)
        self.ui.set_time(self.up_thread.time_list)
    

    def up_otr_wea(self, index, str_wea, str_time, bad_tag):
        if index==1:    
            self.ui.set_label(1, str_time)
            if bad_tag==1:
                self.ui.set_otr_weathercolor(1, "red")
            else:
                self.ui.set_otr_weathercolor(1, "blue")
            self.ui.update_1_weather(str_wea)
        elif index == 2:
            self.ui.set_label(2, str_time)
            if bad_tag==1:
                self.ui.set_otr_weathercolor(2, "red")
            else:
                self.ui.set_otr_weathercolor(2, "blue")
            self.ui.update_2_weather(str_wea)
        elif index == 6:
            if len(self.up_thread.tem) <= 15:
                self.ui.set_graph_tem(self.up_thread.tem)

    def slot_btn(self, isManu):
        if isManu==False: 
            self.up_thread.isManuMode = False
        else:
            self.up_thread.isManuMode = True
            global g_cid
            g_cid = self.ui.get_cid()
        time.sleep(0.5)
        self.up_thread.start()

    def update_wea_ui(self):
        self.up_thread.wt_up_now_sig.connect(self.up_now_wea)
        self.up_thread.wt_up_oth_sig.connect(self.up_otr_wea)
        #self.up_thread.wt_up_gra_sig.connect(self.wt_up_gra_wea)
        self.up_thread.tray_message_sig.connect(self.ui.tray_msg_show)
        self.ui.click_btn_sig.connect(self.slot_btn)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    wea = Weather_Class()
    wea.update_wea_ui()
    

    sys.exit(app.exec_())