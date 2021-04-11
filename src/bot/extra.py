import base64


class Extra:

    @staticmethod
    def base64encode(text: str):
        text = base64.b64encode(text.encode("ascii")).decode("ascii")
        return text
