FILE_EXTENSIONS = {"video": ["mp4"], "image": ["jpeg", "jpg"]}


def get_type(extension: str):
    """ Returns if the file is video, image or some other type """

    for type in FILE_EXTENSIONS.items():
        type = list(type)
        for ext in type[1]:
            if ext == extension:
                return type[0]

    return "other"
