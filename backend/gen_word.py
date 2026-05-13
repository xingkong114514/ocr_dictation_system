# 8
# 4
with open("test.txt","w",encoding='utf-8') as f:
    while(True):
        Unit=int(input("输入单元总数:"))
        if Unit==-1:
            break
        for u in range(1,Unit+1):
            section=int(input("输入节数:"))
            for s in range(1,section+1):
                word=input("输入词语")
                word=word.split(" ")
                print(word)
                print(type(word))
                result = []
                for i in range(len(word)):
                    if(word[i]!=" "):
                        result.append(word[i])
                for i in range(len(result)):
                    f.write('{}.{}.{}.{}\n'.format(u,s,i+1,result[i]))
