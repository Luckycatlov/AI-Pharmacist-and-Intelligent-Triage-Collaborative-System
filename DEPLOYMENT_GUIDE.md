# 医疗问答系统 - LangServe + Docker 部署指南

## 📋 部署概述

本指南将帮助您将医疗问答多智能体系统部署为LangServe服务，并提供Docker容器化支持。

### 部署方式对比

| 方式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 本地LangServe | 简单快速，便于开发 | 需要保持运行 | 开发测试、局域网使用 |
| Docker容器 | 环境一致，易于部署 | 需要学习Docker | 生产环境、团队协作 |
| Docker Compose | 一键启动完整环境 | 配置稍复杂 | 完整系统部署 |

---

## 🚀 方式一：本地LangServe部署（推荐新手）

### 1. 安装依赖

```bash
# 安装部署所需的依赖
pip install -r requirements.txt
```

### 2. 启动服务

#### Windows系统：
```bash
# 双击运行
start_deploy.bat

# 或命令行运行
python deploy.py
```

#### Linux/Mac系统：
```bash
# 添加执行权限
chmod +x start_deploy.sh

# 运行启动脚本
./start_deploy.sh
```

#### 直接启动：
```bash
python deploy.py
```

### 3. 访问服务

服务启动后，您可以通过以下地址访问：

- **服务地址**: http://localhost:8000
- **API文档**: http://localhost:8000/docs （推荐）
- **健康检查**: http://localhost:8000/health
- **问答接口**: http://localhost:8000/qa

### 4. 测试部署

```bash
# 运行自动化测试
python test_deploy.py

# 或手动测试API
curl http://localhost:8000/health
```

### 5. 使用API

#### 方式1：使用Swagger UI（最简单）
1. 浏览器打开 http://localhost:8000/docs
2. 找到 `/qa` 端点
3. 点击 "Try it out"
4. 输入问题并执行

#### 方式2：使用Python
```python
import requests

response = requests.post(
    "http://localhost:8000/qa",
    json={"question": "小儿清热止咳合剂的主要成分是什么？"}
)

answer = response.json()["answer"]
print(answer)
```

#### 方式3：使用curl
```bash
curl -X POST "http://localhost:8000/qa" \
     -H "Content-Type: application/json" \
     -d '{"question": "小儿清热止咳合剂的主要成分是什么？"}'
```

---

## 🐳 方式二：Docker容器部署

### 1. 安装Docker

#### Windows:
1. 下载 Docker Desktop: https://www.docker.com/products/docker-desktop/
2. 安装并启动Docker Desktop

#### Linux:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose

# 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker
```

#### Mac:
```bash
# 使用Homebrew安装
brew install docker docker-compose
```

### 2. 构建Docker镜像

```bash
# 构建镜像
docker build -t medical-qa-system .

# 查看镜像
docker images | grep medical-qa
```

### 3. 运行Docker容器

#### 基础运行：
```bash
docker run -d \
  -p 8000:8000 \
  --name medical-qa-api \
  medical-qa-system
```

#### 持久化数据运行：
```bash
docker run -d \
  -p 8000:8000 \
  --name medical-qa-api \
  -v $(pwd)/chroma_db:/app/chroma_db \
  -v $(pwd)/memory:/app/memory \
  -v $(pwd)/data:/app/data \
  medical-qa-system
```

#### 查看日志：
```bash
# 查看容器日志
docker logs medical-qa-api

# 实时查看日志
docker logs -f medical-qa-api
```

#### 停止容器：
```bash
# 停止容器
docker stop medical-qa-api

# 删除容器
docker rm medical-qa-api
```

### 4. 测试Docker部署

```bash
# 等待容器启动（约30秒）
sleep 30

# 测试健康检查
curl http://localhost:8000/health

# 运行完整测试
python test_deploy.py
```

---

## 🎮 方式三：Docker Compose部署（推荐）

### 1. 一键启动完整环境

```bash
# 启动所有服务
docker-compose up -d

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f medical-qa-api
```

### 2. 管理服务

```bash
# 停止服务
docker-compose stop

# 重启服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 重新构建并启动
docker-compose up -d --build
```

### 3. Docker Compose特性

- ✅ **自动重启**: 容器崩溃时自动重启
- ✅ **健康检查**: 自动监控服务健康状态
- ✅ **数据持久化**: 自动挂载数据目录
- ✅ **网络隔离**: 独立的Docker网络
- ✅ **环境变量**: 支持配置文件管理

---

## 🧪 测试和验证

### 自动化测试

```bash
# 运行完整测试套件
python test_deploy.py

