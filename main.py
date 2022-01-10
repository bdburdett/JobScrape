# Author: Ben Burdett
# Date: 9/11/2021
# Description: Webscraper using Beautiful Soup to search for jobs on indeed, then exporting to a CSV file and uploading 
# to an AWS S3 bucket automatically for specified time. Adjust the EC2 server, but currently running at every minute

import requests
from bs4 import BeautifulSoup
import pandas as pd
import boto3
import os

def extract(page):
    """taking the data from the specified website and parsing"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    url = f'https://www.indeed.com/jobs?q=python%20developer&l=Florida&start={page}'
    r = requests.get(url, headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    return soup

def transform(soup):
    """taking the parsed data from html to a readable format"""
    divs = soup.find_all('div', class_ = 'slider_container')
    for item in divs:
        title = item.find('h2').text
        company = item.find('span', class_ = 'companyName').text.strip()
        try:
            salary = item.find('span', class_ = 'salary-snippet').text.strip()
        except:
            salary = ''
        summary = item.find('div', class_ = 'job-snippet').text.strip().replace('\n', '')

        job = {

            'title'     : title,
            'company'   : company,
            'salary'    : salary,
            'summary'   : summary,
        }
        joblist.append(job)
    return

joblist = []

# For loop to grap as many pages as offered, example is to just get small data set of 4 pages
for i in range(0, 40, 10):
    print(f'Getting page: {i}')
    c = extract(0)
    transform(c)

# Create the jobs file, CSV
df = pd.DataFrame(joblist)
df.to_csv('jobs.csv')

# Connecting to AWS with keys
client = boto3.client('s3',
                      aws_access_key_id=os.environ.get('aws_access_key_id'),
                      aws_secret_access_key=os.environ.get('aws_secret_access_key'))

# CRUD to S3 bucket
for file in os.listdir():
    if '.csv' in file:
        upload_file_bucket = 'S3_Bucket_Name'
        upload_file_key = 'csv/' + str(file)
        client.upload_file(file, upload_file_bucket, upload_file_key)
