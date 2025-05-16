
import Core.Controller
import Config.Locale
import Gui.HomeInterface
import Log.SetupLogger

import sys
import os

# os.environ["QT_WAYLAND_SHELL_INTEGRATION"] = "kde-shell"  # 强制 KDE 集成


 
def config_folder_detection():
    if os.path.isfile('./config/user_conf.json'):
        pass
    else:
        exit('Cannot_find_config')


if __name__ == '__main__':


    config_folder_detection()
    print("\n")
    # print(Core.Controller.hasInitialized())
    print('User locale is '+Config.Locale.GetSystemLang.get_lang())
    print('User language is '+Config.Locale.load_locale(Config.Locale.GetSystemLang.get_lang()))

    # Core.Controller.WindowManager.Login()
    Core.Controller.WindowManager.Main()
