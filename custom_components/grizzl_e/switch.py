from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    store = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if not store:
        return
    async_add_entities([GrizzleEChargeSwitch(store["coordinator"], store["device"])])


class GrizzleEChargeSwitch(CoordinatorEntity, SwitchEntity):
    """Allow or suspend charging (evseEnabled: 0 = charging allowed, 1 = stopped)."""

    _attr_has_entity_name = True
    _attr_name = "Charging"
    _attr_icon = "mdi:ev-station"

    def __init__(self, coordinator, device):
        super().__init__(coordinator)
        self._device = device
        self._attr_unique_id = f"{device.entry.entry_id}_charge_switch"

    @property
    def device_info(self) -> DeviceInfo:
        return self._device.device_info

    @property
    def is_on(self):
        if not self.coordinator.data or "evseEnabled" not in self.coordinator.data:
            return None
        return not self.coordinator.data["evseEnabled"]

    async def async_turn_on(self, **kwargs):
        await self._device.async_send_command(
            "pageEvent", {"evseEnabled": 0, "suspendLimits": 1}
        )

    async def async_turn_off(self, **kwargs):
        await self._device.async_send_command(
            "pageEvent", {"evseEnabled": 1, "suspendLimits": 0}
        )
