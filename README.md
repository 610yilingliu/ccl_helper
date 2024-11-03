# ccl备考助手
使用大模型API进行ccl双向翻译纠正，由于大模型可以识别各种奇怪的口音所以英文发音不好的同学请自行纠正，否则会导致意思正确但考试低分

apikey为openai的apikey，存放在同目录.env文件中（请自行创建.env文件，内容为OPENAI_API_KEY = '你的key'，如果没有就去[OpenAI](https://platform.openai.com/api-keys) 自己建一个(记得充钱)

如果要多次练习，强烈建议仅使用play_sys_sound_only+录音人工判定，调用GPT非常烧钱

使用方法：

```pip install -r requirements.txt```

application.py中有play_sys_sound_only(穷鬼辅助版，模拟考试环境)和text（土豪带评分版，这样会生成每句的AI评价但是很烧钱）

requirements.txt中如果有包装不上可以google查一下对应的包的具体安装名，我直接把import后面接的写上去了，但可能有错