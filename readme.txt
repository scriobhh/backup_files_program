this is intended as a backup program to run in WSL terminal that uses rsync to handle copying files
the script backup.sh was an earlier version of this, it does pretty much exactly the same thing as the python program
make batch script or python script for running in WSL terminal (see if there is some feature detect thing for checking if you are in linux or not)
sudo rsync -av --delete --dry-run src dest
NOTE if src or dest ends with a slash, that means the folder src itself is copied to dest
if src ends with no slash (and its' a directory) that means just the contents of the directory is copied to dest
whether dest ends with a slash or not doesn't seem to make a difference after testing this
the -a option is short for 'archive' and seems to just call rsync recursively (or something... apparantly you're supposed to use it for backup use cases)
the 'sudo' part executes the rsync command with root priveleges (this is necessary for rsync to work in WSL, otherwise you get permissions issues when copying the files)
--delete will delete any files in the dest directory that are not in the src directory (be careful when using this, and don't use it when just copying individual files like TODO.txt into the backup folder since then it will just delete everything that isn't TODO.txt in the backup folder
NOTE if dest doesn't exist, then rsync will create it before copying anything over
from WSL, get access to windows drives through /mnt
e.g. the command 'ls /mnt' will list all windows drives
you can get to C:\dev through /mnt/c/dev


this will only work on systems that have the rsync program
this means linux, WSL on windows, and potentially others like mac, BSD etc. (I haven't checked any of those) has this
(currently it just checks if sys.platform returns 'linux', which is what it will do on linux and in WSL)

1st arg is the destination directory
use the flag --dry-run as the 2nd arg to make all the rsyncs a dry-run

2nd arg is a flag --dry-run that is optional
it sets the --dry-run flag on each run of rsync
this allows you to preview what changes the program will make, without actually writing/deleting any files

if you don't set the --dry-run flag, the program will perform the actual updates to the file system
the program will prompt you to make sure this wasn't a mistake
you enter Y for yes or n for no (case sensitive)

run.sh is used for convenience, so you can store the same dest_dir argument and you can run the program just by typing ./run