# 测试不同的API地址
python test_deploy.py http://your-server-ip:8000
```

### 手动验证清单

- [ ] 访问 http://localhost:8000/docs 查看API文档
- [ ] 测试健康检查: `curl http://localhost:8000/health`
- [ ] 测试问答接口: `python test_deploy.py`
- [ ] 查看容器日志: `docker logs medical-qa-api`
- [ ] 检查数据持久化: 重启后数据是否保留

---

## 🔧 常见问题解决

### 问题1：端口8000被占用

**错误**: `Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
netstat -ano | findstr :8000  # Windows
lsof -i :8000                  # Linux/Mac

# 杀死进程或更改端口
# 编辑 deploy.py，将端口改为8001
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### 问题2：Docker构建失败

**错误**: `pip install` 失败

**解决方案**:
```bash
# 清理Docker缓存
docker system prune -a

# 使用国内镜像源
# 编辑 Dockerfile，添加：
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 问题3：模型文件未找到

**错误**: `Model not found`

**解决方案**:
```bash
# 下载模型
python setup_model.py

# 或在Docker中挂载模型目录
docker run -v $(pwd)/models:/app/models medical-qa-system
```

### 问题4：内存不足

**错误**: `Out of memory`

**解决方案**:
```bash
# 增加Docker内存限制
docker run -m 4g -d medical-qa-system

# 或在docker-compose.yml中添加：
services:
  medical-qa-api:
    mem_limit: 4g
```

---

## 📊 性能优化建议

### 1. 生产环境配置

```python
# deploy.py 中使用生产级配置
if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4,              # 多进程
        log_level="warning",     # 减少日志
        access_log=False,        # 关闭访问日志
        limit_concurrency=100    # 限制并发
    )
```

### 2. Docker资源限制

```yaml
# docker-compose.yml
services:
  medical-qa-api:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          memory: 2G
```

### 3. 负载均衡

```yaml
# 启动多个实例
docker-compose up -d --scale medical-qa-api=3

# 配置Nginx负载均衡
upstream medical_backend {
    server localhost:8001;
    server localhost:8002;
    server localhost:8003;
}
```

---

## 🚀 下一步：云端部署

完成本地Docker部署后，您可以选择：

### 1. 免费云平台
- **Railway.app**: 一键部署，每月$5免费额度
- **Render.com**: 免费套餐，750小时/月
- **Vercel**: 适合API服务，全球CDN

### 2. 云服务器
- **阿里云/腾讯云**: 学生机10元/月起
- **AWS Lightsail**: $3.5/月起
- **Google Cloud**: $300免费额度

### 3. Kubernetes（大规模）
- **阿里云ACK**: 托管K8s服务
- **腾讯云TKE**: 弹性容器服务
- **AWS EKS**: 企业级K8s

---

## 📝 维护和监控

### 日志管理

```bash
# 查看实时日志
docker logs -f medical-qa-api

# 导出日志
docker logs medical-qa-api > api.log

# 日志轮转（在代码中实现）
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler('api.log', maxBytes=10*1024*1024, backupCount=5)
```

### 健康监控

```bash
# 定期健康检查
watch -n 30 'curl http://localhost:8000/health'

# 或使用监控系统
# - Prometheus + Grafana
# - ELK Stack (Elasticsearch, Logstash, Kibana)
```

### 备份策略

```bash
# 备份重要数据
docker cp medical-qa-api:/app/chroma_db ./backup/chroma_db
docker cp medical-qa-api:/app/memory ./backup/memory

# 定期备份脚本
#!/bin/bash
DATE=$(date +%Y%m%d)
docker cp medical-qa-api:/app/chroma_db ./backup/chroma_db_$DATE
tar -czf backup_$DATE.tar.gz ./backup/chroma_db_$DATE
```

---

## 🎯 总结

通过本指南，您已经学会了：

1. ✅ 本地LangServe部署
2. ✅ Docker容器化
3. ✅ Docker Compose编排
4. ✅ 健康检查和测试
5. ✅ 问题排查和解决

**您现在拥有一个完整的、可部署的医疗问答API服务！**

需要帮助或遇到问题？请参考：
- 项目文档: README.md
- 评估系统: evaluation/README.md
- GitHub Issues: https://github.com/Luckycatlov/AI-Pharmacist-and-Intelligent-Triage-Collaborative-System/issues

---

**祝您部署顺利！🏥✨**