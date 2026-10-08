from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.const import UnitOfElectricCurrent
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not store:
        return
    async_add_entities([GrizzleECurrentLimit(store["coordinator"], store["device"])])


class GrizzleECurrentLimit(CoordinatorEntity, NumberEntity):
    """Maximum charging current (currentSet), bounded by minCurrent..curDesign."""

    _attr_has_entity_name = True
    _attr_name = "Current Limit"
    _attr_icon = "mdi:current-ac"
    _attr_device_class = NumberDeviceClass.CURRENT
    _attr_native_unit_of_measurement = UnitOfElectricCurrent.AMPERE
    _attr_native_step = 1
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"{device.entry.entry_id}_current_limit"

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def native_min_value(self) -> float:
        return float((self.coordinator.data or {}).get("minCurrent", 6))

    @property
    def native_max_value(self) -> float:
        return float((self.coordinator.data or {}).get("curDesign", 32))

    @property
    def native_value(self):
        data = self.coordinator.data or {}
        value = data.get("currentSet")
        return None if value is None else float(value)

    async def async_set_native_value(self, value: float) -> None:
        await self._device.async_send_command("pageEvent", {"currentSet": int(value)})
