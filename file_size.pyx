# Enum for size units
class SizeUnit:
    BYTES = 0
    KB = 1
    MB = 2
    GB = 3
    TB = 4
    PB = 5
    EB = 6
    ZB = 7
    YB = 8

    @staticmethod
    def __get_units__():
        """Gives the variable names of our instance we want to expose
        """
        self = SizeUnit
        return list(filter(lambda x: not x.startswith('_'), self.__dict__.keys()))

    @staticmethod
    def __get_unit__(unit: str):
        self = SizeUnit
        return self.__dict__[unit]


cpdef double convert_unit(double size_in_bytes, short unit):
    return size_in_bytes / (1024 ** unit)

cpdef get_largest_unit(double size_in_bytes):
    cdef double last_value = size_in_bytes
    cdef double current_value = 0
    cdef list units = SizeUnit.__get_units__()
    cdef str unit
    cdef str last_unit
    for unit in units:
        current_value = convert_unit(size_in_bytes, SizeUnit.__get_unit__(unit))
        if current_value < 32:
            return last_value, last_unit
        last_value = current_value
        last_unit = unit
    return last_value, unit
