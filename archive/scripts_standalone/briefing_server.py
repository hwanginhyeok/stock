import http.server, socketserver, os

HTML_WRAPPER_TOP = '''<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
</head><body>'''
HTML_WRAPPER_BOT = '</body></html>'

class UTF8Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split('?')[0].lstrip('/')
        if path.endswith('_naver.html') and os.path.exists(path):
            content = open(path, 'rb').read()
            # fragment를 full document로 감쌈
            body = (HTML_WRAPPER_TOP.encode('utf-8')
                    + content
                    + HTML_WRAPPER_BOT.encode('utf-8'))
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            super().do_GET()

    def end_headers(self):
        if self.path.endswith('.html'):
            self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()

    def log_message(self, *a): pass

os.chdir('/home/window11/stock/data/briefings')
with socketserver.TCPServer(('', 8765), UTF8Handler) as s:
    s.serve_forever()
