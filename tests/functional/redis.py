class MockPipe:
    def incr(self, key: str, inc: int):
        pass

    def expire(self, key: str, exp: int):
        pass

    async def execute(self):
        return [1]


class MockRedis:
    def __init__(self):
        self._mem = {}

    async def get(self, name):
        return self._mem.get(name)

    async def set(self, name, value):
        self._mem[name] = value

    async def setex(self, name, time, value):
        self._mem[name] = value

    async def sadd(self, name, value):
        set_name = self._mem.setdefault(name, set())
        set_name.add(value)

    async def smembers(self, name):
        return self._mem.get(name)

    async def expire(self, name, time):
        pass

    async def delete(self, name):
        self._mem.pop(name, None)

    async def flush(self):
        self._mem = {}
        return self._mem

    def pipeline(self):
        return MockPipe()


redis = MockRedis()
