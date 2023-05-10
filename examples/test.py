# import adafruit_json_stream as json_stream
import json_stream
import sys

class FakeResponse:
    def __init__(self, file):
        self.file = file

    def iter_content(self, chunk_size):
        while True:
            yield self.file.read(chunk_size)

f = open(sys.argv[1], "rb")
obj = json_stream.load(FakeResponse(f).iter_content(32))

currently = obj["currently"]
print(currently)
print(currently["time"])
print(currently["icon"])

for i, day in enumerate(obj["daily"]["data"]):
    print(day["time"], day["summary"], day["temperatureHigh"])
    if i > 6:
        break

for source in obj["flags"]["sources"]:
    print(source)
