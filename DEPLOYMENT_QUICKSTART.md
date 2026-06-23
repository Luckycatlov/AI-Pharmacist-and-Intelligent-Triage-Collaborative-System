# 🚀 部署快速开始

## 立即开始（3步部署）

### 第1步：安装依赖（1分钟）
```bash
pip install -r requirements.txt
```

### 第2步：启动服务（2分钟）
```bash
# Windows用户
start_deploy.bat

# Linux/Mac用户
./start_deploy.sh

# 或直接运行
python deploy.py
```

### 第3步：测试服务（1分钟）
```bash
# 浏览器打开
http://localhost:8000/docs

# 或运行测试
python test_deploy.py
```

---

## 📱 快速测试

### 方式1：浏览器测试（推荐）
1. 打开浏览器
2. 访问 http://localhost:8000/docs
3. 点击 `/qa` 端点的 "Try it out"
4. 输入问题：`小儿清热止咳合剂的主要成分是什么？`
5. 点击 "Execute"

### 方式2：命令行测试
```bash
curl -X POST "http://localhost:8000/qa" \
  -H "Content-Type: application/json" \
  -d '{"question": "2岁孩子发烧可以用阿司匹林吗？"}'
```

### 方式3：Python测试
```python
import requests

response = requests.post(
    "http://localhost:8000/qa",
    json={"question": "孕妇可以服用感冒药吗？"}
)

print(response.json()["answer"])
```

---

## 🐳 Docker快速部署

```bash
# 1. 构建镜像
docker build -t medical-qa-system .

# 2. 运行容器
docker run -d -p 8000:8000 --name medical-qa-api medical-qa-system

# 3. 等待30秒后测试
sleep 30
curl http://localhost:8000/health

# 4. 查看日志
docker logs -f medical-qa-api
```

---

## 🎯 验证清单

- [ ] 服务启动成功（访问 http://localhost:8000）
- [ ] API文档可查看（http://localhost:8000/docs）
- [ ] 健康检查正常（http://localhost:8000/health）
- [ ] 问答功能正常（test_deploy.py 通过）
- [ ] 日志输出正常（无ERROR级别日志）

**详细指南**: 请查看 [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)