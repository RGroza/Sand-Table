from datetime import datetime

for i in range(10):
    begin = datetime.now()
    end = datetime.now()
    while ((end.second - begin.second) * 1000000 + end.microsecond - begin.microsecond) < 10:
        end = datetime.now()

    print(begin)
    print(end)
    print(end - begin)
