import psutil, wmi, platform, pythoncom
from datetime import datetime

class Cardinal:
    def up_time_cpu():
        if platform.system() == "Windows":
            pythoncom.CoInitialize()
            for os in wmi.WMI().Win32_OperatingSystem():
                # LastBootUpTime est formaté comme HHMMSS.mmm
                last_boot = os.LastBootUpTime.split('.')[0]
                boot_time = f"{last_boot[8:10]}:{last_boot[10:12]}:{last_boot[12:14]}"
                # print(boot_time)
                current_time = Cardinal.convert_to_second(datetime.now().time().strftime("%H:%M:%S")) 
                boot_timer = Cardinal.convert_to_second(boot_time)
                h, m, s = Cardinal.uptime_calc(boot_timer, current_time)

                return h, m, s

        else:
            # a tester sur un linux
            boot_timer = Cardinal.convert_to_second(psutil.boot_time())
            current_time = Cardinal.convert_to_second(datetime.now().time().strftime("%H:%M:%S"))
            h, m, s = Cardinal.uptime_calc(boot_timer, current_time)

            return h, m, s
    
    def cpu_percent():
        return psutil.cpu_percent(interval=0.5)

    def ram_monitor():
        ram_info = psutil.virtual_memory()
        ram_utiliser = ram_info.used / (1024**3)
        ram_total = ram_info.total / (1024**3)
        # print(f"{ram_utiliser:.2f} Go / {ram_total:.2f} Go")
        return round(ram_utiliser, 0), round(ram_total, 0) # Round arrondi le tous a l'unité du dessus car 0 ne vas pas après la virgule

    def disk_monitor():
        """
        Renvoi un tableau entre 0 et 2
        """
        
        disks = []

        for part in psutil.disk_partitions():
            usage = psutil.disk_usage(part.mountpoint)
            disks.append({
                'free': usage.free,                 # libre en octets
                'mountpoint': part.mountpoint,      # point de montage
                'percent': usage.percent,           # pourcentage utilisé
                'total': usage.total,               # total en octets
                'used': usage.used                  # utilisé en octets
                })
        # print(disks[0]) # 0 a 2 dans le cas de mon pc
        # Format total=1890853056512, used=1747433676800, free=143419379712, percent=92.4
        return disks #0 a 2
    
    def convert_to_second(hour):
        h, m, s = map(int, hour.split(":"))
        total_seconds = h*3600 + m*60 + s
        return total_seconds
    
    def uptime_calc(boot_timer, current_time):
        total_time = current_time - boot_timer
        h = total_time // 3600
        m = (total_time % 3600) // 60
        s = total_time % 60
        return h, m, s

    def freq_cpu():
        freq_cpu_max = psutil.cpu_freq()
        return round(freq_cpu_max.max / 1000, 2)