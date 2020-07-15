from datetime import datetime

begin = datetime.now()
end = datetime.now()
while ((end.seconds - begin.seconds) * 1000000 + end.microsecond - begin.microsecond) < 100:
    end = datetime.now()

print(begin)
print(end)
print(end - begin)