const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const chalk = require('chalk');
const ora = require('ora');

class DependencyInstaller {
  constructor() {
    this.steps = [
      { name: 'Node.js', command: 'node --version', check: (output) => output.includes('v18') },
      { name: 'npm', command: 'npm --version', check: (output) => output.includes('9.') },
      { name: 'Ollama (optional)', command: 'ollama --version', check: (output) => output.includes('ollama') }
    ];
    
    this.issues = [];
  }

  async checkDependencies() {
    console.log(chalk.blue('🔍 Checking system dependencies...'));
    
    for (const step of this.steps) {
      const spinner = ora(`Checking ${step.name}...`).start();
      
      try {
        const result = await this.executeCommand(step.command);
        if (step.check ? step.check(result) : true) {
          spinner.succeed(`${step.name} installed`);
        } else {
          spinner.fail(`${step.name} version issue`);
          this.issues.push(`${step.name} version requirement not met`);
        }
      } catch (error) {
        spinner.warn(`${step.name} not found`);
        this.issues.push(`${step.name} not installed: ${error.message}`);
        
        if (step.name === 'Ollama') {
          console.log(chalk.yellow('⚠️  Ollama is optional - AI features will be limited'));
        }
      }
    }
  }

  async executeCommand(command) {
    return new Promise((resolve, reject) => {
      const child = spawn(command, { shell: true });
      let output = '';
      
      child.stdout.on('data', (data) => {
        output += data.toString();
      });
      
      child.stderr.on('data', (data) => {
        output += data.toString();
      });
      
      child.on('close', (code) => {
        if (code === 0) {
          resolve(output);
        } else {
          reject(new Error(`Command failed with code ${code}`));
        }
      });
      
      child.on('error', (error) => {
        reject(error);
      });
    });
  }

  async fixPackageJson() {
    const filesToFix = [
      { path: 'backend/package.json', issues: ['@nestjs/websockets/@nestjs/platform-socket.io'] },
      { path: 'frontend/package.json', issues: [] }
    ];

    for (const file of filesToFix) {
      if (!fs.existsSync(file.path)) {
        console.log(chalk.yellow(`⚠️  File not found: ${file.path}`));
        continue;
      }

      try {
        const content = fs.readFileSync(file.path, 'utf8');
        
        // Fix WebSocket package name
        if (file.issues.includes('@nestjs/websockets/@nestjs/platform-socket.io')) {
          const fixedContent = content.replace(
            '"@nestjs/websockets/@nestjs/platform-socket.io": "^10.0.0"',
            '"@nestjs/platform-socket.io": "^10.0.0"'
          );
          fs.writeFileSync(file.path, fixedContent);
          console.log(chalk.green(`✅ Fixed WebSocket dependency in ${file.path}`));
        }
        
        // Replace musicxml-json with xml2js
        if (file.issues.includes('musicxml-json')) {
          const fixedContent = content.replace(
            '"musicxml-json": "^1.2.0"',
            '"xml2js": "^0.6.0"'
          );
          fs.writeFileSync(file.path, fixedContent);
          console.log(chalk.green(`✅ Fixed MusicXML dependency in ${file.path}`));
        }
        
      } catch (error) {
        console.log(chalk.red(`❌ Error fixing ${file.path}: ${error.message}`));
      }
    }
  }

  async installDependencies() {
    const projects = ['backend', 'frontend'];
    
    for (const project of projects) {
      const projectPath = path.join(process.cwd(), project);
      
      if (!fs.existsSync(projectPath)) {
        console.log(chalk.yellow(`⚠️  Skipping ${project} - directory not found`));
        continue;
      }

      const spinner = ora(`Installing dependencies for ${project}...`).start();
      
      try {
        await this.executeCommand(`cd ${project} && npm install --no-audit --no-fund`);
        spinner.succeed(`Dependencies installed for ${project}`);
      } catch (error) {
        spinner.fail(`Failed to install dependencies for ${project}`);
        this.issues.push(`npm install failed for ${project}: ${error.message}`);
      }
    }
  }

  async installOllama() {
    const spinner = ora('Installing Ollama (optional)...').start();
    
    try {
      // Check if Ollama is already installed
      await this.executeCommand('ollama --version');
      spinner.succeed('Ollama already installed');
      return;
    } catch (error) {
      // Try to install Ollama
      spinner.text = 'Installing Ollama...';
      
      try {
        // Linux/macOS installation
        if (process.platform === 'linux' || process.platform === 'darwin') {
          await this.executeCommand('curl -fsSL https://ollama.ai/install.sh | sh');
          spinner.succeed('Ollama installed successfully');
        } else {
          // Windows
          spinner.warn('Ollama installation on Windows requires manual setup');
          console.log(chalk.blue('Please visit https://ollama.ai to install Ollama'));
        }
      } catch (installError) {
        spinner.warn('Ollama installation failed');
        console.log(chalk.yellow('⚠️  Continuing without Ollama - AI features will be limited'));
      }
    }
  }

