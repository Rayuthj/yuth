// Minimal static file server for the renderer page
const http = require('http');
const fs = require('fs');
const path = require('path');
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.woff': 'font/woff', '.json': 'application/json' };
module.exports = function serve(root, port = 0) {
  return new Promise((resolve) => {
    const srv = http.createServer((req, res) => {
      const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
      if (!p.startsWith(root)) return res.writeHead(403).end();
      fs.readFile(p, (err, data) => {
        if (err) return res.writeHead(404).end('not found');
        res.writeHead(200, { 'Content-Type': TYPES[path.extname(p)] || 'application/octet-stream' });
        res.end(data);
      });
    });
    srv.listen(port, '127.0.0.1', () => resolve(srv));
  });
};
