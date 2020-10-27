from configparser import ConfigParser


def validate_command_meta(meta_path: str) -> None or dict:
    _c_parser = ConfigParser()
    _c_parser.read(filenames=meta_path)
    meta_content = _c_parser.__dict__["_sections"]

    if not "default" in meta_content:
        return None

    meta_default = meta_content["default"]

    if "version" not in meta_default:
        return None

    return meta_default


def validate_index_file(index_path: str) -> None or dict:
    _c_parser = ConfigParser()
    _c_parser.read(filenames=index_path)
    index_content = _c_parser.__dict__["_sections"]

    if not "MIST-INDEX" in index_content:
        return None

    index_mist = index_content["MIST-INDEX"]

    if not all(x in index_mist for x in (
            "name", "description", "tags", "latest"
    )):
        return None

    return index_mist

__all__ = ("validate_command_meta", "validate_index_file")
