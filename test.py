import os
def list_files(startpath, file):
    buffer = ''
    for root, dirs, files in os.walk(startpath):
        if file in files:
            return root+'\\'+file
    return False
print(list_files(os.getcwd(),'workspace.xml'))