# File: modules/system_status.py

import psutil
import platform
from datetime import datetime
import subprocess
import os
from modules.logger import logger, LogType

class SystemInfo:
    def __init__(self):
        self.start_time = datetime.now()
    
    def get_system_stats(self):
        """Get current system statistics"""
        return {
            'cpu_temp': self.get_cpu_temperature(),
            'cpu_usage': psutil.cpu_percent(),
            'memory': {
                'total': psutil.virtual_memory().total,
                'used': psutil.virtual_memory().used,
                'free': psutil.virtual_memory().free,
                'percent': psutil.virtual_memory().percent
            },
            'disk': {
                'total': psutil.disk_usage('/').total,
                'used': psutil.disk_usage('/').used,
                'free': psutil.disk_usage('/').free,
                'percent': psutil.disk_usage('/').percent
            },
            'uptime': str(datetime.now() - self.start_time)
        }
    
    def get_cpu_temperature(self):
        """Get CPU temperature"""
        try:
            temp = subprocess.check_output(['vcgencmd', 'measure_temp'])
            return float(temp.decode('utf-8').replace('temp=', '').replace('\'C\n', ''))
        except:
            return None
    
    def get_network_info(self):
        """Get network interface information"""
        try:
            wifi_info = subprocess.check_output(['iwconfig', 'wlan0']).decode('utf-8')
            return {
                'wifi_signal': wifi_info,
                'interfaces': psutil.net_if_stats()
            }
        except:
            return None

class UpdateManager:
    def __init__(self):
        self.update_in_progress = False
        self.update_status = "idle"
        self.last_update_log = ""
    
    def get_status(self):
        """Get current update status"""
        return {
            "status": self.update_status,
            "in_progress": self.update_in_progress,
            "last_log": self.last_update_log
        }
    
    def perform_system_update(self):
        """Perform system update"""
        if self.update_in_progress:
            return False, "Update already in progress"
        
        self.update_in_progress = True
        thread = threading.Thread(target=self._run_system_update)
        thread.start()
        return True, "Update started"
    
    def _run_system_update(self):
        """Run system update in background"""
        try:
            self.update_status = "Updating system packages"
            logger.log(LogType.SYSTEM, "update_started")
            
            # Update package list
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            
            # Upgrade packages
            subprocess.run(["sudo", "apt-get", "upgrade", "-y"], check=True)
            
            # Update Python packages
            subprocess.run(["pip", "install", "--upgrade", "-r", "requirements.txt"], 
                         check=True)
            
            self.update_status = "Update complete"
            logger.log(LogType.SYSTEM, "update_completed")
            
            # Check if reboot required
            if os.path.exists("/var/run/reboot-required"):
                self.update_status = "Reboot required"
                logger.log(LogType.SYSTEM, "reboot_required")
        
        except Exception as e:
            self.update_status = f"Update failed: {str(e)}"
            logger.log(LogType.ERROR, "update_failed", {"error": str(e)})
        
        finally:
            self.update_in_progress = False

# Initialize global instances
system_info = SystemInfo()
update_manager = UpdateManager()
