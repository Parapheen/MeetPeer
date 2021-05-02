class AirtableRequestError(Exception):
    """
    Same for airtable
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return "Произошла ошибка во время выполнения запроса на Airtable --> {}".format(
            self.message
        )
