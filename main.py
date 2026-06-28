import argparse
import logging
import os
from pyalpm import Handle


def main():
    # Handle command line args
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="folder to create hierarchy under")
    args = parser.parse_args()

    # Get root dir from cli args, mkdir it and chdir to it
    root = args.root
    root_abs = os.path.abspath(root)
    try:
        os.mkdir(root)
        os.chdir(root)
    except FileExistsError:
        files = os.listdir(root)
        if files:
            logging.error("Root directory already exists and is not empty, exiting")
            return
    logging.debug("creating hierarchy under: {}".format(root))

    # Open local db and get list of locally-installed packages
    handle = Handle("/", "/var/lib/pacman")
    local_db = handle.get_localdb()
    pkgs = local_db.pkgcache

    # Create hierarchy of symlinks for each package
    for pkg in pkgs:
        name = pkg.name
        logging.debug("creating hierarchy for package {}".format(name))
        os.mkdir(name)
        os.chdir(name)

        # Filter files to only entries not a prefix of the next file
        # First perform a lexicographic sort
        files = sorted(pkg.files)
        files_no_prefixes = []
        # For each path, only include if not a prefix of the next path
        for idx, (path, size, mode) in enumerate(files):
            if idx + 1 < len(files):
                next_path = files[idx + 1][0]
                if next_path.startswith(path):
                    continue
            # Remove trailing slash from dirs to avoid issues in next section
            path = path.removesuffix("/")
            files_no_prefixes.append(path)

        # Iterate through filtered files
        for path in files_no_prefixes:
            logging.debug("processing file {}".format(path))
            # Make parent dir, if any
            path_dir = os.path.dirname(path)
            if path_dir:
                logging.debug("making dir {}".format(path_dir))
                os.makedirs(path_dir, exist_ok=True)

            # Construct path under root dir, then symlink to actual file
            actual_file_path = os.path.join("/", path)
            logging.debug("making symlink {} -> {}".format(path, actual_file_path))
            os.symlink(actual_file_path, path)

        # Return to root dir
        os.chdir("..")

if __name__ == "__main__":
    main()