"""
Simple HTTP server to serve the InvoiceShield frontend.
Run this to test the frontend with the backend.
"""
import http.server
import socketserver
import webbrowser
import os

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    # Change to frontend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    Handler = MyHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("=" * 70)
        print(f"🚀 InvoiceShield Frontend Server Running!")
        print("=" * 70)
        print(f"\n📱 Frontend: http://localhost:{PORT}")
        print(f"🔧 Backend:  http://localhost:8000")
        print(f"📚 API Docs: http://localhost:8000/docs")
        print("\n⚠️  Make sure the backend is running:")
        print("   uvicorn app.main:app --reload")
        print("\n✨ Opening browser...")
        print("\nPress Ctrl+C to stop the server\n")
        print("=" * 70)
        
        # Open browser
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 Frontend server stopped")
