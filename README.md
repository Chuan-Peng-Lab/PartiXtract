# PartiXtract

## Introduction

PartiXtract is an innovative tool that utilizes advanced Language Model Machines (LLMs) to automatically extract participant-related information from academic papers. This cutting-edge technology can accurately and efficiently extract a wide range of information about study participants, including their race, ethnicity, education, socio-economic status, and more.

By using LLMs to analyze natural language text in academic papers, PartiXtract can quickly identify and extract relevant information about study participants. This can save researchers significant time and effort compared to manual data entry or extraction methods, while also improving the accuracy and completeness of the extracted data.

## Setup

requirements:

1. First, you need to ensure that you have installed the latest version of the Google Chrome browser on your computer. This is because the program requires Chrome to be installed in order to run.

2. Next, you will need to install the necessary Python dependencies. You can do this by running the following command in your terminal:

    ```shell

    pip install -r requirements.txt

    ```

3. Fill in your ChatGPT API key in the 'api' variable of the program. This is necessary to authenticate your requests to the ChatGPT API and ensure that you can make use of its features.

4. In the PaperReader() constructor, fill in the doi of the papers you need to summarize the information of the subjects in the form of strings

5. Run the program by executing the appropriate command in your terminal or IDE. With everything set up properly, you should be able to start using the program right away.

## Data storage

To facilitate meta-analysis, we need use __neo4j__ database to store data
Convert the data in the obtained csv file into a database Paper node

```sql
LOAD CSV WITH HEADERS FROM "file:///result.csv" as csvLine
CREATE (p:Paper{doi: csvLine.doi,sample_size:csvLine.sample_size,female:csvLine.female,
mean_age:csvLine.mean_age,age_span:csvLine.age_span,education:csvLine.education,race:csvLine.race,area:csvLine.area,socioeconomic:csvLine.socioeconomic,remuneration:csvLine.remuneration,handedness:csvLine.handedness})
```

Researchers can conduct further meta-analysis by customizing the relationship between nodes in neo4j

## Packages Required

1. [openai](https://github.com/openai/openai-python)  
2. [selenium](https://www.selenium.dev/)  
3. [webdriver-manager](https://github.com/SergeyPirogov/webdriver_manager)
