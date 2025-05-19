
import Core.Controller
import Config.Locale
import Gui.HomeInterface
import Log.DevelopLogger
import Log.SetupLogger


import sys
import os

# os.environ["QT_WAYLAND_SHELL_INTEGRATION"] = "kde-shell"  # 强制 KDE 集成


 
def config_folder_detection():
    if os.path.isfile('./config/user_conf.json'):
        pass
    else:
        exit('Cannot_find_config')

def developer_info():
    Log.DevelopLogger.developer_info('Initialized: '+Core.Controller.hasInitialized())
    Log.DevelopLogger.developer_info('User locale is '+Config.Locale.GetSystemLang.get_lang())
    Log.DevelopLogger.developer_info('User language is '+Config.Locale.load_locale(Config.Locale.GetSystemLang.get_lang()))

if __name__ == '__main__':

    config_folder_detection()

    developer_info()

    Core.Controller.WindowManager.init_app()
    Core.Controller.WindowManager.show_login()
    Core.Controller.WindowManager._app.exec()
    # Core.Controller.WindowManager.Main()
