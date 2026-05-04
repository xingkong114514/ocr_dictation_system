with open("oneon.txt","r",encoding="utf-8") as f:
    pre=-1
    i=1
    for line in f.readlines():
        lst=line.split(".")
        U=lst[0]
        S=lst[1]
        word=lst[3][:-1]
        if S!=pre:
            i=1
        with open("oneon_.txt","a+",encoding="utf-8") as f:
            f.write('{}.{}.{}.{}\n'.format(U,S,i,word))
            i+=1
        pre=S

