# RM YOLO Demo Starter

这是 25 届 RM 算法组年度考核的极简 Starter。当前阶段直接使用参考仓库自带的 drone demo 数据集，不加入赛题专用数据要求。

学生需要在此基础上完成 YOLO 二次开发、Git 规范提交、README、Prompt 记录和个人反思。

## 当前 Starter 已包含

- YOLOv8 权重加载
- 单张图片读取
- 基础目标检测
- 目标框、类别名和置信度绘制
- 结果图片保存到 `outputs/`

## 学生需要二次开发

- `--max-det`：保留置信度最高的前 N 个目标
- 视频输入和输出：`assets/example-videos/01.mp4` -> `outputs/01_result.mp4`
- 批量图片处理：`assets/example-images/` -> `outputs/images/`
- 输出处理统计信息
- `docs/prompts.md`：AI 使用记录
- `docs/reflection.md`：个人反思

可选拓展：

- 增加指定类别过滤，例如 `--class-id` 或 `--class-name`
- 增加目标中心点、ROI 颜色统计等可视化

## 数据说明

当前 Starter 使用参考仓库 `ynsrc/python-yolov8-examples` 的 demo 数据：

- 权重：`models/best.pt`
- 图片：`assets/example-images/*.jpg`
- 视频：`assets/example-videos/01.mp4`

这些文件只用于教学和环境验证。第三方来源说明见 `THIRD_PARTY_NOTICES.md`。

## 环境安装

建议 Python 版本：3.9-3.11。

```bash
pip install -r requirements.txt
```

如果需要使用独立虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

如果遇到 `os.setsid`、`safe_run` 或 YOLO 初始化阶段报错，通常是本机 `ultralytics` 版本不合适。先执行：

```bash
pip install --upgrade -r requirements.txt
```

## 运行示例

单张图片：

```bash
python detect.py --source assets/example-images/01.jpg --output outputs/01_result.jpg
```

调整置信度阈值：

```bash
python detect.py --source assets/example-images/01.jpg --conf 0.4 --output outputs/01_conf_04.jpg
```

显示 OpenCV 窗口：

```bash
python detect.py --source assets/example-images/01.jpg --show
```

学生完成二次开发后，建议支持：

```bash
python detect.py --source assets/example-images --conf 0.4 --output outputs/images
python detect.py --source assets/example-videos/01.mp4 --conf 0.4 --max-det 8 --output outputs/01_result.mp4
```

## 目录结构

```text
rm-yolo-demo-starter/
├─ README.md
├─ requirements.txt
├─ detect.py
├─ models/
│  └─ best.pt
├─ assets/
│  ├─ example-images/
│  │  ├─ 01.jpg
│  │  └─ ...
│  └─ example-videos/
│     └─ 01.mp4
├─ outputs/
│  └─ .gitkeep
└─ docs/
   ├─ prompts.md
   └─ reflection.md
```

## 建议 Git 提交节奏

```bash
git commit -m "chore: run starter detection successfully"
git commit -m "feat: add max detection filtering"
git commit -m "feat: support video inference"
git commit -m "feat: support batch image inference"
git commit -m "docs: add prompts and reflection"
```

## 参考来源

- YOLO 示例参考仓库：<https://github.com/ynsrc/python-yolov8-examples>
- Ultralytics 官方仓库：<https://github.com/ultralytics/ultralytics>
- Ultralytics Python 文档：<https://docs.ultralytics.com/usage/python/>
