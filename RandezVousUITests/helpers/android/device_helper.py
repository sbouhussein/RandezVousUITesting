import os

from helpers.common.device_helper_base import DeviceHelperBase

# RV's Trusted Web Activity package, live on Google Play.
RV_ANDROID_PACKAGE = os.getenv("RV_ANDROID_PACKAGE", "com.randezvous.RandezVous")


class DeviceHelper(DeviceHelperBase):
    """Android counterpart to the iOS DeviceHelper, keyed by package name."""

    default_app_id = RV_ANDROID_PACKAGE
