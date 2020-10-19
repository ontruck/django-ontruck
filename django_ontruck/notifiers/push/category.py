from enum import Enum, unique


@unique
class Category(Enum):
    OFFER = 'offer'
    UPDATE_STATUS = 'update_status'
    PROFILE_UPDATED = 'profile_updated'
    JOURNEY_REASSIGNED = 'reassigned'
    POSSIBLE_STANDSTILL = 'standstill'
    ASSIGNED_OFFER = 'assigned_offer'
    CONVERSATION = 'conversation'
    ANNOUNCEMENT = 'announcement'

    @classmethod
    def phone_sound_for(cls, category):
        if category in [cls.UPDATE_STATUS, cls.ANNOUNCEMENT]:
            return 'sonidoChat.m4a'
        else:
            return 'sonidolargo.wav'
