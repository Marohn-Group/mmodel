from pydoc import Helper


class ModelHelper(Helper):

    """Inherite helper function to modify"""

    def help(self, request):
        """Add mmodel specific string to help function"""
        self.output.write(request.doc_long)
        super().help(request)


helper = ModelHelper()
