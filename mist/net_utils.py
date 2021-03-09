import urllib
import pathlib
import urllib.request

def download(url: str, destination: str):
    with open(destination, "w") as f:
        with urllib.request.urlopen(url) as remote:
            f.write(remote.read())
            f.flush()

# This function was taken from:
# https://stackoverflow.com/a/57463161/8153205
#
def file_uri_to_path(file_uri, path_class=pathlib.PurePath):
    """
    This function returns a pathlib.PurePath object for the supplied file URI.

    :param str file_uri: The file URI ...
    :param class path_class: The type of path in the file_uri. By default it uses
        the system specific path pathlib.PurePath, to force a specific type of path
        pass pathlib.PureWindowsPath or pathlib.PurePosixPath
    :returns: the pathlib.PurePath object
    :rtype: pathlib.PurePath
    """
    windows_path = isinstance(path_class(),pathlib.PureWindowsPath)
    file_uri_parsed = urllib.parse.urlparse(file_uri)
    file_uri_path_unquoted = urllib.parse.unquote(file_uri_parsed.path)
    if windows_path and file_uri_path_unquoted.startswith("/"):
        result = path_class(file_uri_path_unquoted[1:])
    else:
        result = path_class(file_uri_path_unquoted)
    if result.is_absolute() == False:
        raise ValueError("Invalid file uri {} : resulting path {} not absolute".format(
            file_uri, result))
    return result

__all__ = ("download", "file_uri_to_path")
