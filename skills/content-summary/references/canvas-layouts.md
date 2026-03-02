# JSON Canvas 知识卡片布局参考

## 核心布局规则（必须遵守）

### 1. 垂直层级布局（自上而下）

```
Y=0:     [源链接/元数据]
Y=150:   [核心主题]
Y=400:   [观点节点行]
Y=620:   [证据节点行]
Y=820:   [延伸阅读 Group]
```

**关键**: 每层 Y 坐标固定，避免节点垂直重叠。

### 2. 水平居中对齐

以画布中心 X=500 为基准：
- 单个节点: 居中放置
- 多个节点: 均匀分布，保持对称

**计算公式**:
```
总宽度 = 节点数 × 节点宽度 + (节点数-1) × 间距
起始X = 500 - 总宽度/2
节点N的X = 起始X + N × (节点宽度 + 间距)
```

### 3. 固定尺寸标准

| 节点类型 | 宽度 | 高度 | 说明 |
|----------|------|------|------|
| 源链接 | 350 | 80 | 固定 |
| 核心主题 | 450 | 160 | 固定 |
| 观点节点 | 320 | 140 | 固定 |
| 证据节点 | 320 | 100 | 固定 |
| 延伸节点 | 280 | 80 | 固定 |

### 4. 间距标准

| 间距类型 | 像素值 |
|----------|--------|
| 节点水平间距 | 60 |
| 层级垂直间距 | 80 |
| Group 内边距 | 30 |

### 颜色语义

| 颜色代码 | 颜色 | 语义 |
|----------|------|------|
| `"5"` | Cyan | 核心主题 |
| `"4"` | Green | 观点/结论 |
| `"3"` | Yellow | 证据/数据 |
| `"2"` | Orange | 引用/参考 |
| `"1"` | Red | 警告/注意 |
| `"6"` | Purple | 延伸/相关 |

## Simple 模式布局（3个观点）

**精确坐标计算**:
- 画布中心: X=500
- 观点节点宽度: 320, 间距: 60
- 3个观点总宽度: 320×3 + 60×2 = 1080
- 起始X: 500 - 1080/2 = -40

```
Y=0:     源链接 (X=325, 居中)
Y=130:   核心主题 (X=275, 居中)
Y=370:   观点1(-40) | 观点2(340) | 观点3(720)
```

### Simple 模式模板（3个观点）

```json
{
  "nodes": [
    {
      "id": "source_link",
      "type": "link",
      "x": 325,
      "y": 0,
      "width": 350,
      "height": 80,
      "url": "{源URL}"
    },
    {
      "id": "core_topic",
      "type": "text",
      "x": 275,
      "y": 130,
      "width": 450,
      "height": 160,
      "text": "# {核心主题}\n\n{一句话概述}",
      "color": "5"
    },
    {
      "id": "point_1",
      "type": "text",
      "x": -40,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点1\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_2",
      "type": "text",
      "x": 340,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点2\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_3",
      "type": "text",
      "x": 720,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点3\n\n{内容}",
      "color": "4"
    }
  ],
  "edges": [
    {"id": "e_src", "fromNode": "source_link", "fromSide": "bottom", "toNode": "core_topic", "toSide": "top", "color": "2"},
    {"id": "e_p1", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_1", "toSide": "top"},
    {"id": "e_p2", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_2", "toSide": "top"},
    {"id": "e_p3", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_3", "toSide": "top"}
  ]
}
```

## Simple 模式布局（4个观点）

**精确坐标计算**:
- 4个观点总宽度: 320×4 + 60×3 = 1460
- 起始X: 500 - 1460/2 = -230

```
Y=0:     源链接 (X=325, 居中)
Y=130:   核心主题 (X=275, 居中)
Y=370:   观点1(-230) | 观点2(150) | 观点3(530) | 观点4(910)
```

### Simple 模式模板（4个观点）

```json
{
  "nodes": [
    {
      "id": "source_link",
      "type": "link",
      "x": 325,
      "y": 0,
      "width": 350,
      "height": 80,
      "url": "{源URL}"
    },
    {
      "id": "core_topic",
      "type": "text",
      "x": 275,
      "y": 130,
      "width": 450,
      "height": 160,
      "text": "# {核心主题}\n\n{一句话概述}",
      "color": "5"
    },
    {
      "id": "point_1",
      "type": "text",
      "x": -230,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点1\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_2",
      "type": "text",
      "x": 150,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点2\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_3",
      "type": "text",
      "x": 530,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点3\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_4",
      "type": "text",
      "x": 910,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点4\n\n{内容}",
      "color": "4"
    }
  ],
  "edges": [
    {"id": "e_src", "fromNode": "source_link", "fromSide": "bottom", "toNode": "core_topic", "toSide": "top", "color": "2"},
    {"id": "e_p1", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_1", "toSide": "top"},
    {"id": "e_p2", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_2", "toSide": "top"},
    {"id": "e_p3", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_3", "toSide": "top"},
    {"id": "e_p4", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_4", "toSide": "top"}
  ]
}
```

