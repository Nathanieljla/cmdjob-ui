# Only needed for access to command line arguments
import sys
import os
import pickle

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtUiTools import *
from shiboken2 import wrapInstance

import core


class Main_Window(QWidget):    
    def __init__(self, ui_file, *args, **kwargs):
        super(Main_Window, self).__init__(*args, **kwargs)
        self.save_path = ''
        
        loader = QUiLoader()
        file = QFile(ui_file)
        file.open(QFile.ReadOnly)
        #We set None here for the parent, otherwise things like dialog will close the app
        self.ui = loader.load( file, None )  
        file.close()
        
        int_validator = QIntValidator(self)
        self.ui.start_frame_value.setValidator(int_validator)
        
        int_validator = QIntValidator(self)
        self.ui.end_frame_value.setValidator(int_validator)
        
        int_validator = QIntValidator(1, 100, self)
        self.ui.task_size_value.setValidator(int_validator)
        
        int_validator = QIntValidator(self)
        self.ui.port_value.setValidator(int_validator)
        
        self.file_data = core.File_Data()

        #pick events
        self.ui.maya_scene_pick.pressed.connect(self.on_pick_maya_scene)
        self.ui.renderer_pick.pressed.connect(self.on_pick_renderer)
        self.ui.backburner_pick.pressed.connect(self.on_pick_backburner)
        
        #menu events
        self.ui.action_save.triggered.connect(self.on_save)
        self.ui.action_load.triggered.connect(self.on_load)
        
        #press events
        self.ui.submit_job_button.clicked.connect(self.on_submit_job)
                
        ##Lets keep things simple and just pull the data when it's required vs. keeping the back-end in sync
        ##string events
        #self.ui.job_name_value.editingFinished.connect(lambda : self.on_str_value_changed(self.ui.job_name_value))
        #self.ui.description_value.editingFinished.connect(lambda : self.on_str_value_changed(self.ui.description_value))
        #self.ui.manager_name_value.editingFinished.connect(lambda : self.on_str_value_changed(self.ui.manager_name_value))
        
        ##int events
        #self.ui.priority_value.editingFinished.connect(lambda : self.on_int_value_changed(self.ui.priority_value))
        #self.ui.start_frame_value.editingFinished.connect(lambda : self.on_int_value_changed(self.ui.start_frame_value))
        #self.ui.end_frame_value.returnPressed.connect(lambda : self.on_int_value_changed(self.ui.end_frame_value))
        #self.ui.task_size_value.returnPressed.connect(lambda : self.on_int_value_changed(self.ui.task_size_value))
        #self.ui.port_value.returnPressed.connect(lambda : self.on_int_value_changed(self.ui.port_value))



    def write_data(self):
        self.file_data.job_name_value = self.ui.job_name_value.text()
        self.file_data.description_value = self.ui.description_value.text()
        self.file_data.priority_value = self.ui.priority_value.value()
        self.file_data.start_frame_value = int(self.ui.start_frame_value.text())
        self.file_data.end_frame_value = int(self.ui.end_frame_value.text())
        self.file_data.task_size_value = int(self.ui.task_size_value.text())
        self.file_data.manager_name_value = self.ui.manager_name_value.text()
        self.file_data.port_value = int(self.ui.port_value.text())
        
        self.file_data.maya_scene_value = self.ui.maya_scene_value.text()
        self.file_data.renderer_value = self.ui.renderer_value.text()
        self.file_data.backburner_value =self.ui.backburner_value.text()     
        

    def read_data(self):
        current_value = self.blockSignals (True)
        
        self.ui.job_name_value.setText(self.file_data.job_name_value)
        self.ui.description_value.setText(self.file_data.description_value)
        self.ui.priority_value.setValue(self.file_data.priority_value)
        self.ui.start_frame_value.setText( str(self.file_data.start_frame_value) ) 
        self.ui.end_frame_value.setText( str(self.file_data.end_frame_value) )
        self.ui.task_size_value.setText( str(self.file_data.task_size_value) )
        self.ui.manager_name_value.setText(self.file_data.manager_name_value)
        self.ui.port_value.setText( str(self.file_data.port_value) )
        
        self.ui.maya_scene_value.setText(self.file_data.maya_scene_value)
        self.ui.renderer_value.setText(self.file_data.renderer_value)
        self.ui.backburner_value.setText(self.file_data.backburner_value)
        
        self.blockSignals(current_value)

        
        
    def set_maya_scene(self, file_path):
        self.file_data.maya_scene_value = file_path
        #Setting our data might now work
        if file_path != self.file_data.maya_scene_value:
            file_path = self.file_data.maya_scene_value
            
        self.ui.maya_scene_value.setText(file_path)
        filename = os.path.basename(file_path).split('.')[0]
        job_name = '{0}-{1}'.format(os.getlogin(), filename)
        self.ui.job_name_value.setText(job_name)
        
    #def on_int_value_changed(self, widget):
        #value = widget.text()
        #print('{0}\'s new value:{1}'.format(widget.objectName(), value))

        #self.file_data.__dict__[widget.objectName()] = int(value)
        #print(self.file_data.__dict__[widget.objectName()])
        
        
    #def on_str_value_changed(self, widget):
        #value = widget.text()
        #print('{0}\'s new value:{1}'.format(widget.objectName(), value))

        #self.file_data.__dict__[widget.objectName()] = value
        #print(self.file_data.__dict__[widget.objectName()])

    
    def on_pick_maya_scene(self):
        file_path, file_filter = QFileDialog.getOpenFileName(self.ui, 'Pick Maya Scene', QDir.currentPath(), 'Maya Scenes (*.ma *.mb)')
        if file_path:
            self.set_maya_scene(file_path)
            
    def on_pick_renderer(self):
        file_path, file_filter = QFileDialog.getOpenFileName(self.ui, 'Pick Render EXE', QDir.currentPath(), 'EXE (*.exe)')
        if file_path:
            self.file_data.renderer_value = file_path
            #Setting our data might now work
            if file_path != self.file_data.renderer_value:
                file_path = self.file_data.renderer_value
                
            self.ui.renderer_value.setText(file_path)
            
            
    def on_pick_backburner(self):
        file_path, file_filter = QFileDialog.getOpenFileName(self.ui, 'Pick Backbuner cmdjob EXE', QDir.currentPath(), 'EXE (*.exe)')
        if file_path:
            self.file_data.backburner_value = file_path
            #Setting our data might now work
            if file_path != self.file_data.backburner_value:
                file_path = self.file_data.backburner_value
                
            self.ui.backburner_value.setText(file_path)
                
            
    def on_save(self, *args, **kwargs):
        start_path = QDir.currentPath()
        _maya_scene_path = self.ui.maya_scene_value.text()
        if not self.save_path and _maya_scene_path:
            start_path = os.path.dirname(_maya_scene_path)
            
        file_path, file_filter = QFileDialog.getSaveFileName(self.ui, 'Save Cmdjob', start_path, 'cmdjob (*.cjob)')
        if file_path:
            self.write_data()
            print(file_path)
            try: 
                file = open(file_path, 'wb')
                pickle.dump(self.file_data, file)
                file.close()
                self.save_path = file_path
            except Exception as e:
                print('save failed')
            
     
    def on_load(self):
        file_path, file_filter = QFileDialog.getOpenFileName(self.ui, 'Load Scene', QDir.currentPath(), 'cmdjob (*.cjob)')
        data = None
        if file_path:
            try:
                file = open(file_path, 'rb')
                data = pickle.load(file)
                file.close()
            except Exception as e:
                print('failed to load data {0}'.format(e))
                
            if data:
                self.file_data = data
                self.read_data()
                self.save_path = file_path
                
                
    def on_submit_job(self):
        if not self.save_path:
            reply = QMessageBox.question(None, 'Save First', 'Would you like to save your config file?') #)
            if reply is QMessageBox.StandardButton.Yes:
                try:
                    self.on_save()
                except Exception as e:
                    print('save failed. Continuing to send command.\nError:{0}'.format(e))
        
        self.write_data()
        self.file_data.send_cmd()
        

def main():
    # You need one (and only one) QApplication instance per application.
    # Pass in sys.argv to allow command line arguments for your app.
    # If you know you won't use command line arguments QApplication([]) works too.
    app = QApplication(sys.argv)
    
    # Create a Qt widget, which will be our window.
    ui_file = os.path.join( os.path.dirname(__file__), r'interface.ui' )
    window = Main_Window(ui_file)
    window.ui.show()
    
    # Start the event loop.
    app.exec_()
    print('app.closed')


if __name__ == '__main__':
    main()
        