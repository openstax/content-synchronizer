import os
import json
import shutil
import sys
from pathlib import Path


def cleanup(rollback_dir):
    shutil.rmtree(rollback_dir)


def rollback(code_dir, rollback_dir):
    try:
        shutil.rmtree('.vscode')
    except:
        pass

    try:
        os.remove('.gitignore')
    except:
        pass

    for root, dirs, files in os.walk(rollback_dir):

        for d in dirs:
            path_dir = os.path.join(root, d)
            dest_path_dir = path_dir.replace(rollback_dir, code_dir)
            os.mkdir(dest_path_dir)

        for f in files:
            path_file = os.path.join(root, f)
            dest_path_file = path_file.replace(rollback_dir, code_dir)
            shutil.copy2(path_file, dest_path_file)

    cleanup(rollback_dir)


def main():
    code_dir = Path(sys.argv[1]).resolve(strict=True)
    rollback_dir = str(sys.argv[1])+'/rollback'
    os.mkdir(rollback_dir)
    try:
        poet_files = f'{code_dir}/poet.json'
        with open(poet_files, 'r') as pf:
            poet_files = json.loads(pf.read())

        # handling .gitignore
        try:
            shutil.move('.gitignore', rollback_dir)
        except FileNotFoundError:
            pass

        gitignore_path = os.path.join(code_dir, '.gitignore')
        with open(gitignore_path, 'x') as f:
            f.write('\n'.join(poet_files['gitignore']))

        # handling .vscode/settings.json
        dest_dir = os.path.join(code_dir, '.vscode')
        try:
            shutil.move(dest_dir, rollback_dir)
        except FileNotFoundError:
            pass

        os.mkdir(dest_dir)
        file = '/settings.json'
        dest_path = dest_dir + file

        with open(dest_path, 'x') as f:
            json.dump(poet_files['vscode'], f, indent=2)

        # handling readme
        try:
            read_me = os.path.join(code_dir, 'README.md')
            shutil.move(read_me, rollback_dir)
        except FileNotFoundError:
            pass

        cleanup(rollback_dir)
    except:
        rollback(code_dir, rollback_dir)
        sys.exit(1)


if __name__ == "__main__":
    main()
