# Website Response Time Checker

import requests
import time


url = input("Enter the URL to check: ")

start = time.time()
response = requests.get(url)
end= time.time()

response_time = end - start

print(f"Response time for {url}: {response_time * 1000:.2f} milliseconds")

