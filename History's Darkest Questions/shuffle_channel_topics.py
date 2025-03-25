from random import shuffle
from os import getcwd, path

file = r"C:\Users\samlb\Documents\Projects\VideoGenerator-v2\History's Darkest Questions\topics.txt"

x = open(file, 'r').readlines()
for line in range(len(x)):
    x[line] = x[line].strip()
shuffle(x)
for line in range(len(x)):
    x[line] = x[line]+'\n'
open(file, 'w').writelines(x)
