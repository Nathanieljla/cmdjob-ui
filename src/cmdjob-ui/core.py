
# Only needed for access to command line arguments
import sys
import os
import subprocess
import tempfile
import re

from PySide2.QtCore import *
from PySide2.QtWidgets import *
from PySide2.QtGui import *


class File_Data(object):
    def __init__(self):
        self.verify_paths = False
        self.job_name_value = ''
        self.description_value = ''
        self.priority_value = 50
        self.start_frame_value = 0
        self.end_frame_value = 100
        self.task_size_value = 2
        self.manager_name_value = r'MD2626-63608I'
        self.port_value = 0
        
        #protected by properties
        self._maya_scene_value = ''
        self._renderer_value = r'C:/Program Files/Autodesk/Maya2023/bin/Render'
        self._backburner_value = r'C:/Program Files (x86)/Autodesk/Backburner/cmdjob.exe'
        
        
    def __set_if_valid(self, var, value):
        """
        unified logic for setting variables that are dependent
        on being a valid os.path.  Seems too basic, but don't
        these things already expand? :)
        """
        if os.path.exists(value):
            var = value

    @property
    def maya_scene_value(self):
        return self._maya_scene_value
    
    @maya_scene_value.setter
    def maya_scene_value(self, value):
        if not self.verify_paths:
            self._maya_scene_value = value
        else:
            self.__set_if_valid(self._maya_scene_value, value)
  
  
    @property
    def renderer_value(self):
        return self._renderer_value
    
    @renderer_value.setter
    def renderer_value(self, value):
        if not self.verify_paths:
            self._renderer_value = value
        else:
            self.__set_if_valid(self._renderer_value, value)     
    
    @property
    def backburner_value(self):
        return self._backburner_value
    
    @backburner_value.setter
    def backburner_value(self, value):
        if not self.verify_paths:
            self._backburner_value = value
        else:
            self.__set_if_valid(self._backburner_value, value)
            
        
    @staticmethod    
    def run_shell_command(cmd, description):
        #NOTE: don't use subprocess.check_output(cmd), because in python 3.6+ this error's with a 120 code.
        print('\n{0}'.format(description))
        print('Calling shell command: {0}'.format(cmd))

        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        stdout = stdout.decode()
        stderr = stderr.decode()
        
        print(stdout)
        print(stderr)
        if proc.returncode:
            raise Exception('Command Failed:\nreturn code:{0}\nstderr:\n{1}\n'.format(proc.returncode, stderr))
        
        return(stdout, stderr)
        
        
    def _find_project_root(self, current_path):
        curent_dir = os.path.dirname(current_path)
        #this means we've hit the top of our file path
        if curent_dir == current_path:
            print("File doesn't seem to be in valid Maya Project Structure !")
            return ''
        
        if os.path.exists(os.path.join(curent_dir, 'workspace.mel')):
            return curent_dir
        else:
            return self._find_project_root(curent_dir)
        
        
    def get_project_path(self):
        return self._find_project_root(self.maya_scene_value)
        
        
    def get_render_directory(self, project_dir):
        workspace_file = os.path.join(project_dir, 'workspace.mel')
        if not os.path.exists(workspace_file):
            print("Couldn't find workspace.mel file !")
            return ''
        else:
            try:
                mel = open(workspace_file, 'r')
                lines = mel.read()
                mel.close()
            except Exception as e:
                print('couldn\'t read workspace file. Error:{0}'.format(e))
                return ''
            
            for result in re.finditer(r'.*\"images\".*\"(?P<folder>.*)\"', lines):
                resultDict = result.groupdict()
                if resultDict['folder']:
                    return os.path.join(project_dir, resultDict['folder'])
             
            print("Couldnt' find image directory in workspace.mel !")   
            return ''

    def get_renderer_name(self):
        return self.renderer_value.rstrip('.ex')
    
    
    def get_task_list(self):
        frame_delta = self.end_frame_value - self.start_frame_value
        
        start_number = self.start_frame_value
        end_number = 0
        file_lines = ''
        for n in range(0, frame_delta, self.task_size_value):
            end_number = start_number + self.task_size_value - 1
            if end_number > self.end_frame_value:
                end_number = self.end_frame_value
                
            line = 'frames{0}-{1}\t{0}\t{1}\n'.format(start_number, end_number)
            print(line)
            file_lines += line
            start_number = end_number + 1
          
        temp_path = tempfile.gettempdir()
        file_name = os.path.join(temp_path, '{0}.txt'.format(self.job_name_value))
        try:
            my_file = open(file_name, 'w')
            my_file.write(file_lines)
            my_file.close()
        except Exception as e:
            print('Failed to write task list. Error:{0}'.format(e))
            file_name = ''
            
        print(file_name)
        return file_name
            
        
    def send_cmd(self):
        ##https://download.autodesk.com/us/systemdocs/pdf/backburner2011_user_guide.pdf
        project_path = self.get_project_path()
        render_directory = self.get_render_directory(project_path)        
        task_list = self.get_task_list()
        
        if not project_path or not render_directory or not task_list:
            print('Submission failed !')
            return
            
        bb_str = r'{0}&-jobName&{1}&-description&{2}&-manager&{3}&-priority&{4}&-taskList&{5}&-taskName&{6}'.format(
            self.backburner_value, self.job_name_value, self.description_value, self.manager_name_value,
            self.priority_value, task_list, 1
        )
        
        executable_str = '{0}&-r&{1}&-s&%tp2&-e&%tp3&-proj&{2}&-rd&{3}&{4}'.format(
            self.get_renderer_name(), 'file', project_path, render_directory, self.maya_scene_value
        )
        
        cmd = bb_str.split('&') + executable_str.split('&')
        self.run_shell_command(cmd, 'Submitting Backburner Job')
        
