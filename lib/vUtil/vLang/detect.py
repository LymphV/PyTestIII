def isEnglish(s): 
    try: 
        s.encode(encoding='utf-8').decode('ascii') 
    except UnicodeDecodeError: 
        return False 
    else: 
        return True


def hasChinese(word):
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def countChinese(word):
    rst = 0
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            rst += 1
    return rst