from simplemp.validator import media_type_ext_dict


def media_type(ext: str) -> str | None:
	for media, exts in media_type_ext_dict.items():
		if ext in exts:
			return media

	return None
