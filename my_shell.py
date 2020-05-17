import subprocess
import os, sys
import grp
import pwd
import shutil
import signal
from datetime import datetime

class bcolors:
    FAIL = '\033[91m'
    ENDC = '\033[0m'

# Simple shell
# COMMANDS        
# 1. info XX    - Checks file/dir exists
# 2. files      - Shows files in directory
# 3. delete XX  - Checks directory/ file exists and delete it
# 4. copy XX YY - Copies XX in YY
# 5. where      - Shows current directory
# 6. down DD    - Checks directory exists and enters
# 7. up         - Check you're not in the root and goes up in the directory tree
# 8. finish     - terminate program
# 9. program name to run external program
# Type any linux command - It will work! :)

 # column headers
header_filescmd = ["File Name", "Type"] 
global dirpath
header_infocmd = ["File Name", "Type", "Owner User", "Owner Group", "Last modified time", "Size", "Executable" ]
width= [25, 11 , 20, 20, 26, 11, 11]


path = os.environ['PATH']
THE_PATH = path.split(':')


# ========================
#    Run command
#    Run an executable somewhere on the path
#    Any number of arguments
# ========================
def runCmd(fields):
  global PID, THE_PATH

  cmd = fields[0]
  cnt = 0
  args = []
  while cnt < len(fields):
      args.append(fields[cnt])
      cnt += 1

  execname = add_path(cmd, THE_PATH)

  # run the executable
  if not execname:
      print ('Executable file ' + str(cmd) +' not found')
  else:
    # execute the command
    print(execname)

  # execv executes a new program, replacing the current process; on success, it does not return.
  # On Unix, the new executable is loaded into  the current process, and will have the same process id as the caller.
  try:
    pid = os.fork()
    if pid == 0:
      os.execv(execname, args)
      os.exit(0)
    else:
      # wait for the child process to exit
      # the 'status' variable is updated with the exit status

      # If we pass 0 to os.waitpid, the request is for the status of
      # any child in the process group of the current process.
      # If we pass -1, the request pertains to any child of the current process.
      _, status = os.waitpid(0, 0)
      # this function gets the exit code from the status
      #if os.WIFSIGNALED(status):
        #returnedsig = os.WTERMSIG(status)
        #signal.signal(signal.SIGINT, sigint_handler)
      exitCode = os.WEXITSTATUS(status)
      if exitCode == 0:
        print ("Complete with return code %d" % (exitCode))
  except :
    print ('Something went wrong there >_<')
    os._exit(0)

# ========================
#    Constructs the full path used to run the external command
#    Checks to see if the file is executable
# ========================
def add_path(cmd, path):
    if cmd[0] not in ['/', '.']:
        for d in path:
            execname = d + "/" +cmd
            if os.path.isfile(execname) and os.access(execname, os.X_OK):
                return execname
        return False
    else:
        return cmd

# ========================
#   FILES COMMAND
#   List file and directory names
#   No arguments
# ========================
def files_cmd(fields, filename):
    global info

    info = []
    if checkArgs(fields, 0):
        info.append(filename)
        info.append(get_file_type(filename))


# ========================
#   INFO COMMAND
#   List file information
#   1 argument: file name
# ========================
def info_cmd(fields):
    global info
    info = []
    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            print_header("info")
            info.append(argument)
            info.append(get_file_type(argument))
            stat_info = os.stat(argument)
            uid = stat_info.st_uid
            gid = stat_info.st_gid
            user = pwd.getpwuid(uid)[0]
            group = grp.getgrgid(gid)[0]
            info.append(user)
            info.append(group)
            info.append(datetime.fromtimestamp(os.stat(argument).st_mtime).strftime('%b %d %Y %H:%M:%S'))
            info.append(os.path.getsize(argument))
            if os.access(argument, os.X_OK):
                info.append("No")
            else:
                info.append("Yes")
        else:
            print("I'm sorry but the file/dir doesn't exists :(")




# ========================
#   DELETE COMMAND
#   Delete the file
#   1 argument: file name
# ========================
def delete_cmd(fields):

    if checkArgs(fields, 1):
        argument = fields[1]

        if os.access(argument, os.F_OK):
            try:
                os.remove(argument)
                print ("File deleted :)")
            except OSError:
                print("I'm sorry you cannot delete this file >_<")

        else:
            print("I'm sorry but the file/dir doesn't exists :(")


