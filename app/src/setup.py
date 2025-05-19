#!/usr/bin/python3

import os
import shutil

import Core.Controller
import Log.SetupLogger

CWD = os.getcwd()

class FolderMkdir():


    def log_folder_mkdir():
        '''创建日志文件夹'''
        try:
            if not os.path.exists(f'{CWD}/log'):
                os.mkdir('log')
                Log.SetupLogger.mkdir_success("Log Folder")
            else:
                Log.SetupLogger.mkdir_skipped("Log Folder")
        except PermissionError:
            Log.SetupLogger.mkdir_failure("Log Folder", "Permission_denied")


    def config_folder_mkdir():
        '''创建配置文件夹'''
        try:
            if not os.path.exists(f'{CWD}/config'):
                os.mkdir('config')
                Log.SetupLogger.mkdir_success("Config Folder")
            else:
                Log.SetupLogger.mkdir_skipped("Config Folder")
        except PermissionError:
            Log.SetupLogger.mkdir_failure("Config Folder", "Permission_denied")

class FileGeneration():

    def config_generation():
        '''复制默认配置文件'''
        try:
            shutil.copy(f'{CWD}/app/res/default_config.json',f'{CWD}/config/user_conf.json')

            Log.SetupLogger.makefile_success("Config Generated")
        except PermissionError:
            Log.SetupLogger.makefile_failure("Config Generated", "Permission_denied")



if __name__ == '__main__':

    Log.SetupLogger.start_setup()

    FolderMkdir.config_folder_mkdir()
    FolderMkdir.log_folder_mkdir()
    FileGeneration.config_generation()

    Core.Controller.WindowManager.init_app()
    Core.Controller.WindowManager.show_setup()
    Core.Controller.WindowManager._app.exec()
