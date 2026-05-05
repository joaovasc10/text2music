"""
Servidor HTTP - TextoMúsica

Servidor simples usando http.server.
Serve os arquivos do frontend em GET /.
Expõe a API via POST em rotas JSON.
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

from music_system import MusicSystem


# Instância global do MusicSystem
music_system = MusicSystem()

# Caminho para a pasta frontend
FRONTEND_PATH = Path(__file__).parent.parent / "frontend"


class TextoMusicaHandler(BaseHTTPRequestHandler):
    """
    Handler para requisições HTTP.
    
    GET /          -> Serve index.html
    GET /style.css -> Serve style.css
    GET /app.js    -> Serve app.js
    
    POST /play     -> Processa e toca sequência
    POST /stop     -> Para reprodução
    POST /reset    -> Reseta configurações
    """
    
    def do_GET(self):
        """Trata requisições GET."""
        try:
            # Mapear paths para arquivos
            if self.path == "/" or self.path == "/index.html":
                file_path = FRONTEND_PATH / "index.html"
                content_type = "text/html; charset=utf-8"
            elif self.path == "/style.css":
                file_path = FRONTEND_PATH / "style.css"
                content_type = "text/css; charset=utf-8"
            elif self.path == "/app.js":
                file_path = FRONTEND_PATH / "app.js"
                content_type = "application/javascript; charset=utf-8"
            else:
                self.send_error(404)
                return
            
            # Verificar se arquivo existe
            if not file_path.exists():
                self.send_error(404)
                return
            
            # Enviar arquivo
            self.send_response(200)
            self.send_header("Content-type", content_type)
            self.end_headers()
            
            with open(file_path, "rb") as f:
                self.wfile.write(f.read())
        
        except Exception as e:
            print(f"ERRO em do_GET: {e}")
            self.send_error(500)
    
    def do_POST(self):
        """Trata requisições POST (API JSON)."""
        try:
            # Obter tamanho do corpo
            content_length = int(self.headers.get("Content-Length", 0))
            
            # Ler o corpo
            body = self.rfile.read(content_length)
            data = json.loads(body.decode("utf-8"))
            
            # ================================================================
            # POST /play - Processar e tocar sequência
            # ================================================================
            if self.path == "/play":
                text = data.get("text", "")
                bpm = data.get("bpm", 120)
                instrument = data.get("instrument", 1)
                octave = data.get("octave", 4)
                volume = data.get("volume", 64)
                
                # Configurar e executar
                music_system.configure(bpm, instrument, octave, volume)
                num_events = music_system.run(text)
                
                response = {
                    "status": "ok",
                    "events": num_events
                }
            
            # ================================================================
            # POST /stop - Parar reprodução
            # ================================================================
            elif self.path == "/stop":
                music_system.stop()
                response = {"status": "ok"}
            
            # ================================================================
            # POST /reset - Resetar configurações
            # ================================================================
            elif self.path == "/reset":
                music_system.reset()
                response = {"status": "ok"}
            
            else:
                self.send_error(404)
                return
            
            # Enviar resposta JSON
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        
        except Exception as e:
            print(f"ERRO em do_POST: {e}")
            self.send_error(500)
    
    def log_message(self, format, *args):
        """Suprimir logs padrão do servidor (opcional)."""
        # Descomente a linha abaixo para ver os logs
        # print(format % args)
        pass


def run_server(host="127.0.0.1", port=8000):
    """
    Inicia o servidor HTTP.
    
    Args:
        host (str): Host a vincular (127.0.0.1 = localhost)
        port (int): Porta (padrão 8000)
    """
    server_address = (host, port)
    httpd = HTTPServer(server_address, TextoMusicaHandler)
    
    print(f"Servidor TextoMúsica iniciado em http://{host}:{port}")
    print("Pressione Ctrl+C para parar.")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor parado.")
        httpd.server_close()


if __name__ == "__main__":
    run_server()
