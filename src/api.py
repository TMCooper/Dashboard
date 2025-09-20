import os, subprocess, sys, time, psutil, glob
from src.backend import Cardinal
from flask import Flask, jsonify, render_template, request

# --- Configuration et variables globales ---
# Assurez-vous que ce chemin est correct par rapport à l'endroit où vous lancez l'app
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'scripts')
# Dictionnaire pour garder une trace des scripts en cours d'exécution
# Format: { 'nom_du_script.py': <objet Popen> }
UTILS_DIR = os.path.join(os.path.dirname(__file__), 'utils') 
running_scripts = {}

class Yui:
    app = Flask(__name__)

    # --- Fonctions Utilitaires ---
    def get_uptime():
        """Retourne l'uptime du système sous forme de tuple (jours, heures, minutes)."""
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        return days, hours, minutes

    # --- Routes API ---
    @app.route('/api/stats')
    def get_stats():
        # On reprend le code de l'étape 1
        h, m, s = Cardinal.up_time_cpu()
        usage_cpu = Cardinal.cpu_percent()
        ram_utiliser, ram_total = Cardinal.ram_monitor()    
        disk_info = Cardinal.disk_monitor()
        freq_cpu = Cardinal.freq_cpu()

        # On retourne les données au format JSON
        return jsonify({
            'cpu_usage': usage_cpu,
            'cpu_freq': freq_cpu,
            'cpu_uptime': [h, m, s],
            'ram_used': ram_utiliser,
            'ram_total': ram_total,
            'disks': disk_info
        })

    @app.route('/api/browse')
    def browse_path():
        path = request.args.get('path', 'C:\\')
        if '..' in path and len(path.split('\\')) < 3:
            path = path.split('\\')[0] + '\\'
        if not os.path.exists(path) or not os.path.isdir(path):
            return jsonify({'error': 'Path not found or is not a directory'}), 404
        try:
            items = []
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                item_type = 'folder' if os.path.isdir(full_path) else 'file'
                items.append({'name': item, 'type': item_type, 'path': full_path})
            return jsonify({'current_path': path, 'items': items})
        except PermissionError:
            return jsonify({'error': 'Permission denied'}), 403
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/open')
    def open_file():
        path = request.args.get('path')
        if not path or not os.path.exists(path):
            return jsonify({'error': 'File not found'}), 404
        try:
            os.startfile(path)
            return jsonify({'status': 'ok', 'message': f'Opened {path}'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # --- NOUVELLES ROUTES POUR LA GESTION DES SCRIPTS ---

    @app.route('/api/scripts')
    def list_scripts():
        """Liste les scripts disponibles dans le dossier src/scripts."""
        if not os.path.exists(SCRIPTS_DIR):
            os.makedirs(SCRIPTS_DIR) # Crée le dossier s'il n'existe pas
            return jsonify([])

        try:
            py_scripts = glob.glob(os.path.join(SCRIPTS_DIR, '*.py'))
            bat_scripts = glob.glob(os.path.join(SCRIPTS_DIR, '*.bat'))
            all_scripts = py_scripts + bat_scripts
            
            # On ne retourne que le nom du fichier, pas le chemin complet
            script_names = [{'name': os.path.basename(s)} for s in all_scripts]
            return jsonify(script_names)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/scripts/view')
    def view_script():
        """Retourne le contenu d'un fichier script."""
        script_name = request.args.get('name')
        if not script_name:
            return jsonify({'error': 'Script name is required'}), 400
        
        # Sécurité : Empêche de remonter dans les répertoires (Directory Traversal)
        script_path = os.path.abspath(os.path.join(SCRIPTS_DIR, script_name))
        if not script_path.startswith(os.path.abspath(SCRIPTS_DIR)):
            return jsonify({'error': 'Access denied'}), 403

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return jsonify({'content': content})
        except FileNotFoundError:
            return jsonify({'error': 'Script not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/scripts/launch', methods=['POST'])
    def launch_script():
        """Lance un script."""
        script_name = request.args.get('name')
        if not script_name:
            return jsonify({'error': 'Script name is required'}), 400

        if script_name in running_scripts:
            return jsonify({'status': 'already_running', 'message': f'{script_name} is already running.'})

        script_path = os.path.join(SCRIPTS_DIR, script_name)
        if not os.path.exists(script_path):
            return jsonify({'error': 'Script not found'}), 404
            
        try:
            command = []
            if script_name.endswith('.py'):
                command = [sys.executable, script_path]
            elif script_name.endswith('.bat'):
                command = [script_path]
            
            # --- AJOUT IMPORTANT ---
            # On dit au sous-processus de s'exécuter DEPUIS le dossier des scripts
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=SCRIPTS_DIR)
            running_scripts[script_name] = process
            
            return jsonify({'status': 'launched', 'message': f'Launched {script_name} with PID {process.pid}.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    @app.route('/api/scripts/stop', methods=['POST'])
    def stop_script():
        """Arrête un script en cours d'exécution."""
        script_name = request.args.get('name')
        if not script_name:
            return jsonify({'error': 'Script name is required'}), 400

        if script_name not in running_scripts:
            return jsonify({'status': 'not_running', 'message': f'{script_name} is not running.'})

        try:
            process_to_kill = running_scripts[script_name]
            parent = psutil.Process(process_to_kill.pid)
            # Termine le processus parent et tous ses enfants
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            
            del running_scripts[script_name] # Retire le script du dictionnaire
            
            return jsonify({'status': 'stopped', 'message': f'Stopped {script_name}.'})
        except psutil.NoSuchProcess:
            # Le processus a peut-être déjà terminé
            del running_scripts[script_name]
            return jsonify({'status': 'already_stopped', 'message': f'{script_name} was already stopped.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/api/run-update', methods=['POST'])
    def run_update_script():
        """Lance le script de mise à jour `update.bat` depuis le dossier `utils`."""
        update_script_path = os.path.join(UTILS_DIR, 'update.bat')

        if not os.path.exists(update_script_path):
            return jsonify({'error': 'Le script update.bat est introuvable !'}), 404
        
        try:
            # On lance le script. Il s'ouvrira dans sa propre fenêtre de commande.
            subprocess.Popen([update_script_path], shell=True)
            return jsonify({'status': 'ok', 'message': 'Lancement du script de mise a jour.'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # --- Route Principale pour afficher l'interface ---
    @app.route('/home')
    def dashboard():
        return render_template('index.html')
    
    @app.route('/')
    def redirection():
        return render_template('redirection.html')