import os
import json


def main():
    ignore = ['.xsd', '*.vsix']
    with open('.gitignore', 'w') as f:
        f.write('\n'.join(ignore))

    os.mkdir('.vscode')
    with open('/code/scripts/settings.json', 'r') as f:
        settings = json.load(f)

    with open('.vscode/settings.json', 'w') as f:
        json.dump(settings, f)

    os.remove("README.md")


if __name__ == "__main__":
    main()
