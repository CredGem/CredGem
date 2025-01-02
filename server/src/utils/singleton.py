class SingletonMeta(type):
    """
    A metaclass for Singleton pattern.
    Ensures that only one instance of a class exists.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            # If no instance exists, create one and store it
            instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
