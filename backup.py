#!/bin/python3
import os
import sys
import json
import subprocess

ARG_KEY = 0
MSG_KEY = 1
ERR_KEY = 2
HI_KEY = 3
NOCOLOR_KEY = 4

ANSI_COLORS = {
    ARG_KEY:        '\033[1;36m',
    MSG_KEY:        '\033[1;35m',
    ERR_KEY:        '\033[1;31m',
    HI_KEY:         '\033[1;32m',
    NOCOLOR_KEY:    '\033[0m',
}

def color_str(key, s):
    temp = ANSI_COLORS[key] + s + ANSI_COLORS[NOCOLOR_KEY]
    return temp

def msg_str(s):
    return color_str(MSG_KEY, s)

def arg_str(s):
    return color_str(ARG_KEY, s)

def err_str(s):
    return color_str(ERR_KEY, s)

def hi_str(s):
    return color_str(HI_KEY, s)

ERROR_STR = err_str('ERROR: ')

def would_you_like_to_continue_prompt(prompt_msg, yes_msg, no_msg):
    continue_flag = yes_no_prompt(prompt_msg)
    if continue_flag:
        print(yes_msg)
        print()
    else:
        print(no_msg)
        print()
        sys.exit(0)

def yes_no_prompt(prompt_msg):
    YES_INPUT='Y'
    NO_INPUT='n'
    while True:
        print()
        print(f'{prompt_msg} ({YES_INPUT}/{NO_INPUT}):')
        yesno = input()
        print()
        if yesno == YES_INPUT:
            return True
        elif yesno == NO_INPUT:
            return False
        else:
            print(ERROR_STR)
            print('INVALID INPUT: ' + arg_str(yesno))
            print('VALID INPUTS ARE ' + arg_str(YES_INPUT) + ' OR ' + arg_str(NO_INPUT) + ' (CASE SENSITIVE)')

def is_dir_empty(path):
    dir_contents = os.listdir(path)
    return (len(dir_contents) == 0)

