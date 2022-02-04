import os
import sys
import win32api
import send2trash

reset = "\x1b[0m"


# -= COLORS =-

def color(r, g, b):
    return "\x1b[38;2;" + ";".join([str(r), str(g), str(b)]) + "m"


red = color(255, 90, 90)
blue = color(30, 120, 255)
green = color(90, 255, 90)
gray = color(127, 127, 127)


# -= EXTRA =-

def press_enter():
    input(gray + "\n [Press Enter]" + reset)


def header():
    print(blue + "\n Mutater's Clip Editor" + reset)


def exit_handler(*args):
    os.system("del temp_clip.mp4")
    os.system("del temp_clip2.mp4")


# -= SCREENS =-

def init():
    directory_path = ""
    #os.system("PATH %PATH%;C:\\ffmpeg\\bin")
    
    directory_path = locate_path(" of clips")
    output_path = locate_path(" to output clips")
    
    clips = next(os.walk(directory_path), (None, None, []))[2]
    
    clips = [name for name in clips if name.endswith(".mp4") and not name.count("temp_clip")]
    
    os.chdir(directory_path)
    
    if not clips:
        os.system("cls")
        header()
        print(red + "\n  Directory contains no clips.")
        press_enter()
        return
    
    for file in clips:
        full_path = directory_path + "\\" + file
        
        load_clip(full_path)
        
        if preview_clip(full_path, True):
            continue
        
        while 1:
            clip = edit_clip(directory_path)
            
            preview_clip(full_path)
            
            if trim_save_clip(full_path, output_path):
                break
    
    os.system("cls")
    header()
    print("\n  No more clips detected!")
    press_enter()


def locate_path(append):
    while 1:
        os.system("cls")
        header()
        print("\n  Input " + green + "folder path" + reset + append + ".")
        path = input("\n >>>")
        
        if os.path.isdir(path):
            return path
        else:
            print(red + "\n  The specified directory does not exist." + reset)
            press_enter()


def load_clip(full_path):
    os.system(f'copy "{full_path}" temp_clip.mp4 /y')


def preview_clip(full_path, edit=False):
    os.system("temp_clip.mp4")
    
    if edit:
        while 1:
            os.system("cls")
            header()
            
            print("\n  Previewing original clip '" + full_path + "'")
            print(f'\n  Type "{red}delete{reset}" to delete the clip, press enter to cancel.')
            delete = input("\n >>>")
            
            if delete == "delete":
                send2trash(full_path)
                os.system("del temp_clip.mp4")
                return True
            return False


def edit_clip(directory_path):
    while 1:
        while 1:
            os.system("cls")
            header()
            
            print("\n  Input start " + green + "time (seconds)" + reset + " of subclip.")
            start = input("\n >>>")
            print("\n  Input end " + green + "time (seconds)" + reset + " of subclip.")
            end = input("\n >>>")
            
            try:
                start = int(start)
                duration = int(end) - start
                break
            except:
                print(red + "\n  Start and end times must be inputted as only numbers.")
                press_enter()
        
        while 1:
            try:
                os.system(f'ffmpeg -i temp_clip.mp4 -ss {start} -t {duration} -vcodec h264_amf -b:v 15m temp_clip2.mp4 -y')
                os.system("copy temp_clip2.mp4 temp_clip.mp4 /y")
                os.system("del temp_clip2.mp4")
                press_enter()
                return
            except Exception as e:
                print(red + "\n  Unable to trim video. Were your start and end times within the video bounds?")
                print("\n  " + str(e))
                press_enter()
                break


def trim_save_clip(full_path, output_path):
    while 1:
        os.system("cls")
        header()
        print("\n  Previewing edited clip '" + full_path + "'")
        print("\n  Input the number for the options given below.")
        print(f'\n   1) {green}Save{reset} clip to output directory.')
        print(f'\n   2) {green}Save{reset} clip to output directory and {red}delete{reset} original clip.')
        print(f'\n   3) Do nothing and {blue}retrim{reset} the already edited clip.')
        print(f'\n   4) {red}Reset{reset} the clip to the original state.')
        option = input("\n >>>")
        
        if option in "12":
            while 1:
                print(f'\n  Input the {green}name{reset} for the clip. Make the name Windows-friendly!')
                clip_name = input("\n >>>").replace(".mp4", "")
                clip_name_output_path = ""
                clip_name_no_path = ""
                
                if clip_name.count("\\") > 0 or clip_name.count("/") > 0:
                    clip_name = clip_name.replace("/", "\\")
                    clip_name_no_path = (
                        clip_name
                        .split("\\")
                        [-1:]
                    )
                    clip_name_no_path = "".join(clip_name_no_path)
                    clip_name_output_path = (
                        clip_name
                        .split("\\")
                        [:-1]
                    )
                    clip_name_output_path = output_path + "\\" + "".join(clip_name_output_path) + "\\"
                else:
                    clip_name_no_path = clip_name
                    clip_name_output_path = output_path
                
                overwrite = True
                if clip_name_no_path + ".mp4" in os.listdir(clip_name_output_path):
                    while 1:
                        os.system("cls")
                        header()
                        print(f'\n  File name already taken. {red}Overwrite{reset}? ({green}y{reset}/{red}n{reset})')
                        option = input("\n >>>")
                        
                        if option == "y":
                            break
                        elif option == "n":
                            overwrite = False
                            break
                
                if not overwrite:
                    continue
                
                os.system(f'copy temp_clip.mp4 "{output_path}\{clip_name}.mp4" /y')
                os.system("del temp_clip.mp4")
                if option == "2":
                    send2trash(full_path)
                return True
        elif option == "3":
            return False
        elif option == "4":
            while 1:
                os.system("cls")
                header()
                print(f'\n  Are you sure you want to {red}reset{reset} the clip to its original state? ({green}y{reset}/{red}n{reset})')
                option = input("\n >>>")
                
                if option == "y":
                    load_clip(full_path)
                    preview_clip(full_path)
                    return False
                elif option == "n":
                    break


if __name__ == "__main__":
    os.system("")
    win32api.SetConsoleCtrlHandler(exit_handler, True)
    init()