
class BaseMessageBackend(object):
    """
    Abstract message backend base class.
    """
    def get_name(self, user):
        """Get name from user object."""
        raise NotImplementedError

    def filter_users(self, names):
        """Filter users with given names."""
        raise NotImplementedError
