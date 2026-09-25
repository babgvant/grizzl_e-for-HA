"""Device class for Grizzl-E EV Charger."""
import aiohttp
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN, MANUFACTURER, MODEL,
    REQUEST_TIMEOUT, CONNECT_TIMEOUT, SOCKET_TIMEOUT,
)

class GrizzleEDevice:
    """Grizzl-E device."""

    def __init__(self, coordinator: DataUpdateCoordinator, entry, session):
        """Initialize the device."""
        self.coordinator = coordinator
        self.entry = entry
        self.session = session

    async def async_send_command(self, endpoint: str, params: dict) -> None:
        """POST a form-encoded control command to the EVSE."""
        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT, connect=CONNECT_TIMEOUT, sock_read=SOCKET_TIMEOUT
        )
        async with self.session.post(
            f"http://{self.entry.data['host']}/{endpoint}",
            auth=aiohttp.BasicAuth(
                self.entry.data["username"], self.entry.data["password"]
            ),
            data=params,
            timeout=timeout,
        ) as resp:
            if resp.status != 200:
                raise HomeAssistantError(f"Grizzl-E command failed: HTTP {resp.status}")
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information.

        Prefer dynamic data from the EVSE payload when available so the
        device registry shows accurate model and firmware.
        """
        data = getattr(self.coordinator, "data", None) or {}
        # Prefer payload model when present, fallback to static default
        model = data.get("model") or MODEL
        # Use EVSE main firmware as device software version; trim whitespace
        sw_version = (data.get("verFWMain") or "").strip() or None
        # Use serial if available for nicer identification in registry
        serial = data.get("serialNum") or data.get("stationId") or None

        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer=MANUFACTURER,
            model=model,
            sw_version=sw_version,
            serial_number=serial,
            configuration_url=f"http://{self.entry.data['host']}",
        )
