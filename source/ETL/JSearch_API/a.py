import http.client

conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "de01264b9dmsh89ceede4da88b5fp17c136jsn16c56b0e2808",
    'x-rapidapi-host': "jsearch.p.rapidapi.com"
}

conn.request("GET", "/job-details?job_id=n20AgUu1KG0BGjzoAAAAAA%3D%3D&country=us", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))