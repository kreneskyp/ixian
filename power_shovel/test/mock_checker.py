class MockChecker(Checker):
    def __init__(self, mock_save=True, mock_check=True, *args, **kwargs):
        self.mock_save = mock_save
        if mock_save:
            self.save = mock.Mock()
        if mock_check:
            self.check = mock.Mock(return_value=True)

        self.mocked_state = 1
        self.id = uuid.uuid4()

    def state(self):
        return {"mock": self.mocked_state}

    def filename(self):
        return "mock-%s" % str(self.id)

    def clone(self):
        instance = type(self)(self.mock_save)
        instance.mocked_state = self.mocked_state
        instance.id = self.id
        if self.mock_save:
            instance.save = self.save
        return instance


class FailingCheck(MockChecker):
    """A checker that always fails the check"""

    def __init__(self, *args, **kwargs):
        super(FailingCheck, self).__init__(*args, **kwargs)
        self.check = Mock(return_value=False)


class PassingCheck(MockChecker):
    """A checker that always passes the check"""

    pass
