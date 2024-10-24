import os
import openai



apikey = os.getenv("OPENAI_API_KEY")


class ccl_helper:
    def __init__(self, apikey):
        '''
        apikey为openai的apikey，存放在同目录.env文件中（请自行创建.env文件，内容为OPENAI_API_KEY = '你的key'，如果没有就去https://platform.openai.com/api-keys自己建一个
        '''
        self.apikey = apikey
        self.dialog = None
        self.dialogidx = 0

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
    
    def robot_speak(self, text):
        '''
        google tts文字转语音没有中文选项（悲）调研可用api中
        '''
        cur_sentance = self.dialog[self.dialogidx]
        is_ch = self.is_chinese(cur_sentance)
        if is_ch:



        # 移动到下一句
        self.dialogidx += 1