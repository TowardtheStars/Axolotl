

import logging
from typing import Callable, Dict, List, Optional, Type, TypeVar, Union
from axolotl.util import annotation

Event = TypeVar('Event')

# In Python 3.10, it should be specified as `TypeAlias`
EventListener = Union[Callable[[Event], None], Type[Callable[[], None]]]

logger = logging.getLogger('axolotl.eventbus')


class EventBus:

    def __init__(self, name:Optional[str]=None) -> None:
        self.__listeners:Dict[Type, List[Callable]] = {}
        self.__name = '{}'.format(name or id(self))
        self.__logger = logger.getChild(self.__name)

    @property
    def name(self):
        return 'EventBus ' + self.__name

    def __register(self, event_type:Type[Event], listener:Callable[[Event], None]):
        if event_type not in self.__listeners.keys():
            self.__listeners[event_type] = []
        self.__listeners[event_type].append(listener)

    @annotation
    def event_listener(self, *event_types:Type[Event]) -> Callable[[EventListener[Event]], EventListener[Event]]:
        '''Annotate a function or a class as an event listener
        If a function is annotated, the function is registered as is.
        If a class is annotated, the class will be instantiated and the instantiated object will be registered as an event listener

        @var event_types: A set of event types that this listener will listen
        '''
        return lambda listener:self.register(*event_types, listener=listener)
    
    def fire_event(self, event:object):
        self.__logger.debug('Fire event %(event)s on bus %(name)s', {'event':event, 'name':self.name})
        
        for path_node in event.__class__.mro():
            for listener in self.__listeners.get(path_node, []):
                try:
                    self.__logger.debug('Calling event listener %s', listener)
                    listener(event)
                except:
                    self.__logger.error('Event listener %s error.', listener, exc_info=True)
        self.__logger.debug('Event listener complete!')


    def register(self, *event_types:Type[Event], listener:EventListener[Event]) -> EventListener[Event]:
        if isinstance(listener, type):
            listener_instance = listener()
            setattr(listener,'INSTANCE', listener_instance)
            for event_type in event_types:
                self.__register(event_type, listener_instance)
        elif isinstance(listener, Callable):
            for event_type in event_types:
                self.__register(event_type, listener)
        
        return listener
    
    def mute_logger(self, v:bool):
        self.__logger.disabled = v

    