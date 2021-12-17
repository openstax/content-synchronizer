class OSBook:
    def __init__(self, book_repo: str, archive_server: str):
        self.book_repo = book_repo
        self.archive_server = archive_server

    def __eq__(self, o: object) -> bool:
        return (isinstance(o, OSBook)
                and o.book_repo == self.book_repo
                and o.archive_server == self.archive_server)

    def __hash__(self) -> int:
        return hash((self.book_repo, self.archive_server))

    def __str__(self) -> str:
        return f"{self.book_repo} {self.archive_server}"

    def __repr__(self) -> str:
        return self.__str__()

    @staticmethod
    def from_pipeline_resource(resource: dict) -> "OSBook":
        source = resource["source"]
        return OSBook(source["book_repo"], source["archive_server"])

    @staticmethod
    def from_osbook_collection(book: dict) -> "OSBook":
        return OSBook(book["book-repo"], book["archive-server"])

    def dict(self):
        return {
            "book-repo": self.book_repo,
            "archive-server": self.archive_server
        }
