class DataInconsistencyError(BaseException):
    pass

class RawDataProcessor:
    @staticmethod
    def banks_to_headers(data):
        headers = [[''], ['Date']]
        items = sorted(data.items())
        for k, v in items:
            sub = sorted(v.items())
            for l, w in sub:
                headers[0].append(k)
                headers[1].append(l)
        return headers

    @staticmethod
    def banks_to_rows(data):
        rows = ['']
        items = sorted(data.items())
        expected_values = 0
        for k, v in items:
            sub = sorted(v.items())
            for l, w in sub:
                if 0 < len(w): rows.append(w)
                expected_values += 1

        if len(rows) != expected_values + 1:
            raise DataInconsistencyError

        return rows
