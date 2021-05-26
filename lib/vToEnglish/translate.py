# Python3.6+, install the googletrans using:
# pip install googletrans
# import Translator to detect language and translate...
from googletrans import Translator

# Customize service URL
translator = Translator(service_urls=['translate.google.cn'])


def translate(text, dest='en', src='auto'):
	"""
		:param text: origin text -> str or list
		:param src: origin language -> str
		:param dest: translation language -> str
		:return: translated text -> str or list

		languages: {‘zh-cn’: ‘chinese (simplified)’, ‘zh-tw’: ‘chinese (traditional)’, ‘en’: ‘english’,
					‘fr’: ‘french’, ‘it’: ‘italian’, ‘ja’: ‘japanese’, ...}
					you can use following statement to supported languages:
						import googletrans
						print(googletrans.LANGUAGES)
	"""
	if isinstance(text, str):
		return translator.translate(text, dest, src).text
	elif isinstance(text, list):
		return [translation.text for translation in translator.translate(text, dest, src)]
	else:
		return None


if __name__ == '__main__':
	# 1. use string
	print(translate("今天在计算所上班"))
	# out: Work at the computing office today

	# 2. use list
	print(translate(["今天的不开心就止于此吧", "明天依旧光芒万丈"]))
	# out: ["Today's unhappiness stops here, right", 'Tomorrow will still shine']

	# 3. use param dest
	print(translate("宝贝", 'zh-tw'))
	# or
	# print(translate(["宝贝", dest='zh-tw'))
	# out: 寶貝

	# 4. use param src
	print(translate("寶貝", src='zh-tw'))
	# out: baby

	# 5. use all param
	print(translate(["今天的不开心就止于此吧", "明天依旧光芒万丈", "宝贝"], 'zh-tw', 'zh-cn'))
	# or
	# print(translate(["今天的不开心就止于此吧", "明天依旧光芒万丈", "宝贝"], dest='zh-tw', src='zh-cn'))
	# out: ['今天的不開心就止於此吧', '明天依舊光芒萬丈', '寶貝']
