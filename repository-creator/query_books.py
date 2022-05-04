import json
import os
import re

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from slugify import slugify

import db_connector as dbc
from github_synchronizer import load_map

load_dotenv()

PG_HOST = os.environ.get("PG_HOST")
PG_PORT = int(os.environ.get("PG_PORT", 5432))
PG_USERNAME = os.environ.get("PG_USERNAME")
PG_PASSWORD = os.environ.get("PG_PASSWORD")
PG_DATABASE = os.environ.get("PG_DATABASE")
QUERY_SIZE = int(os.environ.get("QUERY_SIZE", 1000))

CONNECTION = dbc.connect(host=PG_HOST, port=PG_PORT, username=PG_USERNAME, password=PG_PASSWORD,
                         database=PG_DATABASE)


def query_pg_with_pagination(connection=None, count_query='', query=''):
    """
    This method is used to a Postgres database using pagination

    :param connection: The connection to the DB
    :param count_query: The query to find the count
    :param query: The actual query
    """
    data = []
    count = 0
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(count_query)
            count = cursor.fetchone()[0]
            print(f"Count : {count}")
            i = 0
            limit = QUERY_SIZE
            while i < count:
                print(query.format(limit=limit, i=i))
                cursor.execute(query.format(limit=limit, i=i))
                i += limit
                data.extend(cursor.fetchall())
            cursor.close()
        except Exception as error:
            raise dbc.DBConnectionException(error)
    return {'count': count, 'data': data}


def query_independent_non_openstax_books(connection=None):
    """Queries the vendors books that are not derived from any collection"""
    results = query_pg_with_pagination(connection,
                                       count_query="SELECT count(DISTINCT(m.moduleid)) from modules m where m.portal_type='Collection' and 'OpenStaxCollege' != any(authors) and m.parent is null",
                                       query=" SELECT DISTINCT ON  (m.moduleid) moduleid, m.name, m.authors from modules m where m.portal_type='Collection' and 'OpenStaxCollege' != any(authors) and m.parent is null ORDER BY moduleid ASC LIMIT {limit} OFFSET {i}")
    return {'count': results['count'], 'data': [
        {"collection_id": b[0], "slug": slugify(b[1]), "name": b[1], "repository_name": f"nonosb-{slugify(b[1])}",
         "authors": ", ".join(b[2])} for b in results["data"]]}


def query_openstax_derived_books(connection=None, map=None):
    """Queries the openstax devired books"""
    results = query_pg_with_pagination(connection,
                                       count_query="with osb as (select m.module_ident, m.name, m.moduleid from modules m where m.portal_type='Collection' and 'OpenStaxCollege' = any(authors))  select count(distinct(t.moduleid)) from modules t inner join osb on osb.module_ident=t.parent  where t.portal_type='Collection' and 'OpenStaxCollege'!= any(authors) and t.parent is not null",
                                       query=" with osb as (select m.module_ident, m.name, m.moduleid from modules m where m.portal_type='Collection' and 'OpenStaxCollege' = any(authors))  select DISTINCT ON (t.moduleid) t.moduleid, t.name, t.authors, osb.moduleid, osb.name from modules t inner join osb on osb.module_ident=t.parent  where t.portal_type='Collection' and 'OpenStaxCollege'!= any(authors) and t.parent is not null ORDER BY t.moduleid ASC LIMIT {limit} OFFSET {i}")
    return {'count': results['count'],
            'data': [{"collection_id": b[0], "slug": slugify(b[1]), "name": b[1], "authors": ", ".join(b[2]),
                      "repository_name": f"osbdev-{slugify(b[1])}", "migrate": b[3] in map,
                      "parent_repository_name": map[b[3]]['repository_name'] if b[3] in map else None,
                      "parent_collection_id": b[3], "parent_slug": map[b[3]]['slug'] if b[3] in map else slugify(b[4]),
                      "parent_name": b[4], "parent_branch": map[b[3]]['branch'] if b[3] in map else 'main'} for b in
                     results['data']]}


def query_non_openstax_derived_books(connection):
    """Queries vendors derived books"""
    results = query_pg_with_pagination(connection,
                                       count_query="with nonosb as (select m.module_ident, m.name, m.moduleid from modules m where m.portal_type='Collection' and 'OpenStaxCollege' != any(authors))  select count(distinct(t.moduleid)) from modules t inner join nonosb on nonosb.module_ident=t.parent  where t.portal_type='Collection' and 'OpenStaxCollege'!= any(authors) and t.parent is not null",
                                       query=" with nonosb as (select m.module_ident, m.name, m.moduleid from modules m where m.portal_type='Collection' and 'OpenStaxCollege' != any(authors))  select DISTINCT ON (t.moduleid) t.moduleid, t.name, t.authors, nonosb.moduleid, nonosb.name from modules t inner join nonosb on nonosb.module_ident=t.parent  where t.portal_type='Collection' and 'OpenStaxCollege'!= any(authors) and t.parent is not null ORDER BY t.moduleid ASC LIMIT {limit} OFFSET {i}")
    return {'count': results['count'], 'data': [
        {"collection_id": b[0], "slug": slugify(b[1]), "name": b[1], "authors": ", ".join(b[2]),
         "repository_name": f"nonosb-{slugify(b[1])}",
         "parent_collection_id": b[3], "parent_slug": slugify(b[4]), "parent_name": b[4],
         "parent_repository_name": f"nonosb-{slugify(b[4])}"} for b in results['data']]}


