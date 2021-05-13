from git import Repo
from github3 import login, GitHubError
import json
import os
import shutil
import sys

# TO DO:
# - Don't use absolute paths, or need to pass it in -
# - Containerize/ build the script in dockerfile/image
# Keep in mind: it matters, where your script is being ran and what location it needs to grab the files it needs.
# write tests for the script
# test the docker image

# How to use script:
# Run this script from content-repos directory
# pass in the following args:
# sys.argv[1]   # file to books json
# sys.argv[2]   # file to github creds json
# sys.argv[3]  # where you want the files to go
# sys.argv[4] # not a test run anymore
# you will want to run manually before creating under opsx

# here = f'/Users/brenda/Projects/00_openstax/content-repos/book-repos/{gh}'
# here = f'/Users/brenda/Projects/00_openstax/content-repos/book-repos/{gh}'

# Notes:
# - test run will render to your github
# - _github, should be a loaded json file, passed in as a path


def msg(msg):
    print(f'... {msg}')


def create_remote_repo(repo, gh):
    repo_name = repo['title']
    # clean up existing remote repository
    try:
        book_repo = gh['account'].repository(
            gh['username'], repo_name)
        if book_repo:
            user_resp = input(
                'Book exists REMOTELY, Delete REMOTE book and continue? (y/n) >> ')
            if user_resp == 'y':
                msg(f'Deleting existing remote repository: {repo_name}')
                book_repo.delete()
                msg(f'{repo_name} deleted')
            else:
                print(f'Unable to clone repository: {repo_name}')
                raise
    except:
        pass

    msg(f'Creating Remote Repository: {repo_name}')
    try:
        book_repo = gh['account'].create_repository(
            name=repo_name, private=True, homepage=repo['homepage'], has_projects=False)
        msg(f'{repo_name} created')
        return book_repo
    except GitHubError as error:
        raise error


def clone_private_repo(token, remote_repo):
    private_repo_auth = 'https://{token}:x-oauth-basic'.format(
        token=token)
    clone_url_arr = remote_repo.clone_url.split('//')
    clone_url_arr[0] = private_repo_auth
    private_repo_clone_url = '@'.join(clone_url_arr)

    try:
        cloned_repo = Repo.clone_from(
            private_repo_clone_url, remote_repo.name)
    except:
        user_resp = input(
            'Book exists LOCALLY, Delete LOCAL book and continue? (y/n) >> ')
        if user_resp == 'y':
            shutil.rmtree(remote_repo.name)
            cloned_repo = clone_private_repo(token, remote_repo)
        else:
            print(f'Unable to clone repository: {repo_name}')
            raise

    return cloned_repo


def add_syncing_files(repo):
    archive_syncfile_content = []
    canonical_json_content = []
    for bk in repo["books"]:
        slug = bk["slug"]
        colid = bk["collection_id"]
        archive_syncfile_content.append(slug+' '+colid+'\n')
        canonical_json_content.append(slug)

    repo_name = repo["title"]
    files = []

    def generate_canonical_json(repo_name):
        file_name = 'canonical.json'
        with open(file_name, 'w', encoding='utf8') as json_file:
            json.dump(canonical_json_content, json_file, ensure_ascii=False)
        files.append(file_name)

    def generate_archive_syncfile(repo_name):
        file_name = 'archive-syncfile'
        with open(file_name, 'a') as archive_syncfile:
            archive_syncfile.writelines(archive_syncfile_content)
        files.append(file_name)

    generate_canonical_json(repo_name)
    generate_archive_syncfile(repo_name)
    files = ', '.join(files)
    msg(f'Added {files} to {repo_name}')


def add_license(repo):
    repo_name = repo['title']
    repo_license = repo['license']
    license_path = '/Users/brenda/Projects/00_openstax/content-repos/book-repos/licenses/'
    with open(license_path + repo_license, 'r') as lf:
        repo_license = lf.read()

    with open('LICENSE', 'w') as rl:
        rl.write(repo_license)

    msg(f'Added LICENSE ({repo_license}) to {repo_name}')


def create_book_repo(repo, gh, test_run=True):
    repo_name = repo["title"]
    token = gh["token"]

    gh_session = login(token=token)
    gh['session'] = gh_session
    gh['account'] = gh_session.organization('openstax')
    repo['homepage'] = f'https://github.com/openstax/{repo_name}'

    if test_run:
        gh['account'] = gh_session
        repo['homepage'] = f'https://github.com/{gh["username"]}/{repo_name}'

    # create remote repository
    try:
        book_repo = create_remote_repo(repo, gh)
    except GitHubError as error:
        print(f"Unable to create Remote Repository: {repo_name}")
        print(f"Error: {error}")
        print(f"Error Details: {error.errors}")
        raise

    # clone down remote repository
    try:
        cloned_repo = clone_private_repo(token, book_repo)
        cloned_repo.git.checkout('-b', 'main')
    except:
        print(f"Unable to create Clone Repository: {repo_name}")
        raise

    os.chdir(repo_name)

    # generate and add files to repository
    add_syncing_files(repo)
    add_license(repo)

    # commit and push repository with changes to github
    msg(f'Pushing {repo_name} to github')
    cloned_repo.git.add('--all')
    cloned_repo.git.commit('-m', 'Inital Book Repo Commit')
    cloned_repo.git.push('--set-upstream', 'origin', 'main')

    return book_repo


def main():
    # sys.argv[1]   # file to books json
    # sys.argv[2]   # file to github creds json
    # sys.argv[3]  # where you want the files to go
    # sys.argv[4] # not a test run anymore

    # here = f'/Users/brenda/Projects/00_openstax/content-repos/book-repos/{gh}'
    # here = f'/Users/brenda/Projects/00_openstax/content-repos/book-repos/{gh}'

    with open(sys.argv[2], 'r') as f:
        github_creds = json.load(f)

    with open(sys.argv[1], 'r') as f:
        osbooks = json.load(f)

    for book in osbooks:
        repo_name = book["title"]
        try:
            print(f'\n>>>>> Starting Creating Book Repo: {repo_name}')
            local_repo_path = '/Users/brenda/Projects/00_openstax/content-repos/'
            os.chdir(local_repo_path)
            book_repo = create_book_repo(book, github_creds)
            print(f'>>>>> Book Repo URL: {book_repo.homepage}')
        except:
            continue


if __name__ == "__main__":
    main()
