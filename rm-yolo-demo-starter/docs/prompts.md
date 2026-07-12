# Prompt 记录

请记录你使用 AI 工具辅助开发的关键过程。不要只粘贴完整聊天记录，重点说明你如何判断、采纳和修改 AI 的回答。

## Prompt 1：理解 Starter 代码

我的问题：

```text
请帮我解释 detect.py 中 YOLO 推理、画框和保存结果分别在哪里完成。
```

AI 回答摘要：

```text
1. YOLO推理：run_image函数内，model = YOLO()加载模型，model.predict()执行预测得到检测结果；
2. 画框逻辑：draw_detections函数，通过cv2.rectangle画目标框、cv2.putText绘制类别与置信度文字；
3. 保存结果：run_image函数底部，先自动创建outputs目录，再用cv2.imwrite将标注完成的图片写入指定路径。
同时补充了四段代码对应的行号定位方法，建议在行尾添加#注释标注功能。
```

我采纳了什么：

```text
1. 三段核心代码模块的划分与定位；
2. 在代码行末尾添加#注释标注功能的写法；
3. 区分读取输入、推理、绘图、保存四大完整流程。
```

我没有采纳什么，为什么：

```text
AI提供的批量图片处理、视频推理完整代码，暂时不采纳。当前阶段仅需要弄懂基础图片检测逻辑，批量与视频功能留到Day4自己动手实现，加深代码理解。
```

## Prompt 2：实现多目标过滤

我的问题：

```text
请帮我在 detect.py 中增加 --max-det 参数，只保留置信度最高的前 N 个目标。
```

AI 回答摘要：

```text
1. 使用cv2.VideoCapture打开视频，获取视频宽、高、FPS、总帧数；
2. cv2.VideoWriter创建输出视频文件；
3. 每一帧执行YOLO推理，复用draw_detections绘图函数；
4. 计算实时FPS绘制到画面左上角；
5. 增加键盘监听，按下q或者ESC终止推理；
6. 推理结束释放VideoCapture和VideoWriter资源，防止内存占用。
```

我采纳了什么：

```text
1. 采纳添加--max‑det参数的代码；
2. 采纳置信度排序和截取索引的实现逻辑；
3. 接受args参数传递的方案，修改run_image和run_video的形参列表，调用处传入args；
4. 在单张图片、批量图片循环、视频帧推理三处全部添加筛选代码，保证三处都可以生效；
5. 严格按照4空格缩进编写代码。
```

我自己修改了什么：

```text
1. 最初我没有把args传入run_image函数，出现NameError: name 'args' is not defined报错，我理解了函数作用域原理，手动修改函数定义和调用语句；
2. 一开始if后面的代码没有缩进，程序抛出缩进异常，我对照AI给出的示例修正缩进；
3. 学习boxes.conf和argsort用法，看懂YOLO‑v8返回的boxes结构，明白results[0].boxes是可切片对象；
4. 测试运行命令，执行`--max‑det 2`验证功能，确认只会保留置信度靠前的目标；
5. 后续把这套筛选逻辑复用在批量图片处理、视频帧推理代码里，实现一处参数全局生效。
```

## Prompt 3：实现视频或批量图片处理

我的问题：

```text
帮我完善detect.py代码，实现两个功能：
1. 当--source传入文件夹路径，自动遍历目录里图片文件，批量推理，处理后的图片保存到指定输出目录，文件名和原图保持一致；
2. 编写run_video函数，读取mp4视频逐帧推理，生成标注后的mp4视频，画面显示FPS，按下q键结束运行；
同时复用之前写好的‑‑conf、‑‑max‑det参数。
```

AI 回答摘要：

```text
1. 批量图片部分：在main函数判断如果source是文件夹，筛选`.jpg .jpeg .png .bmp .webp`格式图片；循环读取每张图片，复用YOLO推理与绘图逻辑；利用Path拼接输出路径，保留原文件名；统计全部图片识别到的目标总数并控制台打印；文件夹无图片时给出提示。
2. 视频推理部分：使用cv2.VideoCapture读取视频，获取视频宽、高、FPS、总帧数；通过cv2.VideoWriter创建输出视频；每一帧执行YOLO推理和max‑det筛选；计算实时FPS绘制在画面左上角；监听键盘按键，按下q或者ESC键退出；程序结束之后释放VideoCapture和VideoWriter，避免内存泄漏。
3. 注意：批量图片和视频帧里同样启用max‑det筛选逻辑，并且args参数正确传入，缩进严格遵守Python语法。
4. 给出对应的运行示例命令：批量图片命令、视频推理命令。
```

最终处理结果：

```text
1. 采纳了批量图片的目录遍历、后缀筛选、文件保存逻辑，把之前写好的max‑det筛选代码放到循环内部，每张图片都会根据‑‑max‑det过滤目标；测试命令：python detect.py --source assets/example-images --model models/best.pt --conf 0.3 --max-det 3 --output outputs/images，批量处理全部图片并保存到指定文件夹。
2. 使用AI提供的run_video函数代码，将args参数传入函数内部，每一帧推理后执行置信度筛选；FPS实时绘制在画面；按键退出功能正常；测试视频命令：python detect.py --source assets/example-videos/01.mp4 --model models/best.pt --conf 0.4 --max-det 4 --output outputs/video_result.mp4 --show，视频可以正常生成。
3. 自己排查了MINGW‑Git里的目录路径问题，明白了进入项目文件夹后，代码路径不需要再加外层文件夹前缀；理解了OpenCV视频读写的生命周期，用完必须释放资源。
```
