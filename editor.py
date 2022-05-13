import magic
import os
import subprocess
import sys
import win32api
from send2trash import send2trash


def color(r, g, b):
    return "\x1b[38;2;" + ";".join([str(r), str(g), str(b)]) + "m"

reset = "\x1b[0m"
red = color(255, 90, 90)
green = color(90, 255, 90)
blue = color(30, 120, 255)
yellow = color(255, 255, 30)
gray = color(127, 127, 127)


def press_enter():
    input(f'\n {gray}[Press Enter]{reset}')


def header():
    print(f'{blue}\n Mutater\'s Clip Editor{reset}')


def clear():
    os.system("cls")


def delete(file):
    os.system(f'del "{file}"')


def copy(source, destination):
    os.system(f'copy "{source}" "{destination}" /y')


def play(file):
    os.system('"' + file + '"')


def options(*args):
    print("\n  ", end="")
    print(*args, sep="\n\n  ")
    return input("\n >>>")


def get_files(pathe=""):
    return next(os.walk(pathe), (None, None, []))[2]


def get_file_names(path=""):
    return [os.path.splitext(file)[0] for file in get_files(path)]


def exit_handler(*args):
    e.delete_temps()


class Editor:
    # - MAIN LOOP - #
    
    def start(self):
        if not self.setup():
            return
        
        while 1:
            self.loop()
            
            # If user doesn't want to continue editing in a new location, end the editor
            if not self.edit_again():
                break
    
    def setup(self):
        self.working_directory = os.getcwd() + "\\"
        self.video_codec = (
            open("config.txt", "r")
            .read()
            .split("\n")[0]
            .split("=")[1]
        )
        os.system("PATH %PATH%;" + self.working_directory)
        
        self.clip_path = ""
        self.clip_extension = ""
        
        self.type_checker = magic.Magic(magic.Magic(mime=True, uncompress=True))
        
        self.input_directory = self.input_path(" of clips to edit")
        self.output_directory = self.input_path(" to save clips")
        self.current_clip = 0
        
        os.chdir(os.getcwd())
        
        self.load_clips()
        
        if not self.clips:
            clear()
            header()
            print(f'\n  {red}Directory contains no clips.')
            press_enter()
            return False
        return True
    
    def loop(self):
        for clip_name in self.clips:
            self.current_clip += 1
            self.clip_path = f'{self.input_directory}\\{clip_name}'
            self.clip_extension = clip_name.split(".")[-1]
            
            self.load_clip()
            
            # If the user decides to delete or export the clip without editing,
            # continue to next clip
            if not self.if_edit_clip():
                continue
            
            while 1:
                self.edit_clip()
                play(f'{self.input_directory}\\temp_clip.{self.clip_extension}')
                
                # If clip is exported, continue to next clip
                if self.export_clip():
                    break
            continue
    
    def edit_again(self):
        clear()
        header()
        
        print(f'\n  No more clips detected!')
        option = options(
            f'Type {green}anything{reset} to continue editing.',
            f'Press ENTER without typing to {red}exit{reset}.'
        )
        
        if option:
            self.input_directory = self.input_path(" of clips to edit")
            self.current_clip = 0
            return True
        return False
    
    # - NESTED LOOP - #
    
    def input_path(self, prompt):
        while 1:
            clear()
            header()
            
            option = options(f'Type the {green}path{reset}{prompt}.')
            
            if os.path.isdir(option):
                return option
            else:
                print(f'\n  {red}The specified directory does not exist.{reset}')
                press_enter()
    
    def load_clip(self):
        if "temp_clip" in get_file_names():
            delete("temp_clip.*")
        copy(self.clip_path, f'{self.input_directory}\\temp_clip.{self.clip_extension}')
    
    def load_clips(self):
        clear()
        header()
        print("\n  Loading clips...")
        
        clips = get_files(self.input_directory)
        
        for i in range(len(clips)-1, -1, -1):
            try:
                query = self.type_checker.from_buffer(open(f'{self.input_directory}\\{clips[i]}', "rb").read(2048))
                
                if "video" in query:
                    continue
            except:
                pass
            
            clips.pop(i)
        
        print("\n  Done loading clips. If the program stays frozen, try editing config.txt.")
        self.clips = clips
    
    def if_edit_clip(self):
        play(f'{self.input_directory}\\temp_clip.{self.clip_extension}')
        
        while 1:
            clear()
            header()
            
            option = options(
                f'"{self.clip_path}".',
                f'Clip {self.current_clip} / {len(self.clips)} ({len(self.clips) - self.current_clip} Remaining)',
                f'Type the number for an option below.',
                f' 1) {green}Edit{reset} the clip.',
                f' 2) {yellow}Continue{reset} without editing.',
                f' 3) {red}Delete{reset} the clip.'
            )
            
            if option == "1":
                return True
            elif option == "2":
                if self.export_clip():
                    return False
                return True
            elif option == "3":
                send2trash(self.clip_path)
                return False
    
    def edit_clip(self):
        while 1:
            while 1:
                clear()
                header()
                
                start = options(f'Type start {green}time{reset} of subclip in {green}seconds{reset}.')
                end = options(
                    f'Type end {green}time{reset} of subclip in {green}seconds{reset}.',
                    f'Press {yellow}ENTER{reset} without typing to {red}cancel{reset}.'
                )
                
                try:
                    start = float(start)
                    duration = float(end) - start + 1
                    break
                except:
                    print(f'\n  {reset}Input must be only numbers, e.g. "5" or "2.3" without quotes.')
                    press_enter()
                
            while 1:
                try:
                    source = f'"{self.input_directory}\\temp_clip.{self.clip_extension}"'
                    destination = f'"{self.input_directory}\\temp_clip2.{self.clip_extension}"'
                    ffmpeg = "ffmpeg"
                    
                    os.system("cd")
                    command = f'{ffmpeg} -i {source} -ss {start} -t {duration} -vcodec {self.video_codec} -b:v 15m {destination} -y'
                    
                    os.system(command)
                    copy(destination, source)
                    delete(f'{self.input_directory}\\temp_clip2.*')
                    press_enter()
                    return
                except Exception as e:
                    print(f'\n  {red}Unable to trim video; start and duration were incorrect or another error occured.{reset}')
                    print(f'\n  {e}')
                    press_enter()
                    break
    
    def export_clip(self):
        while 1:
            clear()
            header()
            
            option = options(
                f'Type the number for an option below.',
                f' 1) {green}Save{reset} the clip.',
                f' 2) {green}Save{reset} the clip and {red}delete{reset} the original clip.',
                f' 3) {yellow}Undo{reset} changes to the clip.'
            )
            
            recycle = option == "2"
            if option in "12":
                while 1:
                    clear()
                    header()
                    
                    print(f'\n  "{self.clip_path}"')
                    
                    option = options(
                        f'Type the {blue}name{reset} for the clip.',
                        f'{red}WARNING{reset}: Make the file name Windows-friendly! {red}Don\'t{reset} include the file extension.'
                    )
                    
                    export_path = option.replace("/", "\\")
                    export_path_as_list = export_path.split("\\")
                    export_name = export_path_as_list[-1]
                    
                    # If subdirectory specified in clip name, format it to be added to output directory
                    export_subdirectory = "\\".join(export_path_as_list[:-1])
                    if export_subdirectory:
                        export_subdirectory = f'\\{export_subdirectory}'
                    export_directory = self.output_directory + export_subdirectory + "\\"
                    export_path = export_directory + export_name
                    
                    # If subdirectory does not exist, continue
                    try:
                        os.listdir(export_directory)
                    except:
                        print(f'\n {red}Specified subdirectory path does not exist.{reset}')
                        press_enter()
                        continue
                    
                    # If file exists, prompt for overwrite
                    overwrite = True
                    if f'{export_name}.{self.clip_extension}' in get_files(export_directory):
                        while 1:
                            clear()
                            header()
                            
                            print(f'\n  {red}File already exists in directory.{reset}')
                            
                            option = options(
                                f'Type the number for an option below.',
                                f' 1) {green}Rename{reset} the clip.',
                                f' 2) {red}Overwrite{reset} the file.'
                            )
                            
                            if option == "1":
                                overwrite = False
                                break
                            elif option == "2":
                                break
                    
                    if not overwrite:
                        continue
                    
                    source = f'{self.input_directory}\\temp_clip.{self.clip_extension}'
                    destination = f'{export_path}.{self.clip_extension}'
                    copy(source, destination)
                    delete(f'{self.input_directory}\\temp_clip.*')
                    if recycle:
                        send2trash(self.clip_path)
                    return True
            elif option == "3":
                while 1:
                    clear()
                    header()
                    
                    option = options(
                        f'Type the number for an option below.',
                        f' 1) {green}Confirm{reset}.',
                        f' 2) {red}Cancel{reset}.'
                    )
                    
                    if option == "1":
                        self.load_clip()
                        if self.if_edit_clip():
                            return False
                        return True
                    elif option == "2":
                        break
    
    def delete_temps(self):
        delete(e.input_directory + "\\temp_clip.*")
        delete(e.input_directory + "\\temp_clip2.*")

if __name__ == "__main__":
    win32api.SetConsoleCtrlHandler(exit_handler, True)
    e = Editor()
    e.start()