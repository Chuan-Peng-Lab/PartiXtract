import time

import fitz
import openai
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# api = 'sk-#################'
api = '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'


class PaperReader:

    class Paper:
        # Paper内部类
        def __init__(self):
            self.paper_name = ''
            self.paper_url = ''
            self.paper_authors = ''
            self.paper_abstract = ''
            self.paper_content = ''
            self.paper_references = ''

        def all_text(self):
            return self.paper_name+'\n\n' + self.paper_authors + '\n\n' + \
                self.paper_abstract+'\n\n' + self.paper_content+'\n\n' + self.paper_references

        def saveText(self, ouput_path):
            with open(ouput_path, "w") as file:
                file.write(self.all_text())

    def __init__(self, path, language="zh"):
        self.path = path
        self.language = language
        if path.endswith(".pdf"):
            self.method = "pdf"
            self.paper = self.readPDF()
        elif path.startswith("https://journals.sagepub.com/"):
            self.method = "URL"
            self.paper = self.readURL()
        else:
            raise Exception("File type not supported")

    """ 未完成
    def readPDF(self):
        pdf = fitz.open(self.path)  # pdf文档
        text_list = [page.get_text() for page in pdf]
        text = ' '.join(text_list)
        pdf.close()
        return text 
    """

    def readURL(self):
        driver_op = Options()
        driver_op.add_argument('--window-size=1920,1080')

        # Whether to visualize following two lines:
        driver_op.add_argument('--no-sandbox')
        driver_op.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=Service(
            ChromeDriverManager().install()), options=driver_op)
        driver.get(self.path)
        time.sleep(2)
        # Accept All
        driver.find_element(
            By.XPATH, "/html/body/div[2]/div/div/div/div[2]/div/button[3]").click()

        # Show all of names
        driver.find_element(
            By.XPATH, "//main/article/header/div/div[2]/span/span/span[3]/span").click()

        paper = self.Paper()

        # Get data from website
        paper.paper_name = driver.find_element(
            By.XPATH, "//main/article/header/div/h1").text
        paper.paper_authors = driver.find_element(
            By.XPATH, "//main/article/header/div/div[2]/span").text.replace('\n', '').replace('\r', '')
        paper.paper_abstract = driver.find_element(
            By.XPATH, "//main/article/div[2]/div").text
        paper.paper_content = driver.find_element(
            By.XPATH, "//main/article/section[1]").text
        paper.paper_references = driver.find_element(
            By.XPATH, "//main/article/section[2]").text

        paper.paper_url = self.path
        return paper

    def GPT_Paper(self):
        openai.api_key = api
        messages = [
            {"role": "system", "content": "You are a researcher who is good at summarizing psychology papers in concise sentences"},
            {"role": "assistant", "content": "This is the title: " + self.paper.paper_name + ", author: " + self.paper.paper_authors + ", link: " + self.paper.paper_url +
                ", abstract: " + self.paper.paper_abstract + " of an English document. I need your help to read and summarize the following questions: "},
            {"role": "user", "content": """                 
                 1. Mark the title of the paper (with Chinese translation)
                 2. list all the authors' names (use English)
                 3. mark the first author's affiliation (output {} translation only)                 
                 4. mark the keywords of this article (use English)
                 5. link to the paper, Github code link (if available, fill in Github:None if not)
                 6. summarize according to the following four points.Be sure to use {} answers (proper nouns need to be marked in English)
                    - (1):What is the research background of this article?
                    - (2):What are the past methods? What are the problems with them? Is the approach well motivated?
                    - (3):What is the research methodology proposed in this paper?
                    - (4):On what task and what performance is achieved by the methods in this paper? Can the performance support their goals?
                 Follow the format of the output that follows:                  
                 1. Title: xxx\n\n
                 2. Authors: xxx\n\n
                 3. Affiliation: xxx\n\n                 
                 4. Keywords: xxx\n\n   
                 5. Urls: xxx or xxx , xxx \n\n      
                 6. Summary: \n\n
                    - (1):xxx;\n 
                    - (2):xxx;\n 
                    - (3):xxx;\n  
                    - (4):xxx.\n\n     
                 
                 Be sure to use {} answers (proper nouns need to be marked in English), statements as concise and academic as possible, do not have too much repetitive information, numerical values using the original numbers, be sure to strictly follow the format, the corresponding content output to xxx, in accordance with \n line feed.                 
                 """.format(self.language, self.language, self.language)},
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        result = ''
        for choice in response.choices:
            result += choice.message.content
        print("method_result:\n", result, end="\n\n")
        print("prompt_token_used:", response.usage.prompt_tokens,
              "completion_token_used:", response.usage.completion_tokens,
              "total_token_used:", response.usage.total_tokens, end="\n")
        print("response_time:", response.response_ms/1000.0, 's')
        return result


if __name__ == "__main__":
    PR = PaperReader(
        "https://journals.sagepub.com/doi/full/10.1177/1948550620902281", language="en-us")
    GPT_result = PR.GPT_Paper()
    with open("./test", "w") as file:
        file.write(GPT_result)
    # PR.paper.saveText("paper.txt")
