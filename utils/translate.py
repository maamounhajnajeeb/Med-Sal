from django.utils.translation import gettext as _

def get_translated(name: str):
        """
        just apply translation function
        """
        return _(name)
