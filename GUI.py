from PyQt5 import uic , QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QComboBox, QMainWindow,QApplication,\
     QRadioButton,QVBoxLayout, QFrame,QHBoxLayout, QVBoxLayout,\
        QStackedWidget, QLabel, QGridLayout, QLineEdit, QPushButton,\
            QStatusBar, QMenuBar, QWidget, QTableWidget, QTabWidget,\
            QTextEdit, QLineEdit, QSpinBox, QMessageBox, QTableView,\
                QSlider, QFormLayout
from PyQt5.QtCore import QTimer, QSize, Qt,\
    QThread, pyqtSignal, pyqtSlot
import sys
import pandas as pd
import numpy as np
from database import *
import random

class TableModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self._data.iloc[index.row(), index.column()]
            return str(value)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])


class UI(QMainWindow):
    q_tabs = {} # this dictionary consists of 
                # {"question number": [tab obj, right ans radio button obj]}
    data_table = [] # [["q", "right ans","ans1","ans2","ans3"]......[][]]
    difficulty = 1
    incomplete_data= False  # this variable act as a flage to prevent 
                            # the program from saveing incomplete data  
                            # taken from Q_table. this flage is used
                            # inside save_t_in_db() and readTableData()

    t_seconds = int(12/difficulty)      # related to the GUI Timer 
    second = t_seconds
    minutes = 0

    scoreT = []
    userScore=0
    user_name = None

    def __init__(self):
        super(UI, self).__init__() # type: ignore

        # load the ui file
        uic.loadUi("UI\\mainwindow.ui", self)

        self.HsTable = Highscore_Table()

        self.ui_components()
        self.btn_action()
        self.fill_table()
        # show the app
        self.show()



        self.q_table_db = Questions_Table()
        self.t_in_l_to_l_in_i() # load data to data_table variable to compare

    def ui_components(self):
        '''defining the GUI component from the "mainwindow.ui" file''' 

        # ------- QStackedWidget ------------------
        self.stackedWidget = self.findChild(QStackedWidget,"stackedWidget")
        self.main_p = self.findChild(QWidget,"main_p")
        self.instru_p = self.findChild(QWidget,"instru_p")
        self.questions_p = self.findChild(QWidget,"questions_p")
        self.setting_p = self.findChild(QWidget,"setting_p")
        self.stackedWidget.setCurrentWidget(self.main_p)


        # ------- Main Menu ------------------ 
        self.start_bn = self.findChild(QPushButton, "start_bn")
        self.sett_bn = self.findChild(QPushButton, "sett_bn")
        self.exit_bn = self.findChild(QPushButton, "exit_bn")
        self.highScore_t = self.findChild(QTableView, "high_sc_table")
        self.name_entery = self.findChild(QLineEdit, "userName")

        # ------ Instructions page ------
        self.begin_bn = self.findChild(QPushButton, "begin_bn")
        self.mmenu_bn2 = self.findChild(QPushButton, "mmenu_bn2")
        self.diffi_indicator =self.findChild(QLabel, "diffi_indicator")
        self.diffi_slider =self.findChild(QSlider, "diffi_slider")


        # ------ Questions page ------
        self.tab_widget = self.findChild(QTabWidget, "Q_tabs")
        self.quit_bn = self.findChild(QPushButton, "quit_bn")
        self.nextQ_bn = self.findChild(QPushButton, "nextQ_bn")
        self.timerLabel = self.findChild(QLabel, "timerLabel")
        self.scoreLabel = self.findChild(QLabel, "Score")

        # ------- Setting page -------
        # ---------- Buttons ---------
        self.mmenu_bn = self.findChild(QPushButton, "mmenu_bn")
        self.addQ_bn = self.findChild(QPushButton, "addQ_bn")
        self.SaveQ_bn = self.findChild(QPushButton, "SaveQ_bn")
        self.delQ_bn = self.findChild(QPushButton, "delQ_bn")
        # ---------- text entery ---------
        self.Q_point = self.findChild(QSpinBox, "point_spinBox")
        self.Q_table = self.findChild(QTableWidget, "Q_tableWidget")

    def btn_action(self):
        # navigation between pages

        self.start_bn.clicked.connect(self.disp_instr_p)
        self.sett_bn.clicked.connect(self.disp_setting_p)
        self.exit_bn.clicked.connect(self.exit_game)
        self.begin_bn.clicked.connect(self.disp_ques_p)
        self.mmenu_bn2.clicked.connect(self.disp_menu_p)
        self.mmenu_bn.clicked.connect(self.disp_menu_p)
        self.quit_bn.clicked.connect(self.disp_menu_p_quit)
        self.addQ_bn.clicked.connect(self.addQ_to_table)
        self.SaveQ_bn.clicked.connect(self.save_t_in_db)
        self.delQ_bn.clicked.connect(self.delQ_from_table)
        self.nextQ_bn.clicked.connect(self.nextQ)

        self.diffi_slider.valueChanged.connect(self.slider_acti)
   
    def disp_menu_p_quit(self):
        # display menu page when menu button clicked
        self.stackedWidget.setCurrentWidget(self.main_p)

        # close tabs of this session
        number_of_tabs =len(self.data_table)
        for i in range(number_of_tabs,-1,-1):
            # looping backward because the index 
            # always change when a tap is removed
            self.tab_widget.removeTab(i)
        self.q_tabs = {}
        self.stopTimer()

    def disp_menu_p(self):
        # display menu page when menu button clicked
        self.loadData_to_t()

        self.stackedWidget.setCurrentWidget(self.main_p)

    def disp_setting_p(self):
        # display setting page when setting button clicked
        self.stackedWidget.setCurrentWidget(self.setting_p)
        self.loadData_to_t() #load data from database if existed

    def disp_ques_p(self):
        # display questions page when begin button clicked
        self.stackedWidget.setCurrentWidget(self.questions_p)
        no_of_questions = len(self.data_table)
        for i in range(no_of_questions):
            self.add_q_tab()

        # deactivating tabs so the focuse is on one question
        for i in range(1,no_of_questions+1):
            self.tab_widget.setTabEnabled(i,False)

        self.add_qns_to_tab()
        self.startTimer()

    def add_qns_to_tab(self):
        '''
        add the questions and answers to the tab
        '''
        dt = self.data_table


        for q_count, row_of_data in enumerate(dt):
            q_count = q_count+1 # because the questions in
                                # the dic start from 1 not 0


            # randonomizing the answers
            b = [x+1 for x in range(4) ]
            pos1 = random.choice(b)
            b.remove(pos1)
            pos2 = random.choice(b)
            b.remove(pos2)
            pos3 = random.choice(b)
            b.remove(pos3)
            pos4 = random.choice(b)
            b.remove(pos4)

            q= QLabel(row_of_data[0])
            ans1 = QRadioButton(row_of_data[pos1])
            ans2 = QRadioButton(row_of_data[pos2])
            ans3 = QRadioButton(row_of_data[pos3])
            ans4 = QRadioButton(row_of_data[pos4])
            layout = QFormLayout()
            Q_layout = QVBoxLayout()
            Q_layout.addWidget(ans1)
            Q_layout.addWidget(ans2)
            Q_layout.addWidget(ans3)
            Q_layout.addWidget(ans4)
            layout.addRow(q,Q_layout)
            tabObj = self.q_tabs[f'q{q_count}'][0]  # add the objects created to
                                                    # the tab object which was 
                                                    # stored in the dictionary
            tabObj.setLayout(layout)
            if pos1 == 1:
                right_ans_obj = ans1
            elif pos2 == 1:
                right_ans_obj = ans2
            elif pos3 == 1:
                right_ans_obj = ans3
            elif pos4 == 1:
                right_ans_obj = ans4

            self.q_tabs[f'q{q_count}'].append(right_ans_obj)

    def disp_instr_p(self):
        self.get_user()
        
        if self.user_name != '' and self.user_name != None:
            # display instruction page when start button clicked 
            self.stackedWidget.setCurrentWidget(self.instru_p)

            
            # load the score for each q
            for row in self.data_table:
                self.scoreT.append(row[-1])
        else:
            self.popup_msg('please enter your name',err = 'ERROR',cntnt = 1)
    
    def exit_game(self):
        self.close()
    
    def addQ_to_table(self):
        row_no = self.Q_table.rowCount()
        self.Q_table.setRowCount(row_no+1)
    
    def delQ_from_table(self):
        row_no = self.Q_table.rowCount()
        self.Q_table.setRowCount(row_no-1)

    def loadData_to_t(self):
        
        data = self.q_table_db.get_data()

        # update the table by deleting old record
        # and adding them again from the Database
        if self.Q_table.rowCount() != 0:
            for ii in range(self.Q_table.rowCount()):
                self.delQ_from_table()
        
        for i in range(len(data)):
            self.addQ_to_table()
        # ------- end updating -------

        for count_r, row_of_data in enumerate(data):
            for count_c, item in enumerate(row_of_data):
                if type(item) == int:
                    item = str(item)
                self.Q_table.setItem(count_r,count_c, QtWidgets.QTableWidgetItem(item))

    def t_in_l_to_l_in_i(self):
        '''
        tuble in list to list in list 
        [()]->[[]]
        this is a complementry function to convert 
        the data from the database from tuble inside
        list to list inside list and save the data
        inside the variable data_table in order to
        compare it
        '''
        data = self.q_table_db.get_data()
        for count_r, row_of_data in enumerate(data):
            l = list(row_of_data)
            self.data_table.append(l)

    def save_t_in_db(self):
        '''
        save the data after importing it from the table wadget
        to the database file 
        '''
        self.incomplete_data = False
        db_t = self.readTableData()

        if self.incomplete_data == False and db_t != self.data_table:
            self.data_table = db_t
            self.q_table_db.del_record()
            for i in range(len(db_t)):
                if len(self.data_table) != 0:
                    self.q_table_db.add_question(db_t[i][0],db_t[i][1],\
                        db_t[i][2],db_t[i][3],db_t[i][4],db_t[i][5])
            self.q_table_db.get_data()

    def readTableData(self):
        ''' read table entry and return as a list for each row and all the rows inside on list'''

        rowCount = self.Q_table.rowCount()
        columnCount = self.Q_table.columnCount()
        Q_data=[]
        
        for row in range(rowCount):
            Q_data.insert(row,[])
            for column in range(columnCount):
                widgetItem = self.Q_table.item(row,column)

                if(widgetItem and widgetItem.text):
                    text = widgetItem.text()
                    if column == columnCount-1:
                        try:
                            text = int(text)
                        except:
                            self.incomplete_data= True
                            self.popup_msg(' make sure the you have a number in point flield')

                    Q_data[row].insert(column,text)
                else:
                    self.incomplete_data= True
            
            if columnCount != 0 and self.incomplete_data ==True:
                Q_data.pop()
                self.popup_msg("please don't let any field empty or any empty row otherwise it won't be saved! use delete button to remove any extra field")
                break
        if len(Q_data)==0:
            self.popup_msg('click on add then enter in each field the right input')
        elif len(Q_data)!=0 and self.incomplete_data == False:
            msg = QMessageBox.about(self, "status", "Your data is successfuly saved!")

            
        return Q_data
        
    def fill_table(self):
        new_data_form =[]
        
        data_old = self.HsTable.order_table()

        for count_r, row_of_data in enumerate(data_old):
            l = list(row_of_data)
            new_data_form.append(l)

        data = pd.DataFrame(new_data_form, columns = ['User', 'Highscore'])
        data.index = np.arange(1, len(data) + 1)

        self.model = TableModel(data)
        self.highScore_t.setModel(self.model)

    def slider_acti(self, value):
        _value = str(value)

        if _value == '1':
            self.diffi_indicator.setText('Easy')
            self.diffi_indicator.setStyleSheet("color: green")
            self.difficulty = 1
        elif _value == '2':
            self.diffi_indicator.setText('Normal')
            self.diffi_indicator.setStyleSheet("color: orange")
            self.difficulty = 2
        elif _value == '3':
            self.diffi_indicator.setText('Hard')
            self.diffi_indicator.setStyleSheet("color: red")
            self.difficulty = 3
        else:
            print("something wrong!")
        
        self.t_seconds = int(12/self.difficulty)      # related to the GUI Timer 
        self.second = self.t_seconds

    def add_tab_to_dic(self):
        '''
        create Qtwidget obeject and refere to it with key
        in dictionary and it returns the string (name of tab)
        and the tab object itself
        '''
        dic_lens = len(self.q_tabs)
        dic_tab_name = f'q{dic_lens+1}'
        self.q_tabs[dic_tab_name]= [QWidget()]
        return self.q_tabs[dic_tab_name][0] , dic_tab_name

    def add_q_tab(self):
        tab = self.add_tab_to_dic()
        tab_obj = tab[0]
        tab_name = tab[1]
        self.tab_widget.addTab(tab_obj,tab_name)

    def popup_msg(self,message,err = 'ERROR',cntnt = 1):

        if cntnt == 1:
            msg_content = QMessageBox.Critical
        if cntnt == 2:
            msg_content = QMessageBox.Information

        msg = QMessageBox()
        msg.setIcon(msg_content)
        msg.setText(f"{err}")
        msg.setInformativeText(f'{message}')
        msg.setWindowTitle(f"{err}")
        msg.exec_()

        return msg

    def stopTimer(self):
        self.timer.stop()
        self.timerLabel.setText(f'{self.minutes}:{self.second}')
        self.second = self.t_seconds    
        self.minutes = 0

    def startTimer(self):
        # Timer setting -------------->
        self.timer=QTimer()
        self.timer.timeout.connect(self.timeCounter)
        self.timer.start(1000)

    def timeCounter(self):

        self.second -=1
        if (self.second <= 3):
            text = str(self.minutes) + ':' + str(self.second)
            self.timerLabel.setStyleSheet("color:red")
            self.timerLabel.setText(text)
        else:
            text = str(self.minutes) + ':' + str(self.second)
            self.timerLabel.setStyleSheet("color:green")
            self.timerLabel.setText(text)

        if (self.second == 0):
            text = str(self.minutes) + ':' + str(self.t_seconds)
            self.timerLabel.setStyleSheet("color:green")
            self.timerLabel.setText(text)
            self.nextQ()
        
        # self.second +=1
        # if (self.second == 59):
        #     self.minutes += 1
        #     self.second = 0

    def nextQ(self):
        self.second = self.t_seconds
        
        T_no = self.tab_widget.currentIndex()
        Q_no = T_no + 1
        nextQ_ = Q_no + 1
        if T_no < len(self.data_table)-1:
            result = self.check_ans(Q_no)
            
            self.tab_widget.setTabEnabled(Q_no,True)
            self.tab_widget.setCurrentIndex(Q_no)
            self.tab_widget.setTabEnabled(T_no,False)

        elif T_no == len(self.data_table)-1 and self.second == self.t_seconds:
            result = self.check_ans(Q_no)
            self.stopTimer()
            self.checkWin()
            self.disp_menu_p_quit()

    def check_ans(self, number):
        radio_bn_obj = self.q_tabs[f'q{number}'][1]
        if radio_bn_obj.isChecked() == True:
            self.userScore += (self.scoreT[number-1] * self.difficulty)
            text = 'Score: ' + str(self.userScore)
            self.scoreLabel.setText(text)
            return True
        else:
            return False

    def checkWin(self):
        userScore = self.userScore
        a = sum(self.scoreT)
        
        if userScore >= int(a/2):
            self.popup_msg(f'Congrats your score is {userScore}','YOU WON',2)
            self.HsTable.add_score(self.user_name,userScore)
            self.fill_table()
        else:
            self.popup_msg('you didn\'t pass. try agin','Sorry',2)

    def get_user(self):
        self.user_name = self.name_entery.text()

if __name__ == "__main__":
    # Initialize The App
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()