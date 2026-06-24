import fs from 'fs';
fs.writeFileSync('/Users/wow/.claude-to-im/env_dump.txt', JSON.stringify(process.env, null, 2));
console.log("Dumped env to /Users/wow/.claude-to-im/env_dump.txt");
