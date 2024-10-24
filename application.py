import os
import openai
import hashlib
import string
import subprocess
from google.cloud import texttospeech


apikey = os.getenv("OPENAI_API_KEY")


class ccl_helper:
    def __init__(self, apikey):
        '''
        apikey为openai的apikey，存放在同目录.env文件中（请自行创建.env文件，内容为OPENAI_API_KEY = '你的key'，如果没有就去https://platform.openai.com/api-keys自己建一个
        '''
        self.apikey = apikey
        self.dialog = None
        self.dialogidx = 0
        self.voicepath = "voice"
        self.en_voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Studio-M",
        )
        self.zh_voice = texttospeech.VoiceSelectionParams(
            language_code="cmn-CN",
            name="cmn-CN-Wavenet-A",
        )

    def load_test(self, file):
        '''
        每行为一个对话轮次，常规情况是一行英文（考试时需要你说对应英文），一行中文（考试时需要你说对应英文）
        self.dialog会变成一个列表
        '''
        with open(file, "r") as f:
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
        def remove_punctuations(stext):
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
        path = os.path.join(self.voicepath, text_md5, ".mp3")
        if os.path.exists(path):
            return path
        if is_zh:
            voice = self.zh_voice
        else:
            voice = self.en_voice
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=1.2
        )
        synthesis_input = texttospeech.SynthesisInput(text=text)
        response = self.tts.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
        with open(path, "wb") as out:
            out.write(response.audio_content)
            print(f'MP3 Generated for Content: {text}')
        return path
    
    def talk(self):
        curtext = self.dialog[self.dialogidx]
        soundpath = self.sound_generator(curtext)
        self.playsound(soundpath)
        self.dialogidx += 1
        return curtext

    def record(self):
        '''
        录音
        '''
        pass

    def voice_to_text(self):
        '''
        调用google api语音转文字
        '''
        pass

    def judgement(self, yourresponse, sentence):
        '''
        评分
        '''
        prompt_base = f"""你是一个CCL（Credentialed Community Language Test）考官，需要判断考生的翻译水平。句子1是考生的翻译，句子2是原句，请判断考生的翻译是否正确并给出建议
        句子1：{yourresponse}
        句子2：{sentence}
        """

        pass