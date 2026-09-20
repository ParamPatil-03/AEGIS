const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf8');

const scriptRegex = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
let count = 0;

while ((match = scriptRegex.exec(html)) !== null) {
  count++;
  const code = match[1].trim();
  if (!code) continue;
  try {
    new Function(code);
    console.log(`Script tag #${count}: Valid syntax (${code.length} chars)`);
  } catch (err) {
    console.error(`Script tag #${count}: SYNTAX ERROR:`, err.message);
  }
}
