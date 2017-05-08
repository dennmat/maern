const {app, BrowserWindow, ipcMain} = require('electron');
const path = require('path');
const url = require('url');
const Socket = require('net').Socket;

// Keep a global reference of the window object, if you don't, the window will
// be closed automatically when the JavaScript object is garbage collected.
let win;
let server;

function createWindow () {
  // Create the browser window.
  win = new BrowserWindow({width: 1024, height: 768});
  
  win.setMenu(null);

  // and load the index.html of the app.
  win.loadURL(url.format({
    pathname: path.join(__dirname, 'app/index.html'),
    protocol: 'file:',
    slashes: true
  }));

  // Open the DevTools.
  win.webContents.openDevTools();
 setTimeout(() => {
  win.webContents.send('test-one', 1);
 },500);


  server = new ServerConnector();

  ipcMain.on('send-command', (e, command, mode) => {
    server.write(JSON.stringify({
        "command": command,
        "mode": mode
    }));
  });


  // Emitted when the window is closed.
  win.on('closed', () => {
    // Dereference the window object, usually you would store windows
    // in an array if your app supports multi windows, this is the time
    // when you should delete the corresponding element.
    win = null;
  });
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.on('ready', createWindow);

// Quit when all windows are closed.
app.on('window-all-closed', () => {
  // On macOS it is common for applications and their menu bar
  // to stay active until the user quits explicitly with Cmd + Q
  if (process.platform !== 'darwin') {
    app.quit();
  }
})

app.on('activate', () => {
  // On macOS it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (win === null) {
    createWindow();
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
class ServerConnector {
    constructor() {
        this.socket = Socket();
        this.socket.connect(5000);
    }

    write(data) {
        let buffer = Buffer.from(data, 'utf8');
        let sizeBuffer = Buffer.alloc(4);
        sizeBuffer.writeInt16BE(data.length, 0);
        let outputBuffer = Buffer.concat([sizeBuffer, buffer], 4 + buffer.length);
        console.log("Writting", sizeBuffer, outputBuffer);
        this.socket.write(outputBuffer);
    }
};
/*
var s = require('net').Socket();
s.connect(8080);
s.write('Hello');
s.end();
*/