const { app, BrowserWindow } = require("electron");

const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 600,
    height: 400,
    title: "マイアプリ",
  });

  // デベロッパーツールを開く
  mainWindow.webContents.openDevTools({ mode: "detach" });
  mainWindow.loadFile("index.html");
};

app.once("ready", () => {
  createWindow();
});

app.once("window-all-closed", () => app.quit());
