#! /usr/bin/env python
import os, sys
import grp
import shutil
import pwd
from datetime import datetime


# Simple shell
# COMMANDS          ERRORS CHECKED
# 1. info XX         - check file/dir exists
# 2. files
# 3. delete  XX      - check file exists and delete succeeds
# 4. copy XX YY      - XX exists, YY does not exist copy succeeds
# 5. where
# 6. down DD         - check directory exists and change succeeds
# 7. up              - check not at the top of the directory tree - can't go up from root
# 8. finish

header_filescmd = ["File Name", "Type"]  # column headers
global dirpath
header_infocmd = ["File Name", "Type", "Owner User", "Owner Group", "Last modified time", "Size", "Executable" ]
width= [25, 11 , 20, 20, 26, 11, 11]
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
#   Copy the ‘from’ file to the ‘to’ file 
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
        print ("  Unexpected argument " + fields[num+1] + " for command " + fields[0])
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
    line = input(base + " SantiagoShell>")  
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
        print ("Unknown command " + fields[0])
