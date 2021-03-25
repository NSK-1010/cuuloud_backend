class ResourceAlreadyExistsError(Exception):
    pass


class NotAuthenticatedError(Exception):
    pass


class ResourceDoesNotExistError(Exception):
    pass


class NotMethodAllowedError(Exception):
    pass


class BadRequestError(Exception):
    pass


errors = {
    'ResourceAlreadyExistsError': {
        'message': "このリソースは既に存在しています。",
        'status': 409,
    },
    'NotAuthenticatedError': {
        'message': "認証されていないためこの操作は出来ません。",
        'status': 403,
    },
    'ResourceDoesNotExistError': {
        'message': "指定されたリソースは存在しません。",
        'status': 404,
    },
    'NotMethodAllowedError': {
        'message': "指定されたリソースは存在しません。",
        'status': 405,
    },
    'BadRequestError': {
        'message': "不正な操作です。",
        'status': 400,
    }
}
