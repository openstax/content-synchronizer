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
        poet_files = f'{CODE_DIR}/poet.json'
        with open(poet_files, 'r') as pf:
            poet_files = json.loads(pf.read())

        # handling .gitignore
        try:
            shutil.move('.gitignore', RB_DIR)
        except FileNotFoundError:
            pass

        with open('.gitignore', 'x') as f:
            f.write('\n'.join(poet_files['gitignore']))

        # handling .vscode/settings.json
        dest_dir = '.vscode'
        try:
            shutil.move(dest_dir, RB_DIR)
        except FileNotFoundError:
            pass

        os.mkdir(dest_dir)
        file = '/settings.json'
        dest_path = dest_dir + file

        with open(dest_path, 'x') as f:
            json.dump(poet_files['vscode'], f, indent=2)

        # handling readme
        try:
            shutil.move('README.md', RB_DIR)
        except FileNotFoundError:
            pass

        raise
        cleanup()
    except:
        rollback()
        sys.exit()


if __name__ == "__main__":
    main()
