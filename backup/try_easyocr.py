import easyocr

num=0
reader = easyocr.Reader(['en'],gpu=False)
result = reader.readtext('easy.png',detail = 0)
for i in result:
    if '2023' in i:
        num = num + 1

print(num)
print(result)