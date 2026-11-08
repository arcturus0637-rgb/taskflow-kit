"""Version-independent path checks shared by the installer and evidence tool."""


def is_link(path):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    return path.is_symlink() or getattr(info, 'st_reparse_tag', 0) in (0xA0000003, 0xA000000C)
