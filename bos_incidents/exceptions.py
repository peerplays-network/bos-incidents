class IncidentStorageException(Exception):
    pass


class IncidentStorageLostException(IncidentStorageException):
    pass


class DuplicateIncidentException(IncidentStorageException):
    pass


class InvalidIncidentFormatException(IncidentStorageException):
    pass


class IncidentNotFoundException(IncidentStorageException):
    pass


class InvalidQueryException(IncidentStorageException):
    pass


class EventNotFoundException(IncidentStorageException):
    pass
