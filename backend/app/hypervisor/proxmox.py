from typing import Dict, Any, List
from proxmoxer import ProxmoxAPI
from .base import HypervisorClient
import requests

class ProxmoxClient(HypervisorClient):
    def __init__(self, host: str, user: str, password: str, verify_ssl: bool = False):
        
        if "://" in host:
            self.host = host.split("://")[1]
        else:
            self.host = host
            
        
        try:
            try:
                with open("c:/Users/badda/Desktop/MastersProject/backend/debug_trace.log", "a") as f:
                    f.write(f"PROXMOX: Connecting to {self.host} with user {user}\n")
            except:
                pass
            print(f"Connecting to Proxmox at {self.host} with user {user}")
            self.proxmox = ProxmoxAPI(
                self.host, 
                user=user, 
                password=password, 
                verify_ssl=verify_ssl
            )
        except Exception as e:
            print(f"Failed to connect to Proxmox: {e}")
            import traceback
            traceback.print_exc()
            self.proxmox = None

    def get_status(self) -> Dict[str, Any]:
        if not self.proxmox:
            return {"status": "error", "details": "Not connected"}
        try:
            version = self.proxmox.version.get()
            return {"status": "online", "version": version}
        except Exception as e:
            return {"status": "error", "details": str(e)}

    def list_vms(self) -> List[Dict[str, Any]]:
        if not self.proxmox:
            return []
        vms = []
        for node in self.proxmox.nodes.get():
            node_vms = self.proxmox.nodes(node['node']).qemu.get()
            for vm in node_vms:
                if vm.get('template') != 1:
                    vm['node'] = node['node']
                    vms.append(vm)
        return vms

    def list_templates(self) -> List[Dict[str, Any]]:
        if not self.proxmox:
            return []
        templates = []
        for node in self.proxmox.nodes.get():
            node_vms = self.proxmox.nodes(node['node']).qemu.get()
            for vm in node_vms:
                if vm.get('template') == 1:
                    vm['node'] = node['node']
                    templates.append(vm)
        return templates

    def get_vm_details(self, vm_id: str) -> Dict[str, Any]:
        if not self.proxmox:
            return {}
        
        for node in self.proxmox.nodes.get():
            try:
                vm = self.proxmox.nodes(node['node']).qemu(vm_id).status.current.get()
                config = self.proxmox.nodes(node['node']).qemu(vm_id).config.get()
                ip_address = None
                try:
                    interfaces = self.proxmox.nodes(node['node']).qemu(vm_id).agent.network_get_interfaces.get()
                    for iface in interfaces.get('result', []):
                        if iface['name'] != 'lo':
                            for ip_info in iface.get('ip-addresses', []):
                                if ip_info['ip-address-type'] == 'ipv4':
                                    ip_address = ip_info['ip-address']
                                    break
                        if ip_address:
                            break
                except:
                    pass 
                
                return {"config": config, "status": vm, "node": node['node'], "ip": ip_address}
            except:
                continue
        return {}

    def create_vm(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        if not self.proxmox:
            raise Exception("Not connected to Proxmox")
        
        template_id = config.get("template_id")
        if not template_id:
            raise Exception("Template ID is required")

        template_node = None
        for node in self.proxmox.nodes.get():
            try:
                self.proxmox.nodes(node['node']).qemu(template_id).config.get()
                template_node = node['node']
                break
            except:
                continue
        
        if not template_node:
            raise Exception(f"Template {template_id} not found")

        new_vmid = self.proxmox.cluster.nextid.get()

        clone_params = {
            "newid": new_vmid,
            "name": name,
            "full": 1 
        }
        
        try:
            self.proxmox.nodes(template_node).qemu(template_id).clone.post(**clone_params)
        except Exception as e:
            raise Exception(f"Failed to clone VM: {e}")

        update_params = {}
        if "cpu" in config:
            update_params["cores"] = config["cpu"]
        if "memory" in config:
            update_params["memory"] = config["memory"]
            
        if update_params:
            try:
                self.proxmox.nodes(template_node).qemu(new_vmid).config.post(**update_params)
            except Exception as e:
                print(f"Warning: Failed to update VM config: {e}")

        return {"vmid": new_vmid, "node": template_node}

    def start_vm(self, vm_id: str) -> bool:
        details = self.get_vm_details(vm_id)
        if not details:
            return False
        node = details['node']
        try:
            self.proxmox.nodes(node).qemu(vm_id).status.start.post()
            return True
        except:
            return False

    def stop_vm(self, vm_id: str) -> bool:
        details = self.get_vm_details(vm_id)
        if not details:
            return False
        node = details['node']
        try:
            self.proxmox.nodes(node).qemu(vm_id).status.stop.post()
            return True
        except:
            return False

    def shutdown_vm(self, vm_id: str) -> bool:
        details = self.get_vm_details(vm_id)
        if not details:
            return False
        node = details['node']
        try:
            self.proxmox.nodes(node).qemu(vm_id).status.shutdown.post()
            return True
        except:
            return False

    def get_analytics(self) -> Dict[str, Any]:
        if not self.proxmox:
            return {}
        
        total_cpu = 0
        total_mem = 0
        used_mem = 0
        
        nodes_stats = []
        for node in self.proxmox.nodes.get():
            status = self.proxmox.nodes(node['node']).status.get()
            nodes_stats.append(status)
            
        return {"nodes": nodes_stats}

    def get_vm_stats(self, vm_id: str) -> Dict[str, Any]:
        """Get real-time statistics for a specific VM."""
        details = self.get_vm_details(vm_id)
        if not details:
            return {"status": "error", "details": "VM not found"}
            
        vm_status = details.get("status", {})
        
        stats = {
            "status": vm_status.get("status", "unknown"),
            "uptime_seconds": vm_status.get("uptime", 0),
            "cpu_usage_percent": vm_status.get("cpu", 0) * 100, 
            "memory_used_bytes": vm_status.get("mem", 0),
            "memory_total_bytes": vm_status.get("maxmem", 0),
            "network_in_bytes": vm_status.get("netin", 0),
            "network_out_bytes": vm_status.get("netout", 0),
            "disk_read_bytes": vm_status.get("diskread", 0),
            "disk_write_bytes": vm_status.get("diskwrite", 0)
        }
        
        return stats

    def get_console_ticket(self, vm_id: str) -> Dict[str, Any]:
        """Generate a VNC ticket for NoVNC access."""
        details = self.get_vm_details(vm_id)
        if not details:
            raise Exception("VM not found")
            
        node = details['node']
        
        try:
            res = self.proxmox.nodes(node).qemu(vm_id).vncproxy.post(websocket=1)
            ticket = res.get("ticket")
            port = res.get("port")
            cert = res.get("cert")
            
            if not ticket:
                raise Exception("Failed to get VNC ticket")
                
            return {
                "ticket": ticket,
                "port": port,
                "cert": cert,
                "node": node,
                "host": self.host 
            }
        except Exception as e:
            raise Exception(f"Failed to generate console ticket: {e}")

    def list_isos(self) -> List[Dict[str, Any]]:
        if not self.proxmox:
            return []
        isos = []
        for node in self.proxmox.nodes.get():
            try:
                storages = self.proxmox.nodes(node['node']).storage.get()
                for storage in storages:
                    try:
                        contents = self.proxmox.nodes(node['node']).storage(storage['storage']).content.get(content='iso')
                        for item in contents:
                            item['node'] = node['node']
                            item['storage'] = storage['storage']
                            isos.append(item)
                    except:
                        continue
            except:
                continue
        return isos

    def create_vm_from_iso(self, name: str, iso_file: str, config: Dict[str, Any]) -> Dict[str, Any]:
        if not self.proxmox:
            raise Exception("Not connected to Proxmox")

        storage_name = iso_file.split(":")[0]
        target_node = None
        
        for node in self.proxmox.nodes.get():
            try:
                self.proxmox.nodes(node['node']).storage(storage_name).status.get()
                target_node = node['node']
                break
            except:
                continue
        
        if not target_node:
            try:
                target_node = self.proxmox.nodes.get()[0]['node']
            except:
                raise Exception("No nodes found")

        new_vmid = self.proxmox.cluster.nextid.get()

        params = {
            "vmid": new_vmid,
            "name": name,
            "memory": config.get("memory", 2048),
            "sockets": 1,
            "cores": config.get("cpu", 2),
            "net0": "virtio,bridge=vmbr0",
            "scsihw": "virtio-scsi-pci",
            "cdrom": iso_file, 
            "boot": "order=scsi0;ide2;net0", 
            "bootdisk": "scsi0",
            "ostype": "l26" 
        }
        
        disk_size = config.get("disk_size", "32")
        if isinstance(disk_size, str) and disk_size.upper().endswith("G"):
            disk_size = disk_size[:-1]
            
        target_storage = "local-lvm"
        try:
            self.proxmox.nodes(target_node).storage("local-lvm").status.get()
        except:
            target_storage = "local" 
            
        params["scsi0"] = f"{target_storage}:{disk_size}"

        try:
            self.proxmox.nodes(target_node).qemu.post(**params)
        except Exception as e:
            raise Exception(f"Failed to create VM: {e}")

        return {"vmid": new_vmid, "node": target_node}

    def convert_to_template(self, vm_id: str) -> bool:
        details = self.get_vm_details(vm_id)
        if not details:
            return False
        node = details['node']
        
        try:
            self.stop_vm(vm_id)
            import time
            for _ in range(10):
                status = self.get_vm_stats(vm_id)
                if status.get("status") == "stopped":
                    break
                time.sleep(1)
        except:
            pass
            
        try:
            self.proxmox.nodes(node).qemu(vm_id).template.post()
            return True
        except Exception as e:
            print(f"Failed to convert to template: {e}")
            raise e

    def download_iso(self, url: str, file_name: str, storage: str = "local") -> str:
        if not self.proxmox:
            raise Exception("Not connected to Proxmox")
            
        target_node = None
        for node in self.proxmox.nodes.get():
            try:
                self.proxmox.nodes(node['node']).storage(storage).status.get()
                target_node = node['node']
                break
            except:
                continue
        
        if not target_node:
            raise Exception(f"Storage '{storage}' not found on any node")

        try:
            upid = self.proxmox.nodes(target_node).storage(storage)('download-url').post(
                content="iso",
                filename=file_name,
                url=url
            )
            return str(upid)
        except Exception as e:
            raise Exception(f"Failed to start download: {e}")

    def get_task_status(self, upid: str, node: str) -> Dict[str, Any]:
        if not self.proxmox:
            return {}
        try:
            return self.proxmox.nodes(node).tasks(upid).status.get()
        except:
            return {"status": "unknown"}

    def get_task_log(self, upid: str, node: str) -> List[str]:
        if not self.proxmox:
            return []
        try:
            logs = self.proxmox.nodes(node).tasks(upid).log.get()
            return [l.get('t', '') for l in logs]
        except:
            return []

    def cancel_task(self, upid: str, node: str) -> bool:
        if not self.proxmox:
            return False
        try:
            self.proxmox.nodes(node).tasks(upid).delete()
            return True
        except:
            return False