## Simple 模式布局（5个观点）

**精确坐标计算**:
- 5个观点总宽度: 320×5 + 60×4 = 1840
- 起始X: 500 - 1840/2 = -420

```
Y=0:     源链接 (X=325, 居中)
Y=130:   核心主题 (X=275, 居中)
Y=370:   观点1(-420) | 观点2(-40) | 观点3(340) | 观点4(720) | 观点5(1100)
```

### Simple 模式模板（5个观点）

```json
{
  "nodes": [
    {
      "id": "source_link",
      "type": "link",
      "x": 325,
      "y": 0,
      "width": 350,
      "height": 80,
      "url": "{源URL}"
    },
    {
      "id": "core_topic",
      "type": "text",
      "x": 275,
      "y": 130,
      "width": 450,
      "height": 160,
      "text": "# {核心主题}\n\n{一句话概述}",
      "color": "5"
    },
    {
      "id": "point_1",
      "type": "text",
      "x": -420,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点1\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_2",
      "type": "text",
      "x": -40,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点2\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_3",
      "type": "text",
      "x": 340,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点3\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_4",
      "type": "text",
      "x": 720,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点4\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_5",
      "type": "text",
      "x": 1100,
      "y": 370,
      "width": 320,
      "height": 140,
      "text": "## 观点5\n\n{内容}",
      "color": "4"
    }
  ],
  "edges": [
    {"id": "e_src", "fromNode": "source_link", "fromSide": "bottom", "toNode": "core_topic", "toSide": "top", "color": "2"},
    {"id": "e_p1", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_1", "toSide": "top"},
    {"id": "e_p2", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_2", "toSide": "top"},
    {"id": "e_p3", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_3", "toSide": "top"},
    {"id": "e_p4", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_4", "toSide": "top"},
    {"id": "e_p5", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_5", "toSide": "top"}
  ]
}
```

## Detailed 模式布局（带证据层）

**精确坐标计算**:
- 画布中心: X=500
- 节点宽度: 320, 间距: 60
- 3个节点总宽度: 320×3 + 60×2 = 1080
- 起始X: 500 - 1080/2 = -40

```
Y=0:     元数据(-40) | 源链接(720)
Y=150:   核心主题 (X=275, 居中)
Y=390:   观点1(-40) | 观点2(340) | 观点3(720)
Y=610:   证据1(-40) | 证据2(340) | 证据3(720)
Y=790:   延伸阅读 Group (X=-90)
Y=840:   延伸节点行
```

### Detailed 模式模板（3个观点+证据）

