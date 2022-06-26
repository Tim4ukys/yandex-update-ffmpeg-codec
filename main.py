# -----------------------------
# Author: Tim4ukys (26.05.2022)
# -----------------------------

import requests
import json
import os
import tarfile
from parse import parse
from pyunpack import Archive

CODECS_URL = "https://browser-resources.s3.yandex.net/linux/codecs.json"
PATH_FILE_IN_ARHIVE = "./usr/lib/chromium-browser/libffmpeg.so"

def getLastVersion(j : json):
    maj = 0
    min = 0
    patch = 0

    for j_key in j:
        nmaj, nmin, npatch = parse("{}.{}.{}", j_key)
        nmaj = int(nmaj)
        nmin = int(nmin)
        npatch = int(npatch)
        if nmaj > maj or (nmaj == maj and nmin > min) or (nmaj == maj and nmin == min and npatch > patch):
            maj = nmaj
            min = nmin
            patch = npatch

    return "{}.{}.{}".format(maj, min, patch)

# Check root

if os.getuid() != 0:
    print('Please, launch this program as root..')
    exit(os.EX_NOPERM)


# Load codecs.json

print('Load "codecs.json" ... ', end='')
rCodecJSON = requests.get(CODECS_URL)
if rCodecJSON.status_code == 200:
    print('Done')
else:
    print('Error(code:{})'.format(rCodecJSON.status_code))
    exit(os.EX_TEMPFAIL)
    
# Print last version
CodecJSON = rCodecJSON.json()
codec_key = getLastVersion(CodecJSON)
print("Last version: {}".format(codec_key))


# Download deb arhive
print('Download "codecs.deb" ... ', end='')

rDownloadCodec = requests.get(CodecJSON[codec_key][0])

if rDownloadCodec.status_code == 200:
    print('Done')
else:
    print('Error(code:{})'.format(rDownloadCodec.status_code))
    exit(os.EX_TEMPFAIL)

debFile = open('codecs.deb', 'wb')
debFile.write(rDownloadCodec.content)
debFile.close()


# Extract data.tar
print('Extract "data.tar" file ... ', end='')

Archive('codecs.deb').extractall('.')


# Extract libffmpeg.so
print('Done\nExtract "libffmpeg.so" file ... ', end='')

arhDataDeb = tarfile.open('data.tar', 'r')
libFFMPEG = arhDataDeb.extractfile(PATH_FILE_IN_ARHIVE)

open('/opt/yandex/browser/libffmpeg.so', 'wb').write(libFFMPEG.read())


# Delete temp files
print('Done\nDeleting temporary files ... ', end='')
os.remove("codecs.deb")
os.remove("data.tar")
print('Done')

exit(os.EX_OK)
