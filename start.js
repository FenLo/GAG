// Start script for Windows
const { spawn } = require('child_process');

console.log('Starting GAG Discord Bot...');

const bot = spawn('node', ['bot.js'], {
    stdio: 'inherit',
    shell: true
});

bot.on('close', (code) => {
    console.log(`Bot process exited with code ${code}`);
});
