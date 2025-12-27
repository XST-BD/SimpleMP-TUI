def to_int(value, default=0) -> int:
	if value and value.isdigit():
		return int(value)
	return default