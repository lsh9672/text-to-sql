class DIContainer:
    _instances = {}
    
    @classmethod
    def register(cls, interface, implementation):
        cls._instances[interface] = implementation
    
    @classmethod
    def get(cls, interface):
        return cls._instances.get(interface)
