const { spawn } = require('child_process');
const chalk = require('chalk');
const fs = require('fs');
const path = require('path');

const installPackage = (packageName, alternatives = []) => {
  console.log(chalk.blue(`\n🔧 Installing ${packageName}...`));
  
  for (const alt of alternatives) {
    try {
      const result = spawnSync(`npm install ${alt.name}`, { 
        stdio: 'pipe',
        shell: true,
        cwd: __dirname 
      });
      
      if (result.status === 0) {
        console.log(chalk.green(`✅ ${alt.name} installed successfully`));
        return true;
      }
    } catch (error) {
      console.log(chalk.yellow(`⚠️ ${alt.name} failed: ${error.message}`));
    }
  }
  
  console.log(chalk.red(`❌ Failed to install ${packageName}`));
  return false;
};

const installDependencies = (packages, alternatives = {}) => {
  for (const pkg of packages) {
    const alternativesForPkg = alternatives[pkg] || [];
    installPackage(pkg, alternativesForPkg);
  }
};

const main = () => {
  console.log(chalk.bold.blue('\n🎵 Choral LLM Workbench - Manual Installation\n'));
  console.log(chalk.bold('=====================================\n'));
  
  console.log(chalk.yellow('🔧 Installing Dependencies...'));
  
  console.log(chalk.cyan('\n📦 1. Backend Core Dependencies:'));
  installDependencies(['@nestjs/core', '@nestjs/common', '@nestjs/platform-express'], '@nestjs/websockets'], '@nestjs/platform-socket.io'], 'class-transformer', 'class-validator'], 'reflect-metadata', 'rxjs'], 'axios'], 'uuid'], {
    'class-validator': 'validator'  // Alternative if needed
  }, {
    'reflect-metadata': 'reflect-metadata'  // Alternative if needed
  });
  
  console.log(chalk.cyan('\n📦 2. Backend Audio Dependencies:'));
  installDependencies(['xml2js', 'tone', 'web-audio-api'], 'wavefile'], {
    'tone': 'simple-tone'  // Alternative if needed
  });
  
  console.log(chalk.cyan('\n📦 3. Optional Ollama Integration:'));
  installDependencies(['ollama'], {
    'ollama': 'openai'  // Alternative if needed
  });
  
  console.log(chalk.cyan('\n📦 4. Install Choices:\n'));
  console.log(chalk.gray('   a) Backend only'));
  console.log(chalk.gray('   b) Frontend only'));
  console.log(chalk.gray('   c) Both'));
  console.log(chalk.gray('   d) Selective installation'));
  console.log(chalk.gray('   s) Check environment'));
  console.log(chalk.gray('   x) Exit'));
  
  console.log('\n');
  process.stdout.write('Enter choice (a/b/c/d/s/x): ');
  
  const answer = await new Promise((resolve) => {
    process.stdin.once('data', resolve);
  });
  
  const choice = answer.trim().toLowerCase();
  
  switch (choice) {
    case 'a':
      console.log(chalk.blue('\n🔧 Installing backend dependencies only...'));
      installDependencies(['@nestjs/core', '@nestjs/common', '@nestjs/platform-express', '@nestjs/websockets', '@nestjs/platform-socket.io', 'class-transformer', 'class-validator', 'reflect-metadata', 'rxjs', 'axios', 'uuid'], {
        'xml2js': 'musicxml2json', 'class-validator': 'validator'
      });
      break;
    case 'b':
      console.log(chalk.blue('\n🎨 Installing frontend dependencies only...'));
      installDependencies(['vue@3', '@vitejs/plugin-vue'], 'pinia', 'element-plus', 'tone', 'web-audio-api']);
      break;
    case 'c':
      console.log(chalk.blue('\n🎼 Installing both backend and frontend...'));
      installDependencies(['@nestjs/core', '@nestjs/common', '@nestjs/platform-express', '@nestjs/websockets', '@nestjs/platform-socket.io', 'class-transformer', 'class-validator', 'reflect-metadata', 'rxjs', 'axios', 'uuid', 'xml2js', 'tone', 'web-audio-api', 'vue@3', '@vitejs/plugin-vue', 'pinia', 'element-plus']);
      break;
    case 'd':
      console.log(chalk.blue('\n📦 Selective installation...'));
      installDependencies(['xml2js', 'tone', 'web-audio-api', '@nestjs/core', 'class-validator']);
      break;
    case 's':
      checkEnvironment();
      break;
    case 'x':
      console.log(chalk.yellow('\n� Exiting...'));
      process.exit(0);
      break;
    default:
      console.log(chalk.red('\n❌ Invalid choice. Please select a-x to exit'));
      main();
      break;
  }
}