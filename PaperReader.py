import json

import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

required_list = ["female", "mean_age", "age_span", "education",
                 "race", "area", "socioeconomic", "remuneration", "handedness"]


class PaperReader:

    def __init__(self, path, api):
        self.path = path
        self.api = api
        self.paper_participants = self.paper_crawler()
        self.doi = "10." + path.split('10.')[-1]
        self.GPT_result = ''

    def paper_crawler(self):
        driver_op = Options()
        driver_op.add_argument('--window-size=1920,1080')

        # Whether to visualize following two lines:
        driver_op.add_argument('--headless')
        driver_op.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36")

        driver_op.add_argument('--no-sandbox')
        driver_op.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=driver_op)
        driver.get(self.path)
        paper_participants = ''
        sections = driver.find_elements(By.TAG_NAME, 'section')
        for section in sections:
            if section.text.startswith("Participants"):
                paper_participants = section.text
                break
        return paper_participants

    def GPT_Paper(self):
        openai.api_key = self.api
        messages = [
            {"role": "system", "content": "You are a researcher who is good at summarizing information about subjects in psychology papers in concise sentences"},
            {"role": "assistant", "content": "This is the paragraph in the text that contains the subject's information: <"
             + self.paper_participants + ">, please extract information from it, including but not limited to age, gender, region, race and education level, please try to answer the following questions"},
            {"role": "user", "content":
                """ 
                Please refer to the format of the following example to output the subject information of the paper based on the information I provided and do not output any information other than data:
                "Fourteen self-identified Chinese Buddhists (seven males, seven females, 21–31 years of age, mean 25.4, sd 2.46) participated in this study as paid volunteers. 
                The participants had been attached to local faith communities for 1–7 years (mean 2.5, sd 2.0) when they participated in this study. These participants are recruited from Shanxi Province, China. 
                Eleven participants reported to attend the community activity at least once a week. Twelve participants reported to cultivate themselves according to Mahayana (one of the major schools of Buddhism) doctrine everyday. 
                Ten participants reported to read sutra everyday. The participants were asked to rate the importance they placed on religion and their attitude toward Buddha, 
                based on a 5-point scale (0 ¼ not important or do not believe at all, 4 ¼ very important or strongly believe), resulting a mean rating score of 3.56. All participants had no neurological or psychiatric history. 
                All participants had college education, were right-handed and had normal or corrected-to-normal vision. Informed consent was obtained from all participants prior to scanning. This study was approved by a local ethics committee.",
                output example:
                {
                    "sample_size": 14,
                    "female": 7,
                    "mean_age": 25.4,
                    "age_span": "23-31 and 25.4±2.46",
                    "education": "college education",
                    "race": "Chinese",
                    "area": "Shanxi Province, China",
                    "socioeconomic": "NA",
                    "remuneration": "NA",
                    "handedness": "right-handed"
                },
                """
             },
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        for choice in response.choices:
            self.GPT_result += choice.message.content
        print(self.GPT_result, end="\n\n")
        print("prompt_token_used:", response.usage.prompt_tokens,
              "completion_token_used:", response.usage.completion_tokens,
              "total_token_used:", response.usage.total_tokens, end="\n")
        print("response_time:", response.response_ms/1000.0, 's')

    def save_as_csv(self):
        formated_data = json.loads(self.GPT_result)
        temp = ""
        for i in required_list:
            temp = temp + str(formated_data[i]) if str(
                formated_data[i]) != "NA" else "" + ','
        temp = temp[:-1]
        try:
            open("./result.csv", "r+")
        except IOError:
            file = open("./result.csv", 'w+')
            lable = "doi:ID,"
            for i in required_list:
                lable = lable + i + ","
            lable = lable[:-1]
            file.write(lable+'\n')
            file.close()
        file = open("./result.csv", 'a+')
        file.write(temp+'\n')
        file.close()


if __name__ == "__main__":
    # api = 'sk-#################'
    api = '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'
    PR = PaperReader(
        "https://journals.sagepub.com/doi/10.1177/19485506221107268", api)
    PR.GPT_Paper()
    PR.save_as_csv()
