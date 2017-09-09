#!/usr/bin/python3

import shutil
import tempfile
import os
import time

MAX_AGE_MINUTES = 30;

tempdir = tempfile.gettempdir();
while 1:
    now = time.time();
    for subdir, dirs, files in os.walk(tempdir):
        for folder in dirs:
            path = os.path.join(tempdir, folder);
            mtime = os.path.getmtime(path);
            age = (now-mtime)/60;
            if age > MAX_AGE_MINUTES:
                try:
                    shutil.rmtree(path);
                except:
                    pass;
    time.sleep(MAX_AGE_MINUTES);