```json
{
  "nodes": [
    {
      "id": "group_extend",
      "type": "group",
      "x": -90,
      "y": 790,
      "width": 1180,
      "height": 160,
      "label": "延伸阅读",
      "color": "6"
    },
    {
      "id": "meta_info",
      "type": "text",
      "x": -40,
      "y": 0,
      "width": 300,
      "height": 100,
      "text": "**来源**: {作者}\n**日期**: {日期}\n**类型**: {类型}"
    },
    {
      "id": "source_link",
      "type": "link",
      "x": 720,
      "y": 0,
      "width": 350,
      "height": 80,
      "url": "{源URL}"
    },
    {
      "id": "core_topic",
      "type": "text",
      "x": 275,
      "y": 150,
      "width": 450,
      "height": 160,
      "text": "# {核心主题}\n\n{概述}",
      "color": "5"
    },
    {
      "id": "point_1",
      "type": "text",
      "x": -40,
      "y": 390,
      "width": 320,
      "height": 140,
      "text": "## 观点1\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_2",
      "type": "text",
      "x": 340,
      "y": 390,
      "width": 320,
      "height": 140,
      "text": "## 观点2\n\n{内容}",
      "color": "4"
    },
    {
      "id": "point_3",
      "type": "text",
      "x": 720,
      "y": 390,
      "width": 320,
      "height": 140,
      "text": "## 观点3\n\n{内容}",
      "color": "4"
    },
    {
      "id": "evidence_1",
      "type": "text",
      "x": -40,
      "y": 610,
      "width": 320,
      "height": 100,
      "text": "**证据**\n\n{支撑内容}",
      "color": "3"
    },
    {
      "id": "evidence_2",
      "type": "text",
      "x": 340,
      "y": 610,
      "width": 320,
      "height": 100,
      "text": "**证据**\n\n{支撑内容}",
      "color": "3"
    },
    {
      "id": "evidence_3",
      "type": "text",
      "x": 720,
      "y": 610,
      "width": 320,
      "height": 100,
      "text": "**证据**\n\n{支撑内容}",
      "color": "3"
    },
    {
      "id": "extend_1",
      "type": "text",
      "x": -40,
      "y": 840,
      "width": 280,
      "height": 80,
      "text": "[[{相关主题1}]]",
      "color": "6"
    },
    {
      "id": "extend_2",
      "type": "text",
      "x": 300,
      "y": 840,
      "width": 280,
      "height": 80,
      "text": "[[{相关主题2}]]",
      "color": "6"
    },
    {
      "id": "extend_3",
      "type": "text",
      "x": 640,
      "y": 840,
      "width": 280,
      "height": 80,
      "text": "[[{相关主题3}]]",
      "color": "6"
    }
  ],
  "edges": [
    {"id": "e_meta", "fromNode": "meta_info", "fromSide": "right", "toNode": "core_topic", "toSide": "left"},
    {"id": "e_src", "fromNode": "source_link", "fromSide": "left", "toNode": "core_topic", "toSide": "right", "color": "2"},
    {"id": "e_p1", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_1", "toSide": "top"},
    {"id": "e_p2", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_2", "toSide": "top"},
    {"id": "e_p3", "fromNode": "core_topic", "fromSide": "bottom", "toNode": "point_3", "toSide": "top"},
    {"id": "e_ev1", "fromNode": "point_1", "fromSide": "bottom", "toNode": "evidence_1", "toSide": "top", "label": "支撑"},
    {"id": "e_ev2", "fromNode": "point_2", "fromSide": "bottom", "toNode": "evidence_2", "toSide": "top", "label": "支撑"},
    {"id": "e_ev3", "fromNode": "point_3", "fromSide": "bottom", "toNode": "evidence_3", "toSide": "top", "label": "支撑"}
  ]
}
```

## 动态布局计算公式

当观点数量不是 3/4/5 时，使用以下公式计算：

```javascript
// 配置
const CENTER_X = 500;
const NODE_WIDTH = 320;
const NODE_GAP = 60;

// 计算一行节点的起始 X 坐标
function calcRowStartX(nodeCount) {
  const totalWidth = nodeCount * NODE_WIDTH + (nodeCount - 1) * NODE_GAP;
  return CENTER_X - totalWidth / 2;
}

// 计算第 N 个节点的 X 坐标 (N 从 0 开始)
function calcNodeX(nodeIndex, nodeCount) {
  const startX = calcRowStartX(nodeCount);
  return startX + nodeIndex * (NODE_WIDTH + NODE_GAP);
}

// 示例：6 个观点
// 总宽度 = 6 * 320 + 5 * 60 = 2220
// 起始X = 500 - 2220/2 = -610
// 节点X: -610, -230, 150, 530, 910, 1290
```

## 特殊布局

### 对比型布局（2列）

用于比较两个概念或方案：

```
Y=0:     核心问题 (居中)
Y=200:   方案A(X=100) | 方案B(X=580)
Y=400:   优点A(X=100) | 优点B(X=580)
Y=560:   缺点A(X=100) | 缺点B(X=580)
```

### 时间线布局（水平）

用于有明确时间顺序的内容：

```
Y=200:   [起点] → [事件1] → [事件2] → [事件3] → [当前]
X:       0        300       600       900       1200
```

## ID 生成

使用 16 字符小写十六进制字符串：

```javascript
function generateId() {
  return Array.from({length: 16}, () => 
    Math.floor(Math.random() * 16).toString(16)
  ).join('');
}
```

## 布局检查清单

生成 Canvas 前确认：

- [ ] 所有节点 Y 坐标按层级递增，无垂直重叠
- [ ] 同一行节点 X 坐标均匀分布，无水平重叠
- [ ] 边缘连接方向一致（上层 bottom → 下层 top）
- [ ] Group 节点在数组最前面（z-index 最低）
- [ ] 所有 ID 唯一且为 16 位十六进制
