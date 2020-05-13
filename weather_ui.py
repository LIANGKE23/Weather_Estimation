
import sys
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QApplication, QLineEdit, QDesktopWidget, 
                            QGridLayout, QSystemTrayIcon, QMessageBox, QMenu, QAction, QCheckBox, QDialog, 
                            QVBoxLayout, QHBoxLayout, QComboBox, qApp)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor
from PyQt5.QtCore import *
from PyQt5.QtChart import *
import requests


SEARCH_CITY_URL = r"https://search.heweather.net/find?location="
USR_KEY = r"&key=80aa4504b70a4de4bf27bf4c521dc362"
# SEARCH_GROUP = r"&group=us"


class Ui_Class(QWidget):
    click_btn_sig = pyqtSignal(bool)
    def __init__(self):
        super().__init__()
        self.dg_clicked_flg = True  
        self.usr_define_city = False
        self.usr_def_flag_ret = False
        self.is_bad = False
        self.cid_list = []
        self.city_name_list = []
        self.time_list = []

        self.input = QLabel('Input City', self)
        self.time = QLabel("Current Time",self)
        self.weath= QLabel("Current Weather",self)
        self.weath_1= QLabel("",self)
        self.weath_2= QLabel("",self)
        self.time_line = QLineEdit(self)
        self.time_line.setFixedWidth(120)
        self.weat_line = QLineEdit(self)
        self.weat_line_1 = QLineEdit(self)
        self.weat_line_2 = QLineEdit(self)

        # Chart 
        self.chartView = QChartView()
        self.chart = self.chartView.chart()

        self.setMinimumSize(1000, 600)

        # Image
        self.image = QPixmap('pic/default.jpeg')
        self.label = QLabel()
        self.label.setPixmap(self.image)
        
        self.usr_city_line = QLineEdit(self)
        self.usr_city_line.setFixedWidth(120)
        self.usr_confirm_btn = QPushButton("OK",self)
        
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon('weather.ico'))
        self.trayIcon.activated.connect(self.ico_clicked)

        self.quit_action = QAction("Quit",self,triggered=self.tray_quit)
        self.traymenu = QMenu(self)
        self.traymenu.addAction(self.quit_action)
        self.trayIcon.setContextMenu(self.traymenu)
        
        self.tray_msg_flag = True
        
        self.init_ui()
            
    def tray_quit(self):
        self.trayIcon.setVisible(False)
        qApp.quit()
        
    
    def ico_clicked(self, reason):
        if(reason==QSystemTrayIcon.Trigger or reason==QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.show()
        
    def init_ui(self):
        ui_font = QFont("Times",12)
        self.setFont(ui_font)
        self.resize(480,320)
        self.setWindowTitle("Mini Weather Forecast")
        
        screen_size = QDesktopWidget().screenGeometry()
        app_ui_size = self.geometry()
        self.move((screen_size.width()-app_ui_size.width())/2, (screen_size.height()-app_ui_size.height())/2)
        
        self.time_line.setDisabled(True)
        self.weat_line.setDisabled(True)
        self.weat_line_1.setDisabled(True)
        self.weat_line_2.setDisabled(True)
        self.usr_city_line.setDisabled(False)
        self.usr_confirm_btn.setDisabled(False)
        self.usr_define_city = True
      
        grid = QGridLayout()

        grid.addWidget(self.input, 0, 0)
        grid.addWidget(self.usr_city_line, 0, 1)
        grid.addWidget(self.usr_confirm_btn, 0, 2)

        grid.addWidget(self.time, 1, 0)
        grid.addWidget(self.time_line, 1, 1)
        grid.addWidget(self.weath, 1, 2)
        grid.addWidget(self.weat_line, 1, 3)


        grid.addWidget(self.weath_1, 5, 0, 1, 2)
        grid.addWidget(self.weat_line_1, 5, 1, 1, 3)
        grid.addWidget(self.weath_2, 6, 0)
        grid.addWidget(self.weat_line_2, 6, 1, 1, 3)

        grid.addWidget(self.label,7, 0, 1, 2)

        grid.addWidget(self.chartView, 7, 2, 1, 3)
        
        self.usr_confirm_btn.clicked.connect(self.confirm_btn_click)
        
        self.setLayout(grid)
        self.show()

    def set_time(self,time_list):
        today = time_list[0]
        time_list = ["Today"]
        day = today
        for i in range(6):
            num = int(day[-1])
            num += 1
            num = str(num)
            day = day[:9] + num
            time_list.append(day[5:])
        self.time_list = time_list

    def c2f(self,c):
        f = (c * 9 /5 ) + 32
        return f

    def set_bad(self,is_bad):
        self.is_bad = is_bad

    def set_graph_tem(self,l):
        self.tem = l
        low = QBarSet("Min")
        high = QBarSet("Max")

        print(self.tem)
        self.tem = list(map(self.c2f, self.tem))
        low << self.tem[1] << self.tem[3] <<  self.tem[5] <<  self.tem[7] <<  self.tem[9] << self.tem[11] << self.tem[13]
        high<< self.tem[2] << self.tem[4] <<  self.tem[6] <<  self.tem[8] <<  self.tem[10] <<self.tem[12] << self.tem[14]

        high.setBrush(QColor(255,0,0,127))
        low.setBrush(QColor(0, 100, 255, 127))


        series = QStackedBarSeries()
        series.setLabelsVisible(True)
        series.setLabelsPosition(0)
        series.setLabelsPrecision(2)

        series.append(low)
        series.append(high)


        self.chart.setAnimationOptions(QChart.SeriesAnimations)
        self.chart.addSeries(series)

        ## Axis
        categories = self.time_list
        print(categories)

        axis = QBarCategoryAxis()
        axis.append(categories)
        axis.setTitleText("Day")
        # self.chart.createDefaultAxes()
        self.chart.setAxisX(axis, series)
        # self.chart.axisY().setTitleText("Temperature: C")

        ## image
        cur_tmp = self.tem[0]
        if cur_tmp > 27 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/27U.jpeg')
            else:
                self.image = QPixmap('pic/27.jpeg')
            self.label.setPixmap(self.image)
        elif 17 * 9 / 5 + 32 < cur_tmp <= 27 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/17U.jpeg')
            else:
                self.image = QPixmap('pic/17.jpeg')
            self.label.setPixmap(self.image)
        elif 10 * 9 / 5 + 32 < cur_tmp <= 17 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/10U.jpeg')
            else:
                self.image = QPixmap('pic/10.jpeg')
            self.label.setPixmap(self.image)
        elif 7 * 9 / 5 + 32 < cur_tmp <= 10 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/7U.jpeg')
            else:
                self.image = QPixmap('pic/7.jpeg')
            self.label.setPixmap(self.image)
        elif 5 * 9 / 5 + 32 < cur_tmp <= 7 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/5U.jpeg')
            else:
                self.image = QPixmap('pic/5.jpeg')
            self.label.setPixmap(self.image)
        elif 0 * 9 / 5 + 32 < cur_tmp <= 5 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/0U.jpeg')
            else:
                self.image = QPixmap('pic/0.jpeg')
            self.label.setPixmap(self.image)
        elif -15 * 9 / 5 + 32 < cur_tmp <= -5 * 9 / 5 + 32:
            if self.is_bad:
                self.image = QPixmap('pic/N5U.jpeg')
            else:
                self.image = QPixmap('pic/N5.jpeg')
            self.label.setPixmap(self.image)
        elif cur_tmp < -15 * 9 / 5 + 32:
            self.image = QPixmap('pic/N15.jpeg')
            self.label.setPixmap(self.image)
    
    def update_now_weather(self, str_info):
        self.weat_line.setText(str_info)
    
    def update_time(self, str_info):
        self.time_line.setText(str_info)
    
    def update_1_weather(self, str_info):
        self.weat_line_1.setText(str_info)
        
    def update_2_weather(self, str_info):
        self.weat_line_2.setText(str_info)
    
    def set_now_weathercolor(self, str_color):
        self.weat_line.setStyleSheet("color:"+str_color)
        
    def set_label(self, index, str):
        if index == 1:
            self.weath_1.setText(str)
        elif index == 2:
            self.weath_2.setText(str)
        else:
            pass
     
    def set_otr_weathercolor(self, index, str_color):
        if index==1:
            self.weat_line_1.setStyleSheet("color:"+str_color)
        else:
            self.weat_line_2.setStyleSheet("color:"+str_color)
    
            
    def confirm_btn_click(self):
        if self.usr_define_city==False:
            self.usr_def_flag_ret = False
            self.usr_confirm_btn.setDisabled(True)
            self.manu_check.setDisabled(True)
            self.click_btn_sig.emit(False)
        else:
            self.usr_def_flag_ret = True
            if self.dg_clicked_flg==True:
                self.city_name_list.clear()
                usr_def_city_str = self.usr_city_line.text()
                if len(usr_def_city_str)>0:
                    url_str = SEARCH_CITY_URL+usr_def_city_str+USR_KEY
                    rs_we = requests.get(url_str).json()
                    get_status = rs_we["HeWeather6"][0]["status"]
                    if get_status=="ok":
                        city_num = len(rs_we["HeWeather6"][0]["basic"])
                        city_str_index = 0
                        while(city_str_index<city_num):
                            self.city_name_list.append(rs_we["HeWeather6"][0]["basic"][city_str_index]["admin_area"]+"-"+rs_we["HeWeather6"][0]["basic"][city_str_index]["parent_city"]+"-"+rs_we["HeWeather6"][0]["basic"][city_str_index]["location"])
                            self.cid_list.append(rs_we["HeWeather6"][0]["basic"][city_str_index]["cid"])
                            city_str_index = city_str_index + 1
                        self.showDialog(self.city_name_list)
                    else:
                        QMessageBox.warning(self, "Error", "Cannot find city!")
                else:
                    QMessageBox.warning(self, "Error", "Please input city name!")
            else:
                self.click_btn_sig.emit(True)
                self.dg_clicked_flg=True
    
    def tray_msg_show(self, str_info):
        if len(str_info)>5:    #确保是有效数据
            if self.tray_msg_flag == True:
                self.trayIcon.showMessage("Mini weather Forecast",str_info,QSystemTrayIcon.Information,2000)
            else:
                pass
        else:
            pass
            
    def showDialog(self, city_list):
        vbox=QVBoxLayout()
        hbox=QHBoxLayout()
        self.dialog=QDialog(self)
        self.dialog.resize(100,60)
        self.okBtn=QPushButton("OK")
        self.cancelBtn=QPushButton("Cancel")
        self.okBtn.clicked.connect(self.click_diag_ok_btn)
        self.cancelBtn.clicked.connect(self.click_diag_cancel_btn)
        self.city_cmb = QComboBox(self)
        for ct in city_list:
            self.city_cmb.addItem(ct)

        self.dialog.setWindowTitle("Select City")
        hbox.addWidget(self.okBtn)
        hbox.addWidget(self.cancelBtn)

        vbox.addWidget(self.city_cmb)
        vbox.addLayout(hbox)
        self.dialog.setLayout(vbox)
        
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.exec_()
      
    def click_diag_ok_btn(self):
        select_txt = self.city_cmb.currentText()
        self.usr_city_line.setText(select_txt)
        self.dialog.close()
        self.dg_clicked_flg=False
      
    def click_diag_cancel_btn(self):
        self.dialog.close()
    
    def get_cid(self):
        ret = 0
        index = 0
        usr_cit = self.usr_city_line.text()
        for i in self.city_name_list:
            if usr_cit==i:
                ret = index
                break
            else:
                index = index+1
        return self.cid_list[ret]
        
    def get_usr_define_flg(self):
        return self.usr_define_city
        
    def get_flag(self):
        return self.usr_def_flag_ret
        

