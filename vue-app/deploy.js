import { exec } from 'child_process';
import os from 'os';

const isWindows = os.platform() === 'win32';
const script = isWindows ? 'deploy.bat' : './deploy.sh';

exec(script, (error, stdout, stderr) => {
  if (error) {
    console.error(`Error executing script: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`Error output: ${stderr}`);
    return;
  }
  console.log(`Output: ${stdout}`);
});