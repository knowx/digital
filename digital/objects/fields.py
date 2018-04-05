from oslo_versionedobjects import fields
        

class DigitalServiceBinary(fields.Enum):
    ALL = (
        digital_conductor
    ) = (
        'digital-conductor',
    )

    def __init__(self):
        super(DigitalServiceBinary, self).__init__(
            valid_values=DigitalServiceBinary.ALL)
        
        
class DigitalServiceState(fields.Enum):
    ALL = (
        up, down
    ) = (
        'up', 'down',
    )

    def __init__(self):
        super(DigitalServiceState, self).__init__(
            valid_values=DigitalServiceState.ALL)
        

class ListOfDictsField(fields.AutoTypedField):
    AUTO_TYPE = fields.List(fields.Dict(fields.FieldType()))
    

class DigitalServiceBinaryField(fields.BaseEnumField):
    AUTO_TYPE = DigitalServiceBinary()
    
    
class DigitalServiceField(fields.BaseEnumField):
    AUTO_TYPE = DigitalServiceState()

