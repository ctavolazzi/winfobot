class Bot:
    _REQUIRED_CONFIG_KEYS = ['id', 'inventory', 'logger', 'lock', 'port', 'state', 'memory', 'brain']

    _DEFAULT_CONFIG = {
        'id': lambda: str(uuid.uuid4()),
        'inventory': lambda: {'items': []},
        'lock': lambda: threading.Lock(),
        '_created_at': lambda: datetime.datetime.now(),
        '_updated_at': lambda: datetime.datetime.now(),
        '_parent': lambda: None,
        '_logger_level': 'DEBUG',
        '_restricted_config_keys': lambda: {'id', 'port', 'state', 'memory', 'logger', 'lock'},
        'is_thinking': False,
        'is_updating': False,
        'is_active': True,
        'has_controller': False,
    }

    def __init__(self, config=None):
        self._initialize_default_config()
        self._initialize_default_behaviors()
        self.setup_logger()

        # Set up the bot's self referential config
        self.name = self.generate_name()
        self.type = self.__class__.__name__
        self._base_type = self.__class__.__name__

        # Bind the bot to its components
        self.port = Port({'owner': self}) if not hasattr(self, 'port') else self.port
        self.state = State({'owner': self}) if not hasattr(self, 'state') else self.state
        self.memory = Memory({'owner': self}) if not hasattr(self, 'memory') else self.memory
        self.brain = ThreadedBrain({'owner': self}) if not hasattr(self, 'brain') else self.brain

        # Set up the handlers
        self.message_handler = MessageHandler()
        self.connection_handler = ConnectionHandler()
        self.formatter = JSONFormatter(self)
        self.q = EventQueue(self)

        # Set up default behaviors
        self._behaviors = BehaviorFactory.create_behaviors()

        if config:
            utils.update_config(self, config)

        self.logger.info(f'Initialized {self.__class__.__name__} {self.id} with config {config}')

    # Config methods
    def _initialize_default_config(self):
        utils.run_default_config(self, self._DEFAULT_CONFIG)
        utils.verify_config(self, self._REQUIRED_CONFIG_KEYS)

    def _initialize_default_behaviors(self):
        self._behaviors = BehaviorFactory.create_behaviors()

    def setup_logger(self):
        logger_instance = utils.SingletonLogger(self.__class__.__name__)  # Getting the logger instance
        logger_instance.set_level(self._logger_level)  # Setting the log level
        self.logger = logger_instance.get_logger()  # Getting the logger object

    async def handle_event(self, event):
        if isinstance(event, MessageEvent):
            self.logger.info(f"Bot {self.id} received data from {event.source.id}: {event.message}")
            await self.message_handler.handle_message(event.message, self)
        elif isinstance(event, CommandEvent):
            try:
                if hasattr(self, event.command):
                    getattr(self, event.command)(*event.args)
                    self.logger.info(f"Executed command: {event.command}")
                else:
                    self.logger.error(f"Unknown command: {event.command}")
            except TypeError as e:
                self.logger.error(f"Error executing command {event.command}: {str(e)}")

    def execute(self, command, *args):
        try:
            if hasattr(self, command):
                getattr(self, command)(*args)
                self.logger.info(f"Executed command: {command}")
            else:
                self.logger.error(f"Unknown command: {command}")
        except TypeError as e:
            self.logger.error(f"Error executing command {command}: {str(e)}")

    def add_event(self, event):
        self.q.add_event(event)

    async def process_events(self):
        while self.is_active:  # assuming `is_active` is a flag indicating if the bot is running
            await self.q.process_events(self)