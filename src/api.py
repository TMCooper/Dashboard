from src.backend import Cardinal
from flask import Flask, jsonify, render_template

class Yui:
    app = Flask(__name__)

    @app.route('/api/stats') # Crée une "URL" pour nos données
    def get_stats():
        # On reprend le code de l'étape 1
        h, m, s = Cardinal.up_time_cpu()
        usage_cpu = Cardinal.cpu_percent()
        ram_utiliser, ram_total = Cardinal.ram_monitor()    
        disk_info = Cardinal.disk_monitor()

        # On retourne les données au format JSON
        return jsonify({
            'cpu_usage': usage_cpu,
            'cpu_uptime': [h, m, s],
            'ram_used': ram_utiliser,
            'ram_total': ram_total,
            'disks': disk_info
        })
    
    @app.route('/home')
    def home():
        return render_template("index.html")
