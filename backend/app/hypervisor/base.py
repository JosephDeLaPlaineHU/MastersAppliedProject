
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class HypervisorClient(ABC):
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Check if hypervisor is reachable"""
        pass

    @abstractmethod
    def list_vms(self) -> List[Dict[str, Any]]:
        """List all VMs"""
        pass

    @abstractmethod
    def list_templates(self) -> List[Dict[str, Any]]:
        """List all available templates"""
        pass

    @abstractmethod
    def get_vm_details(self, vm_id: str) -> Dict[str, Any]:
        """Get details of a specific VM"""
        pass

    @abstractmethod
    def create_vm(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new VM"""
        pass

    @abstractmethod
    def start_vm(self, vm_id: str) -> bool:
        """Start a VM"""
        pass

    @abstractmethod
    def stop_vm(self, vm_id: str) -> bool:
        """Stop a VM (Hard Stop)"""
        pass

    @abstractmethod
    def shutdown_vm(self, vm_id: str) -> bool:
        """Shutdown a VM (Graceful)"""
        pass

    @abstractmethod
    def get_analytics(self) -> Dict[str, Any]:
        """Get system-wide analytics (e.g. total CPU/RAM usage of the cluster)"""
        pass

    @abstractmethod
    def get_vm_stats(self, vm_id: str) -> Dict[str, Any]:
        """Get real-time statistics for a specific VM (CPU, RAM, Uptime, etc)"""
        pass

    @abstractmethod
    def get_console_ticket(self, vm_id: str) -> Dict[str, Any]:
        """Generate a VNC ticket for NoVNC access"""
        pass

    @abstractmethod
    def list_isos(self) -> List[Dict[str, Any]]:
        """List available ISO images in storage"""
        pass

    @abstractmethod
    def create_vm_from_iso(self, name: str, iso_file: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a VM from an ISO image"""
        pass

    @abstractmethod
    def convert_to_template(self, vm_id: str) -> bool:
        """Convert a VM to a template"""
        pass

    @abstractmethod
    def download_iso(self, url: str, file_name: str, storage: str = "local") -> str:
        """Trigger an ISO download from a URL. Returns the Task UPID (Unique Process ID)"""
        pass

    @abstractmethod
    def get_task_status(self, upid: str, node: str) -> Dict[str, Any]:
        """Get the status of a background task"""
        pass

    @abstractmethod
    def get_task_log(self, upid: str, node: str) -> List[str]:
        """Get the log of a background task"""
        pass

    @abstractmethod
    def cancel_task(self, upid: str, node: str) -> bool:
        """Cancel a background task"""
        pass
