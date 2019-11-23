from django.test import TestCase

# Create your tests here.

dic = {"a":1, "b":2}
c = dic.get("c")

if not c:
    print(1)