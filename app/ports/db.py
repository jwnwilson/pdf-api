class DbAdapter:
    def create(self, record_data):
        raise NotImplementedError

    def list(self):
        raise NotImplementedError

    def read(self, record_id):
        raise NotImplementedError

    def update(self, record_id, record_data):
        raise NotImplementedError

    def delete(self, record_id):
        raise NotImplementedError
