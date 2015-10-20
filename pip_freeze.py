import subprocess

"""
The purpose of this file is to print out pip requirements
to a file, but clean out some dependencies which are 
unnecessary and cause issues on XUbuntu for Example.
"""

req_file = "PIP_REQUIREMENTS.txt"

print "Dumping pip requirements to a file %s\n"%(req_file)

bash_command = "pip freeze > %s"%(req_file)
subprocess.Popen(bash_command,shell=True).wait()

# These can be filtered out of req_file
# We filter out lines that start with these strings
filterable = ['oneconf']

f = open(req_file,"r")
lines = f.readlines()
# What we'll write
newlines = []
f.close()

# Remove lines
f = open(req_file,"w")
for line in lines:
    found = False
    for package in filterable:
        if package in line:
            found = True
            print "Removing %s from %s"%(line.replace('\n',''),req_file)
            break
    if not found:
        f.write(line)

f.close()

# Add to git
bash_command = "git add %s"%(req_file)
subprocess.Popen(bash_command,shell=True).wait()