def query_all_books(connection=None):
    """Queries all books"""
    return query_pg_with_pagination(connection,
                                    count_query=" SELECT count(m.module_ident) from modules m where m.portal_type = 'Collection' and 'OpenStaxCollege' = any(authors)",
                                    query=" SELECT m.module_ident, m.parent, m.moduleid, m.uuid, m.name, m.minor_version, m.major_version from modules m where m.portal_type = 'Collection' and 'OpenStaxCollege' = any(authors) ORDER BY created ASC LIMIT {limit} OFFSET {i} ")


def query_parent_book_details(connection=None, parent_id=None):
    """Queries the details of a parent book"""
    parent = None
    if connection and parent_id:
        try:
            cursor = connection.cursor()
            cursor.execute(
                f" SELECT m.module_ident, m.moduleid, m.uuid, m.name, m.minor_version, m.major_version from modules m where m.portal_type = 'Collection' and 'OpenStaxCollege' = any(authors) and m.module_ident = {parent_id} ")
            parent = cursor.fetchone()
            cursor.close()
        except Exception as e:
            print(e)
            raise dbc.DBConnectionException(e)
        finally:
            return parent


def build_book_table(books=None, columns=None, fields=None, formatters=None):
    """
    Build the HTML table of a book
    :param books: List of books
    :param columns: The columns of the table
    :param fields: The book variable to use for a row in the table
    :param formatters: Expression to format a row.
    """
    if len(books) < 1 and not (columns and fields):
        return ""
    s = f"<table><tr><th>{'</th><th>'.join(columns)}</th></tr>"
    for b in books:
        s += "<tr>"
        for f in fields:
            if formatters is not None and f in formatters:
                formatted_content = formatters[f]
                res = re.findall(r'\{.*?\}', formatted_content)
                for r in res:
                    formatted_content = formatted_content.replace(r, b[r.replace("{", "").replace("}", "")] if b[
                                                                                                                   r.replace(
                                                                                                                       "{",
                                                                                                                       "").replace(
                                                                                                                       "}",
                                                                                                                       "")] is not None else "")
                s += f"<th>{formatted_content}</th>"
            else:
                s += f"<th>{b[f]}</th>"
        s += "</tr>"
    return s + "</table>"


def update_html(tag=None, content=None, title=''):
    """
    Updates the content of the  .data/index.html using the id attribute and the content passed in parameters
    :param tag: The ID attribute to search for
    :param content: New content to replace when element found.
    :param title: Title of the element
    """
    if tag and content:
        content = f'<div class="{tag}" id="{tag}"> <h2>{title}</h2>' + content + '</div>'
        with open("data/index.html", mode="r") as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        soup.select_one('.' + tag).string = ""
        with open("data/index.html", mode="w") as f:
            f.write(str(soup).replace(f'<div class="{tag}" id="{tag}"></div>', content))


def generate_vendors_books():
    """This method queries vendors books, updates the .data/index.html and generates the ./data/json/non_openstax_users_books.json"""
    vendors_books = query_independent_non_openstax_books(CONNECTION)
    update_html(tag='independent-books', content=build_book_table(
        books=vendors_books['data'], columns=['Slug', 'Collection  ID', 'Name'],
        fields=['slug', 'collection_id', 'name']),
                title=f'Non Openstax Users Books: {vendors_books["count"]}')

    with open('data/json/non_openstax_users_books.json', 'w') as outfile:
        json.dump(vendors_books['data'], outfile)


def generate_openstax_derived_books():
    """
    This method loads a map of collections and Github repositories, queries Openstax derived books,
    updates the .data/index.html and generates the ./data/json/openstax_derieved_books.json"""
    osbooks_map = load_map()
    openstax_derived_books = query_openstax_derived_books(CONNECTION, osbooks_map)
    update_html(tag='openstax-derived-books', content=build_book_table(
        books=openstax_derived_books['data'],
        columns=['Slug', 'Coll. ID', 'Name', 'Parent Coll ID', 'Parent Repository', ' Parent Branch'],
        fields=['slug', 'collection_id', 'name', 'parent_collection_id', 'parent_repository_name', 'parent_branch'],
        formatters={
            'parent_repository_name': '<a href="https://github.com/openstax/{parent_repository_name}" target="_blank">{parent_repository_name}</a>',
            'parent_branch': '<a href="https://github.com/openstax/{parent_repository_name}/tree/{parent_branch}" target="_blank">{parent_branch}</a>'}),
                title=f'Openstax Derived Books: {openstax_derived_books["count"]}')

    with open('data/json/openstax_derived_books.json', 'w') as outfile:
        json.dump(openstax_derived_books['data'], outfile)


def generate_vendors_derived_books():
    """This method queries vendors derived books, updates the .data/index.html and generates the ./data/json/non_openstax_users_derived_books.json"""
    vendors_derived_books = query_non_openstax_derived_books(CONNECTION)
    update_html(tag='vendor-derived-books', content=build_book_table(
        books=vendors_derived_books['data'],
        columns=['Slug', 'Coll. ID', 'Name', 'Parent Coll ID', 'Parent name'],
        fields=['slug', 'collection_id', 'name', 'parent_collection_id', 'parent_name', ]),
                title=f'Non Openstax Users Derived Books: {vendors_derived_books["count"]}')

    with open('data/json/non_openstax_users_derived_books.json', 'w') as outfile:
        json.dump(vendors_derived_books['data'], outfile)


if __name__ == '__main__':
    print(dbc.check_pg_version(CONNECTION))

    generate_vendors_books()
    generate_openstax_derived_books()
    generate_vendors_derived_books()
