def isEnglish(s : str) -> bool: 
    try: 
        s.encode(encoding='utf-8').decode('ascii') 
    except UnicodeDecodeError: 
        return False 
    else: 
        return True


def hasChinese(word : str) -> bool:
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False

def countChinese(word : str) -> bool:
    rst = 0
    for ch in word:
        if '\u4e00' <= ch <= '\u9fff':
            rst += 1
    return rst