  async createEnvironmentFiles() {
    console.log(chalk.blue('🔧 Setting up environment files...'));
    
    const envContent = `
# Choral LLM Workbench Environment Variables

# API Configuration
API_PORT=3000
API_HOST=localhost

# Frontend Configuration
VITE_PORT=5173

# AI Configuration
OLLAMA_HOST=http://localhost:11434
DEFAULT_MODEL=llama3.1

# Audio Configuration
SAMPLE_RATE=22050
BUFFER_SIZE=4096

# File Paths
TEMP_DIR=./temp
UPLOAD_DIR=./uploads
OUTPUT_DIR=./output
`;

    fs.writeFileSync('.env.example', envContent);
    console.log(chalk.green('✅ Environment example file created'));
    
    // Create .gitignore
    const gitignoreContent = `
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
.cache/

# Environment
.env
.env.local

# Temp and uploads
temp/
uploads/
output/

# Logs
logs/
*.log

# OS
.DS_Store
Thumbs.db
`;

    if (!fs.existsSync('.gitignore')) {
      fs.writeFileSync('.gitignore', gitignoreContent);
      console.log(chalk.green('✅ .gitignore file created'));
    }
  }

  async createLaunchScripts() {
    const scriptsContent = {
      'start': 'node setup-dependencies.js start',
      'dev': 'node setup-dependencies.js dev',
      'setup': 'node setup-dependencies.js --force-install',
      'check': 'node setup-dependencies.js --check-only',
      'backend': 'cd backend && npm run start:dev',
      'frontend': 'cd frontend && npm run dev',
      'build': 'npm run build:backend && npm run build:frontend',
      'install-all': 'npm run setup',
      'clean': 'rimraf dist node_modules backend/node_modules frontend/node_modules'
    };

    // Update root package.json
    let rootPackage = {};
    if (fs.existsSync('package.json')) {
      rootPackage = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    }

    rootPackage.scripts = { ...rootPackage.scripts, ...scriptsContent };
    fs.writeFileSync('package.json', JSON.stringify(rootPackage, null, 2));
    console.log(chalk.green('✅ Launch scripts updated in package.json'));
  }

  async main() {
    console.log(chalk.bold.blue('\n🎵 Choral LLM Workbench - Dependency Setup\n'));
    
    const checkOnly = process.argv.includes('--check-only');
    const forceInstall = process.argv.includes('--force-install');
    
    // Check system dependencies
    await this.checkDependencies();
    
    if (checkOnly) {
      if (this.issues.length > 0) {
        console.log(chalk.red('\n❌ Issues found:'));
        this.issues.forEach(issue => console.log(chalk.red(`  - ${issue}`)));
        process.exit(1);
      } else {
        console.log(chalk.green('\n✅ All dependencies satisfied!'));
        process.exit(0);
      }
    }
    
    if (!forceInstall) {
      console.log(chalk.blue('\n📦 To install dependencies, run: npm run setup'));
      console.log(chalk.blue('📋 To check only, run: npm run check\n'));
      return;
    }
    
    // Fix package.json files
    console.log(chalk.blue('\n🔧 Fixing package.json files...'));
    await this.fixPackageJson();
    
    // Install dependencies
    console.log(chalk.blue('\n📦 Installing project dependencies...'));
    await this.installDependencies();
    
    // Try to install Ollama (optional)
    console.log(chalk.blue('\n🤖 Installing Ollama (optional)...'));
    await this.installOllama();
    
    // Create environment files
    console.log(chalk.blue('\n🔧 Setting up environment files...'));
    await this.createEnvironmentFiles();
    
    // Create launch scripts
    console.log(chalk.blue('\n🚀 Creating launch scripts...'));
    await this.createLaunchScripts();
    
    // Summary
    console.log(chalk.bold('\n🎯 Setup Complete!\n'));
    console.log(chalk.green('✅ Dependencies installed'));
    console.log(chalk.green('✅ Package files fixed'));
    console.log(chalk.green('✅ Environment configured'));
    console.log(chalk.green('✅ Launch scripts created'));
    
    if (this.issues.length > 0) {
      console.log(chalk.yellow('\n⚠️  Warnings:'));
      this.issues.forEach(issue => console.log(chalk.yellow(`  - ${issue}`)));
    }
    
    console.log(chalk.bold.blue('\n🚀 Next Steps:'));
    console.log(chalk.blue('npm run dev        # Start both backend and frontend'));
    console.log(chalk.blue('npm run backend      # Start backend only'));
    console.log(chalk.blue('npm run frontend     # Start frontend only'));
    console.log(chalk.blue('npm run build        # Build for production'));
    
    if (this.issues.length === 0) {
      console.log(chalk.green('\n🎉 Ready for development!'));
    } else {
      console.log(chalk.yellow('\n🎧 Some issues were found, but you can still develop with limited functionality'));
    }
  }
}

if (require.main === module) {
  new DependencyInstaller().main().catch(error => {
    console.error(chalk.red('\n❌ Setup failed:'), error.message);
    process.exit(1);
  });
}