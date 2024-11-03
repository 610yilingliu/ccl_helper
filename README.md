# ccl备考助手
使用大模型API进行ccl双向翻译纠正，由于大模型可以识别各种奇怪的口音所以英文发音不好的同学请自行纠正，否则会导致意思正确但考试低分

使用前请确保自己能够通过CLI使用google API 并已配置ADC：[官方文档](https://cloud.google.com/docs/authentication/provide-credentials-adc?hl=zh-cn#google-idp)

apikey为openai的apikey，存放在同目录.env文件中（请自行创建.env文件，内容为OPENAI_API_KEY = '你的key'，如果没有就去[OpenAI](https://platform.openai.com/api-keys) 自己建一个(记得充钱)