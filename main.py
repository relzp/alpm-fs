from pyalpm import Handle


def main():
    # open local db
    handle = Handle("/", "/var/lib/pacman")
    local_db = handle.get_localdb()

    # get installed pkgs in local db
    pkgs = local_db.pkgcache
    # print pkg name and file list
    for pkg in pkgs:
        print(pkg.name)
        files = pkg.files
        for path, size, mode in files:
            print(path)

if __name__ == "__main__":
    main()