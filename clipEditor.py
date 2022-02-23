import os
import subprocess
import sys
import win32api
from send2trash import send2trash

reset = "\x1b[0m"


# -= COLORS =-

def color(r, g, b):
    return "\x1b[38;2;" + ";".join([str(r), str(g), str(b)]) + "m"


red = color(255, 90, 90)
green = color(90, 255, 90)
blue = color(30, 120, 255)
yellow = color(255, 255, 30)
gray = color(127, 127, 127)


# -= EXTRA =-

def press_enter():
    input(gray + "\n [Press Enter]" + reset)


def header():
    print(blue + "\n Mutater's Clip Editor" + reset)


def exit_handler(*args):
    os.system("del temp_clip.*")
    os.system("del temp_clip2.*")


# -= SCREENS =-

def loop():
    directory_path = ""
    working_directory = os.getcwd() + "\\"
    directory_path = locate_path(" of clips to be edited")
    output_path = locate_path(" to output clips")
    vcodec = open("config.txt", "r").read().split("\n")[0].split("=")[1]
    os.system("PATH %PATH%;" + working_directory)
    
    while 1:
        os.chdir(directory_path)
        
        clips = load_clips(directory_path, working_directory)
        
        if not clips:
            os.system("cls")
            header()
            print(red + "\n  Directory contains no clips.")
            press_enter()
            return
    
        for file in clips:
            full_path = directory_path + "\\" + file
            clip_extension = full_path.split(".")[-1]
            
            load_clip(full_path, clip_extension)
            
            if preview_clip(full_path, clip_extension, output_path, True):
                continue
            
            while 1:
                clip = edit_clip(directory_path, working_directory, clip_extension, vcodec)
                
                preview_clip(full_path, clip_extension)
                
                if trim_save_clip(full_path, output_path, clip_extension):
                    break
    
        os.system("cls")
        header()
        print(f'\n  No more clips detected! {green}Continue{reset} editing in a new location? ({green}y{reset}/{red}n{reset})')
        option = input("\n >>>")
        
        if option == "y":
            directory_path = locate_path(" of clipts to be edited")
            continue
        return
            
        


def locate_path(append):
    while 1:
        os.system("cls")
        header()
        print("\n  Type the " + green + "folder path" + reset + append + ".")
        path = input("\n >>>")
        
        if os.path.isdir(path):
            return path
        else:
            print(red + "\n  The specified directory does not exist." + reset)
            press_enter()


def load_clip(full_path, clip_extension):
    os.system("del temp_clip.*")
    os.system(f'copy "{full_path}" temp_clip.{clip_extension} /y')


def load_clips(directory_path, working_directory):
    clips = next(os.walk(directory_path), (None, None, []))[2]
    
    print("\n  Loading clips...")
    
    for i in range(len(clips)-1, -1, -1):
        try:
            query = subprocess.run(f'"{working_directory}ffmpeg" -i "{clips[i]}"', check=True, capture_output=True).stderr
        except subprocess.CalledProcessError as e:
            query = str(e.stderr)
        
        if "Duration:" not in query or "Duration: N/A" in query:
            clips.pop(i)
    
    print("\n  Done loading clips. If the program stays frozen, try editing config.txt.")
    
    return clips


def preview_clip(full_path, clip_extension, output_path="", edit=False):
    os.system("temp_clip." + clip_extension)
    
    if not edit:
        return
    
    while 1:
        os.system("cls")
        header()
        
        print("\n  Previewing original clip '" + full_path + "'")
        print("\n  Input the number for an option below.")
        print(f'\n   1) {blue}Edit{reset} the clip.')
        print(f'\n   2) {yellow}Continue{reset} without editing.')
        print(f'\n   3) {red}Delete{reset} the clip.')
        option = input("\n >>>")
        
        if option == "1":
            return False
        elif option == "2":
            if trim_save_clip(full_path, output_path, clip_extension):
                return True
            return False
        elif option == "3":
            send2trash(full_path)
            return True


def edit_clip(directory_path, working_directory, clip_extension, vcodec):
    while 1:
        while 1:
            os.system("cls")
            header()
            
            print(f'\n  Input start {green}time (seconds){reset} of subclip.')
            start = input("\n >>>")
            print(f'\n  Input end {green}time (seconds){reset} of subclip. Press enter to {red}cancel{reset}.')
            end = input("\n >>>")
            
            if end == "":
                continue
            
            try:
                start = float(start)
                duration = float(end) - start + 1
                break
            except:
                print(red + "\n  Input must be only numbers, e.g. '5' or '2.3' without quotes.")
                press_enter()
        
        while 1:
            try:
                os.system(f'"{working_directory}ffmpeg" -i temp_clip.{clip_extension} -ss {start} -t {duration} -vcodec {vcodec} -b:v 15m temp_clip2.{clip_extension} -y')
                os.system(f'copy temp_clip2.{clip_extension} temp_clip.{clip_extension} /y')
                os.system("del temp_clip2.*")
                press_enter()
                return
            except Exception as e:
                print(red + "\n  Unable to trim video; start and duration were incorrect or another error occured.")
                print("\n  " + str(e))
                press_enter()
                break


def trim_save_clip(full_path, output_path, clip_extension):
    while 1:
        os.system("cls")
        header()
        print("\n  Previewing edited clip '" + full_path + "'")
        print("\n  Input the number for an option below.")
        print(f'\n   1) {green}Save{reset} the clip.')
        print(f'\n   2) {green}Save{reset} the clip and {red}delete{reset} the original clip.')
        print(f'\n   3) {yellow}Undo changes{reset} to the clip.')
        option = input("\n >>>")
        
        if option in "12":
            while 1:
                print(f'\n  Input the name for the clip. Make the name {green}Windows-friendly{reset}!')
                print(f'  NOTE: {red}Don\'t{reset} include the file extension.')
                clip_name = input("\n >>>")
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
                    clip_name_output_path = output_path + "\\" + "\\".join(clip_name_output_path) + "\\"
                else:
                    clip_name_no_path = clip_name
                    clip_name_output_path = output_path
                
                overwrite = True
                
                try:
                    os.listdir(clip_name_output_path)
                except:
                    print(f'\n  {red}Directory path does not exist.{reset}')
                    press_enter()
                    os.system("cls")
                    header()
                    continue
                
                if clip_name_no_path + "." + clip_extension in os.listdir(clip_name_output_path):
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
                
                os.system(f'copy temp_clip.{clip_extension} "{output_path}\{clip_name}.{clip_extension}" /y')
                os.system("del temp_clip." + clip_extension)
                if option == "2":
                    send2trash(full_path)
                return True
        elif option == "3":
            while 1:
                os.system("cls")
                header()
                print(f'\n  Are you sure you want to {red}reset{reset} the clip to its original state? ({green}y{reset}/{red}n{reset})')
                option = input("\n >>>")
                
                if option == "y":
                    load_clip(full_path, clip_extension)
                    preview_clip(full_path, clip_extension)
                    return False
                elif option == "n":
                    break


if __name__ == "__main__":
    os.system("")
    win32api.SetConsoleCtrlHandler(exit_handler, True)
    loop()