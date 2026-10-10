import os

from helpers.common.device_helper_base import DeviceHelperBase

# Verified package name for RV's Trusted Web Activity, already live on Google Play --
# see rvsite/public/.well-known/assetlinks.json.
RV_ANDROID_PACKAGE = os.getenv("RV_ANDROID_PACKAGE", "com.randezvous.RandezVous")


class DeviceHelper(DeviceHelperBase):
    """Android counterpart to helpers.ios.device_helper.DeviceHelper -- shares
    DeviceHelperBase's install-state/foreground logic, keyed by an Android package name
    instead of an iOS bundle ID."""

    default_app_id = RV_ANDROID_PACKAGE
