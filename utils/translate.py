from django.utils.translation import gettext as _

def get_arabic_translated(name: str):
        """
        just apply translation function
        """
        return _(name)


def get_engilsh_translated(name: str):
        return _(name)