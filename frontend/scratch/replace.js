import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const srcDir = path.resolve(__dirname, '../src');

function walkDir(dir, callback) {
  fs.readdirSync(dir).forEach(f => {
    let dirPath = path.join(dir, f);
    let isDirectory = fs.statSync(dirPath).isDirectory();
    isDirectory ? walkDir(dirPath, callback) : callback(dirPath);
  });
}

const colorMap = [
  { regex: /bg-white/g, replacement: 'bg-[#111111]' },
  { regex: /bg-slate-50\/50/g, replacement: 'bg-[#111111]/50' },
  { regex: /bg-slate-50/g, replacement: 'bg-[#111111]' },
  { regex: /bg-slate-100/g, replacement: 'bg-[#1a1a1a]' },
  { regex: /bg-slate-200/g, replacement: 'bg-[#222222]' },
  { regex: /border-slate-50/g, replacement: 'border-[#111111]' },
  { regex: /border-slate-100/g, replacement: 'border-[#222222]' },
  { regex: /border-slate-200/g, replacement: 'border-[#333333]' },
  { regex: /border-slate-800/g, replacement: 'border-[#111111]' },
  { regex: /text-slate-900/g, replacement: 'text-white' },
  { regex: /text-slate-800/g, replacement: 'text-neutral-200' },
  { regex: /text-slate-700/g, replacement: 'text-neutral-300' },
  { regex: /text-slate-600/g, replacement: 'text-neutral-400' },
  { regex: /text-slate-500/g, replacement: 'text-neutral-400' },
  { regex: /text-slate-400/g, replacement: 'text-neutral-500' },
  { regex: /text-slate-300/g, replacement: 'text-neutral-600' },
  { regex: /hover:bg-slate-50/g, replacement: 'hover:bg-[#1a1a1a]' },
  { regex: /bg-slate-900/g, replacement: 'bg-[#00e6b8] text-black' },
];

walkDir(srcDir, (filePath) => {
  if (filePath.endsWith('.svelte')) {
    let content = fs.readFileSync(filePath, 'utf8');
    let original = content;
    
    colorMap.forEach(({ regex, replacement }) => {
      content = content.replace(regex, replacement);
    });

    if (original !== content) {
      fs.writeFileSync(filePath, content);
      console.log(`Updated ${filePath}`);
    }
  }
});
