import pandas as pd


class DatasetGmail:
    def __init__(self, messages):

        self.messages = messages

    def headers(self, filename=None):
        data = []
        for m in self.messages:
            res = {"snippet": m["snippet"]}
            for d in m["payload"]["headers"]:
                res[d["name"]] = d["value"]
            data.append(res)
        self.__dict_to_csv(data, filename=filename)

    #
    # END PUBLIC METHODS
    #

    @staticmethod
    def __dict_to_csv(data, filename=None):
        df = pd.DataFrame(data)
        if filename is not None:
            df.to_csv(filename)
