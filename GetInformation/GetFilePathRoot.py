import os
import re
def get_root_dir():
    root_dir_re=re.compile("(.*)\\\GetInformation\\\GetFilePathRoot.py")
    # print root_dir_re.match(os.path.realpath(__file__)).group(1)
    return root_dir_re.match(os.path.realpath(__file__)).group(1)