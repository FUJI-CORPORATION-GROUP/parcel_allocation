const { ipcRenderer } = require("electron");
const canvas = document.getElementById("dxfCanvas");
const context = canvas.getContext("2d");
const fs = require("fs");
const path = require("path");

document.getElementById("loadDxfButton").addEventListener("click", () => {
  // メインプロセスにDXFファイル読み込みのリクエストを送信
  filePath = "./dxf/30571-1.dxf";
  filePath = "./dxf/sample.dxf";
  ipcRenderer.send("load-dxf-file", filePath);
});

document.getElementById("makeJsonButton").addEventListener("click", () => {
  saveSelectedEdges();
});

ipcRenderer.on("dxf-data", (event, dxfData) => {
  console.log("DXF data received:", dxfData);
  this.formattedDxfEntityData = getFormattedDxfEntitiesData(dxfData);
  drawDxfOnCanvas(this.formattedDxfEntityData);
});

function drawDxfOnCanvas(entityData) {
  context.clearRect(0, 0, canvas.width, canvas.height);
  console.log("drawDxfOnCanvas", entityData);
  entityData.forEach((entity) => {
    if (entity.type === "LINE") {
      context.beginPath();

      if (selectedEdges.includes(entity)) {
        context.strokeStyle = "red"; // 選択されたエッジは赤色で描画
      } else {
        context.strokeStyle = "black";
      }

      context.moveTo(entity.x1, entity.y1);
      context.lineTo(entity.x2, entity.y2);
      context.stroke();
    }
  });
}

function getFormattedDxfEntitiesData(dxfData) {
  // DXFデータの座標の範囲を計算
  const { minX, minY, maxX, maxY } = calculateBoundingBox(dxfData);
  console.log("min-max", minX, minY, maxX, maxY);

  // Canvasのサイズに合わせてスケールとオフセットを計算
  const dxfWidth = maxX - minX;
  const dxfHeight = maxY - minY;

  // Canvasに収めるためのスケーリング
  const scaleX = canvas.width / dxfWidth;
  const scaleY = canvas.height / dxfHeight;
  const scale = Math.min(scaleX, scaleY); // 横と縦のスケールを同じにするため、最小値を使用

  // DXF全体をCanvasの中央に配置するためのオフセット
  const offsetX = -minX * scale + (canvas.width - dxfWidth * scale) / 2;
  const offsetY = -minY * scale + (canvas.height - dxfHeight * scale) / 2;

  // エンティティをCanvasに描画
  console.log("scale", scale, offsetX, offsetY);
  const formattedDxfEntitiesData = dxfData.entities.map((entity) => {
    if (entity.type === "LINE") {
      return {
        type: "LINE",
        x1: entity.vertices[0].x * scale + offsetX,
        y1: entity.vertices[0].y * scale + offsetY,
        x2: entity.vertices[1].x * scale + offsetX,
        y2: entity.vertices[1].y * scale + offsetY,
      };
    }
  });

  console.log("getFormattedDxfEntitiesData", formattedDxfEntitiesData);

  return formattedDxfEntitiesData;
}

/// DXFデータのバウンディングボックスを計算
function calculateBoundingBox(dxfData) {
  let minX = Infinity,
    minY = Infinity,
    maxX = -Infinity,
    maxY = -Infinity;

  dxfData.entities.forEach((entity) => {
    if (entity.type === "LINE") {
      x1 = entity.vertices[0].x;
      y1 = entity.vertices[0].y;
      x2 = entity.vertices[1].x;
      y2 = entity.vertices[1].y;

      minX = Math.min(minX, x1, x2);
      minY = Math.min(minY, y1, y2);
      maxX = Math.max(maxX, x1, x2);
      maxY = Math.max(maxY, y1, y2);
    }
  });

  return { minX, minY, maxX, maxY };
}

let selectedEdges = []; // 複数の選択されたエッジを保持

canvas.addEventListener("click", (event) => {
  const rect = canvas.getBoundingClientRect();
  const mouseX = event.clientX - rect.left;
  const mouseY = event.clientY - rect.top;

  const clickedEdge = findClickedEdge(
    mouseX,
    mouseY,
    this.formattedDxfEntityData
  );
  console.log("canvas click event", mouseX, mouseY, clickedEdge);
  if (clickedEdge) {
    console.log("Clicked edge:", clickedEdge);
    // selectedEdge = clickedEdge; // エッジがクリックされたら選択
    const index = selectedEdges.indexOf(clickedEdge);

    if (index === -1) {
      // エッジが未選択なら追加
      selectedEdges.push(clickedEdge);
    } else {
      // エッジが選択済みなら選択解除
      selectedEdges.splice(index, 1);
    }

    drawDxfOnCanvas(this.formattedDxfEntityData); // 再描画
  }
});

function findClickedEdge(x, y, dxfData) {
  const tolerance = 5; // クリック位置とエッジの距離の許容範囲
  let clickedEdge = null;
  console.log("findClickedEdge", x, y);
  console.log("findClickedEdge", dxfData);

  dxfData.forEach((entity) => {
    if (entity.type === "LINE") {
      x1 = entity.x1;
      y1 = entity.y1;
      x2 = entity.x2;
      y2 = entity.y2;
      console.log("x-y", x1, y1, x2, y2);

      if (isPointNearLineSegment(x, y, x1, y1, x2, y2, tolerance)) {
        clickedEdge = entity;
      }
    }
  });

  return clickedEdge;
}

function saveSelectedEdges() {
  console.log(selectedEdges);
  const json = JSON.stringify(selectedEdges, null, 2); // JSONに変換

  // 保存するファイルパスを指定 ./output/selectedEdges.json
  const filePath = "./out/selectedEdges.json";

  // ファイルに書き込む
  fs.writeFile(filePath, json, (err) => {
    if (err) {
      console.error("ファイルの保存に失敗しました:", err);
    } else {
      console.log("選択されたエッジを保存しました:", filePath);
    }
  });
}

// 点と線分の距離を計算して、クリックがエッジに近いかどうかを判定
function isPointNearLineSegment(px, py, x1, y1, x2, y2, tolerance) {
  const dist =
    Math.abs((y2 - y1) * px - (x2 - x1) * py + x2 * y1 - y2 * x1) /
    Math.sqrt((y2 - y1) ** 2 + (x2 - x1) ** 2);

  console.log("isPointNearLineSegment", dist <= tolerance);
  return dist <= tolerance;
}
