import os
import json
import sys
# import speech
import wave
from pyaudio import PyAudio, paInt16
from pydub import AudioSegment


from Sodiers_voice_xunfei_update import XUNFEI_ASR

class Voice():

    # site = "E:/Win/AutoDrive_Win/auto-win/Soldiers/command.wav"
    def __init__(self):
        self.path = os.curdir + '/command.wav'
        self.mp3_path = os.curdir + '/command.mp3'
        self.asr = ""
        self.framerate = 16000
        self.NUM_SAMPLES = 2000
        self.channels = 1
        self.sampwidth = 2
        self.TIME = 20

    def getword(self):
        self.record()
        return self.voice2word()


    def save_wave_file(self, filename, data):
        '''save the date to the wavfile'''
        wf=wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.sampwidth)
        wf.setframerate(self.framerate)
        wf.writeframes(b"".join(data))
        wf.close()

    def record(self):
        print("yes, please.")
        pa = PyAudio()
        stream = pa.open(format=paInt16,
                        channels=1,
                        rate=self.framerate,
                        input=True,
                        frames_per_buffer=self.NUM_SAMPLES)
        my_buf = []
        count = 0
        
        # 开始录音
        while count < self.TIME:#控制录音时间
            string_audio_data = stream.read(self.NUM_SAMPLES)
            # if count == 0:
            #     speech.say("一秒后请说")
            my_buf.append(string_audio_data)
            count += 1
            # print('.')
        self.save_wave_file(self.path, my_buf)
        self.wav2mp3(self.path, self.mp3_path)
        stream.close()
        print("OK.OK.")

    def voice2word(self):
        return XUNFEI_ASR(self.mp3_path)


    def wav2mp3(self, filepath, savepath):
        sourcefile = AudioSegment.from_wav(filepath)
        sourcefile.export(savepath, format="mp3")

if __name__ == '__main__':
    a = Voice()
    ans = a.getword()
    print(ans)
    exit()