# ========================
#   COPY COMMAND
#   Copy the 'from' file to the 'to' file
#   2 arguments: 'from' file and 'to' file
# ========================
def copy_cmd(fields):
    if checkArgs(fields, 2):
        argument_1 = fields[1]
        argument_2 = fields[2]
        if os.access(argument_1, os.F_OK) and not os.access(argument_2, os.F_OK):
            shutil.copyfile(argument_1, argument_2)
        else:
            print("I'm sorry but the source file doesn't exists or the destination file exists :(")


# ========================
#   WHERE COMMAND
#   Show the current directory
#   No arguments
# ========================
def where_cmd(fields):
    if checkArgs(fields, 0):
        dirpath = os.getcwd()
        print(dirpath)


# ========================
#   DOWN COMMAND
#   Change to the specified directory, inside the current directory
#   1 argument: directory name
# ========================
def down_cmd(fields):

    if checkArgs(fields, 1):
        argument = fields[1]
        if os.access(argument, os.F_OK):
            os.chdir(argument)
        else:
            print("I'm sorry but the directory doesn't exists :(")


# ========================
#   UP COMMAND
#   Change to the parent of the current directory
#   No arguments
# ========================
def up_cmd(fields):
    if checkArgs(fields, 0):
        if os.path.realpath(dirpath) == os.path.realpath("/"):
            print("Hey! You can't go up, you're in the root!")
        else:
            os.chdir("../")


# ========================
#   FINISH COMMAND
#   Exits the shell
#   No arguments
# ========================
def finish_cmd(fields):
    if checkArgs(fields, 0):
        exit()

# ----------------------
# Other functions
# ----------------------
def checkArgs(fields, num):
    numArgs = len(fields) - 1
    if numArgs == num:
        return True
    if numArgs > num:
        print ("  Unexpected argument " + fields[num+1] + "for command " + fields[0])
    else:
        print ("  Missing argument for command " + fields[0])

    return False

def print_file_info():
    fieldNum = 0
    output = ''
    while fieldNum < len(info):
        output += '{field:{fill}<{width}}'.format(field=info[fieldNum], fill=' ', width=width[fieldNum])
        fieldNum += 1
    print (output)


# Print a header.
# Print the header entries, using the corresponding width entries.
def print_header(type_header):
    field_num = 0

    output = ''
    if type_header == "files":
        while field_num < 2:
            output += '{field:{fill}<{width}}'.format(field=header_infocmd[field_num], fill=' ', width=width[field_num])
            field_num += 1
        print  (output)
        print ('-' * 36)
    elif type_header == "info":
        while field_num < len(header_infocmd):
            output += '{field:{fill}<{width}}'.format(field=header_infocmd[field_num], fill=' ', width=width[field_num])
            field_num += 1
        print  (output)
        length = sum(width)
        print ('-' * length)


def get_file_type(filename):

  if os.path.isdir(filename):
    return "Dir"
  elif os.path.isfile(filename):
    return "File"
  elif os.path.islink(filename):
    return "Link"


# ----------------------------------------------------------------------------------------------------------------------

while True:
    dirpath = os.getcwd()
    base = os.path.basename(dirpath)
    line = input(bcolors.FAIL + base + " SantiagoShell>" +bcolors.ENDC)
    fields = line.split()
    # split the command into fields stored in the fields list
    # fields[0] is the command name and anything that follows (if it follows) is an argument to the command

    if fields[0] == "files":
        print_header("files")
        for filename in os.listdir('.'):
            files_cmd(fields, filename)
            print_file_info()
    elif fields[0] == "info":
        info_cmd(fields)
        print_file_info()
    elif fields[0] == "delete":
        delete_cmd(fields)
    elif fields[0] == "copy":
        copy_cmd(fields)
    elif fields[0] == "where":
        where_cmd(fields)
    elif fields[0] == "down":
        down_cmd(fields)
    elif fields[0] == "up":
        up_cmd(fields)
    elif fields[0] == "finish":
        finish_cmd(fields)
    else:
        runCmd(fields)
