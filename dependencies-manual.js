const { execSync } = require('child_process');
const chalk = require('chalk');
const path = require('path');
const fs = require('fs');

const checkPackageExists = (packageName) => {
  try {
    execSync(`npm list ${packageName}`, { stdio: 'pipe', cwd: __dirname });
    return true;
  } catch {
    return false;
  }
};

const checkPythonAndPyenv = () => {
  console.log(chalk.blue('🐍 Checking Python and pyenv...'));
  
  try {
    const pythonVersion = execSync('python --version', { stdio: 'pipe' });
    console.log(chalk.green(`✅ Python: ${pythonVersion.stdout.trim()}`));
  } catch (error) {
    console.log(chalk.red('❌ Python not found - pyenv may help'));
  }
  
  try {
    const pyenvVersion = execSync('pyenv --version', { stdio: 'pipe' });
    console.log(chalk.green(`✅ pyenv: ${pyenvVersion.stdout.trim()}`));
  } catch {
    console.log(chalk.yellow('⚠️  pyenv not found'));
  }
};
  try {
    const pythonVersion = execSync('python --version', { stdio: 'pipe' });
    console.log(chalk.green(`✅ Python: ${pythonVersion.stdout.trim()}`));
  } catch (error) {
    console.log(chalk.red('❌ Python not found - pyenv may help'));
    console.log(chalk.yellow('⚠️  Continuing without Python...'));
  }
  console.log(chalk.blue('🐍 Checking Python and pyenv...'));
  
  try {
    const pythonVersion = execSync('python --version', { stdio: 'pipe', stdio: 'pipe' });
    console.log(chalk.green(`✅ Python: ${pythonVersion.stdout.trim()}`));
  } catch {
    console.log(chalk.red('❌ Python not found - pyenv may help'));
  }
  
  try {
    const pyenvVersion = execSync('pyenv --version', { stdio: 'pipe', stdio: 'pipe' });
    console.log(chalk.green(`✅ pyenv: ${pyenvVersion.stdout.trim()}`));
  } catch {
    console.log(chalk.yellow('⚠️  pyenv not found'));
  }
};

const installAlternativePackages = () => {
  console.log(chalk.blue('\n🔧 Installing alternative packages (musicxml-json → xml2js)...'));
  
  const alternatives = [
    {
      name: 'xml2js',
      reason: 'More reliable MusicXML parsing',
      original: 'musicxml-json'
    },
    {
      name: 'music21',
      reason: 'Professional music notation',
      original: 'tone.js (for advanced features)'
    },
    {
      name: 'simple-web-audio-api',
      reason: 'Simpler, more reliable',
      original: 'web-audio-api'
    }
  ];
  
  alternatives.forEach(({ name, reason, original }) => {
    console.log(chalk.yellow(`⚠️  ${name}: ${reason}`));
    console.log(chalk.gray(`    Replaces: ${original}`));
    
    try {
      execSync(`npm install ${name}`, { stdio: 'pipe', cwd: __dirname });
      console.log(chalk.green(`✅ ${name} installed successfully`));
    } catch (error) {
      console.log(chalk.red(`❌ Failed to install ${name}: ${error.message}`));
    }
  });
};

const installBackend = () => {
  console.log(chalk.blue('\n🔧 Installing backend dependencies...'));
  
  try {
    execSync('cd backend && npm install --no-audit --no-fund --no-audit --legacy-peer-deps', { stdio: 'inherit', stdio: ['pipe', 'pipe'] });
    console.log(chalk.green('✅ Backend dependencies installed'));
  } catch (error) {
    console.log(chalk.red(`❌ Backend installation failed: ${error.message}`));
    console.log(chalk.yellow('\n🔧 Trying alternative installation...'));
      installAlternativePackages();
    }
};

