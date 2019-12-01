from django.test import TestCase

# Create your tests here.

l1 = [1, 2, 3, 4]
l2 = ['a', 'b', 'c', 'd']

for i in l1:
    print("i:",i)
    for q in l2:
        print('q:', q)
        if q == "b":
            break
    print(1121221)
