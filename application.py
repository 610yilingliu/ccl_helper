import os
import hashlib
import string
import time
import subprocess

import sounddevice as sd
import keyboard
import numpy as np
from openai import OpenAI
from scipy.io.wavfile import write

apikey = os.getenv("OPENAI_API_KEY")


class ccl_helper:
    def __init__(self, apikey, scoring_folder = 'scoring'):
        '''
        apikey为openai的apikey，存放在同目录.env文件中（请自行创建.env文件，内容为OPENAI_API_KEY = '你的key'，如果没有就去https://platform.openai.com/api-keys自己建一个(记得充钱)
        '''
        self.dialog = None
        # 控制播放句子序号及储存路径
        self.dialogidx = 0
        self.voicepath = "voice"
        self.output = []
        self.client = OpenAI(
            api_key=apikey
        )
        self.savefolder = os.path.join(scoring_folder, time.strftime("%Y-%m-%d-%H-%M", time.localtime()))
        os.makedirs(self.savefolder, exist_ok=True)
        
    def load_test(self, file):
        '''
        每行为一个对话轮次，常规情况是一行英文（考试时需要你说对应英文），一行中文（考试时需要你说对应英文）
        self.dialog会变成一个列表
        '''
        with open(file, "r", encoding= 'utf-8') as f:
            self.dialog = f.readlines()

    def is_chinese(self, text):
        '''
        判断一个句子是中文还是英文
        '''
        for ch in text:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False
    
    def calculate_md5(self, data):
        def remove_punctuations(text):
            text = text.translate(str.maketrans('', '', string.punctuation))
            text = text.strip()
            return text
        data = remove_punctuations(data)
        md5_hash = hashlib.md5(data.encode()).hexdigest()
        return md5_hash
    
    def playsound(self, file_path):
        command = [
            'ffplay',
            '-autoexit',  # 播放完自动退出
            '-nodisp',    # 不显示视频窗口
            file_path
        ]
        
        try:
        # 运行 ffplay 命令，并将 stdout 和 stderr 重定向到 DEVNULL 以隐藏输出
            subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error playing audio: {e}")

    def text_to_voice(self, text):
        '''
        调用google tts生成mp3文件，返回文件路径
        '''
        cur_sentance = self.dialog[self.dialogidx]
        is_zh = self.is_chinese(cur_sentance)
        text_md5 = self.calculate_md5(text)
        p = text_md5 + '.mp3'
        path = os.path.join(self.voicepath, p)
        if os.path.exists(path):
            return path
        if is_zh:
            voice = 'nova'
        else:
            voice = 'alloy'
        response = self.client.audio.speech.create(
        model="tts-1-hd",
        voice=voice,
        input=text,
        speed = 0.95
        )
        # with open(path, "wb") as out:
        #     out.write(response.audio_content)
        with open(path, "wb") as out:
            out.write(response.content)
        print(f'MP3 Generated')
        return path

    def record(self):
        '''
        录音开始，按下回车键结束录音
        '''
        sample_rate = 44100
        print("开始录音... 按下回车键结束录音")
        
        audio_data = []
        
        def callback(indata, frames, time, status):
            audio_data.append(indata.copy())
        
        stream = sd.InputStream(samplerate=sample_rate, channels=2, callback=callback)
        with stream:
            keyboard.wait('enter')
        
        print("录音结束")
        audio_data = np.concatenate(audio_data, axis=0)
        output_file = os.path.join(self.savefolder, str(self.dialogidx) + '.wav')
        write(output_file, sample_rate, audio_data)
        print(f"录音已保存为 '{output_file}'")


    def voice_to_text(self):
        '''
        调用openAI API语音转文字
        '''
        # 读取reord种存储的wmv文件，存储是为了复盘
        audio_file = os.path.join(self.savefolder, str(self.dialogidx) + '.wav')
        transcription = self.client.audio.transcriptions.create(
        model="whisper-1", 
        file=open(audio_file, "rb")
        )
        return transcription.text

    def judgement(self, yourresponse, sentence):
        '''

        评分
        '''
        prompt = f"""
        原句：{sentence}
        考生翻译：{yourresponse}
        请判断考生的翻译是否正确并给出建议，在给出建议的时候不用再完整的提及原句和考生翻译，只需给出建议。如果考生翻译有错误之处，也需要给出正确的翻译
        """
        response = self.client.chat.completions.create(


                model="gpt-3.5-turbo", 
                messages=[
                    {"role": "system", "content": "你是一个CCL（Credentialed Community Language Test）考官，需要判断考生的翻译水平。在原句是英文时，考生需要将其翻译为中文；在原句时中文时，考生需要将其翻译成英文"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0
            )

        return_message = f'原句：{sentence}, 你的回答：{yourresponse}, GPT评分：{response.choices[0].message.content}'


        return return_message
    
    def write_gpt_result(self):
        fname = os.path.join(self.savefolder, 'gpt_result.txt')
        with open(fname, 'w') as f:
            for line in self.output:
                f.write(line + '\n\n')
        print(f'GPT评分结果已保存为 {fname}')

    def test(self, test_path):
        self.load_test(test_path)

        for _ in range(len(self.dialog)):
            sentence = self.dialog[self.dialogidx]
            sentence_path = self.text_to_voice(sentence)
            self.playsound(sentence_path)
            self.record()
            recorded_text = self.voice_to_text()
            judgement = self.judgement(recorded_text, sentence)
            self.output.append(judgement)
            # 下一句
            self.dialogidx += 1
        self.write_gpt_result()

    def play_sys_sound_only(self, test_path):
        self.load_test(test_path)
        for sentence in self.dialog:
            print(sentence)
            sentence_path = self.text_to_voice(sentence)
            self.playsound(sentence_path)
            time.sleep(15)

if __name__ == '__main__':
    ccl = ccl_helper(apikey)
    # ccl.play_sys_sound_only('./dialogs/03_group_tour')
    ccl.test('./dialogs/03_group_tour')