const installFrontend = () => {
  console.log(chalk.blue('\n🎨 Installing frontend dependencies...'));
  
  try {
    execSync('cd frontend && npm install --no-audit --no-fund --no-audit --legacy-peer-deps', { stdio: 'inherit', stdio: ['pipe', 'pipe'] });
    console.log(chalk.green('✅ Frontend dependencies installed'));
  } catch (error) {
    console.log(chalk.red(`❌ Frontend installation failed: ${error.message}`));
    console.log(chalk.yellow('\n🔧 Trying minimal installation...'));
    
    // Try minimal Vue.js setup
    try {
      execSync('cd frontend && npm install vue@3 @vitejs/plugin-vue pinia', { stdio: 'inherit', stdio: ['pipe', 'pipe'] });
      console.log(chalk.green('✅ Minimal Vue.js setup completed'));
    } catch (error) {
      console.log(chalk.red(`❌ Minimal Vue.js setup failed: ${error.message}`));
    }
  }
};

const checkEnvironment = () => {
  console.log(chalk.blue('\n🔍 Environment Check:'));
  
  // Node.js
  const nodeVersion = execSync('node --version', { stdio: 'pipe' });
  console.log(chalk.green(`✅ Node.js: ${nodeVersion.stdout.trim()}`));
  
  // Python/pyenv
  checkPythonAndPyenv();
  
  // Check if core files exist
  const backendExists = fs.existsSync('backend/src');
  const frontendExists = fs.existsSync('frontend/src');
  
  console.log(chalk.blue('\n📁 Project Structure:'));
  console.log(chalk.green(`✅ Backend: ${backendExists ? 'Found' : 'Missing'}`));
  console.log(chalk.green(`✅ Frontend: ${frontendExists ? 'Found' : 'Missing'}`));
  
  // Ollama
  if (execSync('which ollama', { stdio: 'pipe' }).status === 0) {
    console.log(chalk.green('✅ Ollama: Found'));
  } else {
    console.log(chalk.yellow('⚠️ Ollama: Not found (optional for AI features)'));
  }
};

const createStartScript = () => {
  const scriptContent = `#!/bin/bash
echo "🎵 Choral LLM Workbench - Development Environment"
echo "====================================="

echo "🔧 Starting Backend (http://localhost:3000)"
cd backend && npm run start:dev &

echo "🎨 Starting Frontend (http://localhost:5173)"
cd frontend && npm run dev &
echo ""
echo "🎯 Development Environment Ready!"
echo ""
echo "📚 Backend API: http://localhost:3000/api"
echo "📚 Frontend URL: http://localhost:5173"
echo ""
echo "🔧 Stop servers with Ctrl+C"
`;
  
  fs.writeFileSync('start-dev.sh', scriptContent);
  fs.chmod('start-dev.sh', '755');
  console.log(chalk.green('✅ Created start-dev.sh script'));
};

const main = () => {
  console.log(chalk.bold.blue('\n🎵 Choral LLM Workbench - Manual Setup\n'));
  console.log(chalk.bold('=====================================\n'));
  
  // Environment check
  checkEnvironment();
  
  // Ask user what to do
  console.log(chalk.yellow('\n🤔 What would you like to do?'));
  console.log(chalk.cyan('1. Install Backend Dependencies'));
  console.log(chalk.cyan('2. Install Frontend Dependencies'));
  console.log(chalk.cyan('3. Install All Dependencies'));
  console.log(chalk.cyan('4. Check Environment'));
  console.log(chalk.cyan('5. Create Development Scripts'));
  console.log(chalk.cyan('6. Start Development Servers'));
  console.log(chalk.cyan('0. Exit'));
  console.log('\n');
  
  process.stdout.write('Enter choice (0-6): ');
  
  process.stdin.once('data', (answer) => {
    const choice = answer.trim();
    
    switch (choice) {
      case '1':
        installBackend();
        break;
      case '2':
        installFrontend();
        break;
      case '3':
        console.log(chalk.blue('\n🔧 Installing both backend and frontend...'));
        installBackend();
        installFrontend();
        break;
      case '4':
        checkEnvironment();
        break;
      case '5':
        createStartScript();
        break;
      case '6':
      console.log(chalk.yellow('\n� Exiting...'));
        process.exit(0);
        break;
      default:
        console.log(chalk.red('\n❌ Invalid choice. Please select 0-6.'));
        main();
        break;
    }
  };
}
};

if (require.main === module) {
  main().catch(error => {
    console.error(chalk.red(`❌ Fatal error: ${error.message}`));
    process.exit(1);
  });
}