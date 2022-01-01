#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pyaudio
import numpy as np
import time
import cgi
import codecs

p = pyaudio.PyAudio()

# set prams
INPUT_DEVICE_INDEX = 1
CHUNK = 2 ** 10 # 1024
FORMAT = pyaudio.paInt16
CHANNELS = int(p.get_device_info_by_index(INPUT_DEVICE_INDEX)["maxInputChannels"])
SAMPLING_RATE = int(p.get_device_info_by_index(INPUT_DEVICE_INDEX)["defaultSampleRate"])
RECORD_SECONDS = 6  #time lag入れて10秒

# amp to db
def to_db(x, base=1):
    y=20*np.log10(x/base)
    return y

# main loop
def main():
    while True:
        start = time.time()

        stream = p.open(format = FORMAT,
                        channels = CHANNELS,
                        rate = SAMPLING_RATE,
                        input = True,
                        frames_per_buffer = CHUNK,
                        input_device_index = INPUT_DEVICE_INDEX
                )

        # get specified range of data. size of data equals (CHUNK * (SAMPLING_RATE / CHUNK) * RECORD_SECONDS)
        data = np.empty(0)
        for i in range(0, int(SAMPLING_RATE / CHUNK * RECORD_SECONDS)):
            elm = stream.read(CHUNK, exception_on_overflow = False)
            elm = np.frombuffer(elm, dtype="int16")/float((np.power(2,16)/2)-1)
            data = np.hstack([data, elm])
        # calc RMS
        rms = np.sqrt(np.mean([elm * elm for elm in data]))
        # RMS to db
        db = to_db(rms, 20e-6)
        stream.close()

        elapsed_time = time.time() - start
        #print("経過時間:{:.3f}[sec], デシベル:{:.3f}[db]".format(elapsed_time, db))
        v = valume(format(db))
        return v

def valume(x):
    if float(x) < 40:   #日本騒音調査 ソーチョーによると 40dbは普通 30dbは静か とのことなので
        return 1
    else:
        return 0

try:
    form = cgi.FieldStorage()
    n = main()
    # 初回ロード時
    if form.list == []:
        html = codecs.open('./html/measurement.html', 'r', 'utf-8').read()
    # 「結果を表示」ボタン押下時
    else:
        if n == 0: #0なら静かであることを示す画面に遷移
            html = codecs.open('./html/result1.html', 'r', 'utf-8').read()
        elif n == 1: #1なら賑やかであることを示す画面に遷移
            html = codecs.open('./html/result2.html', 'r', 'utf-8').read()

    print("")
    print(html)
except KeyboardInterrupt:
    pass
finally:
    p.terminate()
