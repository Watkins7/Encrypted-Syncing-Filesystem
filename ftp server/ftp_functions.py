import os

# get just the file names
def get_all_file_names(dirName):

    # list of ALL FILES TO BE RETURNED
    allFiles = list()

    # start directory, and all files in it
    listOfFile = os.listdir(dirName)

    # Iterate over all sub_dir
    for i in listOfFile:

        # Create full path
        fullPath = os.path.join(dirName, i)

        # recursive call to subdirectory
        if os.path.isdir(fullPath):
            allFiles = allFiles + get_all_file_names(fullPath)

        # append name to list
        allFiles.append(i)

    # return list
    return allFiles
