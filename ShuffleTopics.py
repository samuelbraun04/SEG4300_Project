import os

current_working_directory = os.getcwd()
subdirectories = [name for name in os.listdir(current_working_directory) 
                    if os.path.isdir(os.path.join(current_working_directory, name)) 
                    and (name != '.git') and (name != '__pycache__') and (name != 'CONSPIRACY_YOUTUBE_CHANNEL')]

for directory in subdirectories:
    topics = open(os.path.join(current_working_directory, directory, 'topics.txt'), 'r').readlines()
    from random import shuffle
    shuffle(topics)
    open(os.path.join(current_working_directory, directory, 'topics.txt'), 'w').writelines(topics)