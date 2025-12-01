from app.core.config import settings
from app.db import models
from .proxmox import ProxmoxClient
from .base import HypervisorClient

class HypervisorManager:
    @staticmethod
    def get_client(hypervisor: models.Hypervisor = None) -> HypervisorClient:
        
        if hypervisor:
            if hypervisor.type == models.HypervisorType.PROXMOX:
                return ProxmoxClient(
                    host=hypervisor.url,
                    user=hypervisor.auth_user,
                    password=hypervisor.auth_token, 
                    verify_ssl=hypervisor.verify_ssl
                )
        
        return ProxmoxClient(
            host=settings.PROXMOX_URL,
            user=settings.PROXMOX_USER,
            password=settings.PROXMOX_PASSWORD,
            verify_ssl=settings.PROXMOX_VERIFY_SSL
        )
