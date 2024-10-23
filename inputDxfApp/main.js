const { app, BrowserWindow, ipcMain } = require("electron");
const fs = require("fs");
const path = require("path");
const DxfParser = require("dxf-parser");

let mainWindow;

app.on("ready", () => {
  mainWindow = new BrowserWindow({
    width: 1800,
    height: 1600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    },
  });

  // debug
  mainWindow.webContents.openDevTools();
  mainWindow.loadFile("index.html");
});

ipcMain.on("load-dxf-file", (event, filePath) => {
  const parser = new DxfParser();
  console.log("load-dxf-file", filePath);
  const fileContent = fs.readFileSync(path.join(__dirname, filePath), "utf8");

  try {
    const dxfData = parser.parseSync(fileContent);
    console.log("DXF data:", dxfData);
    event.sender.send("dxf-data", dxfData);
  } catch (err) {
    console.error("Error parsing DXF file:", err);
  }
});
