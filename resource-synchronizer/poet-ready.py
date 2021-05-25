import os
import json
import shutil
import sys

RB_DIR = 'rollback'
CODE_DIR = os.environ.get('CODE_DIR')


def cleanup():
    shutil.rmtree(RB_DIR)


def rollback():
    try:
        shutil.rmtree('.vscode')
    except:
        pass

    try:
        os.remove('.gitignore')
    except:
        pass

    for root, dirs, files in os.walk(RB_DIR):

        for d in dirs:
            path_dir = os.path.join(root, d)
            dest_path_dir = path_dir.replace(RB_DIR, CODE_DIR)
            os.mkdir(dest_path_dir)

        for f in files:
            path_file = os.path.join(root, f)
            dest_path_file = path_file.replace(RB_DIR, CODE_DIR)
            shutil.copy2(path_file, dest_path_file)

    cleanup()


def main():
    os.mkdir(RB_DIR)
    try:
        ignore = ['.xsd', '*.vsix']
        try:
            shutil.move('.gitignore', RB_DIR)
        except FileNotFoundError:
            pass

        with open('.gitignore', 'x') as f:
            f.write('\n'.join(ignore))
        print('.gitignore created')

        src_dir = CODE_DIR
        dest_dir = '.vscode'
        file = '/settings.json'

        try:
            shutil.move(dest_dir, RB_DIR)
        except FileNotFoundError:
            pass

        os.mkdir(dest_dir)

        src_path = src_dir + file
        dest_path = dest_dir + file
        shutil.copyfile(src_path, dest_path)

        try:
            shutil.move('README.md', RB_DIR)
        except FileNotFoundError:
            pass

        cleanup()
    except:
        rollback()
        sys.exit()  # exit something went wrong


if __name__ == "__main__":
    main()
