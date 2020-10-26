from enum import Enum, unique


@unique
class Device(Enum):
    ANDROID = 'android'
    IOS = 'ios'
    WEB = 'web'
