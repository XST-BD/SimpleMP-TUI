def int_input_validator(value, maxx, minn):
	digits = ""
	for char in value:
		if char.isdigit():
			digits += char

	if digits != "":
		number = int(digits)
		if number > maxx:
			number = maxx
		elif number < minn:
			number = minn
		return str(number)
	else:
		return ""
