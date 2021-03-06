import dbus

BUS_PREFIX = 'org.openbmc'
OBJ_PREFIX = "/org/openbmc"
GPIO_DEV = '/sys/class/gpio'
BUS = "system"

ENUMS = {
	'org.openbmc.SensorIntegerThreshold.state' : 
		['NOT_SET','NORMAL','LOWER_CRITICAL','LOWER_WARNING','UPPER_WARNING','UPPER_CRITICAL'],
}

def getSystemName():
	#use filename as system name, strip off path and ext
	parts = __file__.replace('.pyc','').replace('.py','').split('/')
	return parts[len(parts)-1]


def getDBus():
	bus = None
	if (BUS == "session"):
		bus = dbus.SessionBus()
	else:
		bus = dbus.SystemBus()
	return bus


def getManagerInterface(bus,manager):
	bus_name = "org.openbmc.managers."+manager
	obj_name = "/org/openbmc/managers/"+manager
	obj = bus.get_object(bus_name,obj_name)
	return dbus.Interface(obj,bus_name)


class DbusProperties(dbus.service.Object):
	def __init__(self):
		dbus.service.Object.__init__(self)
		self.properties = {}

	@dbus.service.method(dbus.PROPERTIES_IFACE,
		in_signature='ss', out_signature='v')
	def Get(self, interface_name, property_name):
		d = self.GetAll(interface_name)
		try:
			v = d[property_name]
			return v
		except:
 			raise dbus.exceptions.DBusException(
				"org.freedesktop.UnknownPropery: "+property_name)

	@dbus.service.method(dbus.PROPERTIES_IFACE,
		in_signature='s', out_signature='a{sv}')
	def GetAll(self, interface_name):
		try:
			d = self.properties[interface_name]
			return d
 		except:
 			raise dbus.exceptions.DBusException(
				"org.freedesktop.UnknownInterface: "+interface_name)

	@dbus.service.method(dbus.PROPERTIES_IFACE,
		in_signature='ssv')
	def Set(self, interface_name, property_name, new_value):
		if (self.properties.has_key(interface_name) == False):
			self.properties[interface_name] = {}
		try:
			old_value = self.properties[interface_name][property_name] 
			if (old_value != new_value):
				self.properties[interface_name][property_name] = new_value
				self.PropertiesChanged(interface_name,{ property_name: new_value }, [])
				
		except:
        		self.properties[interface_name][property_name] = new_value
			self.PropertiesChanged(interface_name,{ property_name: new_value }, [])

	@dbus.service.method("org.openbmc.Object.Properties",
		in_signature='sa{sv}')
	def SetMultiple(self, interface_name, prop_dict):
		if (self.properties.has_key(interface_name) == False):
			self.properties[interface_name] = {}

		value_changed  = False
		for property_name in prop_dict:
			new_value = prop_dict[property_name]
			try:
				old_value = self.properties[interface_name][property_name] 
				if (old_value != new_value):
					self.properties[interface_name][property_name] = new_value
					value_changed = True
				
			except:
        			self.properties[interface_name][property_name] = new_value
				value_changed = True
		if (value_changed == True):
			self.PropertiesChanged(interface_name, prop_dict, [])
	

	@dbus.service.signal(dbus.PROPERTIES_IFACE,
		signature='sa{sv}as')
	def PropertiesChanged(self, interface_name, changed_properties,
		invalidated_properties):
		pass

	@dbus.service.signal("org.openbmc.Object.ObjectMapper",
		signature='ss')
	def ObjectAdded(self,object_path,interface_name):
		pass



