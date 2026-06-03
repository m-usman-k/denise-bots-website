import json
import asyncio
import time
import psutil
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class LiveStatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # We only allow super admins to see stats
        if not self.scope["user"].is_authenticated or not getattr(self.scope["user"], 'is_super_admin', False):
            await self.close()
            return
            
        await self.accept()
        
        # Start the background task to poll stats
        self.polling_task = asyncio.create_task(self.poll_stats())

    async def disconnect(self, close_code):
        # Cancel the polling task when the client disconnects
        if hasattr(self, 'polling_task'):
            self.polling_task.cancel()

    async def poll_stats(self):
        try:
            while True:
                # Fetch stats asynchronously to not block the main event loop
                stats = await asyncio.to_thread(self.get_all_stats)
                
                # Send the stats to the client
                await self.send(text_data=json.dumps(stats))
                
                # Wait 3 seconds before next poll
                await asyncio.sleep(3)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"WebSocket polling error: {e}")

    def get_all_stats(self):
        # 1. Fetch Server Stats
        cpu_percent = psutil.cpu_percent(interval=None)
        
        memory = psutil.virtual_memory()
        ram_used_gb = round(memory.used / (1024**3), 2)
        ram_total_gb = round(memory.total / (1024**3), 2)
        ram_percent = memory.percent
        
        swap = psutil.swap_memory()
        swap_used_gb = round(swap.used / (1024**3), 2)
        swap_total_gb = round(swap.total / (1024**3), 2)
        swap_percent = swap.percent
        
        disk = psutil.disk_usage('/')
        disk_used_gb = round(disk.used / (1024**3), 2)
        disk_total_gb = round(disk.total / (1024**3), 2)
        disk_percent = disk.percent
        
        net = psutil.net_io_counters()
        net_sent_mb = round(net.bytes_sent / (1024**2), 2)
        net_recv_mb = round(net.bytes_recv / (1024**2), 2)
        
        try:
            import os
            load_avg = os.getloadavg()
            load_str = f"{load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}"
        except Exception:
            load_str = "N/A"
        
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_days = uptime_hours // 24
        uptime_str = f"{uptime_days}d {uptime_hours % 24}h" if uptime_days > 0 else f"{uptime_hours}h"
        
        server_stats = {
            'cpu_percent': cpu_percent,
            'ram_used': ram_used_gb,
            'ram_total': ram_total_gb,
            'ram_percent': ram_percent,
            'swap_used': swap_used_gb,
            'swap_total': swap_total_gb,
            'swap_percent': swap_percent,
            'disk_used': disk_used_gb,
            'disk_total': disk_total_gb,
            'disk_percent': disk_percent,
            'net_sent': net_sent_mb,
            'net_recv': net_recv_mb,
            'load_avg': load_str,
            'uptime': uptime_str
        }

        # 2. Fetch PM2 Stats
        pm2_status = {}
        import subprocess
        try:
            result = subprocess.run(['pm2', 'jlist'], capture_output=True, text=True)
            if result.returncode == 0:
                pm2_data = json.loads(result.stdout)
                for process in pm2_data:
                    name = process.get('name')
                    pm2_env = process.get('pm2_env', {})
                    status = pm2_env.get('status', 'offline')
                    uptime = pm2_env.get('pm_uptime', 0)
                    
                    uptime_str_bot = "0s"
                    if uptime > 0:
                        diff = int(time.time() * 1000) - uptime
                        seconds = diff // 1000
                        minutes = seconds // 60
                        hours = minutes // 60
                        if hours > 0: uptime_str_bot = f"{hours}h {minutes % 60}m"
                        elif minutes > 0: uptime_str_bot = f"{minutes}m"
                        else: uptime_str_bot = f"{seconds}s"

                    monit = process.get('monit', {})
                    cpu = monit.get('cpu', 0)
                    memory_val = monit.get('memory', 0)
                    memory_mb = round(memory_val / (1024 * 1024), 1)

                    pm2_status[name] = {
                        'status': status,
                        'uptime': uptime_str_bot,
                        'cpu': cpu,
                        'memory': memory_mb
                    }
        except Exception as e:
            pass

        # 3. Fetch Security / Auth logs
        auth_logs = []
        try:
            auth_res = subprocess.run(['tail', '-n', '100', '/var/log/auth.log'], capture_output=True, text=True)
            if auth_res.returncode == 0:
                lines = auth_res.stdout.split('\n')
                for line in reversed(lines):
                    if not line: continue
                    if "session opened for user" in line or "Failed password" in line or "Accepted publickey" in line or "Disconnected from" in line:
                        auth_logs.append(line)
                        if len(auth_logs) >= 15: break
        except Exception:
            pass
            
        # 4. Fetch App Logs
        app_logs = ""
        try:
            log_res = subprocess.run(['journalctl', '-u', 'denise-bots', '-n', '40', '--no-pager'], capture_output=True, text=True)
            if log_res.returncode == 0:
                app_logs = log_res.stdout
        except Exception:
            pass

        return {
            'server_stats': server_stats,
            'pm2_status': pm2_status,
            'auth_logs': auth_logs,
            'app_logs': app_logs
        }
