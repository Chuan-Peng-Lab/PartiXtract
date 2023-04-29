import json

import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# chatgpt api = 'sk-#################'
api = ""
# csv中所需被试者信息的标签
required_list = [
    "sample_size",
    "female",
    "mean_age",
    "age_span",
    "education",
    "race",
    "area",
    "socioeconomic",
    "remuneration",
    "handedness",
]


class PaperReader:
    # 构造函数,初始化PaperReader类,其中*doi是可变参数(你们自己查查是什么)
    def __init__(self, *doi):
        # 遍历所有doi,分别爬取论文,并提炼被试者信息
        for temp_doi in doi:
            # 初始化类变量
            self.url = "https://journals.sagepub.com/doi/" + temp_doi
            self.api = api
            self.doi = temp_doi
            # 如果爬虫成功爬取信息,再继续进行下两步(函数在if中也会运行的)
            if self.paper_crawler():
                # 使用chatgpt提炼被试者信息
                self.GPT_Paper()
                # 将被试者信息以scv文件格式保存
                self.save_as_csv()
            else:
                print("Internet issue or did not find information of this doi(" +
                      temp_doi+") in https://journals.sagepub.com.")

    # 爬虫函数,有兴趣可以研究一下
    def paper_crawler(self):
        # 初始化驱动
        driver_op = Options()
        driver_op.add_argument("--window-size=1920,1080")

        # 以下两行决定爬取过程是否可见
        driver_op.add_argument("--headless")
        driver_op.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        )

        driver_op.add_argument("--no-sandbox")
        driver_op.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=driver_op
        )
        # 尝试爬取信息
        try:
            # 打开论文的网址
            driver.get(self.url)
            # 初始化储存被试者信息段落的变量
            self.paper_participants = ""
            # 以tagname找到所有section
            sections = driver.find_elements(By.TAG_NAME, "section")
            # 遍历所有sanction,找到前50个字符包括participant或subject的段落,同时不以method开头
            for section in sections:
                if ("participant" in section.text[0:50].lower() or "subject" in section.text[0:50].lower()) and not section.text.startswith("Method"):
                    self.paper_participants = section.text
                    break
        # 如果爬取失败或者,找不到包含participant的段落返回错误,不继续进行接下来的操作
        except:
            return False
        if self.paper_participants == "":
            return False
        return True

    def GPT_Paper(self):
        # 初始化openai的api
        openai.api_key = self.api
        # 指定对话的内容,此处仍可以优化
        messages = [
            {
                "role": "system",
                "content": "You are a researcher who is good at summarizing information about subjects in psychology papers in concise sentences",
            },
            {
                "role": "assistant",
                "content": "This is the paragraph in the text that contains the subject's information: <"
                + self.paper_participants
                + ">, please extract information from it, including but not limited to age, gender, region, race and education level, please try to answer the following questions",
            },
            {
                "role": "user",
                "content": """ 
                Please refer to the format of the following example to output the subject information of the paper based on the information I provided and do not output any information other than data,If unspecified in the text, please use "NA" insteal.
                output example:
                {
                    "sample_size": "",
                    "female": "",
                    "mean_age": "",
                    "age_span": "",
                    "education": "",
                    "race": "",
                    "area": "",
                    "socioeconomic": "",
                    "remuneration": "",
                    "handedness": ""
                }
                """,
            },
        ]
        # 向openai发送请求,并得到响应
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        # 遍历每一句响应,将其添加到同一个变量中
        self.GPT_result = ""
        for choice in response.choices:
            self.GPT_result += choice.message.content
        # 可视化输出,和输出使用的token和响应时间
        print(
            "The subject information summarized in the paper(" +
            self.doi + ") is:",
            end="\n\n",
        )
        print(self.GPT_result, end="\n\n")
        print(
            "prompt_token_used:",
            response.usage.prompt_tokens,
            "completion_token_used:",
            response.usage.completion_tokens,
            "total_token_used:",
            response.usage.total_tokens,
            end="\n",
        )
        print("response_time:", response.response_ms / 1000.0, "s", end="\n\n")
    # 将所返回的json格式响应,保存为csv文件

    def save_as_csv(self):
        # 从字符串读取json格式文件
        formated_data = json.loads(self.GPT_result)
        # 初始化csv格式的被试者数据,以文章的doi开头,并逐一根据定义的标签,向变量中添加元素
        temp = str(self.doi) + ","
        for i in required_list:
            temp = temp + str(formated_data[i]) + ","
        # 最后一个,不需要
        temp = temp[:-1]
        # 尝试打开文件,如果不存在的话,创建文件,并向第一行添加标签
        try:
            open("./result.csv", "r+")
        except IOError:
            file = open("./result.csv", "w+")
            # 输入数据标签
            lable = "doi,"
            for i in required_list:
                lable = lable + i + ","
            lable = lable[:-1]
            file.write(lable + "\n")
            file.close()
        # 输入被试者数据
        file = open("./result.csv", "a+")
        file.write(temp + "\n")
        file.close()


if __name__ == "__main__":
    # 通过构造函数初始化,同时运行类函数
    PaperReader("10.1177/19485506221107268", "10.1177/10597123231163595")
