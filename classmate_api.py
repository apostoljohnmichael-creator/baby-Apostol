
import requests

url = "https://jasminerose-2.onrender.com"

try:
    response = requests.get(url, timeout=60)

    print("Status Code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))

    if response.status_code == 200:
        try:
            data = response.json()
            print("Classmate API Data:", data)
        except ValueError:
            print("The website did not return valid JSON.")
            print("Response:")
            print(response.text[:1000])
    else:
        print("Request failed.")
        print(response.text[:500])

except requests.RequestException as e:
    print("Connection error:", e)