def main():

    if sys.platform != 'linux':
        print(ERROR_STR)
        print('THIS PROGRAM ONLY WORKS ON PLATFORMS WITH RSYNC')
        print()
        sys.exit(-1)

    if len(sys.argv) < 2:
        print(ERROR_STR)
        print('NOT ENOUGH ARGS')
        print('ARGUMENTS ARE: ' + arg_str('dest_dir') + ' [' + msg_str('REQUIRED') + '] ' + arg_str('--dry-run') + ' [' + msg_str('OPTIONAL') + ']')
        print('THING: ' + msg_str('abc'))
        print()
        sys.exit(-1)

    DEST_DIR = sys.argv[1]
    if not os.path.isdir(DEST_DIR):
        if not os.path.exists(DEST_DIR):
            print(msg_str('DEST DIRECTORY ') + arg_str(DEST_DIR) + msg_str(' DOES NOT EXIST'))
            prompt = msg_str('WOULD YOU LIKE TO AUTOMATICALLY CREATE DIRECTORY ') + arg_str(DEST_DIR) + msg_str(' ?')
            would_you_like_to_continue_prompt(prompt, msg_str('CONTINUING...'), msg_str('ABORTING'))
        else:
            print(ERROR_STR)
            print(arg_str(DEST_DIR) + ' ALREADY EXISTS, BUT IS NOT A DIRECTORY')
            print()
            sys.exit(-1)
    elif not is_dir_empty(DEST_DIR):
        print(msg_str('DEST DIRECTORY ') + arg_str(DEST_DIR) + msg_str(' IS NOT EMPTY'))
        would_you_like_to_continue_prompt(msg_str('WOULD YOU LIKE TO CONTINUE?'), msg_str('CONTINUING...'), msg_str('ABORTING'))

    current_abs_file_path = os.path.abspath(__file__)  # NOTE __file__ will be relative to the current working directory
    this_dir = os.path.dirname(current_abs_file_path)
    json_file_path = this_dir + '/' + 'files_to_backup.json'
    f = open(json_file_path, 'r')
    SRC_PATHS = json.load(f)
    f.close()
    for path in SRC_PATHS:
        if not os.path.isfile(path) and not os.path.isdir(path):
            print(ERROR_STR)
            print('INVALID SOURCE FILE: ' + arg_str(path))
            print()
            sys.exit(-1)
        elif path[-1] == '/':
            #put message explaining what putting '/' in or not does
            print('FILE PATH ' + arg_str(path) + ' ENDS WITH A \'' + arg_str('/') + '\' CHARACTER')
            print('IN RSYNC, THIS MEANS THAT THE DIRECTORIES CONTENTS WILL BE COPIED TO ' + arg_str(DEST_DIR) + ' INSTEAD OF THE DIRECTORY ITSELF')
            print('IF YOU OMIT THE \'' + arg_str('/') + '\' AT THE END OF ' + arg_str(path) + ', THE DIRECTORY ITSELF WILL BE COPIED TO ' + arg_str(DEST_DIR))
            print('INCLUDING THE \'' + arg_str('/') + '\' IS MOST LIKELY A MISTAKE')
            would_you_like_to_continue_prompt(msg_str('WOULD YOU LIKE TO CONTINUE?'), msg_str('CONTINUING...'), msg_str('ABORTING'))
    if len(SRC_PATHS) == 0:
        # this is treated as an error case since there is no point in
        # even starting the program if you didn't want to copy some files
        print(ERROR_STR)
        print('NO SOURCE FILE PATHS LOADED')
        print()
        sys.exit(-1)

    # 2nd arg should be '' or '--dry-run'
    # anything else is error
    dry_run_arg = ''
    if len(sys.argv) > 2:
        if sys.argv[2] == '--dry-run':
            dry_run_arg = '--dry-run'
            print(msg_str('THIS IS A DRY RUN'))
            print()
        else:
            print(ERROR_STR)
            print('INVALID ARG: ' + arg_str(sys.argc[2]))
            print('VALID ARGUMENTS ARE ' + arg_str('--dry-run') + ' OR NO ARGS')
            print()
            sys.exit(-1)

    if dry_run_arg != '' and dry_run_arg != '--dry-run':
        print(ERROR_STR)
        print('DRY_RUN_ARG IS IN AN INVALID STATE: ' + arg_str(dry_run_arg))
        print()
        sys.exit(-1)

    if dry_run_arg == '':
        print(msg_str('THIS IS NOT A DRY RUN'))
        would_you_like_to_continue_prompt(msg_str('WOULD YOU LIKE TO CONTINUE?'), msg_str('CONTINUING...'), msg_str('ABORTING'))

    for src_path in SRC_PATHS:
        delete_arg = ''
        if os.path.isdir(src_path):
            delete_arg = '--delete'

        PADDING = 9
        SOURCE = 'SOURCE:'.ljust(PADDING, ' ')
        DEST = 'DEST:'.ljust(PADDING, ' ')
        print(hi_str(' ----------------------------- '))
        print(hi_str(SOURCE) + arg_str(src_path))
        print(hi_str(DEST) + arg_str(DEST_DIR))
        print()

        cmd_args = ['sudo', 'rsync', '-av']
        if dry_run_arg != '':
            cmd_args.append(dry_run_arg)
        if delete_arg != '':
            cmd_args.append(delete_arg)
        cmd_args.append(src_path)
        cmd_args.append(DEST_DIR)

        if delete_arg != '' and not os.path.isdir(src_path):
            print(ERROR_STR)
            print('DELETE_ARG IS IN INVALID STATE: ' + arg_str(delete_arg))
            print()
            sys.exit(-1)

        # //////////////////////////////////////////////////////////////////
        # this is mostly for debug purposes, but I don't see any reason to remove it anytime soon
        # it acts like a last minute sanity check before you make any changes to file system or
        # run rsync on a directory that's going to take a while
        print(msg_str('[DEBUG]') + ' CMD_ARGS: ' + str(cmd_args))
        skip_flag = yes_no_prompt(msg_str('WOULD YOU LIKE TO SKIP THIS FILE?'))
        if skip_flag:
            print(msg_str('SKIPPING...'))
            continue
        # //////////////////////////////////////////////////////////////////
        
        subprocess.run(cmd_args,
                       stdout=sys.stdout,
                       stdin=sys.stdin,
                       stderr=sys.stderr)
        
        print(hi_str(' ----------------------------- '))
        print()
    print(msg_str('BACKING UP COMPLETED'))
    print()

main()
