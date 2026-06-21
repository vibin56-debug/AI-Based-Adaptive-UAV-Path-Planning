from emergency_manager import EmergencyManager

em = EmergencyManager()

print("Initial:", em.is_emergency())

em.trigger_emergency((2,4))

print("Emergency:", em.is_emergency())

print("Goal:", em.get_emergency_goal())

em.clear_emergency()

print("After Clear:", em.is_emergency())
